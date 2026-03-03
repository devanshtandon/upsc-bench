"""Self-evaluation script for UPSC Bench.

Takes pre-computed answers (from Claude answering questions in conversation)
and runs them through the grading/scoring pipeline to generate results
in the same format as runner.py.

Usage:
    python scripts/self_eval.py --answers my_answers.json [--model-name "anthropic/claude-opus-4"]
"""

import argparse
import json
import uuid
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.grader import grade_response
from benchmark.scorer import calculate_score, check_pass_fail, load_cutoffs
from benchmark.db import BenchmarkDB


def run_self_eval(
    dataset_path: str = "data/processed/upsc_bench.json",
    answers_path: str = "data/processed/my_answers.json",
    model_name: str = "anthropic/claude-opus-4-6-20250415",
    output_path: str = "results/raw/results_claude_opus.json",
    db_path: str = "db/benchmark_results.db",
) -> dict:
    """Run evaluation using pre-computed answers.

    Args:
        dataset_path: Path to the upsc_bench.json dataset.
        answers_path: Path to JSON mapping question_id -> answer letter.
        model_name: Model name for results metadata.
        output_path: Where to save results JSON.
        db_path: SQLite database path.

    Returns:
        Summary dict with scores and results.
    """
    # Load dataset
    with open(dataset_path) as f:
        questions = json.load(f)
    print(f"Loaded {len(questions)} questions from {dataset_path}")

    # Load pre-computed answers
    with open(answers_path) as f:
        answers = json.load(f)
    print(f"Loaded {len(answers)} answers from {answers_path}")

    # Init DB
    db = BenchmarkDB(db_path)
    run_id = str(uuid.uuid4())[:8]
    db.create_run(run_id, model_name, "self-eval")

    # Process each question
    all_results = []
    for question in questions:
        qid = question["id"]

        # Get pre-computed answer
        my_answer = answers.get(qid, None)
        if my_answer:
            # Format as a model response for the grader
            raw_output = f"Answer: ({my_answer.upper()})"
        else:
            raw_output = ""  # No answer provided

        # Grade using the existing grader
        grading = grade_response(raw_output, question["correct_answer"])

        # Calculate marks
        if grading["result"] == "correct":
            marks = question["marks_correct"]
        elif grading["result"] == "wrong":
            marks = question["marks_wrong"]
        else:
            marks = question["marks_unanswered"]

        result_entry = {
            "question_id": qid,
            "year": question["year"],
            "paper": question["paper"],
            "question_number": question["question_number"],
            "raw_output": raw_output,
            "extracted_answer": grading["extracted_answer"],
            "correct_answer": grading["correct_answer"],
            "result": grading["result"],
            "marks": marks,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
        all_results.append(result_entry)

        # Save to DB
        db.save_result(run_id, question, raw_output, grading, marks, {})

    db.complete_run(run_id, len(questions))

    # Calculate scores per year/paper
    cutoffs_data = load_cutoffs()
    marking_scheme = cutoffs_data["marking_scheme"]

    scores = {}
    years = sorted(set(r["year"] for r in all_results))
    papers = sorted(set(r["paper"] for r in all_results))

    for year in years:
        scores[year] = {}
        for paper in papers:
            paper_results = [r for r in all_results
                           if r["year"] == year and r["paper"] == paper]
            if not paper_results:
                continue

            score = calculate_score(paper_results, paper, marking_scheme)
            pass_fail = check_pass_fail(score["total_marks"], paper, year, cutoffs_data)
            scores[year][paper] = {**score, **pass_fail}

    # Build summary (same format as runner.py)
    summary = {
        "run_id": run_id,
        "model": model_name,
        "total_questions": len(all_results),
        "overall_correct": sum(1 for r in all_results if r["result"] == "correct"),
        "overall_wrong": sum(1 for r in all_results if r["result"] == "wrong"),
        "overall_unanswered": sum(1 for r in all_results if r["result"] == "unanswered"),
        "overall_accuracy": round(
            sum(1 for r in all_results if r["result"] == "correct")
            / len(all_results) * 100, 2
        ) if all_results else 0,
        "scores_by_year": scores,
        "results": all_results,
    }

    # Save output
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {output_path}")

    # Print summary
    print(f"\n{'='*50}")
    print(f"Results: {model_name}")
    print(f"{'='*50}")
    print(f"Total: {summary['total_questions']} questions")
    print(f"Correct: {summary['overall_correct']} | Wrong: {summary['overall_wrong']} | Unanswered: {summary['overall_unanswered']}")
    print(f"Accuracy: {summary['overall_accuracy']}%")

    for year in years:
        for paper in papers:
            if paper in scores.get(year, {}):
                s = scores[year][paper]
                status = "PASS" if s["passed"] else "FAIL"
                print(f"  {paper.upper()} {year}: {s['total_marks']}/{s['max_marks']} "
                      f"(cutoff: {s['cutoff']}) [{status}, margin: {s['margin']:+.2f}]")

    db.close()
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UPSC Bench self-evaluation")
    parser.add_argument("--dataset", default="data/processed/upsc_bench.json")
    parser.add_argument("--answers", default="data/processed/my_answers.json")
    parser.add_argument("--model-name", default="anthropic/claude-opus-4-6-20250415")
    parser.add_argument("--output", default="results/raw/results_claude_opus.json")
    parser.add_argument("--db", default="db/benchmark_results.db")
    args = parser.parse_args()

    run_self_eval(args.dataset, args.answers, args.model_name, args.output, args.db)
