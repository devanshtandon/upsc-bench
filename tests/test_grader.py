"""Tests for benchmark/grader.py — regex-based MCQ answer extraction."""

from benchmark.grader import normalize_answer, grade_answer, grade_response


# ── normalize_answer ──────────────────────────────────────────


class TestNormalizeAnswer:
    def test_boxed_latex(self):
        assert normalize_answer(r"$\boxed{A}$") == "a"

    def test_boxed_text_latex(self):
        assert normalize_answer(r"$\boxed{\text{B}}$") == "b"

    def test_answer_is_pattern(self):
        assert normalize_answer("The correct answer is (A)") == "a"

    def test_answer_colon(self):
        assert normalize_answer("Answer: C") == "c"

    def test_option_pattern(self):
        assert normalize_answer("Option (D)") == "d"

    def test_parenthesized_end(self):
        assert normalize_answer("Based on analysis, (A)") == "a"

    def test_standalone_letter(self):
        assert normalize_answer("  B  ") == "b"

    def test_case_insensitive(self):
        assert normalize_answer("answer: a") == "a"

    def test_empty_string(self):
        assert normalize_answer("") is None

    def test_none_input(self):
        assert normalize_answer(None) is None

    def test_no_answer_long_text(self):
        # 100+ chars with no clear answer pattern → None
        text = "This is a very long response that discusses many topics " * 3
        assert normalize_answer(text) is None

    def test_last_resort_short(self):
        # Short text with a letter → extracted via last-resort
        assert normalize_answer("I think B") == "b"

    def test_last_resort_long_rejected(self):
        # 60+ chars with a loose letter → rejected (too long for last-resort)
        text = "Let me think about this carefully. The options presented suggest B is plausible."
        assert normalize_answer(text) is None

    def test_answer_with_period(self):
        assert normalize_answer("A.") == "a"

    def test_paren_letter_paren(self):
        assert normalize_answer("(C)") == "c"


# ── grade_answer ──────────────────────────────────────────────


class TestGradeAnswer:
    def test_correct(self):
        assert grade_answer("a", "A") == "correct"

    def test_wrong(self):
        assert grade_answer("b", "A") == "wrong"

    def test_unanswered(self):
        assert grade_answer(None, "A") == "unanswered"

    def test_case_insensitive(self):
        assert grade_answer("C", "c") == "correct"


# ── grade_response (integration) ─────────────────────────────


class TestGradeResponse:
    def test_correct_extraction(self):
        result = grade_response("The answer is B", "b")
        assert result["extracted_answer"] == "b"
        assert result["correct_answer"] == "b"
        assert result["result"] == "correct"

    def test_wrong_extraction(self):
        result = grade_response("Answer: A", "c")
        assert result["extracted_answer"] == "a"
        assert result["result"] == "wrong"

    def test_unparseable(self):
        long_text = "I cannot determine the answer from the given information. " * 3
        result = grade_response(long_text, "a")
        assert result["extracted_answer"] is None
        assert result["result"] == "unanswered"
