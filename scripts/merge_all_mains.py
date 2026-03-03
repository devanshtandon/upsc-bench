"""Merge all Mains regrade results: 4-model comparative + Flash solo grading.

Combines:
1. results/regrade/ — 4 models graded comparatively (candidate_A-D mapped via candidate_mapping.json)
2. results/regrade_flash_solo/ — Gemini 3 Flash graded solo (candidate_id = "gemini_3_flash")

Computes per-paper and total Mains scores for all 5 models, updates leaderboard.json.

Usage:
    python scripts/merge_all_mains.py
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
FLASH_SOLO_DIR = Path("results/regrade_flash_solo")
MAPPING_FILE = REGRADE_DIR / "candidate_mapping.json"
LEADERBOARD_FILE = Path("results/leaderboard.json")
WEB_LEADERBOARD = Path("web/data/leaderboard.json")
QUESTIONS_FILE = Path("data/mains_questions/mains_2025.json")

MODEL_KEY_TO_NAME = {
    "claude_opus": "openrouter/anthropic/claude-opus-4.6",
    "gpt5": "openrouter/openai/gpt-5.2",
    "gemini_3_pro": "openrouter/google/gemini-3.1-pro-preview",
    "gemini_flash": "openrouter/google/gemini-2.5-flash",
    "gemini_3_flash": "openrouter/google/gemini-3-flash-preview",
}


def load_grading_results(directory, label=""):
    """Load all grading batch outputs from a directory."""
    all_results = []
    batch_files = sorted(directory.glob("grading_batch_*.json"))

    if not batch_files:
        print(f"WARNING: No grading batch files found in {directory}")
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

    print(f"[{label}] Loaded {len(all_results)} graded questions from {len(batch_files)} batch files")
    return all_results


def load_questions():
    """Load mains questions for metadata (section info for essays)."""
    with open(QUESTIONS_FILE) as f:
        return {q["id"]: q for q in json.load(f)}


def map_comparative_grades(graded_questions, questions_meta):
    """Map 4-model comparative grades (candidate_A-D) to model-specific results."""
    with open(MAPPING_FILE) as f:
        mapping = json.load(f)

    model_results = {key: [] for key in MODEL_KEY_TO_NAME if key != "gemini_3_flash"}

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
                # Could be gemini_3_flash in the mapping but we handle that separately
                continue

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


def map_flash_solo_grades(graded_questions, questions_meta):
    """Map Flash solo grades directly to gemini_3_flash results."""
    results = []

    for q in graded_questions:
        qid = q["question_id"]
        q_meta = questions_meta.get(qid, {})

        for candidate in q.get("candidates", []):
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
            results.append(result)

    return {"gemini_3_flash": results}


def compute_model_mains_scores(model_results):
    """Compute per-paper and total Mains scores for each model."""
    cutoffs = load_cutoffs()
    model_scores = {}

    for model_key, results in model_results.items():
        if not results:
            print(f"WARNING: No results for {model_key}")
            continue

        by_paper = {}
        for r in results:
            paper = r["paper"]
            if paper not in by_paper:
                by_paper[paper] = []
            by_paper[paper].append(r)

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

        total = calculate_mains_total(paper_scores)
        pass_check = check_mains_pass(total["total_score"], 2025, cutoffs)

        model_scores[model_key] = {
            "paper_scores": paper_scores,
            "total": total,
            "pass_check": pass_check,
        }

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
    """Estimate All-India Rank for Mains based on score."""
    TOTAL_CANDIDATES = 14500
    HUMAN_AIR1_SCORE = 602.14

    if total_score >= HUMAN_AIR1_SCORE:
        return {
            "rank": 1,
            "percentile": 99.99,
            "label": "Exceeds estimated topper",
            "total_candidates": TOTAL_CANDIDATES,
        }
    else:
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
    """Update leaderboard.json with Mains scores for all 5 models."""
    with open(LEADERBOARD_FILE) as f:
        leaderboard = json.load(f)

    cutoffs = load_cutoffs()
    mains_cutoff_2025 = cutoffs.get("mains_cutoffs", {}).get(2025, {})
    full_cutoff = mains_cutoff_2025.get("total", 800)
    full_max = mains_cutoff_2025.get("max_marks", 1750)
    proportional_cutoff = round(full_cutoff / full_max * 1250, 2)

    name_to_key = {v: k for k, v in MODEL_KEY_TO_NAME.items()}

    for model_entry in leaderboard["models"]:
        model_name = model_entry["model"]
        model_key = name_to_key.get(model_name)

        if not model_key:
            for full_name, key in name_to_key.items():
                if key in model_name.lower().replace("-", "_").replace(".", ""):
                    model_key = key
                    break

        if not model_key or model_key not in model_scores:
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

        papers_data = {}

        if "mains_essay" in paper_scores:
            es = paper_scores["mains_essay"]
            papers_data["essay"] = {
                "score": round(es["total_marks"], 2),
                "max_marks": es["max_marks"],
                "score_pct": es["avg_score_pct"],
                "questions_evaluated": es["question_count"],
                "selected_essays": es.get("selected_essays", []),
            }

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
            "2025": {
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

    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=2)
    print(f"\nUpdated {LEADERBOARD_FILE}")

    shutil.copy2(LEADERBOARD_FILE, WEB_LEADERBOARD)
    print(f"Copied to {WEB_LEADERBOARD}")

    return leaderboard


def validate_results(model_results):
    """Run validation checks on all grading results."""
    print("\n=== Validation ===")

    total_graded = sum(len(results) for results in model_results.values())
    expected = 87 * 5  # 87 questions × 5 models
    print(f"Total gradings: {total_graded} (expected: {expected})")

    for model_key, results in model_results.items():
        print(f"  {model_key}: {len(results)} questions graded")

    all_scores = []
    over_75_pct = 0
    errors = 0
    for model_key, results in model_results.items():
        for r in results:
            score = r["total_score"]
            max_marks = r["max_marks"]
            pct = (score / max_marks * 100) if max_marks > 0 else 0
            all_scores.append(pct)
            if pct > 75:
                over_75_pct += 1
            if score > max_marks:
                errors += 1
                print(f"  ERROR: Score {score} exceeds max {max_marks} for {r['question_id']} ({model_key})")

    if all_scores:
        sorted_scores = sorted(all_scores)
        print(f"\nScore distribution (% of max):")
        print(f"  Min: {min(all_scores):.1f}%")
        print(f"  Max: {max(all_scores):.1f}%")
        print(f"  Mean: {sum(all_scores)/len(all_scores):.1f}%")
        print(f"  Median: {sorted_scores[len(sorted_scores)//2]:.1f}%")
        print(f"  >75%: {over_75_pct} ({over_75_pct/len(all_scores)*100:.1f}%)")

    missing_rubric = 0
    for model_key, results in model_results.items():
        for r in results:
            if not r.get("rubric_scores"):
                missing_rubric += 1

    if missing_rubric == 0:
        print("  All answers have rubric scores ✓")
    else:
        print(f"  WARNING: {missing_rubric} answers missing rubric scores")

    if errors == 0:
        print("  No scores exceed max marks ✓")

    return total_graded == expected and errors == 0


def main():
    print("=== Merge All Mains Results (4-model regrade + Flash solo) ===\n")

    questions_meta = load_questions()

    # Load 4-model comparative grades
    comparative_results = load_grading_results(REGRADE_DIR, "4-model comparative")
    model_results = map_comparative_grades(comparative_results, questions_meta)

    # Load Flash solo grades
    flash_results = load_grading_results(FLASH_SOLO_DIR, "Flash solo")
    flash_model_results = map_flash_solo_grades(flash_results, questions_meta)
    model_results.update(flash_model_results)

    # Validate
    valid = validate_results(model_results)

    # Compute scores
    model_scores = compute_model_mains_scores(model_results)

    # Update leaderboard
    update_leaderboard(model_scores)

    print("\n=== Done ===")
    if not valid:
        print("WARNING: Validation had issues — review output above")


if __name__ == "__main__":
    main()
