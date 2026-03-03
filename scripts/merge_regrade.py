"""Merge regrade outputs, map candidates back to models, compute final Mains scores.

Reads all grading_batch_*.json files from results/regrade/,
maps candidate labels to models via candidate_mapping.json,
applies mains_scorer.py functions, and updates leaderboard.json.

Usage:
    python scripts/merge_regrade.py
"""
import json
import shutil
from pathlib import Path

import yaml
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.mains_scorer import (
    calculate_mains_score,
    calculate_essay_score,
    calculate_mains_total,
    check_mains_pass,
    load_cutoffs,
)

REGRADE_DIR = Path("results/regrade")
MAPPING_FILE = REGRADE_DIR / "candidate_mapping.json"
LEADERBOARD_FILE = Path("results/leaderboard.json")
WEB_LEADERBOARD = Path("web/data/leaderboard.json")
QUESTIONS_FILE = Path("data/mains_questions/mains_2025.json")

# Map model keys to full OpenRouter model names
MODEL_KEY_TO_NAME = {
    "claude_opus": "openrouter/anthropic/claude-opus-4.6",
    "gpt5": "openrouter/openai/gpt-5.2",
    "gemini_3_pro": "openrouter/google/gemini-3.1-pro-preview",
    "gemini_flash": "openrouter/google/gemini-2.5-flash",
    "gemini_3_flash": "openrouter/google/gemini-3-flash-preview",
}

# Also need reverse mapping from answer file model names to leaderboard model names
# In case they differ slightly
ANSWER_FILE_MODELS = {
    "claude_opus": "results/raw/mains_answers_claude_opus.json",
    "gpt5": "results/raw/mains_answers_gpt5.json",
    "gemini_3_pro": "results/raw/mains_answers_gemini_3_pro.json",
    "gemini_flash": "results/raw/mains_answers_gemini_flash.json",
}


def load_grading_results():
    """Load all grading batch outputs and merge into a flat list."""
    all_results = []
    batch_files = sorted(REGRADE_DIR.glob("grading_batch_*.json"))

    if not batch_files:
        print("ERROR: No grading batch files found in results/regrade/")
        return []

    for batch_file in batch_files:
        try:
            with open(batch_file) as f:
                batch_data = json.load(f)
            if isinstance(batch_data, list):
                all_results.extend(batch_data)
            else:
                print(f"WARNING: {batch_file.name} is not a list, skipping")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse {batch_file.name}: {e}")

    print(f"Loaded {len(all_results)} graded questions from {len(batch_files)} batch files")
    return all_results


def load_mapping():
    """Load candidate_mapping.json."""
    with open(MAPPING_FILE) as f:
        return json.load(f)


def load_questions():
    """Load mains questions for metadata (section info for essays)."""
    with open(QUESTIONS_FILE) as f:
        return {q["id"]: q for q in json.load(f)}


def map_grades_to_models(graded_questions, mapping, questions_meta):
    """Map candidate grades back to model-specific results.

    Returns: dict of model_key -> list of graded results
    """
    model_results = {key: [] for key in MODEL_KEY_TO_NAME}

    for q in graded_questions:
        qid = q["question_id"]
        q_meta = questions_meta.get(qid, {})

        for candidate in q.get("candidates", []):
            cid = candidate["candidate_id"]
            mapping_key = f"{qid}|{cid}"
            model_key = mapping.get(mapping_key)

            if not model_key:
                print(f"WARNING: No mapping for {mapping_key}")
                continue

            if model_key not in model_results:
                print(f"WARNING: Unknown model key {model_key}")
                continue

            # Build result entry
            result = {
                "question_id": qid,
                "paper": q_meta.get("paper", "unknown"),
                "section": q_meta.get("section"),
                "question_number": q_meta.get("question_number"),
                "total_score": candidate.get("total_score", 0),
                "max_marks": candidate.get("max_marks", q_meta.get("max_marks", 0)),
                "summary": candidate.get("summary", ""),
                "analysis": candidate.get("analysis", ""),
                "rubric_scores": candidate.get("rubric_scores", {}),
                "brief_feedback": candidate.get("brief_feedback", ""),
            }
            model_results[model_key].append(result)

    return model_results


