# UPSC Bench — Project State & Instructions

## RESUME HERE — Immediate Next Action
**Expand coverage and improve grading.**

Deployed at upsc-bench.com. Prelims + Mains complete for 6 AI models + 10 human references (CSE 2024 top 10). Arena feature live — blind side-by-side essay comparison at /arena. Judge calibration validates grading accuracy (-8.8% conservative bias vs coaching benchmarks). Frontend is live with Prelims/Mains toggle, interactive quiz, arena, methodology page with judge validation section.

177 Prelims questions (100 GS1 + 77 CSAT, 2025 only). Answer key validated: 6 coaching key errors corrected, 3 corrupted CSAT passages dropped, 2 disputed questions marked. Answer-first prompting eliminates truncation-caused unanswered results.

Steps to resume:
1. Evaluate more models (Claude Sonnet, DeepSeek R1)
2. Add Prelims years 2020-2023 (PDFs downloaded for some, not parsed)
3. Write proper README for open source release (draft complete, finalize after deploy)
4. **Re-run Mains grading with all 6 models in one comparative batch** — GPT-5.4 and Gemini 3 Flash were solo-graded (inflated by ~1.34x vs comparative). Defer until next data quality round.
5. **When CSE 2025 results are released:** Add 2025 top 10 as primary human reference, keep only AIR 1 from 2024. Switch human color to Faded Lavender (#9A8CB8) to differentiate the newer cohort.
6. **Fix CSAT passage parsing**: Q004, Q023, Q044 have wrong passages (inherited from previous passage group). Recover correct passages from CSAT 2025 PDF to restore these 3 questions.

---

## Project Overview
UPSC Bench is an LLM evaluation benchmark based on India's UPSC Civil Services Examination — both the Preliminary (objective MCQ) and Mains (subjective essay/long-form) stages. It evaluates whether frontier AI models can pass the same exam that millions of Indian aspirants prepare years for. The project has a Python backend (data pipeline + evaluation harness) and a Next.js frontend (leaderboard website).

## Current Status: Phase 6 — Deployment & Expansion

### What's DONE:
1. **Project structure** — All directories, pyproject.toml, .gitignore, .env.example, README.md
2. **Python pipeline scripts** — All 5 files in `pipeline/`
3. **Evaluation harness** — All 5 files in `benchmark/` (grader, scorer, solver, db, runner)
4. **Model configs** — `config/`: claude_opus, gpt5, gemini_3_pro, gemini_flash + cutoffs.yaml
5. **Answer keys (JSON)** — 2024 and 2025, both GS1 and CSAT
   - `data/answer_keys/gs1_2024.json` — 100 questions, Set A
   - `data/answer_keys/csat_2024.json` — 80 questions, Set A
   - `data/answer_keys/gs1_2025.json` — 100 questions
   - `data/answer_keys/csat_2025.json` — 80 questions
6. **Parsed questions** — `data/processed/upsc_bench.json` — 177 questions (100 GS1, 77 CSAT, 2025 only)
   - GS1 2025 data cleaned: fixed word-per-line formatting, III→Ill/m corruption, garbage text, OCR artifacts (90/100 questions affected)
7. **Benchmark results** — 6 models evaluated: GPT-5.2, GPT-5.4, Gemini 3.1 Pro, Claude Opus 4.6, Gemini 2.5 Flash, Gemini 3 Flash
   - GS1 2025 re-run on cleaned data: all models improved (+3 to +19 marks)
   - Grader bug fixed: Claude Opus recovered +59 marks from markdown-bold answer extraction bug
   - Claude Opus: rank #4 Prelims (87.57% accuracy, GS1 173.33)
8. **Real leaderboard data** — `results/leaderboard.json` and `web/data/leaderboard.json` with actual scores, estimated AIR, pass/fail
9. **Next.js frontend** — Fully built, `npm run build` passes cleanly
   - Leaderboard with score bars, breakdown grid, estimated AIR, cutoff rows
   - Year selector (2024, 2025), paper tabs (Prelims Score, GS1, CSAT)
   - Methodology page with "Why This Matters" section and cultural links
   - "UPSC Bench" intro with 3 paragraphs on exam context
   - Indian government aesthetic: saffron/navy/green/cream/gold
10. **Interactive quiz** — 5-question GS1 2025 quiz with instant feedback, extrapolated score, and AI model comparison
11. **Git** — Clean `main` branch, GitHub remote configured
12. **Prelims ranking fix** — Renamed "Overall" → "Prelims Score", rank by GS1 marks with CSAT as pass/fail qualifier, CSAT badge under score, fixed cutoff row
13. **Mains pipeline** — `benchmark/mains_solver.py`, `mains_scorer.py`, `mains_runner.py`, DB schema, grading infrastructure, model configs
14. **Mains question data** — `data/mains_questions/mains_2025.json` — 2025 Mains questions (Essay + GS1-4)
15. **Mains benchmark run** — All 5 models answered 87 Mains questions, graded by calibrated Claude Opus judge
16. **Mains leaderboard** — GPT-5.4 #1 (942.70/1250), GPT-5.2 #2 (897.25), Gemini 3.1 Pro #3, Claude Opus #4, Gemini 3 Flash #5, Gemini 2.5 Flash #6
17. **Human reference** — Shakti Dubey (CSE 2024 AIR 1) added as Mains baseline (602.14/1250 estimated)
18. **Frontend Mains view** — ExamToggle (Prelims/Mains), MainsLeaderboard.tsx, Mains tabs (Total, Essay, GS1-4), paper breakdown
19. **Mobile-responsive redesign** — Card layout for mobile, responsive leaderboard
20. **Documentation update** — README rewrite, About/Methodology page with Mains methodology + FAQ
21. **Judge calibration** — 78 coaching institute model answers (InsightsIAS) graded by same Opus judge; validated -8.8% conservative bias, 9.8% MAE; methodology page updated with validation results
22. **Deployed** — Live on Vercel at upsc-bench.com
23. **Arena feature** — Blind side-by-side essay comparison at /arena; 8 essay topics × 5 models; LMSys Arena-style voting with reveal; mobile-responsive with tab layout; Python build script + static JSON data pipeline
24. **Codebase simplification** — Deleted 12 obsolete scripts (~2,300 lines), untracked 142 intermediate files, consolidated 12 model configs into single registry, extracted shared utilities (Python `common.py` + TS `utils.ts`), fixed 3 bugs, removed dead frontend code
25. **Answer key audit + truncation fix** — Fixed 6 wrong GS1 answers (coaching key errors verified by 6/6 model consensus + independent research), dropped 3 corrupted CSAT questions (passage-question mismatches from PDF parsing), added answer-first prompting to eliminate truncation, bumped max_tokens to 8192, re-ran all 6 models (177 questions each)

### What's NOT DONE:
1. ~~Add GitHub remote and push~~ (done)
2. ~~Run Mains benchmark (all 5 models answer Mains 2025 questions)~~ (done)
3. ~~Grade Mains answers via calibrated Opus judge~~ (done)
4. ~~Generate Mains leaderboard results~~ (done)
5. ~~Frontend: ExamToggle (Prelims/Mains), Mains tabs, rubric breakdown~~ (done)
6. ~~Update About/Methodology page with Mains methodology~~ (done)
7. Evaluate more models (Claude Sonnet, DeepSeek R1)
8. Add Prelims years 2020-2023 (PDFs downloaded for some, not parsed)
9. ~~Deploy frontend (Vercel)~~ (done — upsc-bench.com)
10. ~~Write proper README for open source release~~ (draft done)
11. ~~Judge calibration with coaching institute answers~~ (done)

## Git History
```
cf279ba fix: restore mains data lost during Session 15 leaderboard regeneration
528f4ae fix: answer key audit + truncation fix — re-run all 6 models
ed817c7 data: re-run all 6 models after pipeline audit fixes
aa21baa fix: pipeline audit — grader, scoring, retry, overwrite protection
20d5121 fix: add CSAT passage prompts, bump max_tokens, re-parse 2025 dataset
96e366a fix: grader markdown-bold bug, drop 2024 data, recover CSAT 2025
aa96850 feat: add Arena — blind side-by-side LLM essay comparison
c8a9308 chore: sync leaderboard data and UI updates from GPT-5.4 session
344de91 feat: add GPT-5.4 to benchmark (Prelims rank #3, Mains rank #1)
efae48a Update CLAUDE.md: checkpoint after judge calibration and deployment
87ad72d docs: add judge validation findings to methodology page
a350912 feat: add judge calibration pipeline and validation results
98302c5 Use upsc-bench.com as live link in README
943b9f7 Remove Reducto reference and focus dataset scope on 2025
9a29151 Reframe judge calibration design: validate accuracy, don't force-fit to human scores
813dc13 Sync all documentation with current project state (Prelims + Mains)
04b4c52 Add coaching calibration design doc for LLM-as-judge improvement
b3a6533 Make leaderboard mobile-friendly with card layout and responsive polish
abdbbf3 Add Gemini 3 Flash Mains scores via calibrated Opus solo grading
39e9a1b Add Mains evaluation pipeline with calibrated Opus judge grading
ecc7bfc Add Mains UI components and types needed for page build
f11ca5d Default to Prelims tab until Mains data is populated
84ce865 Add Gemini 3 Flash Preview to benchmark (rank #1, 86.83% accuracy)
bdf732a Update CLAUDE.md: checkpoint after quiz and data cleanup session
da3c5f1 Add interactive quiz and fix GitHub link in footer
6b7ec54 Fix GS1 2025 data quality and re-run all model benchmarks
adf5103 Fix Prelims rankings: rank by GS1 marks instead of combined GS1+CSAT
969795e Update CLAUDE.md checkpoint: project state after UI polish session
ffd5da4 Add complete project: evaluation harness, data pipeline, Next.js leaderboard
73fe510 Polish leaderboard UI: consistent fonts, column hierarchy, methodology callout
37d8ff7 Initial project setup: directory structure, pyproject.toml, configs
```
Branch: `main`

## Data Summary

### Answer Keys
| File | Questions | Year | Paper |
|------|-----------|------|-------|
| `data/answer_keys/gs1_2024.json` | 100 | 2024 | GS Paper I |
| `data/answer_keys/csat_2024.json` | 80 | 2024 | CSAT Paper II |
| `data/answer_keys/gs1_2025.json` | 100 | 2025 | GS Paper I |
| `data/answer_keys/csat_2025.json` | 80 | 2025 | CSAT Paper II |

### Processed Dataset
- `data/processed/upsc_bench.json` — 180 questions (list format, 2025 only)
  - 100 GS1 + 80 CSAT
  - Each question: `{id, year, paper, question_number, question_text, options, has_image, image_paths, image_description, correct_answer, marks_correct, marks_wrong, marks_unanswered}`

### Benchmark Results (leaderboard.json)
6 models evaluated via OpenRouter:
- `openrouter/openai/gpt-5.2`
- `openrouter/openai/gpt-5.4`
- `openrouter/google/gemini-3.1-pro-preview`
- `openrouter/anthropic/claude-opus-4.6`
- `openrouter/google/gemini-2.5-flash`
- `openrouter/google/gemini-3-flash-preview`

Human reference: `human/shakti_dubey_2024` (CSE 2024 AIR 1)

Years: 2025 | Papers: GS1, CSAT (Prelims), Essay + GS1-4 (Mains)

### Downloaded PDFs (gitignored)
| File | Size | Source | Status |
|------|------|--------|--------|
| `data/pdfs/2024/gs_paper1_2024.pdf` | 7.8MB | ClearIAS | Parsed |
| `data/pdfs/2024/csat_paper2_2024.pdf` | 8.4MB | ClearIAS | Parsed |
| `data/pdfs/2023/gs_paper1_2023.pdf` | 6.6MB | ClearIAS | Not parsed |
| `data/pdfs/2022/gs_paper1_2022.pdf` | 9.2MB | ClearIAS | Not parsed |

## Key Technical Details

### Scoring System
- **Prelims GS Paper I**: 100 questions, +2.0 correct, -0.66 wrong, 0 unanswered, max 200
- **Prelims CSAT Paper II**: 80 questions, +2.5 correct, -0.83 wrong, 0 unanswered, max 200
- **Prelims pass criteria**: GS1 score > year-specific General category cutoff; CSAT >= 66/200 (33%)
- **Mains**: Essay (250 marks) + GS1-4 (250 marks each) = 1250 marks total (excluding Optional)
- **Mains scoring**: LLM-as-judge (Claude Opus) with 5-dimension rubric, debiased grading
- **Mains pass criteria**: Total score > proportional cutoff (~571/1250, derived from full exam cutoff)

### Cutoffs (from config/cutoffs.yaml)
| Year | GS1 | CSAT |
|------|-----|------|
| 2025 | 90.00 | 66 |
| 2024 | 87.98 | 66 |
| 2023 | 75.41 | 66 |
| 2022 | 87.54 | 66 |
| 2021 | 87.54 | 66 |
| 2020 | 92.51 | 66 |

### Frontend
- Next.js 16 with App Router, TypeScript, Tailwind CSS v4
- Recharts for bar charts
- Fonts: Playfair Display (serif headings) + Inter (sans-serif body)
- Colors: Saffron #FF9933, Navy #000080, Green #138808, Cream #FFF8F0, Gold #C5A55A
- Dev server: `npm run dev` from `web/` directory (port 3000)
- Build: `npm run build` passes cleanly

### Python
- System Python: `/Library/Developer/CommandLineTools/usr/bin/python3` (has PyMuPDF and PyPDF2)
- Homebrew packages can't be installed (permission issue with `/opt/homebrew`)
- `.env` file exists with API keys (gitignored)

## File Map

```
upsc-bench/
├── CLAUDE.md                          <- THIS FILE
├── pyproject.toml                     <- Python project config
├── .env                               <- API keys (gitignored)
├── .env.example                       <- API key template
├── .gitignore                         <- Excludes PDFs, .env, .next/, node_modules
├── README.md
├── config/
│   ├── cutoffs.yaml                   <- Historical UPSC cutoffs 2020-2025 (Prelims + Mains)
│   ├── judge.yaml                     <- Mains grading rubric weights
│   └── models.yaml                    <- Model registry (6 models, Prelims+Mains defaults)
├── data/
│   ├── pdfs/                          <- Question paper PDFs (gitignored)
│   ├── answer_keys/
│   │   ├── gs1_2024.json              <- Structured answer key
│   │   ├── csat_2024.json             <- Structured answer key
│   │   ├── gs1_2025.json              <- Structured answer key
│   │   ├── csat_2025.json             <- Structured answer key
│   │   └── pdfs/                      <- Raw answer key PDFs (gitignored)
│   ├── processed/
│   │   └── upsc_bench.json            <- 357 merged questions (main dataset)
│   ├── images/                        <- Extracted question images
│   ├── mains_questions/
│   │   └── mains_2025.json            <- Structured Mains questions (Essay + GS1-4)
│   └── rank_mapping.json              <- Score-to-rank mapping data
├── pipeline/
│   ├── extract_pdf.py                 <- PDF to image conversion
│   ├── structure_questions.py         <- LLM-based question structuring
│   ├── merge_answer_keys.py           <- Answer key merging
│   ├── validate_dataset.py            <- Dataset validation
│   └── build_dataset.py               <- Pipeline orchestrator
├── benchmark/
│   ├── common.py                      <- Shared utilities (load_cutoffs, load_config, resolve_model_config, etc.)
│   ├── grader.py                      <- Regex answer extraction + grading
│   ├── scorer.py                      <- UPSC Prelims marks calculation
│   ├── solver.py                      <- LiteLLM prompt construction (MCQ)
│   ├── db.py                          <- SQLite operations (Prelims + Mains tables)
│   ├── runner.py                      <- Main Prelims eval loop (--model KEY or --config FILE)
│   ├── mains_solver.py                <- Mains long-form answer prompt construction
│   ├── mains_scorer.py                <- Mains marks aggregation
│   └── mains_runner.py                <- Mains answer collection pipeline (--model KEY or --config FILE)
├── scripts/
│   ├── generate_leaderboard.py        <- Aggregate results -> leaderboard.json
│   ├── grade_mains.py                 <- Prepare grading input + merge grading output
│   ├── merge_all_mains.py             <- Merge Mains grading batches into per-model results
│   ├── scrape_coaching_answers.py     <- Structure raw InsightsIAS data into calibration format
│   ├── grade_calibration.py           <- Prepare/merge calibration grading batches
│   ├── compute_calibration_metrics.py <- Compute MAE, bias, per-paper breakdown
│   └── build_arena_data.py            <- Extract essay answers -> web/data/arena_data.json
├── results/
│   └── leaderboard.json               <- Real benchmark results (4 models x 2 years)
├── db/                                <- For SQLite (empty)
└── web/                               <- Next.js frontend
    ├── data/leaderboard.json          <- Copy of leaderboard data for static build
    ├── data/arena_data.json           <- Essay answers for arena (8 questions × 5 models)
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx               <- Main leaderboard page
    │   │   ├── globals.css            <- Global styles + animations
    │   │   ├── about/page.tsx         <- Methodology + "Why This Matters"
    │   │   ├── arena/page.tsx         <- Blind side-by-side essay comparison
    │   │   └── quiz/page.tsx          <- Interactive 5-question quiz
    │   ├── components/
    │   │   ├── Header.tsx             <- SVG Ashoka Chakra + title + stats
    │   │   ├── Leaderboard.tsx        <- Prelims ranking table with cutoff rows
    │   │   ├── MainsLeaderboard.tsx   <- Mains ranking table with paper breakdown
    │   │   ├── ArenaEssayPanel.tsx    <- Side-by-side essay display with rubric scores
    │   │   ├── ScoreChart.tsx         <- Recharts bar chart
    │   │   ├── YearSelector.tsx       <- Year filter pills
    │   │   ├── PaperTabs.tsx          <- Paper type toggle
    │   │   ├── QuestionCard.tsx       <- Quiz question display with options
    │   │   └── Footer.tsx             <- Tricolor + disclaimer
    │   ├── lib/
    │   │   ├── data.ts                <- Data loading + filtering + ranking
    │   │   ├── quiz.ts                <- Quiz logic: sampling, scoring, rank extrapolation
    │   │   ├── arena.ts               <- Arena logic: pairings, voting, summary
    │   │   ├── constants.ts           <- Model display names, model colors
    │   │   └── utils.ts               <- Shared utilities (shuffle, getRankClass, HumanIcon)
    │   └── types/
    │       ├── index.ts               <- TypeScript interfaces
    │       └── arena.ts               <- Arena-specific types
    ├── package.json
    └── tsconfig.json
```

## Session Log (latest first)

### Session 16 (2026-03-09) — Fix mains data loss in leaderboard
- **Bug**: `generate_leaderboard.py` only preserved `human/` entries when regenerating — Session 15's re-run wiped all `mains` data from AI model entries. Page defaults to Mains view → empty leaderboard.
- **Fix**: Restored mains data from pre-Session-15 commit (`344de91`), updated script to also preserve `existing_mains` on future re-runs.
- **Deployed** to Vercel (upsc-bench.com) — all 6 AI models + 10 human references showing correctly.

### Session 15 (2026-03-09) — Answer key audit + truncation fix
- **Answer-first prompting** — Changed solver.py SYSTEM_PROMPT and templates to instruct models to state their answer before reasoning. Industry standard (MMLU, GPQA, ARC) that prevents truncation from eating the answer.
- **max_tokens bump** — Increased prelims max_tokens from 4096 to 8192 in config/models.yaml. Gemini 3.1 Pro was hitting 4092-token ceiling on CSAT math/logic questions.
  - Combined effect: Gemini 3.1 Pro unanswered 9→2, Gemini 2.5 Flash 3→0, all others remain 0
- **GS1 2025 answer key corrections** — 6 answers confirmed wrong via unanimous 6-model consensus + independent verification:
  - Q011: a→c (Roy both respected Eastern philosophy AND advocated rational/scientific approach)
  - Q015: a→b (Faxian visited during Chandragupta II, not Samudragupta)
  - Q017: d→b (Only Asmaka-Godavari and Kosala-Sarayu correct, not all four)
  - Q018: c→d (First Gandharva Mahavidyalaya was in Lahore, 1901)
  - Q020: b→c (Nagpur Congress 1920 declared Swaraj AND planned staged implementation)
  - Q064: c→b (Wet-bulb temperature affects thermoregulation, not flooding/cyclones)
  - Q076 added to disputed (c or b both accepted — depends on overseas territory counting)
- **CSAT 2025 passage bug** — Discovered 3 questions (Q004, Q023, Q044) with wrong passages from PDF parsing. Each is the first question of a new passage group that inherited the previous group's passage. Dropped from dataset (180→177 questions).
- **Full re-run** — All 6 models re-evaluated on 177 questions with answer-first prompt
- **New rankings**:
  - #1 GPT-5.2: 92.7% accuracy, GS1 178.7/200
  - #2 Gemini 3.1 Pro: 93.2% accuracy, GS1 176.7/200
  - #3 Gemini 3 Flash: 89.3% accuracy, GS1 173.3/200
  - #4 Claude Opus 4.6: 87.6% accuracy, GS1 173.3/200
  - #5 GPT-5.4: 76.3% accuracy, GS1 162.7/200
  - #6 Gemini 2.5 Flash: 79.1% accuracy, GS1 146.7/200
- 10 human references preserved, `npm run build` passes

### Session 14 (2026-03-05) — Data quality audit & grader bug fix
- **Mains audit** — Verified all 87 questions structurally correct, answer keys cross-referenced against PDFs, grading results integrity checked
  - Found raw results files had stale solo-graded scores → synced with authoritative regrade data (commit c92a0de)
  - GPT-5.4 and Gemini 3 Flash identified as solo-graded (inflated ~1.34x) — deferred to batch re-run
- **Data provenance** — Created `DATA_SOURCES.md` documenting all PDF and JSON sources with URLs
  - Downloaded 5 Mains 2025 PDFs from InsightsIAS (81MB total)
  - Updated `download_pdfs.sh` with all sources + skip-if-exists logic
  - Un-gitignored PDFs for reproducibility
- **Prelims audit** — 7 systematic checks:
  1. Structural integrity: all 357 questions clean (unique IDs, valid options, correct marking schemes)
  2. Answer key cross-reference: all 357 match, 3 dropped questions (GS1 2024) correctly excluded, 4 disputed questions documented
  3. Scoring verification: all 6 models' raw results match leaderboard exactly
  4. Data completeness: 3 models (GPT-5.2, Gemini 3.1 Pro, Gemini 2.5 Flash) only have GS1 2025 (100/357 questions)
  5. Question text quality: no OCR artifacts, no empty options, no duplicates
  6. Image questions: zero (all text-only)
  7. **CRITICAL: Grader bug** — Claude's 27 "unanswered" were actually answered with `Answer: **(D)**` markdown bold format. Regex couldn't parse `**` markers.
- **Grader fix** — Modified `benchmark/grader.py` `normalize_answer()`: try original text first, then retry with `**`/`*` stripped. Fix recovers 25 correct + 2 wrong answers.
  - Claude GS1 avg: 156.09 → 159.76 (+3.67), CSAT totals: +51.67 marks
  - Claude accuracy: 79.83% → 86.83%
  - Claude Prelims rank: #2 → **#1**
- Re-graded all raw results, regenerated leaderboard, restored Mains data + human references, `npm run build` passes
- **Dropped 2024 Prelims data** — Simplified to 2025 only (180 questions). 3 models (GPT-5.2, Gemini 3.1 Pro, Gemini 2.5 Flash) were incomplete (only 100/357 questions) due to a Session 7 re-run that overwrote their files. Root cause: GS1 2025 re-run used year/paper filters, wrote to same output paths, then merge step was only done for Claude.
  - Filtered `upsc_bench.json` from 357 → 180 questions
  - Recovered CSAT 2025 data for 3 incomplete models from SQLite DB (`benchmark_results.db`)
  - All 6 models now have identical 180-question coverage
  - Removed `results/raw/2024_only/` backup directory
  - Claude Opus #1 Prelims (GS1: 157.44, CSAT: 166.70, accuracy: 85.6%)

### Session 13 (2026-03-05) — Full project simplification
- **Phase 1: Frontend dead code removal** — Deleted `PassFailBadge.tsx` (unused), removed `COLORS` export and Grok 4 phantom model entries from `constants.ts`, removed 6 unused CSS classes + 5 keyframes from `globals.css` (~45 lines)
- **Phase 2: Bug fixes** — Wrapped YearSelector `onChange()` in `useEffect` (React anti-pattern fix), added missing `import sys` in `compute_calibration_metrics.py`, added `model` parameter to `db.py` `save_result()` and `save_mains_result()` (was hardcoded `""`)
- **Phase 3: Untrack intermediate results** — Added 10 gitignore entries, `git rm --cached` 142 intermediate JSON files (grading batches, regrade batches, parsing intermediates). Files remain on disk.
- **Phase 4: Delete obsolete scripts** — Removed 12 one-time scripts (~2,300 lines): `merge_regrade.py`, `build_mains_questions.py`, `clean_gs1_2025.py`, `add_2025_questions.py`, `merge_and_build.py`, `self_eval.py`, `build_regrade_batches.py`, `build_flash_solo_batches.py`, `prepare_flash_grading.py`, `combine_results.py`, `merge_answers.py`, `run_2025.sh`
- **Phase 5: Extract shared frontend utilities** — Created `web/src/lib/utils.ts` with `shuffle<T>()`, `getRankClass()`, and `HumanIcon` component. Updated imports in `quiz.ts`, `arena.ts`, `Leaderboard.tsx`, `MainsLeaderboard.tsx`.
- **Phase 6: Extract shared Python utilities** — Created `benchmark/common.py` with `load_cutoffs()`, `load_config()`, `load_questions()`, `load_rubric()`. Updated imports in `scorer.py`, `mains_scorer.py`, `runner.py`, `mains_runner.py`, `generate_leaderboard.py`, `grade_mains.py`.
- **Phase 7: Consolidate model configs** — Replaced 12 individual YAML files with single `config/models.yaml` registry + `resolve_model_config()` in `common.py`. Runners now accept `--model KEY` (e.g., `--model gpt5`) as alternative to `--config FILE`.
- Total: ~2,600 lines removed, 142 files untracked, 13 files deleted, 3 bugs fixed, 2 new shared utility modules created

### Session 12 (2026-03-05) — Arena feature
- Built LMSys Arena-style blind side-by-side essay comparison at `/arena`
- Created Python build script (`scripts/build_arena_data.py`) to extract essay answers from `results/raw/mains_results_*.json` into `web/data/arena_data.json` (366KB, 8 questions × 5 models)
- Arena flow: 5-round sessions, blind Model A/B labels, optional reveal before voting, post-vote rubric score bars + judge feedback
- Mobile-responsive: tab-switched on mobile, true side-by-side grid on desktop
- Added task context to question header explaining UPSC essay requirements and judging criteria
- Code review found & fixed 6 bugs: handleRestart double-randomization, biased sort shuffle replaced with Fisher-Yates, ARENA_MODELS derived per-question, progress bar off-by-one, unused props, inline markdown rendering
- New files: `arena/page.tsx`, `ArenaEssayPanel.tsx`, `lib/arena.ts`, `types/arena.ts`
- Modified: `Footer.tsx` (arena link), `page.tsx` (arena callout), `globals.css` (arena-essay styles)
- Deployed to Vercel (upsc-bench.com/arena)

### Session 11 (2026-03-05) — GPT-5.4 evaluation
- Added GPT-5.4 (`openrouter/openai/gpt-5.4`) to benchmark — full Prelims + Mains evaluation
- Prelims: 357 MCQs, 73.67% accuracy, GS1 avg 155.77/200 (rank #3)
  - GS1 2024: 167.4/200, GS1 2025: 144.14/200, CSAT 2024: 93.44, CSAT 2025: 96.77
- Mains: 87 questions graded by 4 parallel Opus subagents
  - Total: 942.70/1250 (75.4%) — rank #1 Mains, surpassing GPT-5.2's 897.25
  - Essay: 178.00/250 (selected Q2, Q5), GS1: 196.20/250, GS2: 184.10/250, GS3: 195.90/250, GS4: 188.50/250
- Created config files: `config/gpt5_4.yaml`, `config/mains_gpt5_4.yaml`
- Updated `web/src/lib/constants.ts` with GPT-5.4 display name and emerald color (#059669)
- Regenerated leaderboard, `npm run build` passes
- Selectively staged GPT-5.4 changes only (isolated from concurrent arena/human-reference sessions)
- Pushed to GitHub, deployed to Vercel (upsc-bench.com)

### Session 10 (2026-03-03) — Judge calibration & deployment
- Built judge calibration pipeline: scraped 78 model answers from InsightsIAS (GS1-4) using 4 parallel subagents
- Created scripts: `scrape_coaching_answers.py`, `grade_calibration.py`, `compute_calibration_metrics.py`
- Graded all 78 coaching answers with 16 parallel Opus subagents (same judge prompt as AI models)
- Calibration results: -8.8% negative bias (judge is stricter than coaching expectations), 9.8% MAE, 29.5% within expected range
- Per-paper bias: GS1 -9.9%, GS2 -8.0%, GS3 -7.0%, GS4 -10.3%
- Validates H1 (AI genuinely outperforms) over H2 (judge inflates LLM-style answers)
- Updated methodology page with Judge Validation section: metrics tables, per-paper breakdown, explanation
- Deployed to Vercel (upsc-bench.com)

### Session 9 (2026-03-03) — Documentation sync
- Rewrote README.md: complete rewrite with actual scores, correct models (5 AI + human), both Prelims + Mains, methodology summary, setup instructions
- Rewrote About/Methodology page: added Mains Scoring section (rubric table, debiasing, score anchors), Q&A/FAQ section (5 questions), fixed cutoff table (2024: 87.98 not 93.34, added 2025: 90.00), updated Dataset/Models/Limitations sections
- Added QA helper component to about/page.tsx for FAQ rendering
- Updated CLAUDE.md: session log, moved 6 items from NOT DONE to DONE, updated file map, models list, git history, RESUME HERE

### Session 8 (2026-03-02–03) — Mains pipeline run + frontend + mobile
- Ran Mains benchmark: all 5 models answered 87 Mains 2025 questions via OpenRouter
- Graded all answers using calibrated Claude Opus judge with comparative, blind, shuffled grading
- Added Gemini 3 Flash to benchmark (rank #1 Prelims, 86.83% accuracy)
- Added human reference: Shakti Dubey CSE 2024 AIR 1 (602.14/1250 estimated Mains score)
- Built MainsLeaderboard.tsx with paper breakdown tabs (Total, Essay, GS1-4)
- Added ExamToggle (Prelims/Mains) to main page
- Made leaderboard mobile-friendly: card layout on small screens, responsive polish
- Updated leaderboard.json with Mains scores for all models
- Key Mains results: GPT-5.2 #1 (897.25/1250, 71.8%), Gemini 3.1 Pro #2 (865.12), Claude Opus #3 (828.44), Gemini 3 Flash #4 (780.90), Gemini 2.5 Flash #5 (735.80)

### Session 7 (2026-03-02) — GS1 2025 data cleanup + benchmark re-runs
- Created `scripts/clean_gs1_2025.py`: targeted cleanup for GS1 2025 PDF parsing artifacts
  - Fixed word-per-line formatting (47 questions), III→Ill/m corruption (18 questions), LVPK garbage text (5+ options), l→I Roman numeral (4 questions), tilde artifacts, bracket OCR, Q93 corruption
  - 90/100 GS1 2025 questions modified, all other data untouched
- Re-ran all 4 models on cleaned GS1 2025 data:
  - Gemini 3.1 Pro: 148.10 → 151.44 (+3.34)
  - GPT-5.2: 144.14 → 149.46 (+5.32)
  - Claude Opus 4.6: 140.80 → 155.44 (+14.64)
  - Gemini 2.5 Flash: 121.52 → 140.14 (+18.62)
- Updated leaderboard.json with new scores (rankings unchanged)
- Investigated "unanswered" results: none are intentional skips — caused by API errors, grader regex misses, or truncated outputs
- Design decision: keep "always answer" prompt (no skip option) as primary benchmark — random guessing is ~break-even with UPSC marking scheme

### Session 6 (2026-03-02) — Interactive quiz feature
- Built quiz at /quiz: 5 random GS1 2025 questions with instant feedback
- Created QuestionCard.tsx with paragraph-based rendering (fixed whitespace-pre-line issue)
- Created quiz.ts with question sampling, scoring, and rank extrapolation
- Added quiz callout on main page, quiz link in footer
- Added RawQuestion type to types/index.ts
- Copied upsc_bench.json and rank_mapping.json to web/data/

### Session 5 (2026-03-02) — Mains evaluation pipeline
- Built complete Mains pipeline: mains_solver.py, mains_scorer.py, mains_runner.py
- Extended benchmark/db.py with mains_results table
- Created grading infrastructure: scripts/grade_mains.py + config/judge.yaml
- Collected and structured 2025 Mains questions (Essay + GS1-4) into data/mains_questions/mains_2025.json
- Created model configs for Mains (config/mains_*.yaml)
- Added Mains cutoffs to config/cutoffs.yaml
- Updated CLAUDE.md with session 4+5 changes

### Session 4 (2026-03-02) — Prelims ranking fix
- Fixed ranking: renamed "Overall" → "Prelims Score", sort by GS1 marks (not combined GS1+CSAT)
- CSAT treated as qualifying (pass/fail) only — displayed as badge under Prelims Score
- Fixed cutoff row positioning
- Committed as adf5103

### Session 3 (2026-03-02) — UI polish + content + bug fix
- Fixed missing `label` prop on trailing CutoffRow in Leaderboard.tsx
- Rewrote main page intro: "What is this?" -> "UPSC Bench", expanded to 3 paragraphs covering exam difficulty, IAS/IPS/IFS positions, and what UPSC Bench does
- Added "Why This Matters" section to methodology page with cultural context and links (12th Fail, TVF Aspirants, Wikipedia)
- Linter/user also polished Leaderboard.tsx: fixed-width columns via colgroup, grid-based breakdown, Est. AIR moved to last column with saffron badge, breakdown legend footnote, `showRank` prop on CutoffRow
- Linter/user also restructured page.tsx: merged filters into leaderboard section, added methodology callout with "Full methodology" link, removed `data` prop from Header
- Updated .gitignore: added `data/answer_keys/pdfs/` and root `.next/`
- Renamed branch `master` -> `main`
- Committed everything (3 commits total), working tree clean
- No remote configured yet — user needs to provide GitHub URL

### Previous Sessions
- Session 1-2: Built entire project from scratch — directory structure, pipeline scripts, benchmark harness, model configs, answer key extraction, PDF parsing via multimodal LLM, benchmark runs on 4 models, Next.js frontend with full leaderboard UI, 2025 data addition

## Important Notes
- The user prefers parallel subagent execution when possible
- The user wants to open source this project
- upsc.gov.in times out consistently — use coaching institute sources instead
- Google Drive download links frequently die (404) — save downloaded files
- Homebrew installs fail due to `/opt/homebrew` permissions
- Use `/Library/Developer/CommandLineTools/usr/bin/python3` for Python operations
- `.env` exists with API keys — never commit it
