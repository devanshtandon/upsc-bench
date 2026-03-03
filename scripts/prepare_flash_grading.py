"""Create grading batches for Gemini 3 Flash alongside existing 4 models.

Groups all 5 candidates per question for comparative grading.
Output: results/regrade_flash/input_batch_*.json + candidate_mapping.json
"""
import json
import random
from pathlib import Path

MODELS = {
    "claude_opus": "results/raw/mains_answers_claude_opus.json",
    "gpt5": "results/raw/mains_answers_gpt5.json",
    "gemini_3_pro": "results/raw/mains_answers_gemini_3_pro.json",
    "gemini_flash": "results/raw/mains_answers_gemini_flash.json",
    "gemini_3_flash": "results/raw/mains_answers_gemini_3_flash.json",
}

QUESTIONS_FILE = "data/mains_questions/mains_2025.json"
OUTPUT_DIR = Path("results/regrade_flash")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATE_LABELS = ["candidate_A", "candidate_B", "candidate_C", "candidate_D", "candidate_E"]

# Load questions metadata
with open(QUESTIONS_FILE) as f:
    questions = {q["id"]: q for q in json.load(f)}

# Load all model answers, indexed by question_id
model_answers = {}
for model_key, fpath in MODELS.items():
    with open(fpath) as f:
        data = json.load(f)
    for r in data["results"]:
        qid = r["question_id"]
        if qid not in model_answers:
            model_answers[qid] = {}
        model_answers[qid][model_key] = {
            "raw_output": r["raw_output"],
            "word_count": r["word_count"],
        }

# Build per-question entries with shuffled candidate labels
candidate_mapping = {}
all_questions_grouped = []

random.seed(42)

for qid in sorted(model_answers.keys()):
    q_meta = questions.get(qid, {})
    models_for_q = list(model_answers[qid].keys())

    # Shuffle model order for debiasing
    shuffled = models_for_q.copy()
    random.shuffle(shuffled)

    candidates = {}
    for i, model_key in enumerate(shuffled):
        label = CANDIDATE_LABELS[i]
        candidates[label] = model_answers[qid][model_key]
        candidate_mapping[f"{qid}|{label}"] = model_key

    entry = {
        "question_id": qid,
        "paper": q_meta.get("paper", "unknown"),
        "section": q_meta.get("section"),
        "question_number": q_meta.get("question_number"),
        "question_text": q_meta.get("question_text", ""),
        "word_limit": q_meta.get("word_limit", 250),
        "max_marks": q_meta.get("max_marks", 10),
        "question_type": q_meta.get("question_type", "short_answer"),
        "candidates": candidates,
    }
    all_questions_grouped.append(entry)

# Split into batches
# Essays: 1 per batch (8 batches)
# GS: 5 per batch (~16 batches)
essay_qs = [q for q in all_questions_grouped if q["question_type"] == "essay"]
gs_qs = [q for q in all_questions_grouped if q["question_type"] != "essay"]

batches = []
batch_num = 1

# Essay batches (1 question each)
for eq in essay_qs:
    batches.append((f"batch_{batch_num:03d}", [eq]))
    batch_num += 1

# GS batches (5 questions each)
for i in range(0, len(gs_qs), 5):
    chunk = gs_qs[i:i+5]
    batches.append((f"batch_{batch_num:03d}", chunk))
    batch_num += 1

# Write batch files
for batch_id, batch_questions in batches:
    fpath = OUTPUT_DIR / f"input_{batch_id}.json"
    with open(fpath, "w") as f:
        json.dump(batch_questions, f, indent=2)
    n_candidates = sum(len(q["candidates"]) for q in batch_questions)
    print(f"{batch_id}: {len(batch_questions)} questions, {n_candidates} candidates")

# Write candidate mapping
with open(OUTPUT_DIR / "candidate_mapping.json", "w") as f:
    json.dump(candidate_mapping, f, indent=2)

print(f"\nTotal: {len(batches)} batches, {len(all_questions_grouped)} questions")
print(f"Candidate mapping: {len(candidate_mapping)} entries")
print(f"Output: {OUTPUT_DIR}")
