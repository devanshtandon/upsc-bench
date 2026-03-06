#!/usr/bin/env python3
"""Merge validated questions with answer keys and scoring metadata.

Adds correct_answer, marks_correct/wrong/unanswered, id, and dropped flag.
"""

import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCORING = {
    "gs1": {"marks_correct": 2.0, "marks_wrong": -0.66, "marks_unanswered": 0},
    "csat": {"marks_correct": 2.5, "marks_wrong": -0.83, "marks_unanswered": 0},
}


def merge_paper(paper, year):
    """Merge a combined question file with its answer key."""
    # Load combined questions
    combined_path = os.path.join(BASE, f"data/parsed/{paper}_{year}_combined.json")
    with open(combined_path) as f:
        questions = json.load(f)

    # Load answer key
    ak_path = os.path.join(BASE, f"data/answer_keys/{paper}_{year}.json")
    with open(ak_path) as f:
        answer_key = json.load(f)

    answers = answer_key["answers"]
    dropped = answer_key.get("dropped_questions", [])
    disputed = answer_key.get("disputed_questions", {})
    scoring = SCORING[paper]

    merged = []
    for q in questions:
        qn = q["question_number"]
        qn_str = str(qn)

        entry = {
            "id": f"{paper}_{year}_q{qn:03d}",
            "year": year,
            "paper": paper,
            "question_number": qn,
            "question_text": q["question_text"],
            "options": q["options"],
            "has_image": q.get("has_image", False),
            "image_paths": [],
            "image_description": q.get("image_description", ""),
            "correct_answer": answers.get(qn_str, ""),
            "marks_correct": scoring["marks_correct"],
            "marks_wrong": scoring["marks_wrong"],
            "marks_unanswered": scoring["marks_unanswered"],
        }

        # Add passage for CSAT
        if q.get("passage"):
            entry["passage"] = q["passage"]

        # Flag dropped questions
        if qn_str in [str(d) for d in dropped]:
            entry["dropped"] = True

        # Note disputed questions
        if qn_str in disputed:
            entry["disputed"] = True
            entry["disputed_answers"] = disputed[qn_str]

        merged.append(entry)

    # Verify all answer keys matched
    matched = sum(1 for q in merged if q["correct_answer"])
    print(f"  {paper.upper()} {year}: {len(merged)} questions, {matched} with answers")
    if matched != len(merged):
        missing = [q["question_number"] for q in merged if not q["correct_answer"]]
        print(f"  WARNING: Questions without answers: {missing}")

    return merged


def main():
    print("Merging with answer keys...")

    gs1 = merge_paper("gs1", 2025)
    csat = merge_paper("csat", 2025)

    # Write merged files
    for paper, data in [("gs1", gs1), ("csat", csat)]:
        path = os.path.join(BASE, f"data/parsed/{paper}_2025_merged.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Written {len(data)} questions to {path}")

    print(f"\nTotal: {len(gs1) + len(csat)} merged questions")


if __name__ == "__main__":
    main()
