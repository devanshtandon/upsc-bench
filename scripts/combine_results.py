"""Combine per-year benchmark results for each model.

After running 2025-only benchmarks, this script combines them
with existing 2024 results into a single results file per model.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from benchmark.scorer import calculate_score, check_pass_fail, load_cutoffs


def combine_results(result_2024_path: str, result_2025_path: str,
                    output_path: str) -> None:
    """Combine 2024 and 2025 results into a single file."""
    with open(result_2024_path) as f:
        data_2024 = json.load(f)
    with open(result_2025_path) as f:
        data_2025 = json.load(f)

    model = data_2024["model"]
    assert model == data_2025["model"], f"Model mismatch: {model} vs {data_2025['model']}"

    # Combine results lists
    all_results = data_2024["results"] + data_2025["results"]
    total = len(all_results)
    correct = sum(1 for r in all_results if r["result"] == "correct")
    wrong = sum(1 for r in all_results if r["result"] == "wrong")
    unanswered = sum(1 for r in all_results if r["result"] == "unanswered")

    # Combine scores_by_year
    scores = dict(data_2024.get("scores_by_year", {}))
    scores.update(data_2025.get("scores_by_year", {}))

    combined = {
        "run_id": f"{data_2024['run_id']}+{data_2025['run_id']}",
        "model": model,
        "total_questions": total,
        "overall_correct": correct,
        "overall_wrong": wrong,
        "overall_unanswered": unanswered,
        "overall_accuracy": round(correct / total * 100, 2) if total > 0 else 0,
        "scores_by_year": scores,
        "results": all_results,
    }

    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"Combined {model}: {total} questions -> {output_path}")


def main():
    results_dir = Path("results/raw")

    # Backup 2024-only results
    backup_dir = results_dir / "2024_only"
    backup_dir.mkdir(exist_ok=True)

    models = ["claude_opus", "gemini_3_pro", "gemini_flash", "gpt5", "grok4"]

    for model in models:
        f2024 = results_dir / f"results_{model}.json"
        f2025 = results_dir / f"results_{model}_2025.json"

        if not f2024.exists():
            print(f"No 2024 results for {model}, skipping")
            continue
        if not f2025.exists():
            print(f"No 2025 results for {model}, skipping")
            continue

        # Backup 2024
        import shutil
        shutil.copy2(f2024, backup_dir / f"results_{model}.json")

        # Combine
        combine_results(str(f2024), str(f2025), str(f2024))

    print("\nDone. Run scripts/generate_leaderboard.py to update rankings.")


if __name__ == "__main__":
    main()
