# Judge Validation for UPSC Mains Benchmark — Design Doc

**Date:** 2026-03-03
**Status:** Approved (v2 — reframed)
**Goal:** Validate that the Opus LLM-as-judge produces scores consistent with real UPSC grading standards, so we can trust its assessment of AI models — including the possibility that AI genuinely outperforms human toppers.

---

## Problem

We can't tell whether the judge is accurate. All 5 AI models score 58-72% on Mains. The human AIR 1 topper is estimated at ~48%. Two hypotheses explain this:

**H1: AI answers are genuinely better than human toppers.** Plausible. These models solve IMO problems, score 90%+ on MMLU, and have encyclopedic knowledge. A UPSC GS answer that cites specific statistics, constitutional articles, committee reports, and international comparisons — all accurately — could legitimately outperform a human writing under time pressure from memory.

**H2: The LLM judge inflates LLM-style writing.** Also plausible. LLMs produce verbose, well-formatted, comprehensive answers that look impressive to another LLM but might not impress a human examiner who values conciseness, original insight, and practical administrative wisdom over encyclopedic coverage.

**We currently cannot distinguish H1 from H2.** The coaching calibration approach doesn't assume either hypothesis — it measures the judge's accuracy on known-quality human answers to determine which is true.

## Key Principle

**We are not force-calibrating the judge to match human performance.** If the judge is accurate on coaching model answers AND gives AI models higher scores, that's a valid finding — AI genuinely outperforms humans on UPSC Mains. The calibration is about verifying the ruler, not predetermining what it should measure.

---

## Approach

Collect 15-20 model answers from UPSC coaching institutes with expected mark ranges. Grade these with the current judge. Compare. Three possible outcomes:

1. **Judge matches coaching scores:** The judge is well-calibrated. AI models really do score 58-72%. Report with confidence.
2. **Judge inflates coaching scores by X%:** The judge has a measurable bias. Apply correction factor, regrade AI answers, report adjusted scores.
3. **Judge deflates coaching scores:** The judge is actually stricter than real UPSC grading. AI scores might be even higher than reported.

Each outcome is informative. None is predetermined.

---

## Data Collection

### Sources
- **Drishti IAS** — publishes detailed GS model answers with mark expectations
- **Vision IAS** — similar coverage, known for granular marking schemes
- **ForumIAS** — community-contributed answers with faculty estimates
- **UPSC topper answer copies** — some toppers have shared scanned sheets (YouTube, blogs)

### Per-answer fields
```json
{
  "id": "cal_gs1_001",
  "source": "drishti_ias",
  "year": 2025,
  "paper": "mains_gs1",
  "question_text": "...",
  "model_answer": "...",
  "expected_score_low": 7.0,
  "expected_score_high": 8.0,
  "max_marks": 10,
  "notes": "Source URL or reference"
}
```

### Target coverage (15-20 answers)
| Paper | Count | Notes |
|-------|-------|-------|
| Essay | 2-3 | Section A and B |
| GS1 | 4-5 | History, geography, society |
| GS2 | 3-4 | Polity, governance, IR |
| GS3 | 3-4 | Economy, science, security |
| GS4 | 2-3 | Ethics, case studies |

### Preference
- Use 2025 Mains questions where possible (matches our benchmark)
- Fall back to 2024/2023 if 2025 model answers aren't available yet
- Collect from 2+ sources per question where possible and average expected marks

---

## Validation Pipeline

### Step 1: Grade coaching answers with the current judge
Run each coaching model answer through the existing judge prompt (solo grading mode). Record the judge's score per dimension and total.

