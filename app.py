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

    aws_profile = st.text_input(
        "AWS Profile",
        value=os.getenv("AWS_PROFILE", "vscode-user"),
        help="Profile name from ~/.aws/config with Bedrock access",
    )
    aws_region = st.text_input(
        "AWS Region",
        value=os.getenv("AWS_REGION", "us-east-1"),
    )
    if aws_profile:
        os.environ["AWS_PROFILE"] = aws_profile
        os.environ["AWS_REGION"] = aws_region

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
tab_chat, tab_graph, tab_eval = st.tabs(["💬 Chat", "🕸️ Knowledge Graph", "📊 Evaluation"])

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

            if msg["role"] == "assistant" and msg.get("sources"):
                src = msg["sources"]
                g_ents = src.get("graph_entities", [])
                p_qs   = src.get("passage_queries", [])
                if g_ents or p_qs:
                    with st.expander("📎 Retrieved sources", expanded=False):
                        if g_ents:
                            st.markdown(f"**Graph entities queried:** {', '.join(g_ents)}")
                        if p_qs:
                            st.markdown("**Passage search queries:**")
                            for q in p_qs:
                                st.caption(q)

    # Chat input
    question = st.chat_input("Ask about characters, relationships, events...")
    if "pending_question" in st.session_state:
        question = st.session_state.pop("pending_question")

    if question:
        if not aws_profile:
            st.error("Enter your AWS profile name in the sidebar.")
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
                    sources = result.get("sources", {})

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

                    # Sources expander
                    g_ents = sources.get("graph_entities", [])
                    p_qs   = sources.get("passage_queries", [])
                    if g_ents or p_qs:
                        with st.expander("📎 Retrieved sources", expanded=False):
                            if g_ents:
                                st.markdown(f"**Graph entities queried:** {', '.join(g_ents)}")
                            if p_qs:
                                st.markdown("**Passage search queries:**")
                                for q in p_qs:
                                    st.caption(q)

                    # TruLens on-demand evaluation
                    with st.expander("🔬 TruLens Evaluation (on demand)", expanded=False):
                        tru_key = f"tru_{len(st.session_state.messages)}"
                        if st.button("Evaluate this response with RAG Triad", key=tru_key):
                            with st.spinner("Scoring with TruLens (Groundedness · Context Relevance · Answer Relevance)..."):
                                try:
                                    from src.mahabharat.eval_trulens import evaluate_single
                                    scores = evaluate_single(question, G, vector_store)
                                    if scores:
                                        t_col1, t_col2, t_col3 = st.columns(3)
                                        t_col1.metric("Groundedness",      f"{scores['groundedness']:.2f}")
                                        t_col2.metric("Context Relevance", f"{scores['context_relevance']:.2f}")
                                        t_col3.metric("Answer Relevance",  f"{scores['answer_relevance']:.2f}")
                                    else:
                                        st.warning("TruLens scoring returned no results.")
                                except Exception as tru_err:
                                    st.error(f"TruLens error: {tru_err}")

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
                        "sources": sources,
                    })

                    # Update LLM conversation history (keep last 8 turns = 4 exchanges)
                    st.session_state.chat_history.append({"role": "user", "content": [{"text": question}]})
                    st.session_state.chat_history.append({"role": "assistant", "content": [{"text": answer}]})
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


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: EVALUATION DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("### Evaluation Dashboard")
    st.caption(
        "Three-tier evaluation: **Tier 1** keyword/entity recall (fast) · "
        "**Tier 2** RAGAS LLM-judged batch metrics · "
        "**Tier 3** TruLens live RAG Triad tracing"
    )

    import os as _os

    # ── Tier 2: RAGAS ─────────────────────────────────────────────────────────
    st.subheader("Tier 2 · RAGAS Batch Evaluation")
    st.caption("Runs all 25 golden questions through the agent and scores with Amazon Nova Pro as judge. Takes ~15 min.")

    ragas_report_path = "data/ragas_report.json"
    col_run, col_status = st.columns([2, 3])

    with col_run:
        if col_run.button("▶ Run RAGAS Evaluation", use_container_width=True, disabled=not (graph_ready and faiss_ready)):
            with st.spinner("Running RAGAS evaluation (25 questions × LLM judge calls)..."):
                try:
                    from src.mahabharat.eval_ragas import run_ragas_eval
                    ragas_result = run_ragas_eval()
                    st.success("RAGAS evaluation complete.")
                except Exception as e:
                    st.error(f"RAGAS error: {e}")
                    raise

    if _os.path.exists(ragas_report_path):
        import json as _json
        with open(ragas_report_path) as _f:
            ragas_data = _json.load(_f)

        summary = ragas_data.get("summary", {})
        st.markdown("**Latest RAGAS Report**")
        m_cols = st.columns(5)
        metric_labels = {
            "faithfulness":       "Faithfulness",
            "answer_relevancy":   "Answer Relevancy",
            "context_precision":  "Context Precision",
            "context_recall":     "Context Recall",
            "tool_call_accuracy": "Tool Accuracy",
        }
        for col, (key, label) in zip(m_cols, metric_labels.items()):
            val = summary.get(key, 0.0)
            col.metric(label, f"{val:.2f}" if isinstance(val, float) else str(val))

        # Per-sample results table
        per_sample = ragas_data.get("per_sample", [])
        if per_sample:
            with st.expander("📋 Per-Question Results", expanded=False):
                import pandas as _pd
                display_cols = ["id", "category", "question", "faithfulness",
                                "answer_relevancy", "context_precision", "context_recall"]
                df = _pd.DataFrame(per_sample)
                df = df[[c for c in display_cols if c in df.columns]]
                st.dataframe(df, use_container_width=True)
    else:
        st.info("No RAGAS report found. Run the evaluation above to generate one.")

    st.divider()

    # ── Tier 3: TruLens ───────────────────────────────────────────────────────
    st.subheader("Tier 3 · TruLens Live Dashboard")
    st.caption("TruLens records per-query traces with RAG Triad scores in `data/trulens.db`. Launch the dashboard to explore them.")

    tru_col1, tru_col2 = st.columns([2, 3])
    with tru_col1:
        if st.button("🚀 Launch TruLens Dashboard", use_container_width=True):
            try:
                from src.mahabharat.eval_trulens import run_trulens_dashboard
                url = run_trulens_dashboard(port=8502)
                st.success(f"Dashboard started at [{url}]({url})")
            except Exception as e:
                st.error(f"Could not launch dashboard: {e}")

    with tru_col2:
        trulens_db_exists = _os.path.exists("data/trulens.db")
        st.markdown(f"**TruLens DB:** {'✅ exists' if trulens_db_exists else '❌ not yet created'} (`data/trulens.db`)")
        st.caption(
            "TruLens records are written automatically when you click "
            "**Evaluate this response** in the Chat tab."
        )

    st.divider()

    # ── Tier 1: existing keyword eval summary ─────────────────────────────────
    st.subheader("Tier 1 · Keyword / Entity / Tool Recall")
    st.caption("Fast rule-based eval — no LLM judge. Run: `PYTHONPATH=src uv run python -m mahabharat.eval`")

    tier1_report_path = "data/eval_report.json"
    if _os.path.exists(tier1_report_path):
        import json as _json2
        with open(tier1_report_path) as _f2:
            tier1_data = _json2.load(_f2)
        t1_sum = tier1_data.get("summary", {})
        t1_cols = st.columns(4)
        t1_cols[0].metric("Questions",      t1_sum.get("total", "—"))
        t1_cols[1].metric("Entity Recall",  f"{t1_sum.get('entity_recall', 0):.1%}")
        t1_cols[2].metric("Keyword Recall", f"{t1_sum.get('keyword_recall', 0):.1%}")
        t1_cols[3].metric("Tool Accuracy",  f"{t1_sum.get('tool_accuracy', 0):.1%}")
    else:
        st.info("No Tier 1 report found. Run `PYTHONPATH=src uv run python -m mahabharat.eval` first.")
