"""Merge extracted question batches with answer keys to create upsc_bench.json.

Reads batch files from data/processed/, merges with answer keys from data/answer_keys/,
and outputs the final dataset for the benchmark runner.
"""

import json
import sys
from pathlib import Path


def load_and_merge_batches(batch_pattern: str, processed_dir: str = "data/processed") -> list[dict]:
    """Load and merge question batch files, sorted by question_number."""
    batches = sorted(Path(processed_dir).glob(batch_pattern))
    if not batches:
        print(f"No batch files found matching {batch_pattern} in {processed_dir}")
        return []

    all_questions = []
    for batch_file in batches:
        print(f"  Loading {batch_file.name}...")
        with open(batch_file) as f:
            questions = json.load(f)
        all_questions.extend(questions)
        print(f"    -> {len(questions)} questions")

    # Sort by question_number and deduplicate
    all_questions.sort(key=lambda q: q["question_number"])

    # Deduplicate by question_number (keep first occurrence)
    seen = set()
    unique_questions = []
    for q in all_questions:
        qn = q["question_number"]
        if qn not in seen:
            seen.add(qn)
            unique_questions.append(q)
        else:
            print(f"    WARNING: Duplicate question {qn}, keeping first occurrence")

    return unique_questions


def merge_with_answer_key(questions: list[dict], answer_key_path: str,
                          year: int, paper: str) -> list[dict]:
    """Merge extracted questions with answer key to create benchmark dataset entries."""
    with open(answer_key_path) as f:
        answer_key = json.load(f)

    answers = answer_key["answers"]
    dropped = answer_key.get("dropped_questions", [])

    # Marking scheme
    if paper == "gs1":
        marks_correct = 2.0
        marks_wrong = -0.66
    else:  # csat
        marks_correct = 2.5
        marks_wrong = -0.83
    marks_unanswered = 0.0

    dataset_entries = []
    for q in questions:
        qn = q["question_number"]
        qn_str = str(qn)

        # Skip dropped questions
        if qn in dropped:
            print(f"    Skipping dropped question {qn}")
            continue

        correct_answer = answers.get(qn_str)
        if not correct_answer or correct_answer == "dropped":
            print(f"    Skipping question {qn} (no answer or dropped)")
            continue

        entry = {
            "id": f"{paper}_{year}_q{qn:03d}",
            "year": year,
            "paper": paper,
            "question_number": qn,
            "question_text": q["question_text"],
            "options": q["options"],
            "has_image": q.get("has_image", False),
            "image_paths": q.get("image_paths", []),
            "image_description": q.get("image_description", ""),
            "correct_answer": correct_answer,
            "marks_correct": marks_correct,
            "marks_wrong": marks_wrong,
            "marks_unanswered": marks_unanswered,
        }
        dataset_entries.append(entry)

    return dataset_entries


def validate_dataset(entries: list[dict], paper: str) -> bool:
    """Basic validation of the dataset."""
    expected = 100 if paper == "gs1" else 80

    # Count non-dropped questions
    actual = len(entries)
    print(f"  {paper.upper()}: {actual} questions (expected ~{expected} minus dropped)")

    # Check all have required fields
    required_fields = ["id", "year", "paper", "question_number", "question_text",
                       "options", "correct_answer", "marks_correct", "marks_wrong"]
    for entry in entries:
        for field in required_fields:
            if field not in entry:
                print(f"  ERROR: Question {entry.get('question_number', '?')} missing field: {field}")
                return False

        # Check options
        opts = entry["options"]
        for letter in ["a", "b", "c", "d"]:
            if letter not in opts or not opts[letter]:
                print(f"  WARNING: Q{entry['question_number']} missing option {letter}")

    # Check sequential numbering
    numbers = sorted(e["question_number"] for e in entries)
    print(f"  Question range: {numbers[0]} to {numbers[-1]}")

    return True


def main():
    print("=" * 60)
    print("Building UPSC Bench Dataset")
    print("=" * 60)

    all_entries = []

    # Process GS1 2024
    print("\n--- GS Paper I 2024 ---")
    gs1_questions = load_and_merge_batches("gs1_2024_batch*.json")
    if gs1_questions:
        print(f"  Total GS1 questions extracted: {len(gs1_questions)}")
        gs1_entries = merge_with_answer_key(
            gs1_questions,
            "data/answer_keys/gs1_2024.json",
            year=2024,
            paper="gs1"
        )
        if validate_dataset(gs1_entries, "gs1"):
            all_entries.extend(gs1_entries)
            print(f"  GS1 entries added: {len(gs1_entries)}")
    else:
        print("  ERROR: No GS1 questions found!")

    # Process CSAT 2024
    print("\n--- CSAT Paper II 2024 ---")
    csat_questions = load_and_merge_batches("csat_2024_batch*.json")
    if csat_questions:
        print(f"  Total CSAT questions extracted: {len(csat_questions)}")
        csat_entries = merge_with_answer_key(
            csat_questions,
            "data/answer_keys/csat_2024.json",
            year=2024,
            paper="csat"
        )
        if validate_dataset(csat_entries, "csat"):
            all_entries.extend(csat_entries)
            print(f"  CSAT entries added: {len(csat_entries)}")
    else:
        print("  ERROR: No CSAT questions found!")

    # Save final dataset
    output_path = "data/processed/upsc_bench.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_entries, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Dataset saved to {output_path}")
    print(f"Total questions: {len(all_entries)}")
    print(f"  GS1: {sum(1 for e in all_entries if e['paper'] == 'gs1')}")
    print(f"  CSAT: {sum(1 for e in all_entries if e['paper'] == 'csat')}")
    print(f"{'=' * 60}")

    return len(all_entries) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