### Step 2: Measure judge accuracy
Compare `judge_score` vs `coaching_expected_score` (midpoint of range):
- **Global bias:** mean(judge_score - expected_score) across all answers
- **Per-paper bias:** compute separately for essay, GS1, GS2, GS3, GS4
- **Per-dimension bias:** which rubric dimensions does the judge inflate/deflate most?
- **Correlation:** does the judge's ranking of coaching answers match the coaching institutes' ranking? (Spearman's rho)

Key metrics:
- **Mean Absolute Error (MAE):** how far off is the judge on average?
- **Directional bias:** does it systematically over- or under-score?
- **Rank correlation:** does it get the ordering right even if absolute scores are off?

### Step 3: Interpret results

**If MAE < 1 mark (10-mark questions) / < 10 marks (essays):**
Judge is well-calibrated. Current AI scores are trustworthy. No prompt changes needed. Publish with a "validated against coaching model answers" note.

**If systematic positive bias detected (judge > coaching):**
Quantify the bias. Two options:
- **Option A (preferred):** Add coaching model answer excerpts as few-shot calibration examples in the prompt. Let the judge self-correct by seeing what real scores look like. Re-run validation to confirm bias is reduced.
- **Option B:** Apply a post-hoc correction factor to the scores. Less principled but simpler.

Then regrade AI answers with the improved prompt.

**If systematic negative bias detected (judge < coaching):**
The judge is stricter than real UPSC grading. Current AI scores are conservative. Note this in the methodology and consider whether to adjust upward.

### Step 4: Validate corrections (if any)
If the prompt was adjusted, reserve 5 coaching answers as a held-out validation set. Grade with the adjusted prompt. Confirm scores fall within coaching expected ranges. Check that:
- Score differentiation between answers of different quality is preserved
- The judge doesn't collapse into a narrow scoring band

### Step 5: Regrade AI answers (only if prompt changed)
If the prompt was adjusted, regrade all 5 models' 87 Mains answers. Update the leaderboard. If the judge was already accurate, no regrade needed — just add the validation finding to the methodology.

---

## Prompt Improvements (apply regardless of calibration outcome)

These are process fixes that improve judge quality independent of score calibration:

1. **Standardize word limit penalties:** "Deduct 1% of total marks for every 10% the answer exceeds the word limit." Currently ad-hoc.
2. **Use comparative grading exclusively:** Solo grading runs 5-10% higher. Always present multiple answers side by side.
3. **Add inter-rater reliability check:** Grade 5 questions twice with different candidate orderings. Measure consistency before running the full pipeline.

---

## Edge Cases & Mitigations

| Risk | Mitigation |
|------|------------|
| 2025 coaching answers not yet available | Use 2024/2023 answers; validation is about judge accuracy, not question-specific correctness |
| Coaching "expected marks" are noisy | Collect from 2+ sources, average, treat as intervals not point estimates |
| Bias not uniform across papers | Compute per-paper metrics, report separately |
| Few-shot examples bias toward specific answer styles | Use 2-3 diverse examples (structured, flowing, case-study) |
| AI genuinely outperforms humans | This is a valid outcome, not a bug. Report it with the validation evidence. |

---

## Output Artifacts

| File | Description |
|------|-------------|
| `data/calibration/coaching_answers.json` | Golden set of coaching model answers with expected marks |
| `data/calibration/validation_report.json` | Judge accuracy metrics: MAE, bias, rank correlation |
| `config/judge_prompt_v2.txt` | Improved prompt (only if corrections needed) |
| `results/regrade_v2/` | New grading outputs (only if prompt changed) |
| `results/leaderboard.json` | Updated (only if scores changed) |

---

## Future: Human Rater Protocol (not in scope now)

For a future phase with $500-2000 budget:
- Hire 2-3 retired UPSC examiners or senior coaching faculty via Mercor
- Have them grade a mix of AI + human answers (blinded) on the actual UPSC rubric
- Key question: do human examiners also score AI answers higher than human answers?
- Use pairwise ranking ("A is better than B") for higher inter-rater reliability
- This would be the definitive test of H1 vs H2

---

## Success Criteria

1. **Judge accuracy measured:** MAE, directional bias, and rank correlation computed across 15-20 coaching model answers
2. **Bias direction determined:** we know whether the judge inflates, deflates, or is accurate
3. **If bias exists, it's corrected:** prompt adjustments reduce MAE by >50%
4. **AI scores are reported with confidence context:** methodology page explains the validation approach and what the coaching calibration shows
5. **Relative rankings between models are stable:** if rankings change after correction, the change is investigated and explained
