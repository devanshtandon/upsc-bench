# UPSC Bench — Project State & Instructions

## RESUME HERE — Immediate Next Action
**Deploy to Vercel, then expand coverage.**

Both Prelims and Mains are complete: 5 AI models + human reference, 2024+2025 Prelims, 2025 Mains, mobile-responsive frontend with Prelims/Mains toggle, interactive quiz, full methodology page. Documentation is up to date.

Steps to resume:
1. Deploy the frontend (Vercel or similar)
2. Evaluate more models (Claude Sonnet, DeepSeek R1)
3. Add Prelims years 2020-2023 (PDFs downloaded for some, not parsed)
4. Write proper README for open source release (draft complete, finalize after deploy)

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
6. **Parsed questions** — `data/processed/upsc_bench.json` — 357 questions total (197 GS1, 160 CSAT across 2024+2025)
   - GS1 2025 data cleaned: fixed word-per-line formatting, III→Ill/m corruption, garbage text, OCR artifacts (90/100 questions affected)
7. **Benchmark results** — 5 models evaluated: GPT-5.2, Gemini 3.1 Pro, Claude Opus 4.6, Gemini 2.5 Flash, Gemini 3 Flash
   - GS1 2025 re-run on cleaned data: all models improved (+3 to +19 marks)
   - Gemini 3 Flash added: rank #1 Prelims (86.83% accuracy, GS1 avg 157.10)
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
16. **Mains leaderboard** — GPT-5.2 #1 (897.25/1250), Gemini 3.1 Pro #2, Claude Opus #3, Gemini 3 Flash #4, Gemini 2.5 Flash #5
17. **Human reference** — Shakti Dubey (CSE 2024 AIR 1) added as Mains baseline (602.14/1250 estimated)
18. **Frontend Mains view** — ExamToggle (Prelims/Mains), MainsLeaderboard.tsx, Mains tabs (Total, Essay, GS1-4), paper breakdown
19. **Mobile-responsive redesign** — Card layout for mobile, responsive leaderboard
20. **Documentation update** — README rewrite, About/Methodology page with Mains methodology + FAQ

### What's NOT DONE:
1. ~~Add GitHub remote and push~~ (done)
2. ~~Run Mains benchmark (all 5 models answer Mains 2025 questions)~~ (done)
3. ~~Grade Mains answers via calibrated Opus judge~~ (done)
4. ~~Generate Mains leaderboard results~~ (done)
5. ~~Frontend: ExamToggle (Prelims/Mains), Mains tabs, rubric breakdown~~ (done)
6. ~~Update About/Methodology page with Mains methodology~~ (done)
7. Evaluate more models (Claude Sonnet, DeepSeek R1)
8. Add Prelims years 2020-2023 (PDFs downloaded for some, not parsed)
9. Deploy frontend (Vercel)
10. ~~Write proper README for open source release~~ (draft done)

