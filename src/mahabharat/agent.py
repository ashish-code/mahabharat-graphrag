"""
Graph RAG Agent with two retrieval tools via AWS Bedrock converse API.
  1. graph_lookup   — structured graph traversal for relationship/factual questions
  2. passage_search — semantic vector search for narrative/context questions
"""
import json
from typing import List, Dict, Optional
from .config import get_bedrock_client, ANSWER_MODEL, EXTRACTION_MODEL
from .hybrid_retriever import hybrid_graph_lookup, hybrid_passage_search

# ── Tool definitions (Bedrock converse toolConfig format) ─────────────────────
TOOLS = [
    {
        "toolSpec": {
            "name": "graph_lookup",
            "description": (
                "Look up characters, places, events, and their relationships in the "
                "Mahabharata knowledge graph. Use this for questions about: "
                "who is related to whom, family trees, alliances, enemies, who killed whom, "
                "which kingdom someone rules, who taught whom, marriages, parentage."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Character/place/event names to look up in the graph",
                        }
                    },
                    "required": ["entities"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "passage_search",
            "description": (
                "Search the Mahabharata text for narrative passages relevant to the question. "
                "Use this for questions about: events, battles, why something happened, "
                "philosophical teachings (Gita), curses, boons, and story context."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query for relevant passages",
                        }
                    },
                    "required": ["query"],
                }
            },
        }
    },
]

SYSTEM_PROMPT = (
    "You are an expert on the Mahabharata epic, powered by a Graph RAG system.\n"
    "You have two retrieval tools:\n"
    "  • graph_lookup  — structured facts: family trees, relationships, alliances, who killed whom\n"
    "  • passage_search — narrative context: events, reasons, teachings, curses, boons\n\n"
    "ALWAYS call at least one tool before answering. Never answer from memory alone.\n\n"
    "=== ROUTING EXAMPLES ===\n\n"
    'Q: "Who is the father of Arjuna?"\n'
    '→ graph_lookup(entities=["Arjuna"]) — pure relationship question, one tool sufficient.\n\n'
    'Q: "What happened during the dice game?"\n'
    '→ passage_search(query="dice game Yudhishthira Shakuni") — narrative question, one tool sufficient.\n\n'
    'Q: "Why did Karna not reveal his parentage to the Pandavas?"\n'
    '→ graph_lookup(entities=["Karna","Kunti","Pandavas"]) first — get relationship facts.\n'
    '→ passage_search(query="Karna parentage secret loyalty Duryodhana") second — get narrative.\n'
    "→ Synthesise both in your answer.\n\n"
    "=== ANSWER FORMAT ===\n"
    "Write 100–200 words. Cite specific graph relationships and passage events.\n"
    "Do not fabricate details absent from the retrieved context."
)


def _extract_question_entities(question: str, G) -> List[str]:
    """Scan question text for graph node names (case-insensitive, O(n·m))."""
    q_lower = question.lower()
    return [node for node in G.nodes if node.lower() in q_lower]


def _run_tool(name: str, tool_input: dict, graph, vector_store, question: str = "") -> str:
    if name == "graph_lookup":
        entities = tool_input.get("entities", [])
        return hybrid_graph_lookup(question, entities, graph, vector_store)

    if name == "passage_search":
        query = tool_input.get("query", "")
        return hybrid_passage_search(query, graph, vector_store)

    return "Unknown tool"


def chat(
    question: str,
    graph,
    vector_store,
    history: Optional[List[Dict]] = None,
) -> Dict:
    """Run the Graph RAG agentic loop via Bedrock converse."""
    client = get_bedrock_client()

    # Ensure history content is always in Bedrock list-of-blocks format
    messages = []
    for h in (history or []):
        content = h["content"]
        if isinstance(content, str):
            content = [{"text": content}]
        messages.append({"role": h["role"], "content": content})
    # 4B: pre-inject known entity names found in the question as a hint
    question_entities = _extract_question_entities(question, graph)
    user_text = question
    if question_entities:
        hint = f"[Identified entities in this question: {', '.join(question_entities)}]\n\n"
        user_text = hint + question
    messages.append({"role": "user", "content": [{"text": user_text}]})

    tool_calls_log = []
    graph_context_parts = []
    passage_context_parts = []
    answer_text = ""

    while True:
        response = client.converse(
            modelId=ANSWER_MODEL,
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages,
            toolConfig={"tools": TOOLS, "toolChoice": {"auto": {}}},
            inferenceConfig={"maxTokens": 2048, "temperature": 0},
        )

        output_message = response["output"]["message"]
        messages.append(output_message)
        stop_reason = response["stopReason"]

        if stop_reason == "end_turn":
            for block in output_message["content"]:
                if "text" in block:
                    answer_text = block["text"]
            break

        if stop_reason == "tool_use":
            tool_results = []
            for block in output_message["content"]:
                if block.get("type") != "toolUse" and "toolUse" not in block:
                    continue
                tool_block = block.get("toolUse", block)
                name       = tool_block["name"]
                tool_input = tool_block["input"]
                tool_id    = tool_block["toolUseId"]

                result = _run_tool(name, tool_input, graph, vector_store, question=question)

                tool_calls_log.append({
                    "tool": name,
                    "input": tool_input,
                    "result_preview": result[:300] + "..." if len(result) > 300 else result,
                })
                (graph_context_parts if name == "graph_lookup" else passage_context_parts).append(result)

                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_id,
                        "content": [{"text": result}],
                    }
                })

            messages.append({"role": "user", "content": tool_results})
        else:
            answer_text = "Could not generate a response."
            break

    # 4D: derive sources summary from tool call log
    graph_entities_cited = [
        e for tc in tool_calls_log if tc["tool"] == "graph_lookup"
        for e in tc["input"].get("entities", [])
    ]
    passage_queries_used = [
        tc["input"].get("query", "")
        for tc in tool_calls_log if tc["tool"] == "passage_search"
    ]

    return {
        "answer":           answer_text,
        "tool_calls":       tool_calls_log,
        "graph_context":    "\n\n".join(graph_context_parts),
        "passage_context":  "\n\n---\n\n".join(passage_context_parts),
        "assistant_message": {"role": "assistant", "content": [{"text": answer_text}]},
        "sources": {
            "graph_entities": list(dict.fromkeys(graph_entities_cited)),
            "passage_queries": passage_queries_used,
        },
    }
