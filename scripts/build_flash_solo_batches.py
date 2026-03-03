"""Build solo grading batches for Gemini 3 Flash Mains answers.

Creates input batches with 1 candidate per question (just Flash),
using the calibrated judge prompt with score anchors for consistency
with the existing 4-model comparative regrade.

Essays: 2 per batch = 4 batches
GS questions: 8 per batch = ~10 batches
Total: ~14 batches
"""
import json
from pathlib import Path

import yaml

ANSWERS_FILE = Path("results/raw/mains_answers_gemini_3_flash.json")
QUESTIONS_FILE = Path("data/mains_questions/mains_2025.json")
RUBRIC_FILE = Path("config/judge.yaml")
OUTPUT_DIR = Path("results/regrade_flash_solo")

ESSAY_BATCH_SIZE = 2
GS_BATCH_SIZE = 8


def load_data():
    with open(ANSWERS_FILE) as f:
        answers_data = json.load(f)

    with open(QUESTIONS_FILE) as f:
        questions = {q["id"]: q for q in json.load(f)}

    with open(RUBRIC_FILE) as f:
        rubric_config = yaml.safe_load(f)

    return answers_data, questions, rubric_config


def format_rubric(rubric_type, rubric_config):
    """Format rubric dimensions for the prompt."""
    rubric = rubric_config["rubric"][rubric_type]
    lines = []
    for dim_key, dim_info in rubric.items():
        lines.append(f"  {dim_key}: {dim_info['weight']}% — {dim_info['description']}")
    return "\n".join(lines)


def build_batches():
    answers_data, questions, rubric_config = load_data()

    essays = []
    gs_questions = []

    for result in answers_data["results"]:
        qid = result["question_id"]
        q_meta = questions.get(qid, {})

        entry = {
            "question_id": qid,
            "paper": result["paper"],
            "section": result.get("section"),
            "question_number": result["question_number"],
            "question_text": result["question_text"],
            "word_limit": result["word_limit"],
            "max_marks": result["max_marks"],
            "question_type": result["question_type"],
            "answer": result["raw_output"],
            "word_count": result.get("word_count", 0),
        }

        if result["question_type"] == "essay":
            essays.append(entry)
        else:
            gs_questions.append(entry)

    # Build rubric texts
    essay_rubric = format_rubric("essay", rubric_config)
    gs_rubric = format_rubric("gs", rubric_config)

    # Create essay batches
    batches = []
    for i in range(0, len(essays), ESSAY_BATCH_SIZE):
        batch = essays[i:i + ESSAY_BATCH_SIZE]
        for entry in batch:
            entry["rubric_type"] = "Essay Paper"
            entry["rubric_text"] = essay_rubric
        batches.append(batch)

    # Create GS batches
    for i in range(0, len(gs_questions), GS_BATCH_SIZE):
        batch = gs_questions[i:i + GS_BATCH_SIZE]
        for entry in batch:
            entry["rubric_type"] = "GS Paper"
            entry["rubric_text"] = gs_rubric
        batches.append(batch)

    # Write batches
    for idx, batch in enumerate(batches, 1):
        output_file = OUTPUT_DIR / f"input_batch_{idx:03d}.json"
        with open(output_file, "w") as f:
            json.dump(batch, f, indent=2)
        qtypes = set(q["question_type"] for q in batch)
        papers = set(q["paper"] for q in batch)
        print(f"Batch {idx:03d}: {len(batch)} questions ({', '.join(qtypes)}) from {', '.join(papers)}")

    print(f"\nTotal: {len(batches)} batches, {sum(len(b) for b in batches)} questions")
    return batches


if __name__ == "__main__":
    build_batches()
