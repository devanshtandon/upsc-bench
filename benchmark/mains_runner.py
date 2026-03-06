from __future__ import annotations
"""Mains evaluation runner for UPSC Bench.

Loads config, iterates through Mains questions, calls mains_solver to get
long-form answers, and stores raw answers. Judging happens separately
(in-session via subagents or external grading script).
"""

import argparse
import json
import uuid
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

from benchmark.mains_solver import solve_mains_question
from benchmark.common import load_config, load_questions, resolve_model_config
from benchmark.db import BenchmarkDB


def load_existing_answers(output_path: str) -> set[str]:
    """Load already-answered question IDs for resume support."""
    path = Path(output_path)
    if not path.exists():
        return set()

    with open(path) as f:
        data = json.load(f)

    return {r["question_id"] for r in data.get("results", [])}


def run_mains_benchmark(config_or_path: str | dict) -> dict:
    """Run a Mains benchmark — collect model answers only.

    Judging/grading happens separately via in-session subagents.

    Args:
        config_or_path: Path to YAML config file, or a pre-built config dict.

    Returns:
        Dict with model answers and metadata.
    """
    if isinstance(config_or_path, dict):
        config = config_or_path
        config_source = "(models.yaml)"
    else:
        config = load_config(config_or_path)
        config_source = config_or_path
    model_config = config["model"]
    model_name = model_config["name"]
    output_path = config["output_filepath"]

    # Load questions
    questions = load_questions(
        config["input_filepath"],
        filter_years=config.get("filter_years"),
        filter_papers=config.get("filter_papers"),
    )

    # Resume support — skip already-answered questions
    answered_ids = load_existing_answers(output_path)
    remaining = [q for q in questions if q["id"] not in answered_ids]

    print(f"Model: {model_name}")
    print(f"Total questions: {len(questions)}")
    print(f"Already answered: {len(answered_ids)}")
    print(f"Remaining: {len(remaining)}")
    print()

    # Init DB
    db = BenchmarkDB(config["dbfilepath"])
    run_id = str(uuid.uuid4())[:8]
    db.create_run(run_id, model_name, config_source,
                  metadata={"exam_type": "mains"})

    # Load existing results to append to
    all_results = []
    if Path(output_path).exists():
        with open(output_path) as f:
            existing = json.load(f)
            all_results = existing.get("results", [])

    # Determine max_tokens based on question type
    default_max_tokens = model_config.get("max_tokens", 8192)

    for question in tqdm(remaining, desc=f"Mains: {model_name}"):
        # Use lower max_tokens for short answers
        if question.get("question_type") == "essay":
            max_tokens = max(default_max_tokens, 8192)
        else:
            max_tokens = min(default_max_tokens, 4096)

        try:
            response = solve_mains_question(
                question,
                model=model_name,
                temperature=model_config.get("temperature", 0.0),
                max_tokens=max_tokens,
            )
        except Exception as e:
            print(f"\nError on {question['id']}: {e}")
            response = {
                "question_id": question["id"],
                "raw_output": "",
                "word_count": 0,
                "model": model_name,
                "usage": {},
            }

        result_entry = {
            "question_id": question["id"],
            "year": question["year"],
            "paper": question["paper"],
            "section": question.get("section"),
            "question_number": question["question_number"],
            "question_text": question["question_text"],
            "word_limit": question["word_limit"],
            "max_marks": question["max_marks"],
            "question_type": question.get("question_type", "short_answer"),
            "raw_output": response["raw_output"],
            "word_count": response["word_count"],
            "prompt_tokens": response["usage"].get("prompt_tokens", 0),
            "completion_tokens": response["usage"].get("completion_tokens", 0),
        }
        all_results.append(result_entry)

        # Save mains result to DB
        db.save_mains_result(
            run_id=run_id,
            question=question,
            raw_output=response["raw_output"],
            word_count=response["word_count"],
            usage=response.get("usage", {}),
            model=model_name,
        )

        # Incremental save after each question
        output_data = {
            "model": model_name,
            "config": config_source,
            "total_questions": len(questions),
            "answered": len(all_results),
            "results": all_results,
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

    db.complete_run(run_id, len(all_results))
    db.close()

    # Print summary
    print(f"\n{'='*50}")
    print(f"Mains Results: {model_name}")
    print(f"{'='*50}")
    print(f"Total answered: {len(all_results)}")

    papers = sorted(set(r["paper"] for r in all_results))
    for paper in papers:
        paper_results = [r for r in all_results if r["paper"] == paper]
        avg_words = sum(r["word_count"] for r in paper_results) / len(paper_results)
        print(f"  {paper}: {len(paper_results)} questions, avg {avg_words:.0f} words")

    total_tokens = sum(
        r.get("prompt_tokens", 0) + r.get("completion_tokens", 0)
        for r in all_results
    )
    print(f"Total tokens used: {total_tokens:,}")
    print(f"Results saved to {output_path}")

    return output_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UPSC Mains evaluation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", help="Path to Mains model config YAML (legacy)")
    group.add_argument("--model", help="Model key from config/models.yaml (e.g., gpt5, claude_opus)")
    args = parser.parse_args()

    if args.model:
        run_mains_benchmark(resolve_model_config(args.model, exam_type="mains"))
    else:
        run_mains_benchmark(args.config)
