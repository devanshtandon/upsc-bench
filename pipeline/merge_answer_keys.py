"""Merge answer keys from coaching sites into structured question data."""

import json
import os
from pathlib import Path


def load_answer_key(answer_key_path: str) -> dict:
    """Load an answer key JSON file.

    Expected format:
    {
        "source": "vision_ias",
        "year": 2024,
        "paper": "gs1",
        "answers": {"1": "d", "2": "a", "3": "b", ...}
    }
    """
    with open(answer_key_path) as f:
        return json.load(f)


def merge_answer_keys(
    questions: list[dict],
    answer_keys_dir: str,
) -> list[dict]:
    """Merge answer keys into structured questions.

    Args:
        questions: List of structured question dicts (from structure_questions.py).
        answer_keys_dir: Directory containing answer key JSON files.

    Returns:
        Updated questions list with correct_answer and answer_source filled in.
    """
    # Load all answer keys
    keys_by_year_paper: dict[tuple[int, str], list[dict]] = {}

    for key_file in Path(answer_keys_dir).glob("*.json"):
        key_data = load_answer_key(str(key_file))
        year = key_data["year"]
        paper = key_data["paper"]
        k = (year, paper)
        if k not in keys_by_year_paper:
            keys_by_year_paper[k] = []
        keys_by_year_paper[k].append(key_data)

    # Merge into questions
    merged = []
    disputed = []

    for q in questions:
        year = q["year"]
        paper = q["paper"]
        qnum = str(q["question_number"])

        keys = keys_by_year_paper.get((year, paper), [])

        if not keys:
            print(f"Warning: No answer key for {year}/{paper}")
            merged.append(q)
            continue

        # Collect answers from all sources
        answers = {}
        for key_data in keys:
            source = key_data["source"]
            answer = key_data["answers"].get(qnum, "").lower().strip()
            if answer:
                answers[source] = answer

        if not answers:
            print(f"Warning: No answer for {paper}_{year}_q{qnum}")
            merged.append(q)
            continue

        # Check for consensus
        unique_answers = set(answers.values())
        if len(unique_answers) == 1:
            q["correct_answer"] = list(unique_answers)[0]
            q["answer_source"] = ",".join(answers.keys())
        else:
            # Disputed — use majority vote
            from collections import Counter
            vote = Counter(answers.values()).most_common(1)[0]
            q["correct_answer"] = vote[0]
            q["answer_source"] = f"disputed_majority({','.join(f'{s}={a}' for s, a in answers.items())})"
            disputed.append({
                "id": q["id"],
                "answers": answers,
                "chosen": vote[0],
            })

        merged.append(q)

    if disputed:
        print(f"\n⚠ {len(disputed)} disputed answers (majority vote used):")
        for d in disputed:
            print(f"  {d['id']}: {d['answers']} → {d['chosen']}")

    return merged


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Merge answer keys into structured questions")
    parser.add_argument("--questions-dir", default="data/processed",
                        help="Directory with per-paper question JSONs")
    parser.add_argument("--answer-keys-dir", default="data/answer_keys")
    parser.add_argument("--output", default="data/processed/upsc_bench_unvalidated.json")
    args = parser.parse_args()

    # Load all questions
    all_questions = []
    for qfile in sorted(Path(args.questions_dir).glob("*_*.json")):
        if "upsc_bench" in qfile.name:
            continue
        with open(qfile) as f:
            all_questions.extend(json.load(f))

    print(f"Loaded {len(all_questions)} questions")
    merged = merge_answer_keys(all_questions, args.answer_keys_dir)

    # Count stats
    with_answers = sum(1 for q in merged if q["correct_answer"])
    print(f"Questions with answers: {with_answers}/{len(merged)}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"Saved to {args.output}")
