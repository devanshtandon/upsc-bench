#!/usr/bin/env python3
"""Combine per-page extraction chunks into combined files per paper.

For each 2025 paper (gs1, csat), loads all page chunks, deduplicates by
question_number, sorts, and propagates CSAT passage text to questions
that reference passages from previous pages.
"""

import json
import os
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS_DIR = os.path.join(BASE, "data/parsed/chunks")
OUTPUT_DIR = os.path.join(BASE, "data/parsed")


def load_chunks(paper, year):
    """Load all chunk files for a given paper and year."""
    pattern = os.path.join(CHUNKS_DIR, f"{paper}_{year}_page_*.json")
    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} chunk files for {paper} {year}")

    all_questions = []
    passages_by_page = {}  # page -> passage text (for CSAT propagation)

    for f in files:
        with open(f) as fh:
            data = json.load(fh)

        page_num = data.get("page", 0)

        # Handle different structures agents may have used
        questions = data.get("questions", [])

        # Also check for passages stored at page level
        if "passages_starting_on_this_page" in data:
            for p in data["passages_starting_on_this_page"]:
                if isinstance(p, dict) and p.get("passage_text"):
                    passages_by_page[page_num] = p["passage_text"]

        for q in questions:
            q["_source_page"] = page_num
            # Track passages embedded in questions
            if q.get("passage") and q["passage"].strip():
                passages_by_page[page_num] = q["passage"]
            all_questions.append(q)

    return all_questions, passages_by_page


def deduplicate(questions):
    """Keep only one copy of each question_number, preferring the most complete version."""
    by_number = {}
    for q in questions:
        qn = q.get("question_number")
        if qn is None:
            continue

        if qn not in by_number:
            by_number[qn] = q
        else:
            existing = by_number[qn]
            # Prefer the version with more text content
            new_len = len(q.get("question_text", "")) + len(q.get("passage", ""))
            old_len = len(existing.get("question_text", "")) + len(existing.get("passage", ""))
            if new_len > old_len:
                by_number[qn] = q

    return by_number


def propagate_passages(by_number, passages_by_page):
    """For CSAT questions with passage_on_previous_page=true, fill in the passage."""
    # Sort questions by number
    sorted_nums = sorted(by_number.keys())

    # Build a mapping of question_number -> passage text
    # For questions that have their own passage, record it
    last_passage = ""
    for qn in sorted_nums:
        q = by_number[qn]
        if q.get("passage") and q["passage"].strip():
            last_passage = q["passage"]
        elif q.get("passage_on_previous_page"):
            # Look backwards for the nearest passage
            if last_passage:
                q["passage"] = last_passage
            else:
                # Try to find from passages_by_page
                source_page = q.get("_source_page", 0)
                for pg in sorted(passages_by_page.keys(), reverse=True):
                    if pg <= source_page:
                        q["passage"] = passages_by_page[pg]
                        last_passage = q["passage"]
                        break

    return by_number


def clean_question(q):
    """Remove internal tracking fields and normalize."""
    cleaned = {
        "question_number": q["question_number"],
        "question_text": q.get("question_text", "").strip(),
        "options": q.get("options", {}),
        "has_image": q.get("has_image", False),
        "image_description": q.get("image_description", ""),
    }

    # Include passage for CSAT questions
    if q.get("passage") and q["passage"].strip():
        cleaned["passage"] = q["passage"].strip()

    return cleaned


def combine_paper(paper, year, expected_count):
    """Combine all chunks for a paper into a single combined file."""
    print(f"\n{'='*60}")
    print(f"Combining {paper.upper()} {year}")
    print(f"{'='*60}")

    questions, passages_by_page = load_chunks(paper, year)
    print(f"Total raw questions across all pages: {len(questions)}")

    by_number = deduplicate(questions)
    print(f"Unique questions after dedup: {len(by_number)}")

    if paper == "csat":
        by_number = propagate_passages(by_number, passages_by_page)
        # Count how many CSAT questions have passages
        with_passage = sum(1 for q in by_number.values()
                         if q.get("passage") and q["passage"].strip())
        print(f"CSAT questions with passage text: {with_passage}")

    # Sort by question number and clean
    sorted_questions = []
    for qn in sorted(by_number.keys()):
        sorted_questions.append(clean_question(by_number[qn]))

    # Check for gaps
    numbers = [q["question_number"] for q in sorted_questions]
    expected_numbers = list(range(1, expected_count + 1))
    missing = set(expected_numbers) - set(numbers)
    extra = set(numbers) - set(expected_numbers)
    if missing:
        print(f"WARNING: Missing questions: {sorted(missing)}")
    if extra:
        print(f"WARNING: Extra questions: {sorted(extra)}")

    # Write combined file
    output_path = os.path.join(OUTPUT_DIR, f"{paper}_{year}_combined.json")
    with open(output_path, "w") as f:
        json.dump(sorted_questions, f, indent=2, ensure_ascii=False)
    print(f"Written {len(sorted_questions)} questions to {output_path}")

    return sorted_questions


if __name__ == "__main__":
    gs1 = combine_paper("gs1", 2025, expected_count=100)
    csat = combine_paper("csat", 2025, expected_count=80)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"GS1 2025: {len(gs1)} questions")
    print(f"CSAT 2025: {len(csat)} questions")
    print(f"Total: {len(gs1) + len(csat)} questions")
