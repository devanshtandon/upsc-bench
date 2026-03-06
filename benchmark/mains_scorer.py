from __future__ import annotations
"""UPSC Mains scoring — aggregates judge scores across papers.

No negative marking in Mains. Scores come from LLM-as-judge rubric grading.
Essay: 2 essays x 125 marks = 250 marks
GS1-4: ~20 questions each x 10-15 marks = 250 marks per paper
Total: 1250 marks (excluding Optional paper)
"""

from benchmark.common import load_cutoffs


def calculate_mains_score(results: list[dict], paper: str) -> dict:
    """Calculate total score for a single Mains paper.

    Args:
        results: List of graded result dicts with 'total_score' and 'max_marks'.
        paper: Paper key (e.g., 'mains_gs1', 'mains_essay').

    Returns:
        Dict with total_marks, max_marks, avg_score_pct, question_count.
    """
    if not results:
        return {
            "total_marks": 0,
            "max_marks": 0,
            "avg_score_pct": 0.0,
            "question_count": 0,
        }

    total_marks = sum(r["total_score"] for r in results)
    max_marks = sum(r["max_marks"] for r in results)
    avg_score_pct = round(total_marks / max_marks * 100, 2) if max_marks > 0 else 0.0

    return {
        "total_marks": round(total_marks, 2),
        "max_marks": max_marks,
        "avg_score_pct": avg_score_pct,
        "question_count": len(results),
    }


def calculate_essay_score(results: list[dict]) -> dict:
    """Calculate Essay paper score.

    The candidate writes all 8 essays, but we score based on the best 1 from
    each section (A and B), giving 2 essays x 125 marks = 250 marks total.

    Args:
        results: List of graded essay results with 'section', 'total_score', 'max_marks'.

    Returns:
        Dict with total_marks, max_marks, selected essays, and all scores.
    """
    if not results:
        return {
            "total_marks": 0,
            "max_marks": 250,
            "avg_score_pct": 0.0,
            "question_count": 0,
            "selected_essays": [],
        }

    # Group by section
    section_a = [r for r in results if r.get("section") == "A"]
    section_b = [r for r in results if r.get("section") == "B"]

    selected = []

    # Best from section A
    if section_a:
        best_a = max(section_a, key=lambda r: r["total_score"])
        selected.append(best_a)

    # Best from section B
    if section_b:
        best_b = max(section_b, key=lambda r: r["total_score"])
        selected.append(best_b)

    total_marks = sum(r["total_score"] for r in selected)
    max_marks = 250  # 2 x 125
    avg_score_pct = round(total_marks / max_marks * 100, 2) if max_marks > 0 else 0.0

    return {
        "total_marks": round(total_marks, 2),
        "max_marks": max_marks,
        "avg_score_pct": avg_score_pct,
        "question_count": len(selected),
        "selected_essays": [r.get("question_id") for r in selected],
    }


def calculate_mains_total(scores_by_paper: dict) -> dict:
    """Aggregate scores across all 5 Mains papers.

    Args:
        scores_by_paper: Dict mapping paper key to score dict.
            Expected keys: mains_essay, mains_gs1, mains_gs2, mains_gs3, mains_gs4

    Returns:
        Dict with total score out of 1250, breakdown by paper.
    """
    total_marks = 0
    max_marks = 0
    papers_evaluated = 0

    for paper_key in ["mains_essay", "mains_gs1", "mains_gs2", "mains_gs3", "mains_gs4"]:
        paper_score = scores_by_paper.get(paper_key)
        if paper_score:
            total_marks += paper_score["total_marks"]
            max_marks += paper_score["max_marks"]
            papers_evaluated += 1

    score_pct = round(total_marks / max_marks * 100, 2) if max_marks > 0 else 0.0

    return {
        "total_score": round(total_marks, 2),
        "max_marks": max_marks,
        "score_pct": score_pct,
        "papers_evaluated": papers_evaluated,
    }


def check_mains_pass(
    total_score: float,
    year: int,
    cutoffs: dict | None = None,
) -> dict:
    """Check if a Mains total score passes the cutoff.

    Since we evaluate 5 papers (1250 marks) out of the full exam's 7 papers
    (1750 marks), we compute a proportional cutoff.

    Args:
        total_score: Total Mains marks obtained (out of 1250).
        year: Exam year.
        cutoffs: Cutoff data dict. If None, loads from config.

    Returns:
        Dict with 'passed', 'cutoff', 'margin', 'note'.
    """
    if cutoffs is None:
        cutoffs = load_cutoffs()

    mains_cutoffs = cutoffs.get("mains_cutoffs", {}).get(year, {})
    full_cutoff = mains_cutoffs.get("total", 800)
    full_max = mains_cutoffs.get("max_marks", 1750)

    # Proportional cutoff: scale the full exam cutoff to our 1250-mark subset
    proportional_cutoff = round(full_cutoff / full_max * 1250, 2)

    passed = total_score >= proportional_cutoff
    margin = round(total_score - proportional_cutoff, 2)

    return {
        "passed": passed,
        "cutoff": proportional_cutoff,
        "full_exam_cutoff": full_cutoff,
        "margin": margin,
        "note": (
            f"Proportional cutoff: {full_cutoff}/{full_max} scaled to "
            f"{proportional_cutoff}/1250. Approximate — real Mains cutoffs "
            "include Optional paper and Interview marks."
        ),
    }
