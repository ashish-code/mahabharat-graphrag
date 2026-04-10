"""Knowledge graph construction and querying using NetworkX."""
import json
from typing import List, Dict, Set, Tuple
import networkx as nx
from rapidfuzz import process, fuzz
from .config import GRAPH_PATH, FUZZY_MATCH_THRESHOLD
from .aliases import resolve_aliases

# Inverse relationship map — used to auto-generate reverse edges at build time.
# Symmetric relations (IS_ALLY_OF etc.) get an edge added in both directions.
# Relations with no clean inverse are omitted.
INVERSE_RELATIONS: Dict[str, str] = {
    "IS_FATHER_OF":      "IS_SON_OF",
    "IS_MOTHER_OF":      "IS_SON_OF",
    "IS_SON_OF":         "IS_PARENT_OF",
    "IS_DAUGHTER_OF":    "IS_PARENT_OF",
    "IS_HUSBAND_OF":     "IS_WIFE_OF",
    "IS_WIFE_OF":        "IS_HUSBAND_OF",
    "IS_BROTHER_OF":     "IS_BROTHER_OF",       # symmetric
    "IS_SISTER_OF":      "IS_SISTER_OF",         # symmetric
    "IS_ALLY_OF":        "IS_ALLY_OF",           # symmetric
    "IS_ENEMY_OF":       "IS_ENEMY_OF",          # symmetric
    "FOUGHT_AGAINST":    "FOUGHT_AGAINST",        # symmetric
    "IS_TEACHER_OF":     "IS_DISCIPLE_OF",
    "IS_DISCIPLE_OF":    "IS_TEACHER_OF",
    "KILLED":            "WAS_KILLED_BY",
    "WAS_KILLED_BY":     "KILLED",
    "IS_UNCLE_OF":       "IS_NEPHEW_OF",
    "IS_NEPHEW_OF":      "IS_UNCLE_OF",
    "IS_COUSIN_OF":      "IS_COUSIN_OF",         # symmetric
    "IS_GRANDSON_OF":    "IS_GRANDFATHER_OF",
    "IS_GRANDFATHER_OF": "IS_GRANDSON_OF",
    "CURSED_BY":         "CURSED",
    "BLESSED_BY":        "BLESSED",
    "IS_REINCARNATION_OF": "HAS_REINCARNATION",
    # No clean inverse: RULES_OVER, PARTICIPATED_IN, BELONGS_TO,
    #                   FOUGHT_AT, OWNS, BORN_FROM, EXILED_BY,
    #                   GRANTED_BOON_BY, VOWED_TO_KILL, PROTECTED, BETRAYED
}


def build_graph(entities: List[Dict], relationships: List[Dict]) -> nx.MultiDiGraph:
    """
    Build a directed multigraph from extracted entities and relationships.
    Inverse edges are automatically inferred and marked with inferred=True.
    """
    G = nx.MultiDiGraph()

    # Deduplicate entities by normalised name, merging descriptions
    seen_entities: Dict[str, Dict] = {}
    for e in entities:
        name = e.get("name", "").strip()
        if not name:
            continue
        key = name.lower()
        if key not in seen_entities:
            seen_entities[key] = e
        else:
            existing_desc = seen_entities[key].get("description", "")
            new_desc = e.get("description", "")
            if new_desc and new_desc not in existing_desc:
                seen_entities[key]["description"] = existing_desc + "; " + new_desc

    for e in seen_entities.values():
        G.add_node(
            e["name"],
            type=e.get("type", "unknown"),
            description=e.get("description", ""),
        )

    # Add explicit relationships, then infer inverses
    for r in relationships:
        src = r.get("source", "").strip()
        tgt = r.get("target", "").strip()
        rel = r.get("relation", "").strip()
        ctx = r.get("context", "")
        confidence = r.get("confidence", "")
        if not (src and tgt and rel):
            continue

        if src not in G:
            G.add_node(src, type="unknown", description="")
        if tgt not in G:
            G.add_node(tgt, type="unknown", description="")

        G.add_edge(src, tgt, relation=rel, context=ctx,
                   confidence=confidence, inferred=False)

        # Auto-add inverse edge if mapping exists and reverse not already present
        inv_rel = INVERSE_RELATIONS.get(rel)
        if inv_rel and not G.has_edge(tgt, src):
            G.add_edge(tgt, src, relation=inv_rel,
                       context=f"[inferred] {ctx}",
                       confidence=confidence, inferred=True)

    explicit = sum(1 for *_, d in G.edges(data=True) if not d.get("inferred"))
    inferred = G.number_of_edges() - explicit
    print(f"Graph: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges "
          f"({explicit} explicit + {inferred} inferred)")
    return G


