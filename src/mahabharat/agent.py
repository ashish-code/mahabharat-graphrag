"""
Graph RAG Agent with two retrieval tools:
  1. graph_lookup   — structured graph traversal for relationship/factual questions
  2. passage_search — semantic vector search for narrative/context questions

The LLM decides which tool(s) to call based on the question.
"""
import json
from typing import List, Dict, Optional
import anthropic
from .config import ANTHROPIC_API_KEY, ANSWER_MODEL, EXTRACTION_MODEL
from .graph import find_nodes, get_subgraph_context
from .vector_store import similarity_search

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Tool definitions for Claude ───────────────────────────────────────────────
TOOLS = [
    {
        "name": "graph_lookup",
        "description": (
            "Look up characters, places, events, and their relationships in the "
            "Mahabharata knowledge graph. Use this for questions about: "
            "who is related to whom, family trees, alliances, enemies, who killed whom, "
            "which kingdom someone rules, who taught whom, marriages, parentage. "
            "Input: a list of entity names to look up."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of character/place/event names to look up in the graph",
                }
            },
            "required": ["entities"],
        },
    },
    {
        "name": "passage_search",
        "description": (
            "Search the Mahabharata text for narrative passages relevant to the question. "
            "Use this for questions about: events, battles, stories, why something happened, "
            "descriptions of events, context behind decisions, philosophical teachings (Gita), "
            "curses, boons, and narrative details not captured in relationships."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query to find relevant passages",
                }
            },
            "required": ["query"],
        },
    },
]

SYSTEM_PROMPT = """\
You are an expert on the Mahabharata epic, powered by a Graph RAG system with two retrieval tools.

ALWAYS use tools before answering. Never answer from memory alone.

Strategy:
- For relationship/family/who-killed-whom questions → use graph_lookup
- For narrative/event/why/how questions → use passage_search
- For complex questions → use BOTH tools

After retrieving context, provide a comprehensive, accurate answer (100-200 words).
Cite specific relationships and events from the retrieved context.
If context is insufficient, say so rather than hallucinating.
"""


def run_tool(tool_name: str, tool_input: dict, graph, vector_store) -> str:
    """Execute a tool call and return its string result."""
    if tool_name == "graph_lookup":
        entities = tool_input.get("entities", [])
        seed_nodes = find_nodes(graph, entities)
        if not seed_nodes:
            return f"No entities found in graph for: {entities}. Try different spellings."
        context, visited = get_subgraph_context(graph, seed_nodes, hops=2, max_nodes=25)
        return f"Found {len(visited)} related entities.\n\n{context}"

    elif tool_name == "passage_search":
        query = tool_input.get("query", "")
        passages = similarity_search(vector_store, query, k=5)
        return "\n\n---\n\n".join(passages)

    return "Unknown tool"


def chat(
    question: str,
    graph,
    vector_store,
    history: Optional[List[Dict]] = None,
) -> Dict:
    """
    Run the Graph RAG agent loop.
    Returns dict with answer, tool_calls made, and context snippets.
    """
    messages = []

    # Add conversation history
    if history:
        for h in history:
            messages.append(h)

    # Add current question
    messages.append({"role": "user", "content": question})

    tool_calls_log = []
    graph_context_parts = []
    passage_context_parts = []

    # Agentic loop — Claude decides which tools to call
    while True:
        response = client.messages.create(
            model=ANSWER_MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Check stop reason
        if response.stop_reason == "end_turn":
            # Extract final text answer
            answer_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    answer_text = block.text
            break

        if response.stop_reason == "tool_use":
            # Append Claude's response (with tool_use blocks) to messages
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    result = run_tool(tool_name, tool_input, graph, vector_store)

                    tool_calls_log.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result_preview": result[:300] + "..." if len(result) > 300 else result,
                    })

                    if tool_name == "graph_lookup":
                        graph_context_parts.append(result)
                    else:
                        passage_context_parts.append(result)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result,
                    })

            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop
            answer_text = "Could not generate a response."
            break

    return {
        "answer": answer_text,
        "tool_calls": tool_calls_log,
        "graph_context": "\n\n".join(graph_context_parts),
        "passage_context": "\n\n---\n\n".join(passage_context_parts),
        # Return assistant message for history
        "assistant_message": {"role": "assistant", "content": answer_text},
    }
