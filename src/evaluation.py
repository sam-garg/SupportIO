import json
import time
from pathlib import Path
from typing import List, Dict, Any
from src.rag import query_rag
from src.config import DATA_DIR

EVAL_FILE = DATA_DIR / "eval_questions.json"

def load_eval_questions() -> List[Dict[str, Any]]:
    if not EVAL_FILE.exists():
        return []
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def run_evaluation() -> Dict[str, Any]:
    """
    Runs actual evaluation against test dataset and returns real measured metrics.
    """
    questions = load_eval_questions()
    if not questions:
        return {
            "total": 0,
            "retrieval_success_rate": 0.0,
            "escalation_accuracy": 0.0,
            "avg_latency_sec": 0.0,
            "details": []
        }

    correct_retrievals = 0
    correct_escalations = 0
    total_time = 0.0
    details = []

    for item in questions:
        q = item["question"]
        expected_src = item.get("expected_source", "").lower()
        should_esc = item.get("should_escalate", False)

        start_t = time.time()
        result = query_rag(q)
        duration = time.time() - start_t
        total_time += duration

        found_sources = [s["source"].lower() for s in result.get("sources", [])]
        retrieval_pass = (expected_src in " ".join(found_sources)) if expected_src != "none" else (len(found_sources) == 0)
        escalation_pass = (result.get("is_escalated", False) == should_esc)

        if retrieval_pass:
            correct_retrievals += 1
        if escalation_pass:
            correct_escalations += 1

        details.append({
            "question": q,
            "expected_source": item.get("expected_source", "-"),
            "retrieved_sources": [s["source"] for s in result.get("sources", [])],
            "is_escalated": result.get("is_escalated", False),
            "expected_escalate": should_esc,
            "retrieval_pass": retrieval_pass,
            "escalation_pass": escalation_pass,
            "latency": round(duration, 2)
        })

    total = len(questions)
    return {
        "total": total,
        "retrieval_success_rate": round((correct_retrievals / total) * 100, 1),
        "escalation_accuracy": round((correct_escalations / total) * 100, 1),
        "avg_latency_sec": round(total_time / total, 2),
        "details": details
    }
