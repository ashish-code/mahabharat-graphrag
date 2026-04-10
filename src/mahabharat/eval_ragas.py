"""
RAGAS-based deep evaluation of the Mahabharata Graph RAG system.

Metrics (all judged by Amazon Nova Pro via Bedrock):
  - Faithfulness          (LLM judge — no ground truth needed)
  - AnswerRelevancy       (LLM judge — no ground truth needed)
  - ContextPrecision      (LLM judge + reference answer)
  - ContextRecall         (LLM judge + reference answer)
  - ToolCallAccuracy      (rule-based — uses expected_tool from eval set)

Run:
    PYTHONPATH=src uv run python -m mahabharat.eval_ragas
"""
import json
from typing import Dict, List

EVAL_PATH    = "data/eval_questions.json"
RAGAS_REPORT = "data/ragas_report.json"


def _make_ragas_llm():
    """Wrap Amazon Nova Pro (Bedrock) as a RAGAS-compatible LLM judge."""
    from langchain_aws import ChatBedrock
    from ragas.llms import LangchainLLMWrapper
    from mahabharat.config import AWS_PROFILE, AWS_REGION
    import boto3

    session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    bedrock_client = session.client("bedrock-runtime")
    llm = ChatBedrock(
        model_id="amazon.nova-pro-v1:0",
        client=bedrock_client,
    )
    return LangchainLLMWrapper(llm)


def _make_ragas_embeddings():
    """Wrap Bedrock Titan Embeddings as a RAGAS-compatible embeddings model."""
    from langchain_aws import BedrockEmbeddings
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from mahabharat.config import AWS_PROFILE, AWS_REGION
    import boto3

    session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    bedrock_client = session.client("bedrock-runtime")
    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v2:0",
        client=bedrock_client,
    )
    return LangchainEmbeddingsWrapper(embeddings)


def _build_dataset(questions: List[Dict], chat_results: List[Dict]):
    """Convert Q&A + chat results into a RAGAS EvaluationDataset."""
    from ragas import EvaluationDataset
    from ragas.dataset_schema import SingleTurnSample

    samples = []
    for q, r in zip(questions, chat_results):
        if "error" in r:
            continue

        # Combine graph and passage contexts into a list of context strings
        contexts = []
        if r.get("graph_context"):
            contexts.append(r["graph_context"])
        if r.get("passage_context"):
            for chunk in r["passage_context"].split("\n\n---\n\n"):
                chunk = chunk.strip()
                if chunk:
                    contexts.append(chunk)

        if not contexts:
            contexts = ["(no context retrieved)"]

        samples.append(SingleTurnSample(
            user_input=q["question"],
            response=r["answer"],
            retrieved_contexts=contexts,
            reference=q.get("reference", ""),
        ))
    return EvaluationDataset(samples=samples)


def _tool_call_accuracy(questions: List[Dict], chat_results: List[Dict]) -> float:
    """Rule-based tool-call accuracy — no LLM judge needed."""
    correct = 0
    total = 0
    for q, r in zip(questions, chat_results):
        if "error" in r:
            continue
        tools_used = {tc["tool"] for tc in r.get("tool_calls", [])}
        expected = q["expected_tool"]
        if expected == "both":
            ok = "graph_lookup" in tools_used and "passage_search" in tools_used
        else:
            ok = expected in tools_used
        correct += int(ok)
        total += 1
    return correct / total if total else 0.0


def run_ragas_eval(questions_path: str = EVAL_PATH) -> Dict:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from mahabharat.graph import load_graph
    from mahabharat.vector_store import load_vector_store
    from mahabharat.agent import chat

    print("Loading graph and vector store...")
    G  = load_graph()
    vs = load_vector_store()

    ragas_llm        = _make_ragas_llm()
    ragas_embeddings = _make_ragas_embeddings()

    with open(questions_path) as f:
        questions = json.load(f)

    # Step 1: run chat() for each question
    chat_results = []
    for q in questions:
        print(f"  [{q['id']}] {q['question'][:65]}...")
        try:
            r = chat(q["question"], G, vs)
            r["id"] = q["id"]
            chat_results.append(r)
        except Exception as e:
            print(f"    ERROR: {e}")
            chat_results.append({"id": q["id"], "error": str(e)})

    # Step 2: build RAGAS dataset
    dataset = _build_dataset(questions, chat_results)
    print(f"\nRunning RAGAS evaluation on {len(dataset.samples)} samples...")

    # Step 3: configure metrics with Bedrock judge and run
    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
    for m in metrics:
        m.llm = ragas_llm
    # answer_relevancy also needs an embeddings model for query reconstruction
    answer_relevancy.embeddings = ragas_embeddings

    result_df = evaluate(dataset, metrics=metrics).to_pandas()

    # Step 4: rule-based tool accuracy
    tool_acc = _tool_call_accuracy(questions, chat_results)

    # Step 5: aggregate and print
    summary = {
        "faithfulness":       float(result_df["faithfulness"].mean()),
        "answer_relevancy":   float(result_df["answer_relevancy"].mean()),
        "context_precision":  float(result_df["context_precision"].mean()),
        "context_recall":     float(result_df["context_recall"].mean()),
        "tool_call_accuracy": tool_acc,
        "n_samples":          len(result_df),
    }

    print(f"\n{'='*55}")
    print("RAGAS EVALUATION RESULTS")
    print(f"{'='*55}")
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k:<26}: {v:.3f}")
        else:
            print(f"  {k:<26}: {v}")
    print(f"{'='*55}")

    # Per-question detail
    per_sample = result_df.to_dict(orient="records")
    # Enrich with question IDs
    valid_questions = [q for q, r in zip(questions, chat_results) if "error" not in r]
    for row, q in zip(per_sample, valid_questions):
        row["id"]       = q["id"]
        row["category"] = q["category"]
        row["question"] = q["question"]

    report = {
        "summary":    summary,
        "per_sample": per_sample,
    }
    with open(RAGAS_REPORT, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report saved to {RAGAS_REPORT}")
    return report


if __name__ == "__main__":
    run_ragas_eval()
