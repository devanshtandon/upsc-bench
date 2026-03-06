#!/usr/bin/env python3
"""Build arena_data.json for the /arena frontend page.

Reads mains essay answers from results/raw/ and writes a single JSON file
to web/data/arena_data.json with questions and model answers keyed for
efficient lookup.
"""

import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Graded results files (have rubric_scores, total_score, feedback)
GRADED_FILES = [
    "results/raw/mains_results_gpt_5_2.json",
    "results/raw/mains_results_claude_opus_4_6.json",
    "results/raw/mains_results_gemini_3_1_pro_preview.json",
    "results/raw/mains_results_gemini_2_5_flash.json",
]

# Ungraded answer files (raw_output only, no rubric scores)
UNGRADED_FILES = [
    "results/raw/mains_answers_gemini_3_flash.json",
]

OUTPUT_PATH = "web/data/arena_data.json"


def load_results(filepath, graded=True):
    """Load a results/answers file and return (model_id, list of essay entries)."""
    with open(os.path.join(PROJECT_ROOT, filepath)) as f:
        data = json.load(f)

    model = data["model"]
    entries = []

    for r in data["results"]:
        if r["paper"] != "mains_essay":
            continue

        entry = {
            "text": r["raw_output"],
            "word_count": r.get("word_count", 0),
        }

        if graded and "rubric_scores" in r:
            entry["rubric_scores"] = r["rubric_scores"]
            entry["total_score"] = r["total_score"]
            entry["feedback"] = r.get("feedback")
        else:
            entry["rubric_scores"] = None
            entry["total_score"] = None
            entry["feedback"] = None

        entries.append((r["question_id"], r, entry))

    return model, entries


def main():
    questions = {}  # id -> question metadata
    answers = {}    # question_id -> { model_id -> answer_data }

    # Process graded files
    for filepath in GRADED_FILES:
        full_path = os.path.join(PROJECT_ROOT, filepath)
        if not os.path.exists(full_path):
            print(f"  SKIP (not found): {filepath}")
            continue

        model, entries = load_results(filepath, graded=True)
        print(f"  {model}: {len(entries)} essay answers (graded)")

        for qid, raw, entry in entries:
            if qid not in questions:
                questions[qid] = {
                    "id": qid,
                    "section": raw["section"],
                    "question_number": raw["question_number"],
                    "question_text": raw["question_text"],
                    "word_limit": raw["word_limit"],
                    "max_marks": raw["max_marks"],
                }
            answers.setdefault(qid, {})[model] = entry

    # Process ungraded files
    for filepath in UNGRADED_FILES:
        full_path = os.path.join(PROJECT_ROOT, filepath)
        if not os.path.exists(full_path):
            print(f"  SKIP (not found): {filepath}")
            continue

        model, entries = load_results(filepath, graded=False)
        print(f"  {model}: {len(entries)} essay answers (ungraded)")

        for qid, raw, entry in entries:
            if qid not in questions:
                questions[qid] = {
                    "id": qid,
                    "section": raw["section"],
                    "question_number": raw["question_number"],
                    "question_text": raw["question_text"],
                    "word_limit": raw["word_limit"],
                    "max_marks": raw["max_marks"],
                }
            answers.setdefault(qid, {})[model] = entry

    # Build output
    output = {
        "questions": sorted(questions.values(), key=lambda q: q["question_number"]),
        "answers": answers,
    }

    out_path = os.path.join(PROJECT_ROOT, OUTPUT_PATH)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Stats
    n_questions = len(output["questions"])
    n_models = len(set(m for qid in answers for m in answers[qid]))
    file_size = os.path.getsize(out_path)
    print(f"\nWrote {out_path}")
    print(f"  {n_questions} questions, {n_models} models")
    print(f"  File size: {file_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
