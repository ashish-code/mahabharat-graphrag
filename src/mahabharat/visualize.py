"""Graph visualization using pyvis, rendered in Streamlit via HTML."""
import os
import tempfile
from typing import List, Set
import networkx as nx
from pyvis.network import Network
from .graph import build_community_map

# Community border colors (cycle through for as many communities as exist)
COMMUNITY_COLORS = [
    "#FFD700", "#FF6B6B", "#4ECDC4", "#45B7D1",
    "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8",
]

# Node colors by entity type
TYPE_COLORS = {
    "character": "#4A90D9",
    "place":     "#27AE60",
    "event":     "#E67E22",
    "concept":   "#8E44AD",
    "weapon":    "#C0392B",
    "clan":      "#16A085",
    "kingdom":   "#2C3E50",
    "unknown":   "#95A5A6",
}

# Edge colors by relation category
def edge_color(relation: str) -> str:
    r = relation.upper()
    if any(x in r for x in ["FATHER", "MOTHER", "SON", "DAUGHTER", "BROTHER", "SISTER", "WIFE", "HUSBAND", "UNCLE", "AUNT"]):
        return "#E74C3C"   # red — family
    if any(x in r for x in ["KILLED", "ENEMY", "FOUGHT"]):
        return "#C0392B"   # dark red — conflict
    if any(x in r for x in ["ALLY", "DISCIPLE", "TEACHER"]):
        return "#27AE60"   # green — positive
    if any(x in r for x in ["RULES", "BELONGS", "PART"]):
        return "#F39C12"   # orange — political
    return "#7F8C8D"        # grey — other


def build_pyvis(
    G: nx.MultiDiGraph,
    highlight_nodes: List[str] = None,
    max_nodes: int = 50,
    community_map: dict = None,
) -> Network:
    """Convert a NetworkX subgraph to a pyvis Network."""
    net = Network(
        height="500px",
        width="100%",
        directed=True,
        bgcolor="#1a1a2e",
        font_color="white",
    )
    net.set_options("""
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 150,
          "springConstant": 0.04
        },
        "stabilization": {"iterations": 100}
      },
      "edges": {
        "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
        "smooth": {"type": "curvedCW", "roundness": 0.2},
        "font": {"size": 9, "color": "#cccccc", "align": "top"}
      },
      "nodes": {
        "font": {"size": 12, "color": "white"},
        "borderWidth": 2
      }
    }
    """)

    highlight_set: Set[str] = set(highlight_nodes or [])
    nodes_to_show = list(G.nodes)[:max_nodes]

    for node in nodes_to_show:
        attrs = G.nodes[node]
        ntype = attrs.get("type", "unknown")
        color = TYPE_COLORS.get(ntype, TYPE_COLORS["unknown"])
        size = 25 if node in highlight_set else 15
        if node in highlight_set:
            border = "#FFD700"
        elif community_map and node in community_map:
            border = COMMUNITY_COLORS[community_map[node] % len(COMMUNITY_COLORS)]
        else:
            border = color

        net.add_node(
            node,
            label=node,
            title=f"<b>{node}</b><br>Type: {ntype}<br>{attrs.get('description', '')}",
            color={"background": color, "border": border},
            size=size,
            borderWidth=3 if node in highlight_set else 1,
        )

    node_set = set(nodes_to_show)
    for u, v, d in G.edges(data=True):
        if u in node_set and v in node_set:
            rel = d.get("relation", "")
            ctx = d.get("context", "")
            net.add_edge(
                u, v,
                label=rel.replace("_", " "),
                title=ctx,
                color=edge_color(rel),
                width=2,
            )

    return net


def render_subgraph_html(
    G: nx.MultiDiGraph,
    visited_nodes: List[str],
    seed_nodes: List[str],
    max_nodes: int = 40,
) -> str:
    """Render a subgraph as HTML string for st.components.html."""
    if not visited_nodes:
        return ""

    # Build subgraph from visited nodes
    sub_nodes = visited_nodes[:max_nodes]
    subG = G.subgraph(sub_nodes).copy()

    community_map = build_community_map(G)
    net = build_pyvis(subG, highlight_nodes=seed_nodes, max_nodes=max_nodes,
                      community_map=community_map)

    # Save to temp file and read HTML
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        tmp_path = f.name

    net.save_graph(tmp_path)
    with open(tmp_path, "r") as f:
        html = f.read()
    os.unlink(tmp_path)
    return html


def render_full_graph_html(G: nx.MultiDiGraph, max_nodes: int = 80) -> str:
    """Render top N nodes of the full graph."""
    # Prioritize nodes with most connections
    top_nodes = sorted(G.nodes, key=lambda n: G.degree(n), reverse=True)[:max_nodes]
    subG = G.subgraph(top_nodes).copy()

    community_map = build_community_map(G)
    net = build_pyvis(subG, max_nodes=max_nodes, community_map=community_map)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        tmp_path = f.name

    net.save_graph(tmp_path)
    with open(tmp_path, "r") as f:
        html = f.read()
    os.unlink(tmp_path)
    return html
