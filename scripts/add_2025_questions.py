"""Add 2025 questions to the UPSC Bench dataset.

Reads raw extracted questions from /tmp, structures them,
merges with answer keys, and appends to upsc_bench.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def parse_raw_question(raw_text: str, question_number: int) -> dict:
    """Parse raw question text into structured format with question_text and options."""
    text = raw_text.strip()

    # Clean up PDF artifacts
    text = re.sub(r'\s*[(\[]?\s*P\.T\.O\.?\s*[)\]]?\s*$', '', text)
    text = re.sub(r'\s*LVPK[-–]O[-–]PSO?/\d+[A-Z]?\s*', '', text)
    # Remove trailing page numbers - but only standalone ones (not option values)
    # Match page numbers that appear on their own line at the end
    text = re.sub(r'\n\s*\d{1,2}\s*$', '', text)

    # Try to extract options (a), (b), (c), (d) or (a}, (b}, etc.
    # Pattern: (a) or (a} followed by text, then (b) etc.
    option_pattern = r'\(([abcd])[)}\]]\s*'

    # Find all option positions
    option_matches = list(re.finditer(option_pattern, text))

    if len(option_matches) >= 4:
        # Extract question text (everything before first option)
        question_text = text[:option_matches[0].start()].strip()

        # Extract each option
        options = {}
        for i, match in enumerate(option_matches[:4]):
            letter = match.group(1)
            start = match.end()
            end = option_matches[i + 1].start() if i + 1 < len(option_matches) else len(text)
            option_text = text[start:end].strip()
            # Clean up trailing whitespace and newlines
            option_text = re.sub(r'\s+', ' ', option_text).strip()
            options[letter] = option_text
        return {
            "question_number": question_number,
            "question_text": question_text,
            "options": options,
            "has_image": False,
            "image_paths": [],
            "image_description": "",
        }
    else:
        # Fallback: try to split on newlines containing (a), (b), etc.
        lines = text.split('\n')
        question_lines = []
        options = {}
        current_option = None

        for line in lines:
            line = line.strip()
            opt_match = re.match(r'^\(([abcd])[)}\]]\s*(.*)', line)
            if opt_match:
                current_option = opt_match.group(1)
                options[current_option] = opt_match.group(2).strip()
            elif current_option and line and not re.match(r'^\(', line):
                options[current_option] += ' ' + line
            elif not current_option:
                question_lines.append(line)

        question_text = '\n'.join(question_lines).strip()

        if len(options) < 4:
            print(f"  WARNING: Q{question_number} has only {len(options)} options parsed")
            # Fill missing options
            for letter in 'abcd':
                if letter not in options:
                    options[letter] = "[MISSING]"

        return {
            "question_number": question_number,
            "question_text": question_text,
            "options": options,
            "has_image": False,
            "image_paths": [],
            "image_description": "",
        }


def build_2025_entries(raw_questions: dict, answer_key_path: str,
                       paper: str) -> list[dict]:
    """Build dataset entries for 2025 from raw questions + answer key."""
    with open(answer_key_path) as f:
        answer_key = json.load(f)

    answers = answer_key["answers"]
    dropped = answer_key.get("dropped_questions", [])

    if paper == "gs1":
        marks_correct = 2.0
        marks_wrong = -0.66
    else:
        marks_correct = 2.5
        marks_wrong = -0.83

    entries = []
    for qn_str, raw_text in sorted(raw_questions.items(), key=lambda x: int(x[0])):
        qn = int(qn_str)

        if qn in dropped:
            print(f"    Skipping dropped Q{qn}")
            continue

        correct_answer = answers.get(qn_str)
        if not correct_answer or correct_answer == "dropped":
            print(f"    Skipping Q{qn} (no answer)")
            continue

        parsed = parse_raw_question(raw_text, qn)

        entry = {
            "id": f"{paper}_2025_q{qn:03d}",
            "year": 2025,
            "paper": paper,
            "question_number": qn,
            "question_text": parsed["question_text"],
            "options": parsed["options"],
            "has_image": parsed["has_image"],
            "image_paths": parsed["image_paths"],
            "image_description": parsed["image_description"],
            "correct_answer": correct_answer,
            "marks_correct": marks_correct,
            "marks_wrong": marks_wrong,
            "marks_unanswered": 0.0,
        }
        entries.append(entry)

    return entries


def main():
    print("=" * 60)
    print("Adding 2025 Questions to UPSC Bench")
    print("=" * 60)

    # Load existing dataset
    bench_path = "data/processed/upsc_bench.json"
    with open(bench_path) as f:
        existing = json.load(f)
    print(f"Existing dataset: {len(existing)} questions")

    # Remove any existing 2025 entries (in case of re-run)
    existing = [e for e in existing if e.get("year") != 2025]
    print(f"After removing old 2025: {len(existing)} questions")

    new_entries = []

    # GS1 2025
    print("\n--- GS Paper I 2025 ---")
    gs1_raw_path = "/tmp/gs1_2025_raw_questions.json"
    gs1_missing_path = "/tmp/gs1_2025_missing_questions.json"

    if Path(gs1_raw_path).exists():
        with open(gs1_raw_path) as f:
            gs1_raw = json.load(f)

        # Merge missing questions if available
        if Path(gs1_missing_path).exists():
            with open(gs1_missing_path) as f:
                gs1_missing = json.load(f)
            print(f"  Merging {len(gs1_missing)} missing questions")
            gs1_raw.update(gs1_missing)

        print(f"  Total raw GS1 questions: {len(gs1_raw)}")

        gs1_entries = build_2025_entries(
            gs1_raw,
            "data/answer_keys/gs1_2025.json",
            "gs1"
        )
        print(f"  GS1 entries built: {len(gs1_entries)}")
        new_entries.extend(gs1_entries)
    else:
        print("  ERROR: GS1 raw questions not found!")

    # CSAT 2025
    print("\n--- CSAT Paper II 2025 ---")
    csat_raw_path = "/tmp/csat_2025_raw_questions.json"

    if Path(csat_raw_path).exists():
        with open(csat_raw_path) as f:
            csat_raw = json.load(f)
        print(f"  Total raw CSAT questions: {len(csat_raw)}")

        csat_entries = build_2025_entries(
            csat_raw,
            "data/answer_keys/csat_2025.json",
            "csat"
        )
        print(f"  CSAT entries built: {len(csat_entries)}")
        new_entries.extend(csat_entries)
    else:
        print("  ERROR: CSAT raw questions not found!")

    # Validate
    for entry in new_entries:
        for field in ["id", "year", "paper", "question_number", "question_text",
                       "options", "correct_answer"]:
            if field not in entry:
                print(f"  VALIDATION ERROR: {entry.get('id', '?')} missing {field}")

        opts = entry.get("options", {})
        for letter in "abcd":
            if letter not in opts or not opts[letter] or opts[letter] == "[MISSING]":
                print(f"  WARNING: {entry['id']} option ({letter}) is missing or empty")

    # Combine
    combined = existing + new_entries
    combined.sort(key=lambda e: (e["year"], e["paper"], e["question_number"]))

    # Save
    with open(bench_path, "w") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Dataset saved to {bench_path}")
    print(f"Total questions: {len(combined)}")
    for year in sorted(set(e["year"] for e in combined)):
        for paper in ["gs1", "csat"]:
            count = sum(1 for e in combined if e["year"] == year and e["paper"] == paper)
            print(f"  {year} {paper.upper()}: {count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
