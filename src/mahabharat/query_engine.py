"""Graph RAG query engine."""
import re
import json
import anthropic
from typing import List, Dict, Tuple
from .config import ANTHROPIC_API_KEY, ANSWER_MODEL, EXTRACTION_MODEL, TOP_K_VECTOR, TOP_K_GRAPH_HOPS, MAX_GRAPH_CONTEXT_NODES
from .graph import find_nodes, get_subgraph_context
from .vector_store import similarity_search

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

ENTITY_EXTRACT_PROMPT = """\
Extract all character names, place names, and event names from this question about the Mahabharata.
Return ONLY a JSON array of strings. Example: ["Arjuna", "Kurukshetra", "Drona"]

Question: {question}
"""

ANSWER_PROMPT = """\
You are an expert on the Mahabharata epic. Answer the user's question using ONLY the provided context.
Be specific, accurate, and cite relationships and events from the context.
If the context doesn't contain enough information, say so clearly.

=== GRAPH CONTEXT (entities and relationships) ===
{graph_context}

=== PASSAGE CONTEXT (relevant text from the book) ===
{passage_context}

=== USER QUESTION ===
{question}

Provide a comprehensive answer based on the above context:"""


def extract_query_entities(question: str) -> List[str]:
    """Use Claude Haiku to extract named entities from the question."""
    try:
        msg = client.messages.create(
            model=EXTRACTION_MODEL,
            max_tokens=256,
            messages=[{"role": "user", "content": ENTITY_EXTRACT_PROMPT.format(question=question)}]
        )
        raw = msg.content[0].text.strip()
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"Entity extraction error: {e}")
    return []


def answer(
    question: str,
    graph,
    vector_store,
) -> Dict:
    """Full Graph RAG pipeline: entity extraction → graph traversal → passage retrieval → LLM answer."""

    # Step 1: Extract entities from question
    query_entities = extract_query_entities(question)
    print(f"Query entities: {query_entities}")

    # Step 2: Match to graph nodes
    seed_nodes = find_nodes(graph, query_entities)
    print(f"Seed nodes in graph: {seed_nodes}")

    # Step 3: Expand subgraph
    graph_context = ""
    visited_nodes = []
    if seed_nodes:
        graph_context, visited_nodes = get_subgraph_context(
            graph, seed_nodes,
            hops=TOP_K_GRAPH_HOPS,
            max_nodes=MAX_GRAPH_CONTEXT_NODES,
        )
    else:
        graph_context = "No matching entities found in knowledge graph."

    # Step 4: Vector retrieval
    passages = similarity_search(vector_store, question, k=TOP_K_VECTOR)
    passage_context = "\n\n---\n\n".join(passages)

    # Step 5: LLM answer synthesis
    prompt = ANSWER_PROMPT.format(
        graph_context=graph_context,
        passage_context=passage_context,
        question=question,
    )

    response = client.messages.create(
        model=ANSWER_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    answer_text = response.content[0].text

    return {
        "answer": answer_text,
        "query_entities": query_entities,
        "seed_nodes": seed_nodes,
        "graph_nodes_used": visited_nodes,
        "graph_context": graph_context,
        "passage_context": passage_context,
    }
