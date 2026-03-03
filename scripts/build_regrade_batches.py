"""Build regrade batches: group by question, shuffle candidate labels.

Reads the 4 mains_answers files, groups all 4 model answers per question,
assigns shuffled candidate labels (A-D), and writes batch files + mapping.

Usage:
    python scripts/build_regrade_batches.py
"""
import json
import random
from pathlib import Path

ANSWER_FILES = {
    "claude_opus": "results/raw/mains_answers_claude_opus.json",
    "gpt5": "results/raw/mains_answers_gpt5.json",
    "gemini_3_pro": "results/raw/mains_answers_gemini_3_pro.json",
    "gemini_flash": "results/raw/mains_answers_gemini_flash.json",
}

QUESTIONS_FILE = "data/mains_questions/mains_2025.json"
OUTPUT_DIR = Path("results/regrade")
CANDIDATE_LABELS = ["A", "B", "C", "D"]

# Essays are long — 1 per batch. GS questions — 5 per batch.
ESSAY_BATCH_SIZE = 1
GS_BATCH_SIZE = 5


def load_answers():
    """Load all model answers, keyed by (model_key, question_id)."""
    answers = {}
    for model_key, filepath in ANSWER_FILES.items():
        with open(filepath) as f:
            data = json.load(f)
        for result in data["results"]:
            qid = result["question_id"]
            answers[(model_key, qid)] = result
    return answers


def load_questions():
    with open(QUESTIONS_FILE) as f:
        return json.load(f)


def build_batches():
    questions = load_questions()
    answers = load_answers()
    model_keys = list(ANSWER_FILES.keys())

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Separate essays from GS questions
    essay_questions = [q for q in questions if q["paper"] == "mains_essay"]
    gs_questions = [q for q in questions if q["paper"] != "mains_essay"]

    candidate_mapping = {}  # (question_id, candidate_label) -> model_key
    all_batch_items = []  # list of (question, {label: answer})

    rng = random.Random(42)  # deterministic shuffle

    for q in questions:
        qid = q["id"]
        # Shuffle model order for this question
        shuffled_models = model_keys.copy()
        rng.shuffle(shuffled_models)

        question_candidates = {}
        for i, model_key in enumerate(shuffled_models):
            label = CANDIDATE_LABELS[i]
            candidate_mapping[f"{qid}|candidate_{label}"] = model_key
            answer_data = answers.get((model_key, qid))
            if answer_data:
                question_candidates[f"candidate_{label}"] = {
                    "raw_output": answer_data["raw_output"],
                    "word_count": answer_data.get("word_count", 0),
                }
            else:
                question_candidates[f"candidate_{label}"] = {
                    "raw_output": "[NO ANSWER PROVIDED]",
                    "word_count": 0,
                }

        all_batch_items.append({
            "question_id": qid,
            "paper": q["paper"],
            "section": q.get("section"),
            "question_number": q["question_number"],
            "question_text": q["question_text"],
            "word_limit": q["word_limit"],
            "max_marks": q["max_marks"],
            "question_type": q["question_type"],
            "candidates": question_candidates,
        })

    # Split into batches
    essay_items = [item for item in all_batch_items if item["paper"] == "mains_essay"]
    gs_items = [item for item in all_batch_items if item["paper"] != "mains_essay"]

    batches = []

    # Essay batches (1 per batch)
    for i in range(0, len(essay_items), ESSAY_BATCH_SIZE):
        batches.append(essay_items[i:i + ESSAY_BATCH_SIZE])

    # GS batches (5 per batch)
    for i in range(0, len(gs_items), GS_BATCH_SIZE):
        batches.append(gs_items[i:i + GS_BATCH_SIZE])

    # Write batch files
    for idx, batch in enumerate(batches, 1):
        batch_file = OUTPUT_DIR / f"input_batch_{idx:03d}.json"
        with open(batch_file, "w") as f:
            json.dump(batch, f, indent=2)
        papers = set(item["paper"] for item in batch)
        qids = [item["question_id"] for item in batch]
        print(f"Batch {idx:03d}: {len(batch)} questions ({', '.join(papers)}) — {qids}")

    # Write candidate mapping
    mapping_file = OUTPUT_DIR / "candidate_mapping.json"
    with open(mapping_file, "w") as f:
        json.dump(candidate_mapping, f, indent=2)

    print(f"\nTotal: {len(batches)} batches, {len(all_batch_items)} questions, mapping has {len(candidate_mapping)} entries")
    return len(batches)


if __name__ == "__main__":
    build_batches()
