from __future__ import annotations
"""Aggregate per-model result JSONs into leaderboard.json for the frontend.

Reads all results from results/raw/, computes rankings, pass/fail against
real UPSC cutoffs, and outputs a single leaderboard.json.
"""

import json
import os
import shutil
from pathlib import Path

import yaml

from benchmark.scorer import estimate_rank, load_rank_mapping


def load_cutoffs(cutoffs_path: str = "config/cutoffs.yaml") -> dict:
    """Load UPSC cutoff marks and marking scheme."""
    with open(cutoffs_path) as f:
        return yaml.safe_load(f)


def aggregate_model_results(results_path: str, cutoffs: dict, rank_data: dict | None = None) -> dict:
    """Aggregate a single model's results into leaderboard format.

    Args:
        results_path: Path to a model's result JSON.
        cutoffs: Cutoff data from cutoffs.yaml.

    Returns:
        Dict with model name, scores, pass/fail per year/paper, and overall stats.
    """
    with open(results_path) as f:
        data = json.load(f)

    model = data["model"]
    results = data.get("results", [])
    scores_by_year = data.get("scores_by_year", {})

    # Overall stats
    total = len(results)
    correct = sum(1 for r in results if r["result"] == "correct")
    wrong = sum(1 for r in results if r["result"] == "wrong")
    unanswered = sum(1 for r in results if r["result"] == "unanswered")
    accuracy = round(correct / total * 100, 2) if total > 0 else 0.0

    # Compute overall marks per paper across all years
    paper_totals = {}
    for year_str, papers in scores_by_year.items():
        for paper, score_data in papers.items():
            if paper not in paper_totals:
                paper_totals[paper] = {
                    "total_marks": 0,
                    "max_marks": 0,
                    "correct": 0,
                    "wrong": 0,
                    "unanswered": 0,
                    "years_passed": 0,
                    "years_total": 0,
                }
            pt = paper_totals[paper]
            pt["total_marks"] += score_data.get("total_marks", 0)
            pt["max_marks"] += score_data.get("max_marks", 0)
            pt["correct"] += score_data.get("correct_count", 0)
            pt["wrong"] += score_data.get("wrong_count", 0)
            pt["unanswered"] += score_data.get("unanswered_count", 0)
            pt["years_total"] += 1
            if score_data.get("passed", False):
                pt["years_passed"] += 1

    # Per-year detail for frontend
    yearly = {}
    for year_str, papers in scores_by_year.items():
        year = int(year_str) if isinstance(year_str, str) else year_str
        yearly[year] = {}
        for paper, score_data in papers.items():
            yearly[year][paper] = {
                "marks": score_data.get("total_marks", 0),
                "max_marks": score_data.get("max_marks", 0),
                "correct": score_data.get("correct_count", 0),
                "wrong": score_data.get("wrong_count", 0),
                "unanswered": score_data.get("unanswered_count", 0),
                "accuracy": score_data.get("accuracy", 0),
                "passed": score_data.get("passed", False),
                "cutoff": score_data.get("cutoff", 0),
                "margin": score_data.get("margin", 0),
            }
            # Add rank estimation for GS1
            if paper == "gs1" and rank_data:
                rank_info = estimate_rank(score_data.get("total_marks", 0), year, rank_data)
                yearly[year][paper]["estimated_rank"] = rank_info

    # Overall pass: passed GS1 cutoff AND CSAT qualifying in all years
    gs1_all_pass = paper_totals.get("gs1", {}).get("years_passed", 0) == paper_totals.get(
        "gs1", {}
    ).get("years_total", 0)
    csat_all_pass = paper_totals.get("csat", {}).get("years_passed", 0) == paper_totals.get(
        "csat", {}
    ).get("years_total", 0)

    # Average GS1 marks across years for ranking
    gs1_avg_marks = 0.0
    gs1_years = paper_totals.get("gs1", {}).get("years_total", 0)
    if gs1_years > 0:
        gs1_avg_marks = round(paper_totals["gs1"]["total_marks"] / gs1_years, 2)

    return {
        "model": model,
        "overall": {
            "total_questions": total,
            "correct": correct,
            "wrong": wrong,
            "unanswered": unanswered,
            "accuracy": accuracy,
            "gs1_avg_marks": gs1_avg_marks,
            "gs1_all_years_pass": gs1_all_pass,
            "csat_all_years_pass": csat_all_pass,
        },
        "paper_totals": paper_totals,
        "yearly": yearly,
    }


def generate_leaderboard(
    results_dir: str = "results/raw",
    cutoffs_path: str = "config/cutoffs.yaml",
    output_path: str = "results/leaderboard.json",
    web_data_path: str = "web/data/leaderboard.json",
) -> dict:
    """Generate the full leaderboard from all model results.

    Args:
        results_dir: Directory containing per-model result JSONs.
        cutoffs_path: Path to cutoffs YAML.
        output_path: Where to write leaderboard.json.
        web_data_path: Copy to web/data/ for frontend static build.

    Returns:
        The leaderboard data dict.
    """
    cutoffs = load_cutoffs(cutoffs_path)
    rank_data = load_rank_mapping()

    # Load all model results
    models = []
    results_path = Path(results_dir)

    if not results_path.exists():
        print(f"No results directory found at {results_dir}")
        return {"models": [], "metadata": {}}

    for result_file in sorted(results_path.glob("results_*.json")):
        print(f"Loading {result_file.name}...")
        model_data = aggregate_model_results(str(result_file), cutoffs, rank_data)
        models.append(model_data)

    # Rank by overall accuracy (descending), then GS1 marks as tiebreaker
    models.sort(key=lambda m: (m["overall"]["accuracy"], m["overall"]["gs1_avg_marks"]), reverse=True)
    for i, model in enumerate(models):
        model["rank"] = i + 1

    leaderboard = {
        "models": models,
        "metadata": {
            "total_models": len(models),
            "years": sorted({
                int(y) for m in models
                for y in m.get("yearly", {}).keys()
            }) or [2024],
            "papers": ["gs1", "csat"],
            "cutoffs": cutoffs["cutoffs"],
            "marking_scheme": cutoffs["marking_scheme"],
        },
    }

    # Write to results/
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(leaderboard, f, indent=2)
    print(f"Leaderboard saved to {output_path}")

    # Copy to web/data/ for frontend
    if web_data_path:
        Path(web_data_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, web_data_path)
        print(f"Copied to {web_data_path}")

    # Print summary table
    print(f"\n{'='*70}")
    print(f"{'Rank':<5} {'Model':<30} {'Accuracy':<10} {'GS1 Avg':<10} {'Pass?'}")
    print(f"{'='*70}")
    for m in models:
        o = m["overall"]
        pass_str = ("GS1:Y" if o["gs1_all_years_pass"] else "GS1:N") + " " + (
            "CSAT:Y" if o["csat_all_years_pass"] else "CSAT:N"
        )
        print(f"{m['rank']:<5} {m['model']:<30} {o['accuracy']:<10} {o['gs1_avg_marks']:<10} {pass_str}")

    return leaderboard


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate UPSC Bench leaderboard")
    parser.add_argument("--results-dir", default="results/raw")
    parser.add_argument("--cutoffs", default="config/cutoffs.yaml")
    parser.add_argument("--output", default="results/leaderboard.json")
    parser.add_argument("--web-data", default="web/data/leaderboard.json")
    args = parser.parse_args()

    generate_leaderboard(args.results_dir, args.cutoffs, args.output, args.web_data)
