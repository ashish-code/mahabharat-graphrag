"""Mahabharat Graph RAG — Streamlit frontend."""
import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Mahabharat Graph RAG",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stChatMessage { border-radius: 12px; }
.tool-badge {
    display: inline-block; padding: 2px 8px; border-radius: 10px;
    font-size: 11px; font-weight: bold; margin: 2px;
}
.badge-graph { background: #1a6b3c; color: #7dfa9d; }
.badge-passage { background: #1a3d6b; color: #7db8fa; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚔️ Mahabharat")
    st.caption("Graph RAG Chatbot")

    api_key = st.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
    )
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    st.divider()

    graph_ready = os.path.exists("data/graph.json")
    faiss_ready = os.path.exists("data/faiss_index")
    st.markdown("**Index status**")
    st.markdown(f"{'✅' if graph_ready else '❌'} Knowledge Graph")
    st.markdown(f"{'✅' if faiss_ready else '❌'} Vector Index")

    if not (graph_ready and faiss_ready):
        st.warning(
            "Build the index first:\n"
            "```\n./build_fast.sh\n```\n"
            "*(~5 min, 200 chunks)*"
        )
    else:
        if st.button("🔄 Reload Index", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

    show_tools = st.toggle("Show tool calls", value=True)
    show_graph_viz = st.toggle("Show graph visualization", value=True)

# ── Resource loading ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading knowledge graph and vector index...")
def load_resources():
    from src.mahabharat.graph import load_graph
    from src.mahabharat.vector_store import load_vector_store
    return load_graph(), load_vector_store()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_graph = st.tabs(["💬 Chat", "🕸️ Knowledge Graph"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("### Ask the Mahabharata")
    st.caption(
        "Powered by **Graph RAG** · The AI agent chooses between "
        "structured graph traversal and semantic passage search."
    )

    # Example questions
    EXAMPLES = [
        "What is the relationship between Karna and the Pandavas?",
        "Who killed Abhimanyu and how?",
        "Describe the family tree of the Kauravas.",
        "What role did Krishna play in the Kurukshetra war?",
        "Why did Bhishma take a vow of celibacy?",
        "Who were the teachers of Arjuna?",
        "How is Draupadi related to Drupada and Dhrishtadyumna?",
        "Who killed Drona and why was he tricked?",
    ]

    with st.expander("💡 Example questions", expanded=not st.session_state.get("messages")):
        cols = st.columns(2)
        for i, q in enumerate(EXAMPLES):
            if cols[i % 2].button(q, key=f"ex_{i}", use_container_width=True):
                st.session_state.pending_question = q

    # Chat history display
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # LLM-format history

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant" and show_tools and msg.get("tool_calls"):
                tool_calls = msg["tool_calls"]
                badges = ""
                for tc in tool_calls:
                    if tc["tool"] == "graph_lookup":
                        entities = tc["input"].get("entities", [])
                        badges += f'<span class="tool-badge badge-graph">🕸️ Graph: {", ".join(entities)}</span> '
                    else:
                        query = tc["input"].get("query", "")[:40]
                        badges += f'<span class="tool-badge badge-passage">📄 Passages: {query}...</span> '
                st.markdown(badges, unsafe_allow_html=True)

            if msg["role"] == "assistant" and show_graph_viz and msg.get("graph_html"):
                with st.expander("🕸️ Subgraph used in this answer", expanded=False):
                    components.html(msg["graph_html"], height=520, scrolling=False)

    # Chat input
    question = st.chat_input("Ask about characters, relationships, events...")
    if "pending_question" in st.session_state:
        question = st.session_state.pop("pending_question")

    if question:
        if not api_key:
            st.error("Add your Anthropic API key in the sidebar.")
            st.stop()

        if not (graph_ready and faiss_ready):
            st.error("Run the build pipeline first (`./build_fast.sh`).")
            st.stop()

        G, vector_store = load_resources()

        # Show user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Run agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking... (running Graph RAG agent)"):
                try:
                    from src.mahabharat.agent import chat as agent_chat
                    from src.mahabharat.visualize import render_subgraph_html
                    from src.mahabharat.graph import find_nodes, get_subgraph_context

                    result = agent_chat(
                        question,
                        G,
                        vector_store,
                        history=st.session_state.chat_history,
                    )

                    answer = result["answer"]
                    tool_calls = result.get("tool_calls", [])

                    st.markdown(answer)

                    # Tool call badges
                    if show_tools and tool_calls:
                        badges = ""
                        for tc in tool_calls:
                            if tc["tool"] == "graph_lookup":
                                entities = tc["input"].get("entities", [])
                                badges += f'<span class="tool-badge badge-graph">🕸️ Graph: {", ".join(entities)}</span> '
                            else:
                                query = tc["input"].get("query", "")[:40]
                                badges += f'<span class="tool-badge badge-passage">📄 Passages: {query}...</span> '
                        st.markdown(badges, unsafe_allow_html=True)

                    # Graph visualization for this answer
                    graph_html = ""
                    if show_graph_viz:
                        # Collect all entities from graph_lookup calls
                        all_entities = []
                        for tc in tool_calls:
                            if tc["tool"] == "graph_lookup":
                                all_entities.extend(tc["input"].get("entities", []))

                        if all_entities:
                            seed_nodes = find_nodes(G, all_entities)
                            if seed_nodes:
                                _, visited = get_subgraph_context(G, seed_nodes, hops=2, max_nodes=30)
                                graph_html = render_subgraph_html(G, visited, seed_nodes)
                                with st.expander("🕸️ Subgraph used in this answer", expanded=True):
                                    components.html(graph_html, height=520, scrolling=False)

                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "tool_calls": tool_calls,
                        "graph_html": graph_html,
                    })

                    # Update LLM conversation history (keep last 8 turns = 4 exchanges)
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    if len(st.session_state.chat_history) > 8:
                        st.session_state.chat_history = st.session_state.chat_history[-8:]

                except Exception as e:
                    st.error(f"Error: {e}")
                    raise


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: KNOWLEDGE GRAPH EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_graph:
    st.markdown("### Knowledge Graph Explorer")
    st.caption("Full character relationship graph. Highlighted nodes = query seeds. Drag to explore.")

    if not graph_ready:
        st.info("Build the index first to explore the graph.")
    else:
        G, _ = load_resources()

        col1, col2 = st.columns([3, 1])
        with col2:
            st.markdown("**Legend**")
            st.markdown("🔵 Character  🟢 Place  🟠 Event  🟣 Concept")
            st.markdown("🔴 Family ties  🟥 Conflict  🟩 Alliance")
            st.divider()
            search_entity = st.text_input("Focus on entity:", placeholder="e.g. Arjuna")
            max_nodes = st.slider("Max nodes shown", 20, 100, 60)

        with col1:
            from src.mahabharat.visualize import render_subgraph_html, render_full_graph_html
            from src.mahabharat.graph import find_nodes, get_subgraph_context

            if search_entity:
                seed_nodes = find_nodes(G, [search_entity])
                if seed_nodes:
                    _, visited = get_subgraph_context(G, seed_nodes, hops=2, max_nodes=max_nodes)
                    html = render_subgraph_html(G, visited, seed_nodes, max_nodes=max_nodes)
                    st.caption(f"Showing subgraph around **{', '.join(seed_nodes)}** ({len(visited)} nodes)")
                else:
                    st.warning(f"'{search_entity}' not found in graph.")
                    html = render_full_graph_html(G, max_nodes=max_nodes)
            else:
                html = render_full_graph_html(G, max_nodes=max_nodes)
                st.caption(f"Showing top {max_nodes} most-connected nodes")

            components.html(html, height=560, scrolling=False)

        st.divider()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Entities", G.number_of_nodes())
        col_b.metric("Total Relationships", G.number_of_edges())
        col_c.metric("Characters", sum(1 for n in G.nodes if G.nodes[n].get("type") == "character"))
