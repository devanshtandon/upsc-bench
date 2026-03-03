"""Validate the UPSC Bench dataset for completeness and correctness."""

import json
import os
import sys
from pathlib import Path


def validate_dataset(dataset_path: str, images_dir: str = "data/images") -> bool:
    """Validate the UPSC Bench dataset.

    Checks:
    - Expected question counts per year/paper
    - Sequential numbering
    - All options present (a, b, c, d)
    - Valid answer format
    - Image files exist for questions with has_image=True

    Returns:
        True if validation passes, False otherwise.
    """
    with open(dataset_path) as f:
        questions = json.load(f)

    errors = []
    warnings = []

    # Expected counts
    expected = {
        "gs1": 100,
        "csat": 80,
    }
    years = [2020, 2021, 2022, 2023, 2024]
    valid_answers = {"a", "b", "c", "d"}

    # Group by year and paper
    grouped: dict[tuple[int, str], list[dict]] = {}
    for q in questions:
        k = (q["year"], q["paper"])
        if k not in grouped:
            grouped[k] = []
        grouped[k].append(q)

    # Check all year/paper combos exist
    for year in years:
        for paper in ["gs1", "csat"]:
            k = (year, paper)
            if k not in grouped:
                errors.append(f"Missing: {paper} {year}")
                continue

            qs = sorted(grouped[k], key=lambda q: q["question_number"])

            # Check count
            if len(qs) != expected[paper]:
                errors.append(
                    f"{paper} {year}: Expected {expected[paper]} questions, got {len(qs)}"
                )

            # Check sequential numbering
            numbers = [q["question_number"] for q in qs]
            expected_numbers = list(range(1, expected[paper] + 1))
            if numbers != expected_numbers:
                missing = set(expected_numbers) - set(numbers)
                extra = set(numbers) - set(expected_numbers)
                if missing:
                    errors.append(f"{paper} {year}: Missing question numbers: {sorted(missing)}")
                if extra:
                    errors.append(f"{paper} {year}: Unexpected question numbers: {sorted(extra)}")

            # Check each question
            for q in qs:
                qid = q["id"]

                # Check options
                opts = q.get("options", {})
                for opt_key in ["a", "b", "c", "d"]:
                    if opt_key not in opts or not opts[opt_key].strip():
                        errors.append(f"{qid}: Missing or empty option '{opt_key}'")

                # Check answer
                answer = q.get("correct_answer", "")
                if not answer:
                    errors.append(f"{qid}: No correct_answer")
                elif answer not in valid_answers:
                    errors.append(f"{qid}: Invalid answer '{answer}' (expected a/b/c/d)")

                # Check question text
                if not q.get("question_text", "").strip():
                    errors.append(f"{qid}: Empty question_text")

                # Check image files exist
                if q.get("has_image"):
                    for img_path in q.get("image_paths", []):
                        if not os.path.exists(img_path):
                            warnings.append(f"{qid}: Image not found: {img_path}")

    # Check unique IDs
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        from collections import Counter
        dupes = [id for id, count in Counter(ids).items() if count > 1]
        errors.append(f"Duplicate IDs: {dupes}")

    # Report
    total = len(questions)
    print(f"\n{'='*60}")
    print(f"UPSC Bench Dataset Validation Report")
    print(f"{'='*60}")
    print(f"Total questions: {total}")
    print(f"Expected total: {sum(expected[p] * len(years) for p in expected)}")

    for year in years:
        for paper in ["gs1", "csat"]:
            k = (year, paper)
            count = len(grouped.get(k, []))
            status = "✓" if count == expected[paper] else "✗"
            print(f"  {status} {paper} {year}: {count}/{expected[paper]}")

    if errors:
        print(f"\n✗ {len(errors)} ERRORS:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"\n⚠ {len(warnings)} WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    if not errors:
        print(f"\n✓ Validation PASSED")
        return True
    else:
        print(f"\n✗ Validation FAILED")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate UPSC Bench dataset")
    parser.add_argument("--dataset", default="data/processed/upsc_bench.json")
    parser.add_argument("--images-dir", default="data/images")
    args = parser.parse_args()

    success = validate_dataset(args.dataset, args.images_dir)
    sys.exit(0 if success else 1)
