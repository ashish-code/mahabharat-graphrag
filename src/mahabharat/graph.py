"""Knowledge graph construction and querying using NetworkX."""
import json
from typing import List, Dict, Set, Tuple
import networkx as nx
from .config import GRAPH_PATH


def build_graph(entities: List[Dict], relationships: List[Dict]) -> nx.MultiDiGraph:
    """Build a directed multigraph from extracted entities and relationships."""
    G = nx.MultiDiGraph()

    # Deduplicate entities by normalized name
    seen_entities: Dict[str, Dict] = {}
    for e in entities:
        name = e.get("name", "").strip()
        if not name:
            continue
        key = name.lower()
        if key not in seen_entities:
            seen_entities[key] = e
        else:
            # Merge descriptions
            existing_desc = seen_entities[key].get("description", "")
            new_desc = e.get("description", "")
            if new_desc and new_desc not in existing_desc:
                seen_entities[key]["description"] = existing_desc + "; " + new_desc

    for key, e in seen_entities.items():
        G.add_node(
            e["name"],
            type=e.get("type", "unknown"),
            description=e.get("description", ""),
        )

    # Add relationships
    for r in relationships:
        src = r.get("source", "").strip()
        tgt = r.get("target", "").strip()
        rel = r.get("relation", "").strip()
        ctx = r.get("context", "")
        if src and tgt and rel:
            # Add nodes if missing
            if src not in G:
                G.add_node(src, type="unknown", description="")
            if tgt not in G:
                G.add_node(tgt, type="unknown", description="")
            G.add_edge(src, tgt, relation=rel, context=ctx)

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def save_graph(G: nx.MultiDiGraph, path: str = GRAPH_PATH):
    """Persist graph to JSON."""
    data = {
        "nodes": [
            {"id": n, **G.nodes[n]}
            for n in G.nodes
        ],
        "edges": [
            {"source": u, "target": v, **d}
            for u, v, d in G.edges(data=True)
        ]
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Graph saved to {path}")


def load_graph(path: str = GRAPH_PATH) -> nx.MultiDiGraph:
    """Load graph from JSON."""
    with open(path) as f:
        data = json.load(f)

    G = nx.MultiDiGraph()
    for node in data["nodes"]:
        node_id = node.pop("id")
        G.add_node(node_id, **node)
    for edge in data["edges"]:
        src = edge.pop("source")
        tgt = edge.pop("target")
        G.add_edge(src, tgt, **edge)

    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def find_nodes(G: nx.MultiDiGraph, query_entities: List[str]) -> List[str]:
    """Fuzzy-match entity names in the graph."""
    graph_nodes = list(G.nodes)
    graph_nodes_lower = {n.lower(): n for n in graph_nodes}

    matched = []
    for qe in query_entities:
        qe_lower = qe.lower()
        # Exact match
        if qe_lower in graph_nodes_lower:
            matched.append(graph_nodes_lower[qe_lower])
            continue
        # Substring match
        for node_lower, node in graph_nodes_lower.items():
            if qe_lower in node_lower or node_lower in qe_lower:
                matched.append(node)
                break

    return list(set(matched))


def get_subgraph_context(
    G: nx.MultiDiGraph,
    seed_nodes: List[str],
    hops: int = 2,
    max_nodes: int = 20,
) -> Tuple[str, List[str]]:
    """
    BFS from seed nodes up to `hops` away.
    Returns (context_text, all_node_names_visited).
    """
    visited: Set[str] = set()
    frontier = set(seed_nodes)

    for _ in range(hops):
        next_frontier = set()
        for node in frontier:
            if node not in G:
                continue
            visited.add(node)
            # Neighbors (both in and out edges)
            for neighbor in list(G.successors(node)) + list(G.predecessors(node)):
                if neighbor not in visited:
                    next_frontier.add(neighbor)
        frontier = next_frontier
        visited.update(frontier)
        if len(visited) >= max_nodes:
            break

    # Build context text
    lines = []

    # Node descriptions
    lines.append("=== ENTITIES ===")
    for node in list(visited)[:max_nodes]:
        if node in G:
            attrs = G.nodes[node]
            etype = attrs.get("type", "")
            desc = attrs.get("description", "")
            lines.append(f"- {node} ({etype}): {desc}")

    # Edge relationships
    lines.append("\n=== RELATIONSHIPS ===")
    edge_count = 0
    for u, v, d in G.edges(data=True):
        if (u in visited or v in visited) and edge_count < 60:
            rel = d.get("relation", "")
            ctx = d.get("context", "")
            lines.append(f"- {u} --[{rel}]--> {v}" + (f"  ({ctx})" if ctx else ""))
            edge_count += 1

    return "\n".join(lines), list(visited)
