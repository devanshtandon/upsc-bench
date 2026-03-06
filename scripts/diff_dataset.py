#!/usr/bin/env python3
"""Diff old vs new dataset to document improvements."""

import json
import os
import difflib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    with open(path) as f:
        return json.load(f)


def by_id(questions):
    """Index questions by (paper, question_number)."""
    return {(q["paper"], q["question_number"]): q for q in questions}


def text_diff_ratio(old_text, new_text):
    """Return similarity ratio between two texts (0=totally different, 1=identical)."""
    return difflib.SequenceMatcher(None, old_text, new_text).ratio()


def main():
    old_data = load(os.path.join(BASE, "data/processed/upsc_bench_old.json"))
    new_data = load(os.path.join(BASE, "data/processed/upsc_bench.json"))

    old_idx = by_id(old_data)
    new_idx = by_id(new_data)

    # Filter to 2025 only (we only re-parsed 2025)
    old_2025 = {k: v for k, v in old_idx.items() if v["year"] == 2025}
    new_2025 = {k: v for k, v in new_idx.items() if v["year"] == 2025}

    print(f"Old dataset: {len(old_2025)} questions (2025)")
    print(f"New dataset: {len(new_2025)} questions (2025)")

    # Find new/removed questions
    old_keys = set(old_2025.keys())
    new_keys = set(new_2025.keys())
    added = new_keys - old_keys
    removed = old_keys - new_keys
    common = old_keys & new_keys

    if added:
        print(f"\nNEW questions (not in old): {len(added)}")
        for k in sorted(added):
            print(f"  {k[0].upper()} Q{k[1]}")

    if removed:
        print(f"\nREMOVED questions (not in new): {len(removed)}")
        for k in sorted(removed):
            print(f"  {k[0].upper()} Q{k[1]}")

    # Compare common questions
    changed = []
    unchanged = []
    categories = {
        "question_text_changed": [],
        "options_changed": [],
        "passage_added": [],
        "passage_changed": [],
        "answer_changed": [],
    }

    for k in sorted(common):
        old_q = old_2025[k]
        new_q = new_2025[k]

        diffs = []

        # Compare question text
        old_text = old_q.get("question_text", "")
        new_text = new_q.get("question_text", "")
        if old_text != new_text:
            ratio = text_diff_ratio(old_text, new_text)
            diffs.append(f"question_text (similarity: {ratio:.1%})")
            categories["question_text_changed"].append((k, ratio, old_text, new_text))

        # Compare options
        old_opts = old_q.get("options", {})
        new_opts = new_q.get("options", {})
        if old_opts != new_opts:
            changed_keys = [key for key in "abcd" if old_opts.get(key) != new_opts.get(key)]
            diffs.append(f"options ({', '.join(changed_keys)})")
            categories["options_changed"].append((k, changed_keys))

        # Compare passage
        old_passage = old_q.get("passage", "")
        new_passage = new_q.get("passage", "")
        if not old_passage and new_passage:
            diffs.append("passage ADDED")
            categories["passage_added"].append(k)
        elif old_passage != new_passage and new_passage:
            diffs.append("passage changed")
            categories["passage_changed"].append(k)

        # Compare answer
        old_ans = old_q.get("correct_answer", "")
        new_ans = new_q.get("correct_answer", "")
        if old_ans != new_ans:
            diffs.append(f"answer: {old_ans} → {new_ans}")
            categories["answer_changed"].append((k, old_ans, new_ans))

        if diffs:
            changed.append((k, diffs))
        else:
            unchanged.append(k)

    # Print summary
    print(f"\n{'='*60}")
    print(f"DIFF SUMMARY")
    print(f"{'='*60}")
    print(f"Total 2025 questions compared: {len(common)}")
    print(f"Changed: {len(changed)}")
    print(f"Unchanged: {len(unchanged)}")

    # Detailed changes
    if categories["question_text_changed"]:
        print(f"\n--- Question text changed ({len(categories['question_text_changed'])}) ---")
        severely_changed = []
        minor_changes = []
        for k, ratio, old_t, new_t in categories["question_text_changed"]:
            if ratio < 0.8:
                severely_changed.append((k, ratio, old_t, new_t))
            else:
                minor_changes.append((k, ratio))

        if severely_changed:
            print(f"\n  MAJOR changes (< 80% similarity): {len(severely_changed)}")
            for k, ratio, old_t, new_t in severely_changed[:10]:
                print(f"    {k[0].upper()} Q{k[1]} ({ratio:.0%} similar)")
                print(f"      OLD: {old_t[:100]}...")
                print(f"      NEW: {new_t[:100]}...")

        if minor_changes:
            print(f"\n  Minor changes (>= 80% similarity): {len(minor_changes)}")
            for k, ratio in minor_changes[:20]:
                print(f"    {k[0].upper()} Q{k[1]} ({ratio:.0%} similar)")

    if categories["options_changed"]:
        print(f"\n--- Options changed ({len(categories['options_changed'])}) ---")
        for k, keys in categories["options_changed"][:20]:
            print(f"  {k[0].upper()} Q{k[1]}: options {', '.join(keys)}")

    if categories["passage_added"]:
        print(f"\n--- Passages ADDED ({len(categories['passage_added'])}) ---")
        for k in categories["passage_added"]:
            print(f"  {k[0].upper()} Q{k[1]}")

    if categories["passage_changed"]:
        print(f"\n--- Passages changed ({len(categories['passage_changed'])}) ---")
        for k in categories["passage_changed"]:
            print(f"  {k[0].upper()} Q{k[1]}")

    if categories["answer_changed"]:
        print(f"\n--- Answer keys changed ({len(categories['answer_changed'])}) ---")
        for k, old_a, new_a in categories["answer_changed"]:
            print(f"  {k[0].upper()} Q{k[1]}: {old_a} → {new_a}")


if __name__ == "__main__":
    main()
