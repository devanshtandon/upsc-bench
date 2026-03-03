"""Merge partial answer files into a single my_answers.json."""
import json
import sys
from pathlib import Path


def merge_answers(output_path="data/processed/my_answers.json"):
    """Merge all partial answer files."""
    answer_files = sorted(Path("data/processed").glob("answers_*.json"))
    if not answer_files:
        print("No answer files found!")
        return False

    all_answers = {}
    for f in answer_files:
        print(f"Loading {f.name}...")
        with open(f) as fh:
            answers = json.load(fh)
        print(f"  -> {len(answers)} answers")
        all_answers.update(answers)

    # Validate
    with open("data/processed/upsc_bench.json") as f:
        questions = json.load(f)

    question_ids = {q["id"] for q in questions}
    answered_ids = set(all_answers.keys())

    missing = question_ids - answered_ids
    extra = answered_ids - question_ids

    if missing:
        print(f"\nWARNING: {len(missing)} questions not answered:")
        for qid in sorted(missing):
            print(f"  - {qid}")

    if extra:
        print(f"\nWARNING: {len(extra)} answers for non-existent questions:")
        for qid in sorted(extra):
            print(f"  - {qid}")

    # Save merged answers
    with open(output_path, "w") as f:
        json.dump(all_answers, f, indent=2)

    print(f"\nMerged {len(all_answers)} answers -> {output_path}")
    print(f"Coverage: {len(answered_ids & question_ids)}/{len(question_ids)} questions")
    return True


if __name__ == "__main__":
    merge_answers()
