# UPSC Bench — Project State & Instructions

## RESUME HERE — Immediate Next Action
**Connect GitHub remote and push. Then expand the benchmark to more models and years.**

The project is functional end-to-end: questions are parsed, answer keys are merged, benchmarks have been run against 4 models on 2024+2025 papers, and the Next.js leaderboard displays real results. The git history is clean on the `main` branch (3 commits) but no remote is configured yet.

Steps to resume:
1. Add GitHub remote: `git remote add origin <REPO_URL>` and push
2. Optionally add more models (Claude Sonnet, DeepSeek R1) to the benchmark
3. Optionally add more years (2020-2023) once PDFs are parsed
4. Deploy the frontend (Vercel or similar)

---

## Project Overview
UPSC Bench is an LLM evaluation benchmark based on India's UPSC Civil Services Preliminary Examination. It evaluates whether frontier AI models can pass the same exam that millions of Indian aspirants prepare years for. The project has a Python backend (data pipeline + evaluation harness) and a Next.js frontend (leaderboard website).

## Current Status: Phase 4 — Polish & Release

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
7. **Benchmark results** — 4 models evaluated on 2024+2025: GPT-5.2, Gemini 3.1 Pro, Claude Opus 4.6, Gemini 2.5 Flash
8. **Real leaderboard data** — `results/leaderboard.json` and `web/data/leaderboard.json` with actual scores, estimated AIR, pass/fail
9. **Next.js frontend** — Fully built, `npm run build` passes cleanly
   - Leaderboard with score bars, breakdown grid, estimated AIR, cutoff rows
   - Year selector (2024, 2025), paper tabs (Overall, GS1, CSAT)
   - Methodology page with "Why This Matters" section and cultural links
   - "UPSC Bench" intro with 3 paragraphs on exam context
   - Indian government aesthetic: saffron/navy/green/cream/gold
10. **Git** — 3 commits on `main` branch, working tree clean, no remote configured yet

### What's NOT DONE:
1. Add GitHub remote and push
2. Evaluate more models (Claude Sonnet, DeepSeek R1)
3. Add years 2020-2023 (PDFs downloaded for some, not parsed)
4. Deploy frontend (Vercel)
5. Write proper README for open source release

## Git History
```
f566af8 Add complete project: evaluation harness, data pipeline, Next.js leaderboard
1a8b958 Polish leaderboard UI: consistent fonts, column hierarchy, methodology callout
294a172 Initial project setup: directory structure, pyproject.toml, configs
```
Branch: `main` (renamed from `master`)

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
4 models evaluated via OpenRouter:
- `openrouter/openai/gpt-5.2`
- `openrouter/google/gemini-3.1-pro-preview`
- `openrouter/anthropic/claude-opus-4.6`
- `openrouter/google/gemini-2.5-flash`

Years: 2024, 2025 | Papers: GS1, CSAT

### Downloaded PDFs (gitignored)
| File | Size | Source | Status |
|------|------|--------|--------|
| `data/pdfs/2024/gs_paper1_2024.pdf` | 7.8MB | ClearIAS | Parsed |
| `data/pdfs/2024/csat_paper2_2024.pdf` | 8.4MB | ClearIAS | Parsed |
| `data/pdfs/2023/gs_paper1_2023.pdf` | 6.6MB | ClearIAS | Not parsed |
| `data/pdfs/2022/gs_paper1_2022.pdf` | 9.2MB | ClearIAS | Not parsed |

## Key Technical Details

### Scoring System
- **GS Paper I**: 100 questions, +2.0 correct, -0.66 wrong, 0 unanswered, max 200
- **CSAT Paper II**: 80 questions, +2.5 correct, -0.83 wrong, 0 unanswered, max 200
- **Pass criteria**: GS1 score > year-specific General category cutoff; CSAT >= 66/200 (33%)

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
│   ├── cutoffs.yaml                   <- Historical UPSC cutoffs 2020-2025
│   ├── claude_opus.yaml
│   ├── gpt5.yaml
│   ├── gemini_3_pro.yaml
│   └── gemini_flash.yaml
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
│   └── rank_mapping.json              <- Score-to-rank mapping data
├── pipeline/
│   ├── extract_pdf.py                 <- PDF to image conversion
│   ├── structure_questions.py         <- LLM-based question structuring
│   ├── merge_answer_keys.py           <- Answer key merging
│   ├── validate_dataset.py            <- Dataset validation
│   └── build_dataset.py               <- Pipeline orchestrator
├── benchmark/
│   ├── grader.py                      <- Regex answer extraction + grading
│   ├── scorer.py                      <- UPSC marks calculation
│   ├── solver.py                      <- LiteLLM prompt construction
│   ├── db.py                          <- SQLite operations
│   └── runner.py                      <- Main eval loop
├── scripts/
│   ├── generate_leaderboard.py        <- Aggregate results -> leaderboard.json
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
    │   │   └── about/page.tsx         <- Methodology + "Why This Matters"
    │   ├── components/
    │   │   ├── Header.tsx             <- SVG Ashoka Chakra + title + stats
    │   │   ├── Leaderboard.tsx        <- Ranking table with cutoff rows
    │   │   ├── ScoreChart.tsx         <- Recharts bar chart
    │   │   ├── YearSelector.tsx       <- Year filter pills
    │   │   ├── PaperTabs.tsx          <- Paper type toggle
    │   │   ├── PassFailBadge.tsx      <- Pass/fail indicator
    │   │   └── Footer.tsx             <- Tricolor + disclaimer
    │   ├── lib/
    │   │   ├── data.ts                <- Data loading + filtering + ranking
    │   │   └── constants.ts           <- Colors, model display names
    │   └── types/index.ts             <- TypeScript interfaces
    ├── package.json
    └── tsconfig.json
```

## Session Log (latest first)

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
