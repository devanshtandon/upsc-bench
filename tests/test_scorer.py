"""Tests for benchmark/scorer.py — Prelims scoring, pass/fail, rank estimation."""

from benchmark.scorer import calculate_score, check_pass_fail, estimate_rank


# ── calculate_score ───────────────────────────────────────────


class TestCalculateScore:
    def test_gs1_perfect_score(self):
        results = [{"result": "correct"}] * 100
        score = calculate_score(results, "gs1")
        assert score["total_marks"] == 200.0
        assert score["correct_count"] == 100
        assert score["wrong_count"] == 0
        assert score["accuracy"] == 100.0

    def test_gs1_all_wrong(self):
        results = [{"result": "wrong"}] * 100
        score = calculate_score(results, "gs1")
        assert score["total_marks"] == -66.0
        assert score["wrong_count"] == 100

    def test_gs1_mixed(self):
        results = (
            [{"result": "correct"}] * 70
            + [{"result": "wrong"}] * 20
            + [{"result": "unanswered"}] * 10
        )
        score = calculate_score(results, "gs1")
        # 70 × 2.0 + 20 × (-0.66) + 10 × 0 = 140 - 13.2 = 126.8
        assert score["total_marks"] == 126.8
        assert score["correct_count"] == 70
        assert score["wrong_count"] == 20
        assert score["unanswered_count"] == 10
        assert score["total_questions"] == 100

    def test_csat_scheme(self):
        results = (
            [{"result": "correct"}] * 60
            + [{"result": "wrong"}] * 15
            + [{"result": "unanswered"}] * 5
        )
        score = calculate_score(results, "csat")
        # 60 × 2.5 + 15 × (-0.83) = 150 - 12.45 = 137.55
        assert score["total_marks"] == 137.55

    def test_empty_results(self):
        score = calculate_score([], "gs1")
        assert score["total_marks"] == 0
        assert score["accuracy"] == 0.0
        assert score["total_questions"] == 0


# ── check_pass_fail ───────────────────────────────────────────


class TestCheckPassFail:
    def test_gs1_pass(self, sample_cutoffs):
        result = check_pass_fail(100, "gs1", 2025, sample_cutoffs)
        assert result["passed"] is True
        assert result["cutoff"] == 90.0
        assert result["margin"] == 10.0

    def test_gs1_fail(self, sample_cutoffs):
        result = check_pass_fail(80, "gs1", 2025, sample_cutoffs)
        assert result["passed"] is False
        assert result["margin"] == -10.0

    def test_csat_at_qualifying(self, sample_cutoffs):
        result = check_pass_fail(66, "csat", 2025, sample_cutoffs)
        assert result["passed"] is True
        assert result["margin"] == 0.0

    def test_csat_below_qualifying(self, sample_cutoffs):
        result = check_pass_fail(65, "csat", 2025, sample_cutoffs)
        assert result["passed"] is False


# ── estimate_rank ─────────────────────────────────────────────


class TestEstimateRank:
    def test_above_topper(self, sample_rank_data):
        result = estimate_rank(170, 2025, sample_rank_data)
        assert result["rank"] == 1
        assert result["label"] == "Exceeds estimated topper"

    def test_below_cutoff(self, sample_rank_data):
        result = estimate_rank(80, 2025, sample_rank_data)
        assert result["rank"] is None
        assert result["label"] == "Did not qualify"

    def test_interpolation(self, sample_rank_data):
        # Score 130 is between 140 (rank 100) and 120 (rank 1000)
        result = estimate_rank(130, 2025, sample_rank_data)
        assert result["rank"] is not None
        assert 100 < result["rank"] < 1000
        assert result["label"] in ("Top 500", "Top 1,000")

    def test_no_year_data(self, sample_rank_data):
        result = estimate_rank(150, 2030, sample_rank_data)
        assert result["rank"] is None
        assert result["label"] == "No data"

    def test_at_cutoff(self, sample_rank_data):
        result = estimate_rank(90, 2025, sample_rank_data)
        # At the lowest distribution point → should match or be at cutoff
        assert result["rank"] is not None
