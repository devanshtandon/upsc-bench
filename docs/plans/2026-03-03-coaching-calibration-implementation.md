# Judge Validation via Coaching Calibration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Validate the Opus LLM-as-judge by grading coaching institute model answers and measuring accuracy against their expected marks.

**Architecture:** Scrape InsightsIAS model answer synopses for 2025 Mains, structure them into a calibration dataset, grade them with the current judge, compute accuracy metrics (MAE, bias, rank correlation), and determine whether the judge needs correction.

**Tech Stack:** Python 3, requests/WebFetch for scraping, JSON for data, existing judge infrastructure (config/judge_prompt.txt, benchmark/mains_scorer.py)

---

### Task 1: Create calibration data directory and schema

**Files:**
- Create: `data/calibration/README.md`
- Create: `data/calibration/coaching_answers.json` (empty array initially)

**Step 1: Create directory**

```bash
mkdir -p data/calibration
```

**Step 2: Create empty coaching_answers.json with schema comment**

```json
[]
```

**Step 3: Commit**

```bash
git add data/calibration/
git commit -m "feat: add calibration data directory for judge validation"
```

---

### Task 2: Scrape InsightsIAS GS1 model answers

**Files:**
- Create: `scripts/scrape_coaching_answers.py`

**Step 1: Write scraper script**

Fetch InsightsIAS 2025 Mains GS Paper 1 synopsis page. Extract question text and key answer points for each of the 20 questions. Structure into the calibration schema.

Source URL: `https://www.insightsonindia.com/2025/09/01/upsc-mains-2025-general-studies-gs-paper-1-complete-question-wise-analysis-and-synopsis/`

The script should:
1. Fetch each GS paper page (GS1, GS2, GS3, GS4)
2. Parse the HTML to extract per-question model answer content
3. For each question, capture: question text, model answer text (the synopsis/key points), max_marks (10 or 15 based on question number)
4. Assign expected score ranges: coaching model answers are "ideal" answers, so expected score = 70-80% of max marks (these are what a well-prepared candidate should aim for, not perfect answers)
5. Write to `data/calibration/coaching_answers.json`

```python
#!/usr/bin/env python3
"""Scrape InsightsIAS model answers for UPSC Mains 2025 calibration."""
import json
import re
import sys
from pathlib import Path

# URLs will be fetched manually via WebFetch due to scraping limitations
# This script structures the raw scraped content into calibration format

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
        "questions": 19,  # GS4 has paired sub-questions
    },
}


def get_marks(paper, question_number):
    """Determine max marks based on paper and question number."""
    if paper == "mains_gs4":
        # GS4: Q1-6 are 10-mark (paired a/b), Q7-12 are 20-mark case studies
        if question_number <= 6:
            return 10
        else:
            return 20
    else:
        # GS1-3: Q1-10 are 10 marks, Q11-20 are 15 marks
        if question_number <= 10:
            return 10
        else:
            return 15


def expected_score_range(max_marks):
    """Coaching model answers represent 'ideal' preparation.

    These are what a well-prepared candidate writes — not perfect,
    but comprehensive. Expected score: 65-75% of max marks.
    A real UPSC examiner would give a good model answer this range.
    """
    low = round(max_marks * 0.65, 1)
    high = round(max_marks * 0.75, 1)
    return low, high


def main():
    """Main entry point — processes raw scraped content files."""
    raw_dir = Path("data/calibration/raw")
    if not raw_dir.exists():
        print(f"Create {raw_dir}/ and add scraped content files first.")
        print("Files should be named: gs1_raw.txt, gs2_raw.txt, etc.")
        print("Content: question text followed by model answer for each question.")
        sys.exit(1)

    calibration_data = []

    for paper_key, paper_info in PAPERS.items():
        raw_file = raw_dir / f"{paper_key.replace('mains_', '')}_raw.json"
        if not raw_file.exists():
            print(f"Skipping {paper_key}: {raw_file} not found")
            continue

        with open(raw_file) as f:
            questions = json.load(f)

        for q in questions:
            qnum = q["question_number"]
            max_marks = get_marks(paper_key, qnum)
            low, high = expected_score_range(max_marks)

            entry = {
                "id": f"cal_{paper_key.replace('mains_', '')}_{qnum:03d}",
                "source": "insightsonindia",
                "year": 2025,
                "paper": paper_key,
                "question_number": qnum,
                "question_text": q["question_text"],
                "model_answer": q["model_answer"],
                "expected_score_low": low,
                "expected_score_high": high,
                "max_marks": max_marks,
                "word_limit": 150 if max_marks == 10 else 250,
                "notes": paper_info["url"],
            }
            calibration_data.append(entry)

    with open(CALIBRATION_FILE, "w") as f:
        json.dump(calibration_data, f, indent=2, ensure_ascii=False)

    print(f"Written {len(calibration_data)} calibration answers to {CALIBRATION_FILE}")


if __name__ == "__main__":
    main()
```