def save_graph(G: nx.MultiDiGraph, path: str = GRAPH_PATH):
    """Persist graph to JSON."""
    data = {
        "nodes": [{"id": n, **G.nodes[n]} for n in G.nodes],
        "edges": [{"source": u, "target": v, **d} for u, v, d in G.edges(data=True)],
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
    """
    Match query entity names to graph nodes using three-stage resolution:
      1. Alias table  — maps epithets/nicknames to canonical names
      2. Exact match  — case-insensitive
      3. Fuzzy match  — rapidfuzz token_sort_ratio >= FUZZY_MATCH_THRESHOLD

    Return type is List[str] (unchanged from previous implementation).
    """
    graph_nodes_lower: Dict[str, str] = {n.lower(): n for n in G.nodes}

    # Stage 1: resolve aliases (may expand the list with canonical names)
    candidates = resolve_aliases(query_entities)

    matched: List[str] = []
    for qe in candidates:
        qe_lower = qe.lower().strip()
        if not qe_lower:
            continue

        # Stage 2: exact match
        if qe_lower in graph_nodes_lower:
            matched.append(graph_nodes_lower[qe_lower])
            continue

        # Stage 3: fuzzy match
        result = process.extractOne(
            qe_lower,
            list(graph_nodes_lower.keys()),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=FUZZY_MATCH_THRESHOLD,
        )
        if result:
            matched.append(graph_nodes_lower[result[0]])

    # Deduplicate preserving first-seen order
    seen: Set[str] = set()
    out: List[str] = []
    for n in matched:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def get_subgraph_context(
    G: nx.MultiDiGraph,
    seed_nodes: List[str],
    hops: int = 2,
    max_nodes: int = 20,
) -> Tuple[str, List[str]]:
    """
    BFS from seed nodes up to `hops` away (traversing both directions).
    Returns (context_text, all_node_names_visited).
    """
    visited: Set[str] = set()
    frontier: Set[str] = set(seed_nodes)

    for _ in range(hops):
        next_frontier: Set[str] = set()
        for node in frontier:
            if node not in G:
                continue
            visited.add(node)
            for neighbor in list(G.successors(node)) + list(G.predecessors(node)):
                if neighbor not in visited:
                    next_frontier.add(neighbor)
        frontier = next_frontier
        visited.update(frontier)
        if len(visited) >= max_nodes:
            break

    lines: List[str] = []

    lines.append("=== ENTITIES ===")
    for node in list(visited)[:max_nodes]:
        if node in G:
            attrs = G.nodes[node]
            etype = attrs.get("type", "")
            desc = attrs.get("description", "")
            lines.append(f"- {node} ({etype}): {desc}")

    lines.append("\n=== RELATIONSHIPS ===")
    edge_count = 0
    for u, v, d in G.edges(data=True):
        if (u in visited or v in visited) and edge_count < 60:
            rel = d.get("relation", "")
            ctx = d.get("context", "")
            inferred = d.get("inferred", False)
            tag = " [inferred]" if inferred else ""
            lines.append(f"- {u} --[{rel}]--> {v}{tag}" + (f"  ({ctx})" if ctx else ""))
            edge_count += 1

    return "\n".join(lines), list(visited)