def compute_model_mains_scores(model_results):
    """Compute per-paper and total Mains scores for each model."""
    cutoffs = load_cutoffs()
    model_scores = {}

    for model_key, results in model_results.items():
        if not results:
            print(f"WARNING: No results for {model_key}")
            continue

        # Group results by paper
        by_paper = {}
        for r in results:
            paper = r["paper"]
            if paper not in by_paper:
                by_paper[paper] = []
            by_paper[paper].append(r)

        # Calculate per-paper scores
        paper_scores = {}

        # Essay paper — uses special selection logic
        essay_results = by_paper.get("mains_essay", [])
        if essay_results:
            essay_score = calculate_essay_score(essay_results)
            paper_scores["mains_essay"] = essay_score

        # GS papers
        for paper_key in ["mains_gs1", "mains_gs2", "mains_gs3", "mains_gs4"]:
            paper_results = by_paper.get(paper_key, [])
            if paper_results:
                paper_score = calculate_mains_score(paper_results, paper_key)
                paper_scores[paper_key] = paper_score

        # Total across all papers
        total = calculate_mains_total(paper_scores)

        # Pass/fail check
        pass_check = check_mains_pass(total["total_score"], 2025, cutoffs)

        model_scores[model_key] = {
            "paper_scores": paper_scores,
            "total": total,
            "pass_check": pass_check,
        }

        # Print summary
        model_name = MODEL_KEY_TO_NAME.get(model_key, model_key)
        print(f"\n{model_name}:")
        print(f"  Total: {total['total_score']:.2f}/{total['max_marks']} ({total['score_pct']:.1f}%)")
        for pk, ps in paper_scores.items():
            marks = ps.get("total_marks", 0)
            max_m = ps.get("max_marks", 0)
            pct = ps.get("avg_score_pct", 0)
            print(f"  {pk}: {marks:.2f}/{max_m} ({pct:.1f}%)")
        print(f"  Pass: {pass_check['passed']} (cutoff: {pass_check['cutoff']:.2f}, margin: {pass_check['margin']:.2f})")

    return model_scores


def _estimate_mains_rank(total_score):
    """Estimate All-India Rank for Mains based on score.

    The human AIR 1 (Shakti Dubey, CSE 2024) scored an estimated 602/1250
    (proportionally scaled from 843/1750). Any AI model scoring above that
    would place at AIR 1 or better. For models below that threshold, we
    do a rough linear interpolation against the ~14,500 Mains candidates.
    """
    TOTAL_CANDIDATES = 14500
    HUMAN_AIR1_SCORE = 602.14  # proportionally estimated

    if total_score >= HUMAN_AIR1_SCORE:
        return {
            "rank": 1,
            "percentile": 99.99,
            "label": "Exceeds estimated topper",
            "total_candidates": TOTAL_CANDIDATES,
        }
    else:
        # Rough interpolation: cutoff ~571 maps to rank ~14500,
        # AIR 1 ~602 maps to rank 1. Linear between them.
        CUTOFF = 571.43
        if total_score <= CUTOFF:
            rank = TOTAL_CANDIDATES
        else:
            fraction = (total_score - CUTOFF) / (HUMAN_AIR1_SCORE - CUTOFF)
            rank = max(1, int(TOTAL_CANDIDATES * (1 - fraction)))
        percentile = round((1 - rank / TOTAL_CANDIDATES) * 100, 2)
        return {
            "rank": rank,
            "percentile": percentile,
            "label": f"~{rank:,}" if rank > 100 else "Top 100",
            "total_candidates": TOTAL_CANDIDATES,
        }


