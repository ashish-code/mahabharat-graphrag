"""
Graph RAG Agent with two retrieval tools via AWS Bedrock converse API.
  1. graph_lookup   — structured graph traversal for relationship/factual questions
  2. passage_search — semantic vector search for narrative/context questions
"""
import json
from typing import List, Dict, Optional
from .config import get_bedrock_client, ANSWER_MODEL, EXTRACTION_MODEL
from .graph import find_nodes, get_subgraph_context
from .vector_store import similarity_search

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
    "ALWAYS use tools before answering. Never answer from memory alone.\n\n"
    "Strategy:\n"
    "- Relationship/family/who-killed-whom questions → use graph_lookup\n"
    "- Narrative/event/why/how questions → use passage_search\n"
    "- Complex questions → use BOTH tools\n\n"
    "After retrieving context, provide a comprehensive accurate answer (100-200 words). "
    "Cite specific relationships and events from the retrieved context."
)


def _run_tool(name: str, tool_input: dict, graph, vector_store) -> str:
    if name == "graph_lookup":
        entities = tool_input.get("entities", [])
        seed_nodes = find_nodes(graph, entities)
        if not seed_nodes:
            return f"No entities found in graph for: {entities}."
        context, visited = get_subgraph_context(graph, seed_nodes, hops=2, max_nodes=25)
        return f"Found {len(visited)} related entities.\n\n{context}"

    if name == "passage_search":
        passages = similarity_search(vector_store, tool_input.get("query", ""), k=5)
        return "\n\n---\n\n".join(passages)

    return "Unknown tool"


def chat(
    question: str,
    graph,
    vector_store,
    history: Optional[List[Dict]] = None,
) -> Dict:
    """Run the Graph RAG agentic loop via Bedrock converse."""
    client = get_bedrock_client()

    messages = list(history or [])
    messages.append({"role": "user", "content": [{"text": question}]})

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

                result = _run_tool(name, tool_input, graph, vector_store)

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

    return {
        "answer": answer_text,
        "tool_calls": tool_calls_log,
        "graph_context": "\n\n".join(graph_context_parts),
        "passage_context": "\n\n---\n\n".join(passage_context_parts),
        "assistant_message": {"role": "assistant", "content": [{"text": answer_text}]},
    }
