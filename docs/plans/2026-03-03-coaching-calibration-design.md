# Coaching Calibration for LLM-as-Judge — Design Doc

**Date:** 2026-03-03
**Status:** Approved
**Goal:** Calibrate the Opus judge's Mains scoring against coaching institute model answers to produce credible, externally-anchored scores.

---

## Problem

All 5 AI models score 58-72% on Mains, while the human AIR 1 topper (Shakti Dubey, CSE 2024) is estimated at ~48%. The judge's own prompt says >75% is "almost never awarded" and 55-65% is "top-100 level," yet GPT-5.2 scores 71.8% overall and 74.4% on essays. Scores are inflated by an estimated 15-20% relative to real UPSC grading.

Without an external anchor, the benchmark's headline claim — "AI models pass UPSC Mains" — is unverifiable.

## Approach

Collect 15-20 model answers from UPSC coaching institutes (Drishti IAS, Vision IAS, ForumIAS) that come with expected mark ranges. Run these through the current judge. Compute the calibration offset. Adjust the prompt and regrade.

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

## Calibration Pipeline

### Step 1: Grade coaching answers with current judge
Run each coaching model answer through the existing judge prompt (solo grading mode). Record the judge's score.

### Step 2: Compute calibration offset
Compare `judge_score` vs `coaching_expected_score` (midpoint of range):
- **Global offset:** mean(judge_score - expected_score) across all answers
- **Per-paper offset:** compute separately for essay, GS1, GS2, GS3, GS4
- **Per-dimension offset:** content_accuracy, analytical_depth, etc.

If per-paper sample size < 3, fall back to global offset.

### Step 3: Adjust the prompt
Two mechanisms applied together:

**A. Shift score anchors** by the computed offset. Example if global offset = +12%:
```
Current:                          Adjusted:
<30%  = Irrelevant               <25%  = Irrelevant
30-45% = Basic                   25-35% = Basic
45-55% = Adequate (median)  -->  33-43% = Adequate (median)
55-65% = Strong (top-100)        43-53% = Strong (top-100)
65-75% = Excellent (rare)        53-63% = Excellent (rare)
>75%  = Near-perfect             >63%  = Near-perfect
```

**B. Add 2-3 calibration examples** in the prompt:
- Include short excerpts (150-200 words) of coaching model answers with their expected marks
- Use diverse styles (structured list, flowing prose, case-study format) to avoid style bias

**C. Enforce dimension-level caps** (not just total):
- No individual dimension score should exceed 70% of its maximum allocation

**D. Standardize word limit penalties:**
- Deduct 1% of total marks for every 10% the answer exceeds the word limit

### Step 4: Validate on held-out subset
Reserve 5 coaching answers for validation (don't use them in prompt examples). Grade with the adjusted prompt. Check scores fall within coaching expected ranges. Iterate if needed.

### Step 5: Regrade AI answers
Once calibrated, regrade all 5 models' 87 Mains answers with the new prompt. Update leaderboard.

---

## Edge Cases & Mitigations

| Risk | Mitigation |
|------|------------|
| 2025 coaching answers not yet available | Use 2024/2023 answers; calibration is about score distribution, not question-specific correctness |
| Coaching "expected marks" are noisy | Collect from 2+ sources, average, treat as intervals |
| Offset not uniform across papers | Compute per-paper offsets, apply independently |
| Over-correction compresses AI score range | Validation step (Step 4) catches this before full regrade |
| Few-shot examples bias toward specific answer styles | Use 2-3 diverse examples (structured, flowing, case-study) |

---

## Output Artifacts

| File | Description |
|------|-------------|
| `data/calibration/coaching_answers.json` | Golden set of coaching model answers with expected marks |
| `data/calibration/calibration_report.json` | Offset analysis: global, per-paper, per-dimension |
| `config/judge_prompt_v2.txt` | Recalibrated prompt with shifted anchors + examples |
| `results/regrade_v2/` | New grading outputs |
| `results/leaderboard.json` | Updated with calibrated scores |

---

## Future: Human Rater Protocol (not in scope now)

For a future phase with $500-2000 budget:
- Hire 2-3 retired UPSC examiners or senior coaching faculty via Mercor
- Have them grade 20-30 AI answers on the actual rubric
- Use pairwise ranking ("A is better than B") rather than absolute scoring for higher inter-rater reliability
- Compute Elo/Bradley-Terry rankings from pairwise preferences
- Use human scores as gold-standard anchors, replacing coaching estimates

---

## Success Criteria

1. Judge scores on coaching model answers fall within the coaching expected mark range (within 1 mark for 10-mark questions, 2 marks for 15-mark questions, 15 marks for essays)
2. AI model scores shift to a plausible range relative to the human AIR 1 baseline (~48%)
3. Relative rankings between models are preserved (if the ordering changes, investigate why)
4. Score differentiation between models is maintained (spread > 5% between best and worst)
