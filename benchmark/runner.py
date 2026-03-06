from __future__ import annotations
"""Main evaluation runner for UPSC Bench.

Loads config, iterates through questions, calls solver, grades answers,
computes scores, and stores results.
"""

import argparse
import json
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

from benchmark.grader import grade_response
from benchmark.scorer import calculate_score, check_pass_fail
from benchmark.common import load_cutoffs, load_config, load_questions, resolve_model_config
from benchmark.solver import solve_question
from benchmark.db import BenchmarkDB


def run_benchmark(config_or_path: str | dict, force: bool = False) -> dict:
    """Run a full benchmark evaluation.

    Args:
        config_or_path: Path to YAML config file, or a pre-built config dict.
        force: If True, overwrite existing results file. Otherwise abort.

    Returns:
        Dict with run summary including scores and pass/fail results.
    """
    if isinstance(config_or_path, dict):
        config = config_or_path
        config_source = "(models.yaml)"
    else:
        config = load_config(config_or_path)
        config_source = config_or_path

    # Check overwrite protection before doing any work
    output_path = config["output_filepath"]
    if Path(output_path).exists() and not force:
        print(f"ERROR: {output_path} already exists. Use --force to overwrite.")
        sys.exit(1)

    model_config = config["model"]
    model_name = model_config["name"]

    # Load questions
    questions = load_questions(
        config["input_filepath"],
        filter_years=config.get("filter_years"),
        filter_papers=config.get("filter_papers"),
        max_questions=config.get("max_questions"),
    )

    print(f"Model: {model_name}")
    print(f"Questions: {len(questions)}")
    print(f"Vision: {model_config.get('supports_vision', True)}")
    print()

    # Init DB
    db = BenchmarkDB(config["dbfilepath"])
    run_id = str(uuid.uuid4())[:8]
    db.create_run(run_id, model_name, config_source)

    # Run evaluation
    all_results = []

    for question in tqdm(questions, desc=f"Evaluating {model_name}"):
        # Solve
        try:
            response = solve_question(
                question,
                model=model_name,
                temperature=model_config.get("temperature", 0.0),
                max_tokens=model_config.get("max_tokens", 4096),
                supports_vision=model_config.get("supports_vision", True),
            )
        except Exception as e:
            print(f"\nError on {question['id']}: {e}")
            response = {
                "question_id": question["id"],
                "raw_output": "",
                "model": model_name,
                "usage": {},
            }

        # Grade
        grading = grade_response(
            response["raw_output"],
            question["correct_answer"],
            disputed_answers=question.get("disputed_answers"),
        )

        # Calculate marks for this question
        paper = question["paper"]
        if grading["result"] == "correct":
            marks = question["marks_correct"]
        elif grading["result"] == "wrong":
            marks = question["marks_wrong"]
        else:
            marks = question["marks_unanswered"]

        # Store result
        result_entry = {
            "question_id": question["id"],
            "year": question["year"],
            "paper": paper,
            "question_number": question["question_number"],
            "raw_output": response["raw_output"],
            "extracted_answer": grading["extracted_answer"],
            "correct_answer": grading["correct_answer"],
            "result": grading["result"],
            "marks": marks,
            "usage": response.get("usage", {}),
        }
        all_results.append(result_entry)

        db.save_result(run_id, question, response["raw_output"],
                       grading, marks, response.get("usage", {}),
                       model=model_name)

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

    # Overall summary
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
    parser = argparse.ArgumentParser(description="Run UPSC Bench evaluation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", help="Path to model config YAML (legacy)")
    group.add_argument("--model", help="Model key from config/models.yaml (e.g., gpt5, claude_opus)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing results file")
    args = parser.parse_args()

    if args.model:
        run_benchmark(resolve_model_config(args.model, exam_type="prelims"), force=args.force)
    else:
        run_benchmark(args.config, force=args.force)