**Step 2: Commit script**

```bash
git add scripts/scrape_coaching_answers.py
git commit -m "feat: add coaching answer scraper for judge calibration"
```

---

### Task 3: Collect coaching model answers from InsightsIAS

**Files:**
- Create: `data/calibration/raw/gs1_raw.json`
- Create: `data/calibration/raw/gs2_raw.json`
- Create: `data/calibration/raw/gs3_raw.json`
- Create: `data/calibration/raw/gs4_raw.json`

**Step 1: Fetch each InsightsIAS page via WebFetch**

For each of the 4 GS papers, fetch the InsightsIAS synopsis page. Extract question text and model answer content. Save as structured JSON in `data/calibration/raw/`.

Each raw file should be a JSON array:
```json
[
  {
    "question_number": 1,
    "question_text": "Discuss the salient features of the Harappan architecture.",
    "model_answer": "The Harappan civilization (c. 2600-1900 BCE) is notable for... [full synopsis content]"
  },
  ...
]
```

Target: collect 5 questions per paper = 20 total calibration answers (mix of 10-mark and 15-mark). Prioritize questions that overlap with our existing benchmark questions in `data/mains_questions/mains_2025.json`.

**Step 2: Run the structuring script**

```bash
python scripts/scrape_coaching_answers.py
```

Expected: `data/calibration/coaching_answers.json` populated with 20 entries.

**Step 3: Spot-check the data**

Verify 3-4 entries manually: question text matches, model answer is substantive (not just headers), marks are correct.

**Step 4: Commit**

```bash
git add data/calibration/
git commit -m "feat: collect 20 coaching model answers from InsightsIAS for calibration"
```

---

### Task 4: Build calibration grading script

**Files:**
- Create: `scripts/grade_calibration.py`

**Step 1: Write the grading script**

This script reads `data/calibration/coaching_answers.json`, grades each coaching model answer with the current judge prompt (solo mode), and writes results to `data/calibration/grading_results.json`.

