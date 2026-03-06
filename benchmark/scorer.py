from __future__ import annotations
"""UPSC Prelims scoring formula.

GS Paper I:  +2.0 correct, -2/3 wrong, 0 unanswered (100 Qs, max 200)
CSAT Paper II: +2.5 correct, -5/6 wrong, 0 unanswered (80 Qs, max 200)
"""

import json
from pathlib import Path

from benchmark.common import load_cutoffs


def load_rank_mapping(rank_path: str = "data/rank_mapping.json") -> dict:
    """Load score-to-rank interpolation data."""
    path = Path(rank_path)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def estimate_rank(score: float, year: int, rank_data: dict | None = None) -> dict:
    """Estimate UPSC All-India Rank from GS1 score.

    Uses linear interpolation between known score-rank anchor points.
    Returns estimated rank, percentile, and context label.

    Args:
        score: GS1 marks obtained (out of 200).
        year: Exam year.
        rank_data: Rank mapping data. If None, loads from file.

    Returns:
        Dict with 'rank', 'percentile', 'label', 'total_appeared'.
    """
    if rank_data is None:
        rank_data = load_rank_mapping()

    year_data = rank_data.get(str(year))
    if not year_data:
        return {"rank": None, "percentile": None, "label": "No data", "total_appeared": None}

    total = year_data["total_appeared"]
    cutoff = year_data["cutoff_general"]
    topper = year_data["estimated_topper"]
    dist = year_data["distribution"]

    # Below cutoff
    if score < cutoff:
        return {
            "rank": None,
            "percentile": None,
            "label": "Did not qualify",
            "total_appeared": total,
        }

    # Above estimated topper
    if score >= topper:
        return {
            "rank": 1,
            "percentile": round((1 - 1 / total) * 100, 4),
            "label": "Exceeds estimated topper",
            "total_appeared": total,
        }

    # Interpolate between anchor points
    # dist is sorted descending by score
    for i in range(len(dist) - 1):
        high = dist[i]
        low = dist[i + 1]
        if low["score"] <= score <= high["score"]:
            # Linear interpolation
            score_range = high["score"] - low["score"]
            rank_range = low["rank"] - high["rank"]
            if score_range == 0:
                rank = high["rank"]
            else:
                fraction = (high["score"] - score) / score_range
                rank = high["rank"] + fraction * rank_range
            rank = max(1, round(rank))
            percentile = round((1 - rank / total) * 100, 2)

            # Context label
            if rank <= 10:
                label = "Topper territory"
            elif rank <= 100:
                label = "Top 100"
            elif rank <= 500:
                label = "Top 500"
            elif rank <= 1000:
                label = "Top 1,000"
            elif rank <= 5000:
                label = "Top 5,000"
            else:
                label = f"Top {(rank // 1000 + 1) * 1000:,}"

            return {
                "rank": rank,
                "percentile": percentile,
                "label": label,
                "total_appeared": total,
            }

    # Fallback — at cutoff boundary
    return {
        "rank": year_data["mains_qualified"],
        "percentile": round((1 - year_data["mains_qualified"] / total) * 100, 2),
        "label": "At cutoff",
        "total_appeared": total,
    }


def calculate_score(
    results: list[dict],
    paper: str,
    marking_scheme: dict | None = None,
) -> dict:
    """Calculate UPSC score for a set of graded results.

    Args:
        results: List of graded result dicts with 'result' field.
        paper: Paper type ('gs1' or 'csat').
        marking_scheme: Optional marking scheme dict. If None, uses defaults.

    Returns:
        Dict with total_marks, correct_count, wrong_count, unanswered_count,
        total_questions, max_marks, accuracy.
    """
    if marking_scheme is None:
        marking_scheme = {
            "gs1": {"correct": 2.0, "wrong": -0.6667, "unanswered": 0.0,
                    "total_questions": 100, "max_marks": 200},
            "csat": {"correct": 2.5, "wrong": -0.8333, "unanswered": 0.0,
                     "total_questions": 80, "max_marks": 200},
        }

    scheme = marking_scheme[paper]

    correct = sum(1 for r in results if r["result"] == "correct")
    wrong = sum(1 for r in results if r["result"] == "wrong")
    unanswered = sum(1 for r in results if r["result"] == "unanswered")

    total_marks = (
        correct * scheme["correct"]
        + wrong * scheme["wrong"]
        + unanswered * scheme["unanswered"]
    )

    # Round to 2 decimal places (UPSC rounds to 2 decimals)
    total_marks = round(total_marks, 2)
    total_questions = correct + wrong + unanswered
    accuracy = round(correct / total_questions * 100, 2) if total_questions > 0 else 0.0

    return {
        "total_marks": total_marks,
        "max_marks": scheme["max_marks"],
        "correct_count": correct,
        "wrong_count": wrong,
        "unanswered_count": unanswered,
        "total_questions": total_questions,
        "accuracy": accuracy,
    }


def check_pass_fail(
    score: float,
    paper: str,
    year: int,
    cutoffs: dict | None = None,
) -> dict:
    """Check if a score passes the UPSC cutoff for a given year.

    Args:
        score: Total marks obtained.
        paper: Paper type ('gs1' or 'csat').
        year: Exam year.
        cutoffs: Cutoff data dict. If None, loads from config.

    Returns:
        Dict with 'passed' (bool), 'cutoff' (float), 'margin' (float).
    """
    if cutoffs is None:
        cutoffs = load_cutoffs()

    year_cutoffs = cutoffs["cutoffs"].get(year, {})

    if paper == "gs1":
        cutoff = year_cutoffs.get("gs1", 0)
    else:
        cutoff = year_cutoffs.get("csat_qualifying", 66)

    passed = score >= cutoff
    margin = round(score - cutoff, 2)

    return {
        "passed": passed,
        "cutoff": cutoff,
        "margin": margin,
    }
