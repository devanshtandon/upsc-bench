#!/usr/bin/env python3
"""Mains grading infrastructure.

Two modes:
1. prepare: Read model answer files, produce grading_input.json for subagent grading
2. merge: Read grading output files, merge scores back into mains_results files

Usage:
    python scripts/grade_mains.py prepare --answers results/raw/mains_answers_*.json
    python scripts/grade_mains.py merge --scores results/grading/ --output results/raw/
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import yaml


def load_rubric(judge_path: str = "config/judge.yaml") -> dict:
    """Load the grading rubric."""
    with open(judge_path) as f:
        return yaml.safe_load(f)


def prepare_grading_input(answer_files: list[str], output_path: str,
                          batch_size: int = 25) -> dict:
    """Prepare grading input from model answer files.

    Reads all model answers, strips model identity (debiasing), and splits
    into batches for parallel subagent grading.

    Args:
        answer_files: List of paths to mains_answers_*.json files.
        output_path: Where to write the grading input JSON.
        batch_size: Number of answers per grading batch.

    Returns:
        Summary dict with batch count and total answers.
    """
    rubric = load_rubric()
    all_answers = []

    for fpath in answer_files:
        with open(fpath) as f:
            data = json.load(f)

        model = data["model"]
        for result in data["results"]:
            all_answers.append({
                "question_id": result["question_id"],
                "year": result["year"],
                "paper": result["paper"],
                "question_number": result["question_number"],
                "question_text": result["question_text"],
                "word_limit": result["word_limit"],
                "max_marks": result["max_marks"],
                "question_type": result.get("question_type", "short_answer"),
                "section": result.get("section"),
                # Debiased: label as "candidate" not model name
                "candidate_id": f"candidate_{hash(model) % 10000:04d}",
                "candidate_answer": result["raw_output"],
                "word_count": result["word_count"],
                # Store model for merge step (not shown to graders)
                "_model": model,
            })

    # Split into batches
    batches = []
    for i in range(0, len(all_answers), batch_size):
        batch = all_answers[i:i + batch_size]
        batch_id = f"batch_{i // batch_size + 1:03d}"
        batches.append({
            "batch_id": batch_id,
            "answers": batch,
            "count": len(batch),
        })

    output = {
        "total_answers": len(all_answers),
        "batch_size": batch_size,
        "num_batches": len(batches),
        "rubric": rubric["rubric"],
        "batches": batches,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Prepared {len(all_answers)} answers in {len(batches)} batches")
    print(f"Written to {output_path}")

    return {
        "total_answers": len(all_answers),
        "num_batches": len(batches),
        "output_path": output_path,
    }


def merge_grading_output(scores_dir: str, answers_dir: str,
                         output_dir: str) -> dict:
    """Merge grading scores back into per-model result files.

    Reads grading output JSON files (one per batch), maps scores back to
    models using the _model field, and produces mains_results_*.json files.

    Args:
        scores_dir: Directory containing grading output batch files.
        answers_dir: Directory containing original mains_answers_*.json files.
        output_dir: Where to write mains_results_*.json files.

    Returns:
        Summary dict with models and scores.
    """
    # Load all grading scores
    score_files = sorted(glob.glob(f"{scores_dir}/grading_batch_*.json"))
    all_scores = {}  # question_id -> {candidate_id -> score_data}

    for fpath in score_files:
        with open(fpath) as f:
            batch_data = json.load(f)

        for score in batch_data.get("scores", []):
            key = (score["question_id"], score.get("candidate_id", ""))
            all_scores[key] = score

    # Load original answers to get model mapping
    answer_files = sorted(glob.glob(f"{answers_dir}/mains_answers_*.json"))
    model_results = {}  # model -> list of results

    for fpath in answer_files:
        with open(fpath) as f:
            data = json.load(f)

        model = data["model"]
        model_results[model] = []
        candidate_id = f"candidate_{hash(model) % 10000:04d}"

        for result in data["results"]:
            qid = result["question_id"]
            score_key = (qid, candidate_id)
            score_data = all_scores.get(score_key, {})

            graded_result = {
                **result,
                "model": model,
                "rubric_scores": score_data.get("rubric_scores", {}),
                "total_score": score_data.get("total_score", 0),
                "max_marks": result["max_marks"],
                "feedback": score_data.get("brief_feedback", ""),
            }
            model_results[model].append(graded_result)

    # Write per-model result files
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    summary = {}

    for model, results in model_results.items():
        # Derive slug from model name
        slug = model.split("/")[-1].replace(".", "_").replace("-", "_")
        output_path = f"{output_dir}/mains_results_{slug}.json"

        total_score = sum(r["total_score"] for r in results)
        max_marks = sum(r["max_marks"] for r in results)

        output_data = {
            "model": model,
            "total_score": round(total_score, 2),
            "max_marks": max_marks,
            "score_pct": round(total_score / max_marks * 100, 2) if max_marks else 0,
            "results": results,
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        summary[model] = {
            "total_score": round(total_score, 2),
            "max_marks": max_marks,
            "questions_graded": len(results),
            "output_path": output_path,
        }
        print(f"{model}: {total_score:.1f}/{max_marks} "
              f"({total_score/max_marks*100:.1f}%) -> {output_path}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Mains grading infrastructure")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # prepare command
    prep = subparsers.add_parser("prepare", help="Prepare grading input batches")
    prep.add_argument("--answers", nargs="+", required=True,
                      help="Paths to mains_answers_*.json files")
    prep.add_argument("--output", default="results/mains_grading_input.json",
                      help="Output path for grading input")
    prep.add_argument("--batch-size", type=int, default=25,
                      help="Answers per grading batch")

    # merge command
    merge = subparsers.add_parser("merge", help="Merge grading scores into results")
    merge.add_argument("--scores", default="results/grading/",
                       help="Directory with grading output batch files")
    merge.add_argument("--answers", default="results/raw/",
                       help="Directory with original mains_answers files")
    merge.add_argument("--output", default="results/raw/",
                       help="Output directory for mains_results files")

    args = parser.parse_args()

    if args.command == "prepare":
        prepare_grading_input(args.answers, args.output, args.batch_size)
    elif args.command == "merge":
        merge_grading_output(args.scores, args.answers, args.output)


if __name__ == "__main__":
    main()
