"""Tests for benchmark/mains_scorer.py — Mains scoring aggregation."""

from benchmark.mains_scorer import (
    calculate_mains_score,
    calculate_essay_score,
    calculate_mains_total,
    check_mains_pass,
)


# ── calculate_mains_score ─────────────────────────────────────


class TestCalculateMainsScore:
    def test_basic(self):
        results = [
            {"total_score": 30, "max_marks": 50},
            {"total_score": 25, "max_marks": 50},
            {"total_score": 40, "max_marks": 50},
        ]
        score = calculate_mains_score(results, "mains_gs1")
        assert score["total_marks"] == 95
        assert score["max_marks"] == 150
        assert score["question_count"] == 3

    def test_empty(self):
        score = calculate_mains_score([], "mains_gs1")
        assert score["total_marks"] == 0
        assert score["max_marks"] == 0
        assert score["question_count"] == 0
        assert score["avg_score_pct"] == 0.0


# ── calculate_essay_score ─────────────────────────────────────


class TestCalculateEssayScore:
    def test_picks_best_per_section(self):
        results = [
            {"section": "A", "total_score": 80, "max_marks": 125, "question_id": "e1"},
            {"section": "A", "total_score": 95, "max_marks": 125, "question_id": "e2"},
            {"section": "B", "total_score": 70, "max_marks": 125, "question_id": "e3"},
            {"section": "B", "total_score": 85, "max_marks": 125, "question_id": "e4"},
        ]
        score = calculate_essay_score(results)
        # Best A = 95, Best B = 85 → total = 180
        assert score["total_marks"] == 180
        assert score["max_marks"] == 250
        assert score["question_count"] == 2
        assert "e2" in score["selected_essays"]
        assert "e4" in score["selected_essays"]

    def test_single_section(self):
        results = [
            {"section": "A", "total_score": 100, "max_marks": 125, "question_id": "e1"},
        ]
        score = calculate_essay_score(results)
        assert score["total_marks"] == 100
        assert score["max_marks"] == 250
        assert score["question_count"] == 1

    def test_empty(self):
        score = calculate_essay_score([])
        assert score["total_marks"] == 0
        assert score["max_marks"] == 250
        assert score["question_count"] == 0


# ── calculate_mains_total ─────────────────────────────────────


class TestCalculateMainsTotal:
    def test_all_papers(self):
        scores = {
            "mains_essay": {"total_marks": 180, "max_marks": 250},
            "mains_gs1": {"total_marks": 190, "max_marks": 250},
            "mains_gs2": {"total_marks": 170, "max_marks": 250},
            "mains_gs3": {"total_marks": 185, "max_marks": 250},
            "mains_gs4": {"total_marks": 175, "max_marks": 250},
        }
        total = calculate_mains_total(scores)
        assert total["total_score"] == 900
        assert total["max_marks"] == 1250
        assert total["papers_evaluated"] == 5
        assert total["score_pct"] == 72.0

    def test_partial(self):
        scores = {
            "mains_essay": {"total_marks": 180, "max_marks": 250},
            "mains_gs1": {"total_marks": 190, "max_marks": 250},
            "mains_gs2": {"total_marks": 170, "max_marks": 250},
        }
        total = calculate_mains_total(scores)
        assert total["total_score"] == 540
        assert total["papers_evaluated"] == 3

    def test_empty(self):
        total = calculate_mains_total({})
        assert total["total_score"] == 0
        assert total["papers_evaluated"] == 0


# ── check_mains_pass ──────────────────────────────────────────


class TestCheckMainsPass:
    def test_pass(self, sample_cutoffs):
        # Proportional cutoff: 800/1750 × 1250 ≈ 571.43
        result = check_mains_pass(600, 2025, sample_cutoffs)
        assert result["passed"] is True
        assert result["margin"] > 0

    def test_fail(self, sample_cutoffs):
        result = check_mains_pass(500, 2025, sample_cutoffs)
        assert result["passed"] is False
        assert result["margin"] < 0

    def test_cutoff_calculation(self, sample_cutoffs):
        result = check_mains_pass(0, 2025, sample_cutoffs)
        # 800/1750 × 1250 = 571.43 (rounded to 2 decimals)
        assert result["cutoff"] == round(800 / 1750 * 1250, 2)