```python
#!/usr/bin/env python3
"""Grade coaching model answers with the current judge for calibration.

Reads coaching_answers.json, formats each answer with the judge prompt,
and writes grading output. Designed for in-session subagent grading
(the actual grading is done by Claude subagents, not API calls).

This script prepares the grading input batches.

Usage:
    python scripts/grade_calibration.py prepare   # Create grading input batches
    python scripts/grade_calibration.py merge      # Merge grading output into report
"""
import json
import sys
from pathlib import Path

import yaml

CALIBRATION_FILE = Path("data/calibration/coaching_answers.json")
RUBRIC_FILE = Path("config/judge.yaml")
GRADING_DIR = Path("data/calibration/grading")
RESULTS_FILE = Path("data/calibration/grading_results.json")

BATCH_SIZE = 5  # 5 questions per grading batch


def format_rubric(rubric_type, rubric_config):
    """Format rubric dimensions for the prompt."""
    key = "essay" if "essay" in rubric_type.lower() else "gs"
    rubric = rubric_config["rubric"][key]
    lines = []
    for dim_key, dim_info in rubric.items():
        lines.append(f"  {dim_key}: {dim_info['weight']}% — {dim_info['description']}")
    return "\n".join(lines)


def prepare():
    """Create grading input batches from coaching answers."""
    with open(CALIBRATION_FILE) as f:
        answers = json.load(f)

    with open(RUBRIC_FILE) as f:
        rubric_config = yaml.safe_load(f)

    GRADING_DIR.mkdir(parents=True, exist_ok=True)

    # Add rubric text to each answer
    for a in answers:
        rubric_type = "Essay Paper" if a["paper"] == "mains_essay" else "GS Paper"
        a["rubric_type"] = rubric_type
        a["rubric_text"] = format_rubric(rubric_type, rubric_config)

    # Batch them
    batches = []
    for i in range(0, len(answers), BATCH_SIZE):
        batches.append(answers[i:i + BATCH_SIZE])

    for idx, batch in enumerate(batches, 1):
        output_file = GRADING_DIR / f"cal_input_batch_{idx:03d}.json"
        with open(output_file, "w") as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)
        print(f"Batch {idx:03d}: {len(batch)} questions")

    print(f"\nTotal: {len(batches)} batches, {len(answers)} questions")
    print(f"Output: {GRADING_DIR}/")


def merge():
    """Merge grading outputs into a single results file with calibration comparison."""
    with open(CALIBRATION_FILE) as f:
        answers = {a["id"]: a for a in json.load(f)}

    results = []
    batch_files = sorted(GRADING_DIR.glob("cal_grading_batch_*.json"))

    if not batch_files:
        print("ERROR: No grading output files found. Run subagent grading first.")
        sys.exit(1)

    for batch_file in batch_files:
        with open(batch_file) as f:
            batch_data = json.load(f)
        for q in batch_data:
            qid = q["question_id"]
            # Find matching calibration answer
            cal_id = None
            for aid, a in answers.items():
                if (a["paper"] == q.get("paper") or
                    aid.endswith(f"_{q.get('question_number', 0):03d}")):
                    if a["question_number"] == q.get("question_number"):
                        cal_id = aid
                        break

            candidate = q["candidates"][0] if q.get("candidates") else {}
            judge_score = candidate.get("total_score", 0)
            max_marks = candidate.get("max_marks", 0)

            cal_answer = answers.get(cal_id, {})
            expected_low = cal_answer.get("expected_score_low", 0)
            expected_high = cal_answer.get("expected_score_high", 0)
            expected_mid = (expected_low + expected_high) / 2

            results.append({
                "calibration_id": cal_id,
                "question_id": qid,
                "paper": cal_answer.get("paper", "unknown"),
                "question_number": cal_answer.get("question_number"),
                "max_marks": max_marks,
                "judge_score": judge_score,
                "judge_pct": round(judge_score / max_marks * 100, 1) if max_marks > 0 else 0,
                "expected_low": expected_low,
                "expected_high": expected_high,
                "expected_mid": expected_mid,
                "expected_pct": round(expected_mid / max_marks * 100, 1) if max_marks > 0 else 0,
                "offset": round(judge_score - expected_mid, 2),
                "within_range": expected_low <= judge_score <= expected_high,
                "rubric_scores": candidate.get("rubric_scores", {}),
                "summary": candidate.get("summary", ""),
                "brief_feedback": candidate.get("brief_feedback", ""),
            })

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Merged {len(results)} grading results to {RESULTS_FILE}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("prepare", "merge"):
        print("Usage: python scripts/grade_calibration.py [prepare|merge]")
        sys.exit(1)

    if sys.argv[1] == "prepare":
        prepare()
    else:
        merge()
```

**Step 2: Commit**

```bash
git add scripts/grade_calibration.py
git commit -m "feat: add calibration grading script (prepare + merge modes)"
```

---

### Task 5: Grade coaching answers with Opus subagents

**Files:**
- Read: `data/calibration/grading/cal_input_batch_*.json`
- Create: `data/calibration/grading/cal_grading_batch_*.json`

**Step 1: Run prepare mode**

```bash
python scripts/grade_calibration.py prepare
```

Expected: 4 input batch files in `data/calibration/grading/`.

**Step 2: Launch Opus subagents**

Launch one Opus subagent per batch. Each subagent reads its input batch, grades each coaching model answer using the calibrated judge prompt (same prompt as used for AI answers), and writes the grading output.

Use the same grading prompt and rubric as the current judge. The key is to grade these coaching answers *identically* to how we graded AI answers — solo mode, same score anchors, same rubric dimensions.

**Step 3: Verify all batches completed**

```bash
ls data/calibration/grading/cal_grading_batch_*.json | wc -l
```

Expected: same count as input batches.

**Step 4: Run merge mode**

