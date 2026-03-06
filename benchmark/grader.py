from __future__ import annotations
"""Deterministic grading for UPSC Prelims MCQ answers.

Extracts a/b/c/d from model output via regex and compares with correct answer.
No LLM grader needed — UPSC Prelims is single-correct MCQ.
"""

import re


# Patterns ordered from most specific to least specific
ANSWER_PATTERNS = [
    # LaTeX boxed: $\boxed{A}$, \boxed{A}, or $\boxed{\text{A}}$ (common in reasoning models)
    r"\\boxed\{\\text\{([A-Da-d])\}\}",
    r"\\boxed\{([A-Da-d])\}",
    # "The correct answer is (A)" / "The answer is A"
    r"(?:the\s+)?(?:correct\s+)?answer\s+is\s*[:\-]?\s*\(?([A-Da-d])\)?",
    # "Answer: A" / "Answer: (A)"
    r"answer\s*[:\-]\s*\(?([A-Da-d])\)?",
    # "Option (A)" / "Option A"
    r"option\s*\(?([A-Da-d])\)?",
    # Standalone letter in parentheses at end: "(A)" or "(a)"
    r"\(([A-Da-d])\)\s*\.?\s*$",
    # "A)" or "a)" at end of response
    r"([A-Da-d])\)\s*\.?\s*$",
    # Just a single letter line (common in terse model outputs)
    r"^\s*([A-Da-d])\s*\.?\s*$",
]


def normalize_answer(raw_output: str) -> str | None:
    """Extract a single answer letter (a/b/c/d) from model output.

    Tries multiple regex patterns to handle different model output formats.
    Returns lowercase letter or None if no answer could be extracted.

    Args:
        raw_output: Raw text output from the LLM.

    Returns:
        Lowercase letter 'a', 'b', 'c', or 'd', or None if unparseable.
    """
    if not raw_output or not raw_output.strip():
        return None

    text = raw_output.strip()

    # Try patterns on original text — take LAST match, not first.
    # Models reason aloud ("could be A... actually it's B"), so the final
    # mention is the intended answer.
    for pattern in ANSWER_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            return matches[-1].lower()

    # Retry with markdown bold/italic markers stripped —
    # e.g. Claude outputs "Answer: **(D)**" which the patterns can't parse
    stripped = re.sub(r"\*{1,2}", "", text)
    if stripped != text:
        for pattern in ANSWER_PATTERNS:
            matches = re.findall(pattern, stripped, re.IGNORECASE | re.MULTILINE)
            if matches:
                return matches[-1].lower()

    # Last resort: find the last occurrence of a standalone a/b/c/d
    # This handles cases where the model discusses options then states answer
    last_match = None
    for match in re.finditer(r"\b([A-Da-d])\b", text):
        candidate = match.group(1).lower()
        if candidate in {"a", "b", "c", "d"}:
            last_match = candidate

    # Only use last-resort if the text is short (likely just an answer)
    if last_match and len(text) < 20:
        return last_match

    return None


def grade_answer(model_answer: str | None, correct_answer: str) -> str:
    """Grade a single answer.

    Args:
        model_answer: Extracted answer letter (a/b/c/d) or None.
        correct_answer: The correct answer letter.

    Returns:
        "correct", "wrong", or "unanswered"
    """
    if model_answer is None:
        return "unanswered"

    if model_answer.lower() == correct_answer.lower():
        return "correct"

    return "wrong"


def grade_response(raw_output: str, correct_answer: str, disputed_answers: list[str] | None = None) -> dict:
    """Extract answer from model output and grade it.

    Args:
        raw_output: Raw text output from the LLM.
        correct_answer: The correct answer letter.
        disputed_answers: Optional list of acceptable answers for disputed questions.

    Returns:
        Dict with 'extracted_answer', 'correct_answer', 'result'
    """
    extracted = normalize_answer(raw_output)
    result = grade_answer(extracted, correct_answer)

    # For disputed questions, accept any of the valid answers
    if result == "wrong" and extracted and disputed_answers:
        if extracted.lower() in [a.lower() for a in disputed_answers]:
            result = "correct"

    return {
        "extracted_answer": extracted,
        "correct_answer": correct_answer,
        "result": result,
    }
