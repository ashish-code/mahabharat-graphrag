"""
Offline evaluation harness for the Mahabharata Graph RAG chatbot.

Scores answers on:
  - entity_recall:  fraction of expected entity names mentioned in the answer
  - keyword_recall: fraction of expected keywords mentioned in the answer
  - tool_correct:   whether the correct tool(s) were called

Run:
    PYTHONPATH=src uv run python -m mahabharat.eval

Requires:
  - data/graph.json and data/faiss_index/ (built via build pipeline)
  - AWS credentials with Bedrock access
  - data/eval_questions.json (golden Q&A dataset)
"""
import json
from typing import Dict, List

EVAL_PATH   = "data/eval_questions.json"
REPORT_PATH = "data/eval_report.json"


def score_answer(
    answer: str,
    expected_entities: List[str],
    expected_keywords: List[str],
) -> Dict:
    a = answer.lower()
    ent_hits = [e for e in expected_entities if e.lower() in a]
    kw_hits  = [k for k in expected_keywords  if k.lower() in a]
    return {
        "entity_recall":  len(ent_hits) / len(expected_entities) if expected_entities else 1.0,
        "keyword_recall": len(kw_hits)  / len(expected_keywords)  if expected_keywords  else 1.0,
        "entity_hits":    ent_hits,
        "keyword_hits":   kw_hits,
    }


def score_tool_use(tool_calls: List[Dict], expected_tool: str) -> bool:
    tools_used = {tc["tool"] for tc in tool_calls}
    if expected_tool == "both":
        return "graph_lookup" in tools_used and "passage_search" in tools_used
    return expected_tool in tools_used


def run_eval(questions_path: str = EVAL_PATH) -> Dict:
    from .graph import load_graph
    from .vector_store import load_vector_store
    from .agent import chat

    print("Loading graph and vector store...")
    G  = load_graph()
    vs = load_vector_store()

    with open(questions_path) as f:
        questions = json.load(f)

    results = []
    for q in questions:
        print(f"  [{q['id']}] {q['question'][:65]}...")
        try:
            result = chat(q["question"], G, vs)
            scores  = score_answer(result["answer"],
                                   q["expected_entities"],
                                   q["expected_keywords"])
            tool_ok = score_tool_use(result["tool_calls"], q["expected_tool"])
            results.append({
                "id":             q["id"],
                "category":       q["category"],
                "question":       q["question"],
                "answer_preview": result["answer"][:120] + "...",
                "entity_recall":  scores["entity_recall"],
                "keyword_recall": scores["keyword_recall"],
                "tool_correct":   tool_ok,
                "entity_hits":    scores["entity_hits"],
                "keyword_hits":   scores["keyword_hits"],
                "tools_used":     [tc["tool"] for tc in result["tool_calls"]],
            })
        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({
                "id": q["id"], "category": q["category"], "question": q["question"],
                "error": str(e),
                "entity_recall": 0.0, "keyword_recall": 0.0, "tool_correct": False,
            })

    # Aggregate by category
    categories = sorted({r["category"] for r in results})
    print(f"\n{'='*65}")
    print(f"EVAL RESULTS  ({len(results)} questions)")
    print(f"{'='*65}")
    print(f"{'Category':<16} {'N':>3}  {'Entity':>8}  {'Keyword':>8}  {'Tool':>6}")
    print(f"{'-'*65}")
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        n   = len(cat_results)
        er  = sum(r["entity_recall"]  for r in cat_results) / n
        kr  = sum(r["keyword_recall"] for r in cat_results) / n
        ta  = sum(r["tool_correct"]   for r in cat_results) / n
        print(f"{cat:<16} {n:>3}  {er:>8.1%}  {kr:>8.1%}  {ta:>6.1%}")

    print(f"{'-'*65}")
    total = len(results)
    avg_er = sum(r["entity_recall"]  for r in results) / total
    avg_kr = sum(r["keyword_recall"] for r in results) / total
    avg_ta = sum(r["tool_correct"]   for r in results) / total
    print(f"{'OVERALL':<16} {total:>3}  {avg_er:>8.1%}  {avg_kr:>8.1%}  {avg_ta:>6.1%}")
    print(f"{'='*65}")

    report = {
        "summary": {
            "total":          total,
            "entity_recall":  avg_er,
            "keyword_recall": avg_kr,
            "tool_accuracy":  avg_ta,
        },
        "by_category": {
            cat: {
                "entity_recall":  sum(r["entity_recall"]  for r in results if r["category"] == cat) / len([r for r in results if r["category"] == cat]),
                "keyword_recall": sum(r["keyword_recall"] for r in results if r["category"] == cat) / len([r for r in results if r["category"] == cat]),
                "tool_accuracy":  sum(r["tool_correct"]   for r in results if r["category"] == cat) / len([r for r in results if r["category"] == cat]),
            }
            for cat in categories
        },
        "results": results,
    }

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to {REPORT_PATH}")
    return report


if __name__ == "__main__":
    run_eval()