```bash
python scripts/grade_calibration.py merge
```

Expected: `data/calibration/grading_results.json` with per-question comparison.

**Step 5: Commit**

```bash
git add data/calibration/
git commit -m "feat: grade coaching model answers for judge calibration"
```

---

### Task 6: Compute validation metrics

**Files:**
- Create: `scripts/compute_calibration_metrics.py`
- Create: `data/calibration/validation_report.json`

**Step 1: Write metrics computation script**

```python
#!/usr/bin/env python3
"""Compute judge validation metrics from calibration grading results.

Reads grading_results.json and computes:
- MAE (Mean Absolute Error) — global and per-paper
- Directional bias — does judge systematically over/under-score?
- Score correlation — Spearman rank correlation
- Per-dimension analysis
- Recommendation: calibrated / needs adjustment / needs investigation

Usage:
    python scripts/compute_calibration_metrics.py
"""
import json
import statistics
from pathlib import Path

RESULTS_FILE = Path("data/calibration/grading_results.json")
REPORT_FILE = Path("data/calibration/validation_report.json")


def compute_metrics(results):
    """Compute calibration metrics."""
    offsets = [r["offset"] for r in results]
    pct_offsets = [r["judge_pct"] - r["expected_pct"] for r in results]
    within_range_count = sum(1 for r in results if r["within_range"])

    # Global metrics
    mae = statistics.mean(abs(o) for o in offsets)
    mean_offset = statistics.mean(offsets)
    median_offset = statistics.median(offsets)
    std_offset = statistics.stdev(offsets) if len(offsets) > 1 else 0

    mae_pct = statistics.mean(abs(o) for o in pct_offsets)
    mean_offset_pct = statistics.mean(pct_offsets)

    # Per-paper metrics
    papers = set(r["paper"] for r in results)
    per_paper = {}
    for paper in papers:
        paper_results = [r for r in results if r["paper"] == paper]
        paper_offsets = [r["offset"] for r in paper_results]
        paper_pct_offsets = [r["judge_pct"] - r["expected_pct"] for r in paper_results]
        per_paper[paper] = {
            "count": len(paper_results),
            "mae": round(statistics.mean(abs(o) for o in paper_offsets), 2),
            "mean_offset": round(statistics.mean(paper_offsets), 2),
            "mean_offset_pct": round(statistics.mean(paper_pct_offsets), 1),
            "within_range_pct": round(
                sum(1 for r in paper_results if r["within_range"]) / len(paper_results) * 100, 1
            ),
        }

    # Determine recommendation
    if mae_pct < 5:
        recommendation = "WELL_CALIBRATED"
        recommendation_detail = (
            "Judge scores are within 5 percentage points of coaching expectations. "
            "Current AI model scores can be reported with confidence."
        )
    elif mean_offset_pct > 5:
        recommendation = "POSITIVE_BIAS"
        recommendation_detail = (
            f"Judge inflates scores by ~{mean_offset_pct:.1f} percentage points on average. "
            "Consider adding few-shot calibration examples to the prompt and regrading."
        )
    elif mean_offset_pct < -5:
        recommendation = "NEGATIVE_BIAS"
        recommendation_detail = (
            f"Judge deflates scores by ~{abs(mean_offset_pct):.1f} percentage points. "
            "Current AI scores may be conservative. Consider noting this in methodology."
        )
    else:
        recommendation = "MARGINAL"
        recommendation_detail = (
            "Judge bias is small but measurable. Current scores are approximately correct. "
            "Consider minor prompt adjustments."
        )

    report = {
        "summary": {
            "total_answers_graded": len(results),
            "within_expected_range": within_range_count,
            "within_expected_range_pct": round(within_range_count / len(results) * 100, 1),
        },
        "global_metrics": {
            "mae_marks": round(mae, 2),
            "mae_pct": round(mae_pct, 1),
            "mean_offset_marks": round(mean_offset, 2),
            "mean_offset_pct": round(mean_offset_pct, 1),
            "median_offset_marks": round(median_offset, 2),
            "std_offset_marks": round(std_offset, 2),
            "interpretation": (
                "Positive offset = judge scores higher than coaching expectation. "
                "Negative offset = judge scores lower."
            ),
        },
        "per_paper": per_paper,
        "recommendation": recommendation,
        "recommendation_detail": recommendation_detail,
        "per_question_results": [
            {
                "id": r["calibration_id"],
                "paper": r["paper"],
                "q_num": r["question_number"],
                "max": r["max_marks"],
                "judge": r["judge_score"],
                "expected_mid": r["expected_mid"],
                "offset": r["offset"],
                "within_range": r["within_range"],
            }
            for r in results
        ],
    }

    return report


def print_report(report):
    """Print human-readable report."""
    s = report["summary"]
    g = report["global_metrics"]

    print("=" * 60)
    print("JUDGE VALIDATION REPORT")
    print("=" * 60)
    print(f"\nAnswers graded: {s['total_answers_graded']}")
    print(f"Within expected range: {s['within_expected_range']}/{s['total_answers_graded']} ({s['within_expected_range_pct']}%)")
    print(f"\nMean Absolute Error: {g['mae_marks']} marks ({g['mae_pct']}%)")
    print(f"Mean offset: {g['mean_offset_marks']:+.2f} marks ({g['mean_offset_pct']:+.1f}%)")
    print(f"Median offset: {g['median_offset_marks']:+.2f} marks")
    print(f"Std dev: {g['std_offset_marks']:.2f} marks")

    print(f"\nPer-paper breakdown:")
    for paper, metrics in report["per_paper"].items():
        print(f"  {paper}: MAE={metrics['mae']}, bias={metrics['mean_offset_pct']:+.1f}%, "
              f"in-range={metrics['within_range_pct']}% (n={metrics['count']})")

    print(f"\nRECOMMENDATION: {report['recommendation']}")
    print(f"  {report['recommendation_detail']}")

    print(f"\nPer-question detail:")
    for r in report["per_question_results"]:
        marker = "✓" if r["within_range"] else "✗"
        print(f"  {marker} {r['id']}: judge={r['judge']}/{r['max']} "
              f"expected={r['expected_mid']}/{r['max']} offset={r['offset']:+.1f}")


def main():
    with open(RESULTS_FILE) as f:
        results = json.load(f)

    report = compute_metrics(results)
    print_report(report)

    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()
```

