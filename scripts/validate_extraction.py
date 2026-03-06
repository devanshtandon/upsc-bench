#!/usr/bin/env python3
"""Validate combined extraction results for data quality."""

import json
import re
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_combined(paper, year):
    path = os.path.join(BASE, f"data/parsed/{paper}_{year}_combined.json")
    with open(path) as f:
        return json.load(f)


def check_count(questions, paper, expected):
    """Check question count."""
    actual = len(questions)
    status = "PASS" if actual == expected else "FAIL"
    print(f"  [{status}] Count: {actual}/{expected}")
    return actual == expected


def check_sequential(questions, expected_count):
    """Check for sequential numbering without gaps or duplicates."""
    numbers = [q["question_number"] for q in questions]
    expected = list(range(1, expected_count + 1))
    missing = sorted(set(expected) - set(numbers))
    duplicates = [n for n in numbers if numbers.count(n) > 1]
    duplicates = sorted(set(duplicates))

    if not missing and not duplicates:
        print(f"  [PASS] Sequential numbering: 1-{expected_count}, no gaps or duplicates")
        return True
    if missing:
        print(f"  [FAIL] Missing questions: {missing}")
    if duplicates:
        print(f"  [FAIL] Duplicate questions: {duplicates}")
    return False


def check_options(questions):
    """Check that every question has exactly 4 options (a, b, c, d)."""
    issues = []
    for q in questions:
        opts = q.get("options", {})
        expected_keys = {"a", "b", "c", "d"}
        actual_keys = set(opts.keys())
        if actual_keys != expected_keys:
            issues.append(f"Q{q['question_number']}: has keys {sorted(actual_keys)}")
        # Check for empty options
        for k in expected_keys:
            if k in opts and (not opts[k] or not opts[k].strip()):
                issues.append(f"Q{q['question_number']}: option '{k}' is empty")

    if not issues:
        print(f"  [PASS] All questions have exactly 4 options (a, b, c, d)")
        return True
    for issue in issues:
        print(f"  [FAIL] {issue}")
    return False


def check_ocr_artifacts(questions):
    """Check for common OCR corruption patterns."""
    patterns = [
        (r'\bIll\b', "III→Ill corruption"),
        (r'\b111\b', "III→111 corruption"),
        (r'(?<!\d)11(?!\d)', "II→11 corruption (in non-numeric context)"),
        (r'\bLVPK\b', "Booklet code leak"),
        (r'\bP\.T\.O\b', "Page marker leak"),
        (r'\b56A\b', "Booklet code leak"),
    ]

    issues = []
    for q in questions:
        text = q.get("question_text", "")
        # Also check options
        for k, v in q.get("options", {}).items():
            text += " " + v

        for pattern, desc in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Filter out legitimate uses of "11" in numeric contexts
                if pattern == r'(?<!\d)11(?!\d)':
                    # Skip if it's part of a number like "2011", "1100", etc.
                    # Only flag if it appears to be a Roman numeral context
                    if any(ctx in text for ctx in ["Statement 11", "item 11"]):
                        issues.append(f"Q{q['question_number']}: {desc} - '{matches[0]}' in context")
                else:
                    issues.append(f"Q{q['question_number']}: {desc}")

    if not issues:
        print(f"  [PASS] No OCR artifact patterns found")
        return True
    for issue in issues:
        print(f"  [WARN] {issue}")
    return False


def check_empty_text(questions):
    """Check for questions with empty or very short text."""
    issues = []
    for q in questions:
        text = q.get("question_text", "")
        if len(text) < 20:
            issues.append(f"Q{q['question_number']}: text too short ({len(text)} chars): '{text[:50]}'")

    if not issues:
        print(f"  [PASS] All questions have substantial text (>20 chars)")
        return True
    for issue in issues:
        print(f"  [FAIL] {issue}")
    return False


def check_roman_numerals(questions):
    """Check that Roman numerals are properly formatted."""
    issues = []
    for q in questions:
        text = q.get("question_text", "")
        for k, v in q.get("options", {}).items():
            text += " " + v

        # Check for lowercase roman numerals that should be uppercase
        if re.search(r'\biii\b', text) and 'III' not in text:
            issues.append(f"Q{q['question_number']}: lowercase 'iii' found (should be 'III')")
        if re.search(r'\bii\b', text) and 'II' not in text:
            issues.append(f"Q{q['question_number']}: lowercase 'ii' found (should be 'II')")

    if not issues:
        print(f"  [PASS] Roman numerals appear properly formatted")
        return True
    for issue in issues:
        print(f"  [WARN] {issue}")
    return False


def check_csat_passages(questions):
    """Check that CSAT passage-based questions have passage text."""
    passage_questions = []
    missing_passages = []

    for q in questions:
        text = q.get("question_text", "").lower()
        if "passage" in text or "above passage" in text:
            passage_questions.append(q["question_number"])
            if not q.get("passage") or not q["passage"].strip():
                missing_passages.append(q["question_number"])

    print(f"  [INFO] {len(passage_questions)} questions reference passages")
    if not missing_passages:
        print(f"  [PASS] All passage-referencing questions have passage text")
        return True
    print(f"  [WARN] Questions missing passage text: {missing_passages}")
    return False


def check_table_questions(questions, known_table_qs):
    """Spot-check known table questions."""
    issues = []
    for qn in known_table_qs:
        q = next((q for q in questions if q["question_number"] == qn), None)
        if q is None:
            issues.append(f"Q{qn}: not found")
            continue
        text = q.get("question_text", "")
        if "|" in text or "\n" in text:
            print(f"  [PASS] Q{qn}: contains table formatting")
        else:
            issues.append(f"Q{qn}: expected table but no | or newline found")

    if not issues:
        return True
    for issue in issues:
        print(f"  [WARN] {issue}")
    return False


def main():
    all_pass = True

    # GS1 2025
    print("\n" + "=" * 60)
    print("VALIDATING GS1 2025")
    print("=" * 60)
    gs1 = load_combined("gs1", 2025)

    all_pass &= check_count(gs1, "gs1", 100)
    all_pass &= check_sequential(gs1, 100)
    all_pass &= check_options(gs1)
    all_pass &= check_empty_text(gs1)
    all_pass &= check_ocr_artifacts(gs1)
    all_pass &= check_roman_numerals(gs1)

    # Known table questions in GS1 2025
    print("\n  Table question spot-checks:")
    check_table_questions(gs1, [3, 17, 39, 52, 55, 57, 79, 80, 84, 96])

    # CSAT 2025
    print("\n" + "=" * 60)
    print("VALIDATING CSAT 2025")
    print("=" * 60)
    csat = load_combined("csat", 2025)

    all_pass &= check_count(csat, "csat", 80)
    all_pass &= check_sequential(csat, 80)
    all_pass &= check_options(csat)
    all_pass &= check_empty_text(csat)
    all_pass &= check_ocr_artifacts(csat)
    all_pass &= check_roman_numerals(csat)
    all_pass &= check_csat_passages(csat)

    # Summary
    print("\n" + "=" * 60)
    print(f"OVERALL: {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