def update_leaderboard(model_scores):
    """Update leaderboard.json with Mains scores."""
    # Load existing leaderboard
    with open(LEADERBOARD_FILE) as f:
        leaderboard = json.load(f)

    cutoffs = load_cutoffs()
    mains_cutoff_2025 = cutoffs.get("mains_cutoffs", {}).get(2025, {})
    full_cutoff = mains_cutoff_2025.get("total", 800)
    full_max = mains_cutoff_2025.get("max_marks", 1750)
    proportional_cutoff = round(full_cutoff / full_max * 1250, 2)

    # Map from full model names to model keys (reverse lookup)
    name_to_key = {v: k for k, v in MODEL_KEY_TO_NAME.items()}

    # Also build a mapping from leaderboard model names to answer file model names
    # in case they differ slightly
    leaderboard_name_to_key = {}
    for model_entry in leaderboard["models"]:
        model_name = model_entry["model"]
        # Try exact match first
        if model_name in name_to_key:
            leaderboard_name_to_key[model_name] = name_to_key[model_name]
        else:
            # Try partial match
            for full_name, key in name_to_key.items():
                if key in model_name.lower().replace("-", "_").replace(".", ""):
                    leaderboard_name_to_key[model_name] = key
                    break

    # Update each model entry with Mains data
    for model_entry in leaderboard["models"]:
        model_name = model_entry["model"]
        model_key = leaderboard_name_to_key.get(model_name)

        if not model_key or model_key not in model_scores:
            # Try harder to find match
            for key in model_scores:
                if key in model_name.lower().replace("-", "_").replace("/", ""):
                    model_key = key
                    break

        if not model_key or model_key not in model_scores:
            print(f"WARNING: No mains scores for leaderboard model {model_name}")
            continue

        scores = model_scores[model_key]
        paper_scores = scores["paper_scores"]
        total = scores["total"]
        pass_check = scores["pass_check"]

        # Build the mains data structure matching MainsYearData type
        papers_data = {}

        # Essay
        if "mains_essay" in paper_scores:
            es = paper_scores["mains_essay"]
            papers_data["essay"] = {
                "score": round(es["total_marks"], 2),
                "max_marks": es["max_marks"],
                "score_pct": es["avg_score_pct"],
                "questions_evaluated": es["question_count"],
                "selected_essays": es.get("selected_essays", []),
            }

        # GS1-4
        for gs_key in ["mains_gs1", "mains_gs2", "mains_gs3", "mains_gs4"]:
            if gs_key in paper_scores:
                ps = paper_scores[gs_key]
                short_key = gs_key.replace("mains_", "")
                papers_data[short_key] = {
                    "score": round(ps["total_marks"], 2),
                    "max_marks": ps["max_marks"],
                    "score_pct": ps["avg_score_pct"],
                    "questions_evaluated": ps["question_count"],
                }

        model_entry["mains"] = {
            2025: {
                "total_score": round(total["total_score"], 2),
                "max_marks": total["max_marks"],
                "score_pct": total["score_pct"],
                "passed": pass_check["passed"],
                "cutoff": pass_check["cutoff"],
                "margin": pass_check["margin"],
                "estimated_rank": _estimate_mains_rank(total["total_score"]),
                "papers": papers_data,
            }
        }

    # Update metadata
    leaderboard["metadata"]["mains_years"] = [2025]
    leaderboard["metadata"]["mains_papers"] = [
        "mains_total", "essay", "mains_gs1", "mains_gs2", "mains_gs3", "mains_gs4"
    ]
    leaderboard["metadata"]["mains_cutoffs"] = {
        "2025": {
            "proportional_cutoff": proportional_cutoff,
            "max_marks": 1250,
        }
    }

    # Write updated leaderboard
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=2)
    print(f"\nUpdated {LEADERBOARD_FILE}")

    # Copy to web/data/
    shutil.copy2(LEADERBOARD_FILE, WEB_LEADERBOARD)
    print(f"Copied to {WEB_LEADERBOARD}")

    return leaderboard


def validate_results(graded_questions, model_results):
    """Run validation checks on grading results."""
    print("\n=== Validation ===")

    # Check total answers graded
    total_graded = sum(
        len(q.get("candidates", []))
        for q in graded_questions
    )
    print(f"Total candidate gradings: {total_graded} (expected: 348 = 87 questions × 4 models)")

    # Check per-model counts
    for model_key, results in model_results.items():
        print(f"  {model_key}: {len(results)} questions graded")

    # Check score ranges
    all_scores = []
    over_75_pct = 0
    for model_key, results in model_results.items():
        for r in results:
            score = r["total_score"]
            max_marks = r["max_marks"]
            pct = (score / max_marks * 100) if max_marks > 0 else 0
            all_scores.append(pct)
            if pct > 75:
                over_75_pct += 1
            if score > max_marks:
                print(f"  ERROR: Score {score} exceeds max {max_marks} for {r['question_id']} ({model_key})")

    if all_scores:
        print(f"\nScore distribution (% of max):")
        print(f"  Min: {min(all_scores):.1f}%")
        print(f"  Max: {max(all_scores):.1f}%")
        print(f"  Mean: {sum(all_scores)/len(all_scores):.1f}%")
        print(f"  Median: {sorted(all_scores)[len(all_scores)//2]:.1f}%")
        print(f"  >75%: {over_75_pct} ({over_75_pct/len(all_scores)*100:.1f}%)")

    # Check for missing rubric scores
    missing_rubric = 0
    for model_key, results in model_results.items():
        for r in results:
            if not r.get("rubric_scores"):
                missing_rubric += 1
                print(f"  WARNING: Missing rubric scores for {r['question_id']} ({model_key})")

    if missing_rubric == 0:
        print("  All answers have rubric scores ✓")

    return total_graded == 348


def main():
    print("=== Merge Regrade Results ===\n")

    # Load data
    graded_questions = load_grading_results()
    if not graded_questions:
        print("No grading results to merge. Exiting.")
        return

    mapping = load_mapping()
    questions_meta = load_questions()

    # Map grades to models
    model_results = map_grades_to_models(graded_questions, mapping, questions_meta)

    # Validate
    validate_results(graded_questions, model_results)

    # Compute scores
    model_scores = compute_model_mains_scores(model_results)

    # Update leaderboard
    update_leaderboard(model_scores)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