## Git History
```
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
- `data/processed/upsc_bench.json` — 357 questions (list format)
  - 2024: 177 questions (97 GS1 + 80 CSAT)
  - 2025: 180 questions (100 GS1 + 80 CSAT)
  - Each question: `{id, year, paper, question_number, question_text, options, has_image, image_paths, image_description, correct_answer, marks_correct, marks_wrong, marks_unanswered}`

### Benchmark Results (leaderboard.json)
5 models evaluated via OpenRouter:
- `openrouter/openai/gpt-5.2`
- `openrouter/google/gemini-3.1-pro-preview`
- `openrouter/anthropic/claude-opus-4.6`
- `openrouter/google/gemini-2.5-flash`
- `openrouter/google/gemini-3-flash-preview`

Human reference: `human/shakti_dubey_2024` (CSE 2024 AIR 1)

Years: 2024, 2025 | Papers: GS1, CSAT (Prelims), Essay + GS1-4 (Mains)

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
│   ├── claude_opus.yaml
│   ├── gpt5.yaml
│   ├── gemini_3_pro.yaml
│   ├── gemini_flash.yaml
│   ├── mains_claude_opus.yaml         <- Mains model configs
│   ├── mains_gpt5.yaml
│   ├── mains_gemini_3_pro.yaml
│   └── mains_gemini_flash.yaml
├── data/
│   ├── pdfs/                          <- Question paper PDFs (gitignored)
│   ├── answer_keys/
│   │   ├── gs1_2024.json              <- Structured answer key
│   │   ├── csat_2024.json             <- Structured answer key
│   │   ├── gs1_2025.json              <- Structured answer key
│   │   ├── csat_2025.json             <- Structured answer key
│   │   └── pdfs/                      <- Raw answer key PDFs (gitignored)
│   ├── processed/
│   │   ├── upsc_bench.json            <- 357 merged questions (main dataset)
│   │   ├── gs1_2024_batch[1-4].json   <- Intermediate parsing outputs
│   │   ├── csat_2024_batch[1-4].json  <- Intermediate parsing outputs
│   │   ├── answers_gs1_part[1-2].json <- Model answer batches
│   │   ├── answers_csat_part[1-2].json
│   │   └── my_answers.json            <- Self-eval answers
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
│   ├── grader.py                      <- Regex answer extraction + grading
│   ├── scorer.py                      <- UPSC Prelims marks calculation
│   ├── solver.py                      <- LiteLLM prompt construction (MCQ)
│   ├── db.py                          <- SQLite operations (Prelims + Mains tables)
│   ├── runner.py                      <- Main Prelims eval loop
│   ├── mains_solver.py                <- Mains long-form answer prompt construction
│   ├── mains_scorer.py                <- Mains marks aggregation
│   └── mains_runner.py                <- Mains answer collection pipeline
├── scripts/
│   ├── generate_leaderboard.py        <- Aggregate results -> leaderboard.json
│   ├── clean_gs1_2025.py              <- GS1 2025 data quality cleanup script
│   ├── grade_mains.py                 <- Prepare grading input + merge grading output
│   ├── self_eval.py                   <- Self-evaluation script
│   ├── merge_and_build.py             <- Merge + build pipeline
│   ├── merge_answers.py               <- Answer merging utility
│   ├── combine_results.py             <- Results combiner
│   ├── add_2025_questions.py          <- 2025 question adder
│   └── run_2025.sh                    <- 2025 benchmark runner
├── results/
│   └── leaderboard.json               <- Real benchmark results (4 models x 2 years)
├── db/                                <- For SQLite (empty)
└── web/                               <- Next.js frontend
    ├── data/leaderboard.json          <- Copy of leaderboard data for static build
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx               <- Main leaderboard page
    │   │   ├── globals.css            <- Global styles + animations
    │   │   ├── about/page.tsx         <- Methodology + "Why This Matters"
    │   │   └── quiz/page.tsx          <- Interactive 5-question quiz
    │   ├── components/
    │   │   ├── Header.tsx             <- SVG Ashoka Chakra + title + stats
    │   │   ├── Leaderboard.tsx        <- Prelims ranking table with cutoff rows
    │   │   ├── MainsLeaderboard.tsx   <- Mains ranking table with paper breakdown
    │   │   ├── ScoreChart.tsx         <- Recharts bar chart
    │   │   ├── YearSelector.tsx       <- Year filter pills
    │   │   ├── PaperTabs.tsx          <- Paper type toggle
    │   │   ├── PassFailBadge.tsx      <- Pass/fail indicator
    │   │   ├── QuestionCard.tsx       <- Quiz question display with options
    │   │   └── Footer.tsx             <- Tricolor + disclaimer
    │   ├── lib/
    │   │   ├── data.ts                <- Data loading + filtering + ranking
    │   │   ├── quiz.ts                <- Quiz logic: sampling, scoring, rank extrapolation
    │   │   └── constants.ts           <- Colors, model display names
    │   └── types/index.ts             <- TypeScript interfaces
    ├── package.json
    └── tsconfig.json
```

## Session Log (latest first)

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
