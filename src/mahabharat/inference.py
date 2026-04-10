"""
Transitive relationship inference rules for the Mahabharata knowledge graph.
Applied after build_graph() to derive relationships not explicitly stated in text.
All inferred edges are tagged inferred=True so they are distinguishable from extracted data.
"""
from typing import Dict, List, Tuple
import networkx as nx

# Each rule: (rel_A→B, rel_B→C) → (inferred rel_A→C, confidence)
TRANSITIVE_RULES: List[Tuple[str, str, str, str]] = [
    # Alliance transitivity: friend of ally is ally (weak)
    ("IS_ALLY_OF",     "IS_ALLY_OF",     "IS_ALLY_OF",        "low"),
    # Enemy propagation: enemy of my ally is my enemy (weak)
    ("IS_ENEMY_OF",    "IS_ALLY_OF",     "IS_ENEMY_OF",       "low"),
    # Family composition: grandparent via father
    ("IS_FATHER_OF",   "IS_FATHER_OF",   "IS_GRANDFATHER_OF", "medium"),
    ("IS_MOTHER_OF",   "IS_FATHER_OF",   "IS_GRANDFATHER_OF", "medium"),
    ("IS_FATHER_OF",   "IS_MOTHER_OF",   "IS_GRANDFATHER_OF", "medium"),
    ("IS_MOTHER_OF",   "IS_MOTHER_OF",   "IS_GRANDFATHER_OF", "medium"),
]


def apply_transitive_rules(G: nx.MultiDiGraph) -> int:
    """
    Apply TRANSITIVE_RULES to G, adding new inferred edges.
    Skips if an edge A→C already exists (any relation).
    Returns count of edges added.
    """
    added = 0
    nodes = list(G.nodes)
    for A in nodes:
        for B in list(G.successors(A)):
            for C in list(G.successors(B)):
                if C == A:
                    continue
                for rel_ab, rel_bc, inferred_rel, conf in TRANSITIVE_RULES:
                    ab_matches = any(
                        d.get("relation") == rel_ab
                        for u, v, d in G.out_edges(A, data=True) if v == B
                    )
                    if not ab_matches:
                        continue
                    bc_matches = any(
                        d.get("relation") == rel_bc
                        for u, v, d in G.out_edges(B, data=True) if v == C
                    )
                    if not bc_matches:
                        continue
                    # Only add if no direct edge A→C exists yet
                    if G.has_edge(A, C):
                        continue
                    ctx = f"[inferred] {A} {rel_ab} {B}, {B} {rel_bc} {C}"
                    G.add_edge(A, C, relation=inferred_rel,
                               context=ctx, confidence=conf, inferred=True)
                    added += 1
    return added


def apply_sibling_inference(G: nx.MultiDiGraph) -> int:
    """
    If A and B share a common parent (both have IS_SON_OF or IS_DAUGHTER_OF
    pointing to the same node) and no sibling edge exists, infer IS_BROTHER_OF
    (low confidence) in both directions.
    Returns count of edges added.
    """
    added = 0
    parent_to_children: Dict = {}
    for u, v, d in G.edges(data=True):
        if d.get("relation") in ("IS_SON_OF", "IS_DAUGHTER_OF"):
            parent_to_children.setdefault(v, set()).add(u)

    for parent, children in parent_to_children.items():
        child_list = list(children)
        for i, A in enumerate(child_list):
            for B in child_list[i + 1:]:
                ctx = f"[inferred] both {A} and {B} are children of {parent}"
                if not G.has_edge(A, B):
                    G.add_edge(A, B, relation="IS_BROTHER_OF",
                               context=ctx, confidence="low", inferred=True)
                    added += 1
                if not G.has_edge(B, A):
                    G.add_edge(B, A, relation="IS_BROTHER_OF",
                               context=ctx, confidence="low", inferred=True)
                    added += 1
    return added


def apply_all_inference(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Run all inference rules and print a summary line."""
    n1 = apply_transitive_rules(G)
    n2 = apply_sibling_inference(G)
    print(f"Inference rules: +{n1} transitive edges, +{n2} sibling edges "
          f"(total edges now: {G.number_of_edges()})")
    return G
