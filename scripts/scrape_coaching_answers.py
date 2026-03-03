#!/usr/bin/env python3
"""Structure coaching model answers for UPSC Mains 2025 calibration.

Reads raw scraped content from data/calibration/raw/ and structures it
into the calibration dataset format at data/calibration/coaching_answers.json.

Sources: InsightsIAS 2025 Mains question-wise synopses.

Usage:
    python scripts/scrape_coaching_answers.py
"""
import json
import re
import sys
from pathlib import Path

CALIBRATION_FILE = Path("data/calibration/coaching_answers.json")

PAPERS = {
    "mains_gs1": {
        "url": "https://www.insightsonindia.com/2025/09/01/upsc-mains-2025-general-studies-gs-paper-1-complete-question-wise-analysis-and-synopsis/",
        "questions": 20,
    },
    "mains_gs2": {
        "url": "https://www.insightsonindia.com/2025/09/01/upsc-mains-2025-general-studies-gs-paper-2-complete-question-wise-analysis-and-synopsis/",
        "questions": 20,
    },
    "mains_gs3": {
        "url": "https://www.insightsonindia.com/2025/09/03/upsc-mains-2025-general-studies-gs-paper-3-complete-question-wise-synopsis-and-analysis/",
        "questions": 20,
    },
    "mains_gs4": {
        "url": "https://www.insightsonindia.com/2025/09/03/upsc-mains-2025-general-studies-gs-paper-4-complete-question-wise-synopsis-and-analysis/",
        "questions": 19,
    },
}


def get_marks(paper, question_number):
    """Determine max marks based on paper and question number.

    question_number can be int (1-20) or str ("1a", "1b", "7", etc.)
    """
    # Extract the numeric part of question_number
    qnum_str = str(question_number)
    numeric_part = int("".join(c for c in qnum_str if c.isdigit()))

    if paper == "mains_gs4":
        # GS4: Q1a-Q6b are 10-mark each, Q7-Q12 are 20-mark case studies
        if numeric_part <= 6:
            return 10
        else:
            return 20
    else:
        # GS1-3: Q1-10 are 10 marks, Q11-20 are 15 marks
        if numeric_part <= 10:
            return 10
        else:
            return 15


def expected_score_range(max_marks):
    """Coaching model answers represent 'ideal' preparation.

    These are what a well-prepared candidate writes — not perfect,
    but comprehensive. Expected score: 65-75% of max marks.
    A real UPSC examiner would give a good coaching model answer this range.
    """
    low = round(max_marks * 0.65, 1)
    high = round(max_marks * 0.75, 1)
    return low, high


def main():
    """Process raw scraped content files into calibration dataset."""
    raw_dir = Path("data/calibration/raw")
    if not raw_dir.exists():
        print(f"Create {raw_dir}/ and add scraped content files first.")
        print("Files should be named: gs1_raw.json, gs2_raw.json, etc.")
        sys.exit(1)

    calibration_data = []

    for paper_key, paper_info in PAPERS.items():
        short_key = paper_key.replace("mains_", "")
        raw_file = raw_dir / f"{short_key}_raw.json"
        if not raw_file.exists():
            print(f"Skipping {paper_key}: {raw_file} not found")
            continue

        with open(raw_file) as f:
            questions = json.load(f)

        print(f"Processing {paper_key}: {len(questions)} questions from {raw_file}")

        for q in questions:
            qnum = q["question_number"]
            max_marks = get_marks(paper_key, qnum)
            low, high = expected_score_range(max_marks)

            # Handle string question numbers (e.g. "1a", "1b" for GS4)
            qnum_str = str(qnum)
            qnum_id = qnum_str.replace(" ", "").lower()

            # Clean question text — remove leading "Q1.(a)" style prefixes
            question_text = q["question_text"]
            question_text = re.sub(r'^Q\d+\.?\s*(\([a-z]\))?\s*', '', question_text).strip()

            entry = {
                "id": f"cal_{short_key}_{qnum_id}",
                "source": "insightsonindia",
                "year": 2025,
                "paper": paper_key,
                "question_number": qnum,
                "question_text": question_text,
                "model_answer": q["model_answer"],
                "expected_score_low": low,
                "expected_score_high": high,
                "max_marks": max_marks,
                "word_limit": 150 if max_marks == 10 else 250,
                "notes": paper_info["url"],
            }
            calibration_data.append(entry)

    CALIBRATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(calibration_data, f, indent=2, ensure_ascii=False)

    print(f"\nWritten {len(calibration_data)} calibration answers to {CALIBRATION_FILE}")


if __name__ == "__main__":
    main()
