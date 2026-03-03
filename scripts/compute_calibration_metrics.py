#!/usr/bin/env python3
"""Compute judge validation metrics from calibration grading results.

Reads grading_results.json and computes:
- MAE (Mean Absolute Error) — global and per-paper
- Directional bias — does judge systematically over/under-score?
- Within-range accuracy — what % of scores fall in the expected range?
- Per-dimension analysis
- Recommendation: calibrated / needs adjustment / needs investigation

Usage:
    python scripts/compute_calibration_metrics.py
"""
import json
import statistics
from pathlib import Path

RESULTS_FILE = Path("data/calibration/grading_results.json")
REPORT_FILE = Path("data/calibration/validation_report.json")


def compute_metrics(results):
    """Compute calibration metrics from grading results."""
    offsets = [r["offset"] for r in results]
    pct_offsets = [r["judge_pct"] - r["expected_pct"] for r in results]
    within_range_count = sum(1 for r in results if r["within_range"])

    # Global metrics
    mae = statistics.mean(abs(o) for o in offsets)
    mean_offset = statistics.mean(offsets)
    median_offset = statistics.median(offsets)
    std_offset = statistics.stdev(offsets) if len(offsets) > 1 else 0

    mae_pct = statistics.mean(abs(o) for o in pct_offsets)
    mean_offset_pct = statistics.mean(pct_offsets)

    # Per-paper metrics
    papers = sorted(set(r["paper"] for r in results))
    per_paper = {}
    for paper in papers:
        paper_results = [r for r in results if r["paper"] == paper]
        paper_offsets = [r["offset"] for r in paper_results]
        paper_pct_offsets = [r["judge_pct"] - r["expected_pct"] for r in paper_results]
        per_paper[paper] = {
            "count": len(paper_results),
            "mae": round(statistics.mean(abs(o) for o in paper_offsets), 2),
            "mean_offset": round(statistics.mean(paper_offsets), 2),
            "mean_offset_pct": round(statistics.mean(paper_pct_offsets), 1),
            "within_range_pct": round(
                sum(1 for r in paper_results if r["within_range"]) / len(paper_results) * 100, 1
            ),
        }

    # Per-dimension analysis (aggregate across all results)
    dim_scores = {}
    for r in results:
        for dim_key, dim_data in r.get("rubric_scores", {}).items():
            if dim_key not in dim_scores:
                dim_scores[dim_key] = []
            if isinstance(dim_data, dict):
                dim_scores[dim_key].append(dim_data.get("score", 0))

    per_dimension = {}
    for dim_key, scores in dim_scores.items():
        if scores:
            per_dimension[dim_key] = {
                "mean_score": round(statistics.mean(scores), 2),
                "std_score": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
                "count": len(scores),
            }

    # Determine recommendation
    if mae_pct < 5:
        recommendation = "WELL_CALIBRATED"
        recommendation_detail = (
            "Judge scores are within 5 percentage points of coaching expectations. "
            "Current AI model scores can be reported with confidence."
        )
    elif mean_offset_pct > 5:
        recommendation = "POSITIVE_BIAS"
        recommendation_detail = (
            f"Judge inflates scores by ~{mean_offset_pct:.1f} percentage points on average. "
            "Consider adding few-shot calibration examples to the prompt and regrading."
        )
    elif mean_offset_pct < -5:
        recommendation = "NEGATIVE_BIAS"
        recommendation_detail = (
            f"Judge deflates scores by ~{abs(mean_offset_pct):.1f} percentage points. "
            "Current AI scores may be conservative. Consider noting this in methodology."
        )
    else:
        recommendation = "MARGINAL"
        recommendation_detail = (
            "Judge bias is small but measurable. Current scores are approximately correct. "
            "Consider minor prompt adjustments."
        )

    report = {
        "summary": {
            "total_answers_graded": len(results),
            "within_expected_range": within_range_count,
            "within_expected_range_pct": round(within_range_count / len(results) * 100, 1),
        },
        "global_metrics": {
            "mae_marks": round(mae, 2),
            "mae_pct": round(mae_pct, 1),
            "mean_offset_marks": round(mean_offset, 2),
            "mean_offset_pct": round(mean_offset_pct, 1),
            "median_offset_marks": round(median_offset, 2),
            "std_offset_marks": round(std_offset, 2),
            "interpretation": (
                "Positive offset = judge scores higher than coaching expectation. "
                "Negative offset = judge scores lower."
            ),
        },
        "per_paper": per_paper,
        "per_dimension": per_dimension,
        "recommendation": recommendation,
        "recommendation_detail": recommendation_detail,
        "per_question_results": [
            {
                "id": r["calibration_id"],
                "paper": r["paper"],
                "q_num": r["question_number"],
                "max": r["max_marks"],
                "judge": r["judge_score"],
                "expected_mid": r["expected_mid"],
                "offset": r["offset"],
                "within_range": r["within_range"],
            }
            for r in results
        ],
    }

    return report


def print_report(report):
    """Print human-readable report to stdout."""
    s = report["summary"]
    g = report["global_metrics"]

    print("=" * 60)
    print("JUDGE VALIDATION REPORT")
    print("=" * 60)
    print(f"\nAnswers graded: {s['total_answers_graded']}")
    print(f"Within expected range: {s['within_expected_range']}/{s['total_answers_graded']} "
          f"({s['within_expected_range_pct']}%)")
    print(f"\nMean Absolute Error: {g['mae_marks']} marks ({g['mae_pct']}%)")
    print(f"Mean offset: {g['mean_offset_marks']:+.2f} marks ({g['mean_offset_pct']:+.1f}%)")
    print(f"Median offset: {g['median_offset_marks']:+.2f} marks")
    print(f"Std dev: {g['std_offset_marks']:.2f} marks")

    print(f"\nPer-paper breakdown:")
    for paper, metrics in report["per_paper"].items():
        print(f"  {paper}: MAE={metrics['mae']}, bias={metrics['mean_offset_pct']:+.1f}%, "
              f"in-range={metrics['within_range_pct']}% (n={metrics['count']})")

    if report.get("per_dimension"):
        print(f"\nPer-dimension averages:")
        for dim, metrics in report["per_dimension"].items():
            print(f"  {dim}: mean={metrics['mean_score']}, std={metrics['std_score']} "
                  f"(n={metrics['count']})")

    print(f"\nRECOMMENDATION: {report['recommendation']}")
    print(f"  {report['recommendation_detail']}")

    print(f"\nPer-question detail:")
    for r in report["per_question_results"]:
        marker = "Y" if r["within_range"] else "N"
        print(f"  [{marker}] {r['id']}: judge={r['judge']}/{r['max']} "
              f"expected={r['expected_mid']}/{r['max']} offset={r['offset']:+.1f}")


def main():
    if not RESULTS_FILE.exists():
        print(f"ERROR: {RESULTS_FILE} not found.")
        print("Run 'python scripts/grade_calibration.py merge' first.")
        sys.exit(1)

    with open(RESULTS_FILE) as f:
        results = json.load(f)

    report = compute_metrics(results)
    print_report(report)

    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()
