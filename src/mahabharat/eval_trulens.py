"""
TruLens-based live evaluation of the Mahabharata Graph RAG system.

RAG Triad metrics (LLM judge — Amazon Nova Pro via Bedrock):
  - Groundedness       (is the answer supported by retrieved context?)
  - Context Relevance  (is retrieved context relevant to the question?)
  - Answer Relevance   (does the answer address the question?)

Architecture:
  - RAGWrapper instruments retrieve() and query() with @instrument
  - TruCustomApp wraps RAGWrapper for trace capture
  - Feedback functions use trulens.providers.bedrock.Bedrock as judge
  - All traces + scores stored in data/trulens.db (SQLite)

Usage:
    from mahabharat.eval_trulens import build_tru_app, evaluate_single

    # Build a reusable instrumented app
    tru, tru_app = build_tru_app(G, vector_store)

    # Record a single turn
    with tru_app as recording:
        answer = tru_app.app.query(question)

    # Run the TruLens Streamlit dashboard
    tru.run_dashboard(port=8502)
"""
import numpy as np
import time
from typing import Optional, Dict

TRULENS_DB = "data/trulens.db"


def _make_bedrock_provider():
    """Return a TruLens feedback provider backed by Amazon Nova Pro on Bedrock."""
    from trulens.providers.bedrock import Bedrock
    from mahabharat.config import AWS_PROFILE, AWS_REGION
    import boto3

    session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    return Bedrock(
        model_id="amazon.nova-pro-v1:0",
        region_name=AWS_REGION,
        # Pass boto3 session credentials through environment — Bedrock provider
        # reads AWS_PROFILE from the environment set by app.py / config.py
    )


class RAGWrapper:
    """
    Thin instrumented wrapper around chat() and hybrid_retriever for TruLens.
    @instrument on retrieve() and query() exposes them as traceable spans so
    TruLens can map feedback selectors to the right inputs/outputs.
    """

    def __init__(self, G, vector_store):
        self.G = G
        self.vector_store = vector_store

    def retrieve(self, query: str) -> str:
        """Passage retrieval — TruLens uses the return value as the context."""
        from mahabharat.hybrid_retriever import hybrid_passage_search
        return hybrid_passage_search(query, self.G, self.vector_store)

    def query(self, question: str) -> str:
        """Full agentic call — returns the answer string."""
        from mahabharat.agent import chat
        result = chat(question, self.G, self.vector_store)
        return result["answer"]


def build_tru_app(G, vector_store, app_name: str = "MahabharatRAG"):
    """
    Build a TruCustomApp wrapping RAGWrapper with RAG Triad feedback functions.

    Returns (tru_session, tru_app).

    Usage:
        tru, tru_app = build_tru_app(G, vs)
        with tru_app as recording:
            answer = tru_app.app.query(question)
    """
    from trulens.core import TruSession, Feedback, Select
    from trulens.apps.app import instrument
    from trulens.apps.custom import TruCustomApp

    # Instrument the wrapper methods before wrapping
    RAGWrapper.retrieve = instrument(RAGWrapper.retrieve)
    RAGWrapper.query    = instrument(RAGWrapper.query)

    tru = TruSession(database_url=f"sqlite:///{TRULENS_DB}")
    provider = _make_bedrock_provider()

    # Groundedness: is the answer supported by the retrieved passages?
    f_groundedness = (
        Feedback(provider.groundedness_measure_with_cot_reasons, name="Groundedness")
        .on(Select.RecordCalls.retrieve.rets)   # context = retrieve() return
        .on_output()                              # answer  = query() return
    )

    # Context Relevance: is retrieved context relevant to the question?
    f_context_rel = (
        Feedback(provider.context_relevance_with_cot_reasons, name="Context Relevance")
        .on_input()                               # question = query() input
        .on(Select.RecordCalls.retrieve.rets)     # context  = retrieve() return
        .aggregate(np.mean)
    )

    # Answer Relevance: does the answer address the question?
    f_answer_rel = (
        Feedback(provider.relevance_with_cot_reasons, name="Answer Relevance")
        .on_input()                               # question = query() input
        .on_output()                              # answer   = query() return
    )

    rag = RAGWrapper(G, vector_store)
    tru_app = TruCustomApp(
        rag,
        app_name=app_name,
        feedbacks=[f_groundedness, f_context_rel, f_answer_rel],
        tru_session=tru,
    )
    return tru, tru_app


def evaluate_single(question: str, G, vector_store) -> Optional[Dict]:
    """
    Run one question through TruLens and return the three RAG Triad scores.

    Waits up to 30 s for async feedback computation before reading results.
    Returns None on failure.
    """
    try:
        tru, tru_app = build_tru_app(G, vector_store)
        with tru_app as recording:
            answer = tru_app.app.query(question)

        # Wait for async feedback computation (LLM judge calls are async in TruLens)
        for _ in range(10):
            time.sleep(3)
            records, _ = tru.get_records_and_feedback(app_ids=[tru_app.app_id])
            if not records.empty and not records.iloc[-1].get("Groundedness", None) is None:
                break

        if records.empty:
            return None

        latest = records.iloc[-1]
        return {
            "answer":            answer,
            "groundedness":      float(latest.get("Groundedness",      0) or 0),
            "context_relevance": float(latest.get("Context Relevance", 0) or 0),
            "answer_relevance":  float(latest.get("Answer Relevance",  0) or 0),
        }
    except Exception as e:
        print(f"  TruLens eval error: {e}")
        return None


def run_trulens_dashboard(port: int = 8502):
    """
    Launch the TruLens Streamlit dashboard in a background thread.
    The dashboard reads from data/trulens.db automatically.
    """
    from trulens.core import TruSession
    import threading

    def _run():
        tru = TruSession(database_url=f"sqlite:///{TRULENS_DB}")
        tru.run_dashboard(port=port)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return f"http://localhost:{port}"