**Step 2: Run the metrics script**

```bash
python scripts/compute_calibration_metrics.py
```

Expected output: MAE, directional bias, per-paper breakdown, and a recommendation (WELL_CALIBRATED, POSITIVE_BIAS, NEGATIVE_BIAS, or MARGINAL).

**Step 3: Commit**

```bash
git add scripts/compute_calibration_metrics.py data/calibration/validation_report.json
git commit -m "feat: compute judge validation metrics from coaching calibration"
```

---

### Task 7: Act on calibration results

This task depends on the output of Task 6. Three paths:

**Path A — WELL_CALIBRATED (MAE < 5%):**
No prompt changes needed. Add a "Judge Validation" section to the methodology page citing the calibration results. Commit and done.

**Path B — POSITIVE_BIAS (judge inflates by >5%):**
1. Create `config/judge_prompt_v2.txt` with few-shot calibration examples from coaching answers
2. Re-run Task 5 with the new prompt on 5 held-out coaching answers to validate
3. If MAE improves, regrade all 5 models' 87 Mains answers with the new prompt
4. Update leaderboard

**Path C — NEGATIVE_BIAS (judge deflates by >5%):**
Note in methodology that scores are conservative. No prompt changes needed unless the bias is extreme (>10%).

**Step 1: Read the validation report**

```bash
cat data/calibration/validation_report.json | python -m json.tool | head -30
```

**Step 2: Follow the appropriate path above**

**Step 3: Commit final results**

```bash
git add -A
git commit -m "feat: apply calibration findings to judge [PATH_TAKEN]"
```

---

### Task 8: Update methodology page

**Files:**
- Modify: `web/src/app/about/page.tsx`

**Step 1: Add a "Judge Validation" section**

Add a section to the About/Methodology page explaining:
- How the judge was validated (coaching model answers from InsightsIAS)
- Key metrics (MAE, bias direction)
- What this means for the benchmark's credibility
- Link to the full validation report

**Step 2: Build and verify**

```bash
cd web && npm run build
```

**Step 3: Commit**

```bash
git add web/src/app/about/page.tsx
git commit -m "docs: add judge validation methodology to about page"
```
