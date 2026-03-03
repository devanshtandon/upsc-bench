from __future__ import annotations
"""Main evaluation runner for UPSC Bench.

Loads config, iterates through questions, calls solver, grades answers,
computes scores, and stores results.
"""

import argparse
import json
import uuid
from pathlib import Path

import yaml
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

from benchmark.grader import grade_response
from benchmark.scorer import calculate_score, check_pass_fail, load_cutoffs
from benchmark.solver import solve_question
from benchmark.db import BenchmarkDB


def load_config(config_path: str) -> dict:
    """Load YAML config for a benchmark run."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_questions(input_path: str, filter_years: list[int] | None = None,
                   filter_papers: list[str] | None = None,
                   max_questions: int | None = None) -> list[dict]:
    """Load and filter questions from the dataset."""
    with open(input_path) as f:
        questions = json.load(f)

    if filter_years:
        questions = [q for q in questions if q["year"] in filter_years]
    if filter_papers:
        questions = [q for q in questions if q["paper"] in filter_papers]
    if max_questions:
        questions = questions[:max_questions]

    return questions


def run_benchmark(config_path: str) -> dict:
    """Run a full benchmark evaluation.

    Args:
        config_path: Path to YAML config file.

    Returns:
        Dict with run summary including scores and pass/fail results.
    """
    config = load_config(config_path)
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
    print(f"Vision: {model_config.get('supports_vision', False)}")
    print()

    # Init DB
    db = BenchmarkDB(config["dbfilepath"])
    run_id = str(uuid.uuid4())[:8]
    db.create_run(run_id, model_name, config_path)

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
        grading = grade_response(response["raw_output"], question["correct_answer"])

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
                       grading, marks, response.get("usage", {}))

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
    output_path = config["output_filepath"]
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
    parser.add_argument("--config", required=True, help="Path to model config YAML")
    args = parser.parse_args()

    run_benchmark(args.config)
