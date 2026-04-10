"""
Hybrid retrieval: graph-guided FAISS search + passage-guided graph expansion.
Uses Reciprocal Rank Fusion to merge ranked lists, then cross-encoder reranking.
"""
from typing import List, Tuple
import networkx as nx
from langchain_community.vectorstores import FAISS
from .graph import find_nodes, get_subgraph_context
from .vector_store import similarity_search_with_score
from .config import RRF_K, TOP_K_HYBRID, RERANKER_MODEL, RERANKER_TOP_N

# Lazy-loaded cross-encoder (avoids slow import at startup)
_cross_encoder = None


def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        from sentence_transformers import CrossEncoder
        print(f"  Loading cross-encoder ({RERANKER_MODEL})...")
        _cross_encoder = CrossEncoder(RERANKER_MODEL)
    return _cross_encoder


def _scan_passages_for_entities(passages: List[str], G: nx.MultiDiGraph) -> List[str]:
    """Return graph node names that appear verbatim in any passage (fast O(n*m) scan)."""
    combined = " ".join(passages).lower()
    return [node for node in G.nodes if node.lower() in combined]


def _rrf_merge(
    list_a: List[Tuple[str, float]],
    list_b: List[Tuple[str, float]],
    k: int = RRF_K,
) -> List[str]:
    """Reciprocal Rank Fusion of two ranked passage lists → deduplicated merged order."""
    scores: dict = {}
    for rank, (text, _) in enumerate(list_a):
        scores[text] = scores.get(text, 0.0) + 1.0 / (k + rank + 1)
    for rank, (text, _) in enumerate(list_b):
        scores[text] = scores.get(text, 0.0) + 1.0 / (k + rank + 1)
    return [t for t, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]


def _rerank(query: str, passages: List[str], top_n: int = RERANKER_TOP_N) -> List[str]:
    """Cross-encoder reranking: score (query, passage) pairs, return top_n."""
    if not passages:
        return passages
    try:
        ce = _get_cross_encoder()
        pairs = [(query, p) for p in passages]
        ce_scores = ce.predict(pairs)
        ranked = sorted(zip(passages, ce_scores), key=lambda x: x[1], reverse=True)
        return [p for p, _ in ranked[:top_n]]
    except Exception as e:
        print(f"  Reranker error (falling back to top-{top_n} by rank): {e}")
        return passages[:top_n]


def hybrid_graph_lookup(
    query: str,
    entities: List[str],
    G: nx.MultiDiGraph,
    vector_store: FAISS,
) -> str:
    """
    Graph-guided hybrid retrieval.
    1. BFS from entity seeds → structured graph context
    2. Two FAISS queries: original + entity-enriched
    3. RRF merge + cross-encoder rerank → supporting passages
    4. Return graph context + reranked passages
    """
    # 1. Graph traversal
    seed_nodes = find_nodes(G, entities)
    if not seed_nodes:
        return f"No entities found in graph for: {entities}."
    graph_ctx, visited = get_subgraph_context(G, seed_nodes, hops=2, max_nodes=25)

    # 2. Two FAISS queries: original + entity-enriched
    enriched_query = query + " " + " ".join(list(visited)[:10])
    base_results     = similarity_search_with_score(vector_store, query,           k=TOP_K_HYBRID)
    enriched_results = similarity_search_with_score(vector_store, enriched_query,  k=TOP_K_HYBRID)

    # 3. RRF merge → cross-encoder rerank
    merged   = _rrf_merge(base_results, enriched_results)
    reranked = _rerank(query, merged)

    passages_text = "\n\n---\n\n".join(reranked) if reranked else "(no supporting passages)"
    return (
        f"Found {len(visited)} related entities.\n\n"
        f"{graph_ctx}\n\n"
        f"=== SUPPORTING PASSAGES ===\n{passages_text}"
    )


def hybrid_passage_search(
    query: str,
    G: nx.MultiDiGraph,
    vector_store: FAISS,
) -> str:
    """
    Passage-guided hybrid retrieval.
    1. FAISS search → top passages
    2. Scan passages for graph entity names → expand seeds
    3. Shallow BFS on found entities → supporting graph facts
    4. Cross-encoder rerank passages
    5. Return reranked passages + graph context
    """
    # 1. FAISS
    base_results = similarity_search_with_score(vector_store, query, k=TOP_K_HYBRID)
    raw_passages = [p for p, _ in base_results]

    # 2. Scan passages for entity names
    passage_entities = _scan_passages_for_entities(raw_passages, G)

    # 3. Shallow graph expansion (1 hop)
    graph_ctx = ""
    if passage_entities:
        seed_nodes = find_nodes(G, passage_entities)
        if seed_nodes:
            graph_ctx, _ = get_subgraph_context(G, seed_nodes, hops=1, max_nodes=15)

    # 4. Rerank
    reranked = _rerank(query, raw_passages)

    passages_text = "\n\n---\n\n".join(reranked) if reranked else "(no passages found)"
    result = passages_text
    if graph_ctx:
        result += f"\n\n=== RELATED GRAPH FACTS ===\n{graph_ctx}"
    return result
