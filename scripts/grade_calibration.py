#!/usr/bin/env python3
"""Grade coaching model answers with the current judge for calibration.

Reads coaching_answers.json, prepares grading input batches (same format
as the Mains regrade), and merges grading outputs into a results file.

Usage:
    python scripts/grade_calibration.py prepare   # Create grading input batches
    python scripts/grade_calibration.py merge      # Merge grading output into report
"""
import json
import sys
from pathlib import Path

import yaml

CALIBRATION_FILE = Path("data/calibration/coaching_answers.json")
RUBRIC_FILE = Path("config/judge.yaml")
GRADING_DIR = Path("data/calibration/grading")
RESULTS_FILE = Path("data/calibration/grading_results.json")

BATCH_SIZE = 5  # 5 questions per grading batch


def format_rubric(rubric_config, paper):
    """Format rubric dimensions for the prompt."""
    key = "essay" if "essay" in paper.lower() else "gs"
    rubric = rubric_config["rubric"][key]
    lines = []
    for dim_key, dim_info in rubric.items():
        lines.append(f"  {dim_key}: {dim_info['weight']}% — {dim_info['description']}")
    return "\n".join(lines)


def prepare():
    """Create grading input batches from coaching answers."""
    with open(CALIBRATION_FILE) as f:
        answers = json.load(f)

    with open(RUBRIC_FILE) as f:
        rubric_config = yaml.safe_load(f)

    GRADING_DIR.mkdir(parents=True, exist_ok=True)

    # Build input entries matching the solo grading format
    entries = []
    for a in answers:
        rubric_type = "Essay Paper" if a["paper"] == "mains_essay" else "GS Paper"
        rubric_text = format_rubric(rubric_config, a["paper"])

        entry = {
            "question_id": a["id"],
            "paper": a["paper"],
            "section": None,
            "question_number": a["question_number"],
            "question_text": a["question_text"],
            "word_limit": a["word_limit"],
            "max_marks": a["max_marks"],
            "question_type": "short_answer" if a["max_marks"] <= 15 else "case_study",
            "answer": a["model_answer"],
            "candidate_id": "coaching_model",
            "rubric_type": rubric_type,
            "rubric_text": rubric_text,
        }
        entries.append(entry)

    # Batch them
    batches = []
    for i in range(0, len(entries), BATCH_SIZE):
        batches.append(entries[i:i + BATCH_SIZE])

    for idx, batch in enumerate(batches, 1):
        output_file = GRADING_DIR / f"cal_input_batch_{idx:03d}.json"
        with open(output_file, "w") as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)
        print(f"Batch {idx:03d}: {len(batch)} questions")

    print(f"\nTotal: {len(batches)} batches, {len(entries)} questions")
    print(f"Output: {GRADING_DIR}/")


def merge():
    """Merge grading outputs into a single results file with calibration comparison."""
    with open(CALIBRATION_FILE) as f:
        answers = {a["id"]: a for a in json.load(f)}

    results = []
    batch_files = sorted(GRADING_DIR.glob("cal_grading_batch_*.json"))

    if not batch_files:
        print("ERROR: No grading output files found.")
        print("Expected files: data/calibration/grading/cal_grading_batch_*.json")
        sys.exit(1)

    for batch_file in batch_files:
        with open(batch_file) as f:
            batch_data = json.load(f)

        for q in batch_data:
            qid = q["question_id"]

            # Handle two output formats:
            # Format A (standard): {"question_id": ..., "candidates": [{...}]}
            # Format B (flat): {"question_id": ..., "candidate_id": ..., "total_score": ...}
            if q.get("candidates"):
                candidate = q["candidates"][0]
            else:
                # Flat format — extract rubric scores from dimension_scores or rubric_scores
                rubric_scores = q.get("rubric_scores", q.get("dimension_scores", {}))
                # Normalize dimension_scores format (has nested weight/max/score)
                normalized = {}
                for dim_key, dim_val in rubric_scores.items():
                    if isinstance(dim_val, dict):
                        normalized[dim_key] = {
                            "score": dim_val.get("score", 0),
                            "justification": dim_val.get("justification", ""),
                        }
                # Compute total from dimension scores if not provided
                total = q.get("total_score", sum(
                    d.get("score", 0) for d in normalized.values()
                ))
                candidate = {
                    "candidate_id": q.get("candidate_id", "coaching_model"),
                    "summary": q.get("summary", ""),
                    "analysis": q.get("analysis", ""),
                    "rubric_scores": normalized,
                    "total_score": total,
                    "max_marks": q.get("max_marks", 0),
                    "brief_feedback": q.get("brief_feedback", ""),
                }

            judge_score = candidate.get("total_score", 0)
            max_marks = candidate.get("max_marks", 0)

            cal_answer = answers.get(qid, {})
            expected_low = cal_answer.get("expected_score_low", 0)
            expected_high = cal_answer.get("expected_score_high", 0)
            expected_mid = (expected_low + expected_high) / 2

            results.append({
                "calibration_id": qid,
                "paper": cal_answer.get("paper", "unknown"),
                "question_number": cal_answer.get("question_number"),
                "max_marks": max_marks,
                "judge_score": judge_score,
                "judge_pct": round(judge_score / max_marks * 100, 1) if max_marks > 0 else 0,
                "expected_low": expected_low,
                "expected_high": expected_high,
                "expected_mid": expected_mid,
                "expected_pct": round(expected_mid / max_marks * 100, 1) if max_marks > 0 else 0,
                "offset": round(judge_score - expected_mid, 2),
                "within_range": expected_low <= judge_score <= expected_high,
                "rubric_scores": candidate.get("rubric_scores", {}),
                "summary": candidate.get("summary", ""),
                "brief_feedback": candidate.get("brief_feedback", ""),
            })

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Merged {len(results)} grading results to {RESULTS_FILE}")

    # Print quick summary
    if results:
        offsets = [r["offset"] for r in results]
        within = sum(1 for r in results if r["within_range"])
        import statistics
        print(f"\nQuick summary:")
        print(f"  Within expected range: {within}/{len(results)}")
        print(f"  Mean offset: {statistics.mean(offsets):+.2f} marks")
        print(f"  Median offset: {statistics.median(offsets):+.2f} marks")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("prepare", "merge"):
        print("Usage: python scripts/grade_calibration.py [prepare|merge]")
        sys.exit(1)

    if sys.argv[1] == "prepare":
        prepare()
    else:
        merge()
