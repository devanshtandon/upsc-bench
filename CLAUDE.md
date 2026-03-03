# UPSC Bench — Project State & Instructions

## ⚡ RESUME HERE — Immediate Next Action
**Parse the 2024 question paper PDFs into structured JSON using a multimodal LLM.**

The answer keys are done (JSON files exist). The blocker is extracting the actual question text + options from the scanned PDF images. Steps:

1. Ask the user which API key they have available (Google/Anthropic/OpenAI) and create `.env`
2. Write `scripts/parse_pdf_with_llm.py` that:
   - Uses PyMuPDF (`fitz`) to convert PDF pages to images (English pages only — every other page starting from page 3)
   - Sends each page image to a multimodal LLM (Gemini Flash recommended for cost)
   - Extracts structured questions: `{question_number, question_text, options: {a,b,c,d}, has_image, image_description}`
   - Handles two-column layout (~5 questions per page, 23 English pages for 100 questions)
3. Run on `data/pdfs/2024/gs_paper1_2024.pdf` → save to `data/processed/gs1_2024_questions.json`
4. Run on `data/pdfs/2024/csat_paper2_2024.pdf` → save to `data/processed/csat_2024_questions.json`
5. Merge questions + answer keys (`data/answer_keys/gs1_2024.json`, `csat_2024.json`) → `data/processed/upsc_bench.json`
6. Then run benchmark against real LLMs

**Key constraint:** PDFs are scanned images (ClearIAS watermarked). PyPDF2 returns no useful text. Must use vision/multimodal LLM.
**Python to use:** `/Library/Developer/CommandLineTools/usr/bin/python3` (has PyMuPDF and PyPDF2 installed)

---

## Project Overview
UPSC Bench is an LLM evaluation benchmark based on India's UPSC Civil Services Preliminary Examination. It evaluates whether frontier AI models can pass the same exam that millions of Indian aspirants prepare years for. The project has a Python backend (data pipeline + evaluation harness) and a Next.js frontend (leaderboard website).

## Current Status: Phase 2 — Data Pipeline (In Progress)

### What's DONE:
1. **Project structure** — All directories created, pyproject.toml, .gitignore, .env.example, README.md
2. **Python pipeline scripts** — All 5 files in `pipeline/` (extract_pdf.py, structure_questions.py, merge_answer_keys.py, validate_dataset.py, build_dataset.py)
3. **Evaluation harness** — All 5 files in `benchmark/` (grader.py, scorer.py, solver.py, db.py, runner.py)
4. **Model configs** — 6 YAML files in `config/` (gpt4o, claude_opus, claude_sonnet, gemini_pro, gemini_flash, deepseek_r1) + cutoffs.yaml
5. **Leaderboard aggregator** — `scripts/generate_leaderboard.py`
6. **Next.js frontend** — Fully built and builds successfully (`npm run build` passes)
   - Components: Header, Footer, Leaderboard, ScoreChart, YearSelector, PaperTabs, PassFailBadge
   - Pages: Home (page.tsx) and About/Methodology (about/page.tsx)
   - Styling: Indian government aesthetic with saffron/navy/green/cream/gold palette
   - Data layer: types/index.ts, lib/data.ts, lib/constants.ts
7. **Sample leaderboard.json** — Placeholder data with 6 models × 5 years (in `results/leaderboard.json` AND `web/data/leaderboard.json`)
8. **Answer keys (JSON)** — 2024 GS1 and CSAT answer keys saved as structured JSON
   - `data/answer_keys/gs1_2024.json` — 100 questions, Set A, source: ForumIAS (official UPSC key)
   - `data/answer_keys/csat_2024.json` — 80 questions, Set A, source: Universal Institutions / ForumIAS
   - GS1 has 3 dropped questions: Q20, Q52, Q57
   - CSAT has 3 disputed questions: Q12 (a/d), Q53 (b/c), Q71 (b/a)
   - Answer keys have been **sanity-checked** against actual paper questions (Q1, Q5, Q8 verified correct)

### What's IN PROGRESS:
- **Extracting structured questions from 2024 PDF question papers**
  - PDFs are scanned images (no extractable text), need multimodal parsing
  - English pages have been converted to PNG images at `/tmp/upsc_pages/gs1_2024/page_XX.png`
  - 23 English pages (pages 3,5,7,...,47 of 48-page PDF), ~5 questions per page
  - Pattern: English/Hindi pages alternate for each question set
  - Paper is Set A (marked "KSPC-P-GSPO" with "(N-A)" page numbers)
  - User suggested using Gemini or another multimodal LLM to parse the PDFs
  - **No API keys are configured yet** — need user to provide at least one (GOOGLE_API_KEY or ANTHROPIC_API_KEY)

### What's NOT DONE:
1. Parse 2024 GS Paper 1 PDF → structured questions JSON
2. Parse 2024 CSAT Paper 2 PDF → structured questions JSON
3. Merge questions + answer keys → `data/processed/upsc_bench.json`
4. Set up `.env` file with API keys
5. Run benchmark on real questions with real LLMs
6. Generate real `leaderboard.json` from actual results
7. Replace placeholder data on frontend with real results
8. Download additional years (2020-2023) — user said to focus on 2024 first

## Downloaded PDFs

| File | Size | Source | Status |
|------|------|--------|--------|
| `data/pdfs/2024/gs_paper1_2024.pdf` | 7.8MB | ClearIAS | Set A, 48 pages, scanned images |
| `data/pdfs/2024/csat_paper2_2024.pdf` | 8.4MB | ClearIAS | Not yet processed |
| `data/pdfs/2023/gs_paper1_2023.pdf` | 6.6MB | ClearIAS | Not yet processed |
| `data/pdfs/2022/gs_paper1_2022.pdf` | 9.2MB | ClearIAS | Not yet processed |
| `data/answer_keys/pdfs/gs1_2024_anskey.pdf` | 6.3MB | PWOnlyIAS (Google Drive) | Already extracted to JSON |
| `data/answer_keys/pdfs/csat_2024_anskey.pdf` | 9.7MB | PWOnlyIAS (Google Drive) | Already extracted to JSON |
| `data/answer_keys/pdfs/gs1_2022_anskey.pdf` | 93KB | theIASHub (Google Drive) | Not processed |
| `data/answer_keys/pdfs/csat_2022_anskey.pdf` | 80KB | theIASHub (Google Drive) | Not processed |

## Key Technical Details

### PDF Parsing
- ClearIAS PDFs are **scanned images** — PyPDF2 only extracts watermark text, not question content
- Use PyMuPDF (`fitz`) for PDF-to-image conversion (installed at system Python)
- System Python: `/Library/Developer/CommandLineTools/usr/bin/python3` (has PyPDF2 and PyMuPDF installed)
- Homebrew packages can't be installed (permission issue with `/opt/homebrew`)
- The extraction script should use a multimodal LLM (Gemini recommended for cost) to read page images

### PDF Page Structure (GS Paper 1 2024)
- 48 pages total, pages 1-2 are covers/instructions
- English pages: 3, 5, 7, ..., 47 (0-indexed: 2, 4, 6, ..., 46) — 23 pages
- Hindi pages: 4, 6, 8, ..., 48 (0-indexed: 3, 5, 7, ..., 47) — 23 pages
- Two-column layout, ~5 questions per English page
- Some questions include tables (Q9, Q10, Q55, etc.)
- Some questions may include map/diagram images
- Footer: "KSPC-P-GSPO" + "(N-A)" where N is page number

### Scoring System
- **GS Paper I**: 100 questions, +2.0 correct, -0.66 wrong, 0 unanswered, max 200
- **CSAT Paper II**: 80 questions, +2.5 correct, -0.83 wrong, 0 unanswered, max 200
- **Pass criteria**: GS1 score > year-specific General category cutoff; CSAT ≥ 66/200 (33%)
- 2024 cutoffs: GS1 = 93.34, CSAT qualifying = 66

### Frontend
- Next.js 15 with App Router, TypeScript, Tailwind CSS v4
- Recharts for bar charts
- Fonts: Playfair Display (serif headings) + Inter (sans-serif body)
- Colors: Saffron #FF9933, Navy #000080, Green #138808, Cream #FFF8F0, Gold #C5A55A
- Dev server: `npm run dev` from `web/` directory (port 3000)
- Build: `npm run build` passes cleanly

### Models to Evaluate
| Model | Config | Vision? |
|-------|--------|---------|
| Claude Opus 4 | `config/claude_opus.yaml` | Yes |
| Claude Sonnet 4 | `config/claude_sonnet.yaml` | Yes |
| GPT-4o | `config/gpt4o.yaml` | Yes |
| Gemini 2.5 Pro | `config/gemini_pro.yaml` | Yes |
| Gemini 2.0 Flash | `config/gemini_flash.yaml` | Yes |
| DeepSeek R1 | `config/deepseek_r1.yaml` | No (text fallback) |

## File Map

```
upsc-bench/
├── CLAUDE.md                          ← THIS FILE
├── pyproject.toml                     ← Python project config (uv)
├── .env.example                       ← API key template (no .env yet!)
├── .gitignore
├── README.md
├── config/
│   ├── cutoffs.yaml                   ← Historical UPSC cutoffs 2020-2024
│   ├── claude_opus.yaml
│   ├── claude_sonnet.yaml
│   ├── gpt4o.yaml
│   ├── gemini_pro.yaml
│   ├── gemini_flash.yaml
│   └── deepseek_r1.yaml
├── data/
│   ├── pdfs/2024/                     ← Downloaded question paper PDFs
│   ├── pdfs/2023/                     ← Downloaded (GS1 only)
│   ├── pdfs/2022/                     ← Downloaded (GS1 only)
│   ├── answer_keys/
│   │   ├── gs1_2024.json              ← ✅ Structured answer key
│   │   ├── csat_2024.json             ← ✅ Structured answer key
│   │   └── pdfs/                      ← Raw answer key PDFs
│   ├── images/                        ← For extracted question images (empty)
│   └── processed/                     ← For final dataset (empty)
├── pipeline/
│   ├── extract_pdf.py                 ← Reducto API integration
│   ├── structure_questions.py         ← LLM-based question structuring
│   ├── merge_answer_keys.py           ← Answer key merging
│   ├── validate_dataset.py            ← Dataset validation
│   └── build_dataset.py               ← Pipeline orchestrator
├── benchmark/
│   ├── grader.py                      ← Regex answer extraction + grading
│   ├── scorer.py                      ← UPSC marks calculation
│   ├── solver.py                      ← LiteLLM prompt construction
│   ├── db.py                          ← SQLite operations
│   └── runner.py                      ← Main eval loop
├── scripts/
│   └── generate_leaderboard.py        ← Aggregate results → leaderboard.json
├── results/
│   └── leaderboard.json               ← Sample/placeholder data
├── db/                                ← For SQLite (empty)
└── web/                               ← Next.js frontend
    ├── data/leaderboard.json          ← Copy of leaderboard data for static build
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx               ← Main leaderboard page ("use client")
    │   │   ├── globals.css
    │   │   └── about/page.tsx         ← Methodology page
    │   ├── components/
    │   │   ├── Header.tsx             ← SVG Ashoka Chakra + title
    │   │   ├── Leaderboard.tsx        ← Ranking table
    │   │   ├── ScoreChart.tsx         ← Recharts bar chart
    │   │   ├── YearSelector.tsx       ← Year filter
    │   │   ├── PaperTabs.tsx          ← Paper type toggle
    │   │   ├── PassFailBadge.tsx      ← Pass/fail indicator
    │   │   └── Footer.tsx             ← Tricolor + disclaimer
    │   ├── lib/
    │   │   ├── data.ts                ← Data loading + filtering
    │   │   └── constants.ts           ← Colors, model names
    │   └── types/index.ts             ← TypeScript interfaces
    └── package.json
```

## Next Steps (for next session)
1. **Set up API key** — Create `.env` with at least `GOOGLE_API_KEY` (for Gemini, cheapest for vision parsing)
2. **Parse 2024 GS1 PDF** — Write a script using Gemini or Claude to read each English page image and extract structured questions (question_number, question_text, options a/b/c/d, has_image, image_description)
3. **Parse 2024 CSAT PDF** — Same approach
4. **Build upsc_bench.json** — Merge structured questions with answer keys
5. **Run benchmark** — Execute against at least 2-3 models with real questions
6. **Update frontend** — Replace placeholder leaderboard.json with real results

## Temporary Files
- `/tmp/upsc_pages/gs1_2024/page_XX.png` — English page images from GS1 2024 PDF (23 files, DPI 150)
- These are temporary and will need to be regenerated if lost

## Important Notes
- The user prefers parallel subagent execution when possible
- The user wants to focus on 2024 only first, then add other years later
- upsc.gov.in times out consistently — use coaching institute sources instead
- Google Drive download links frequently die (404) — save downloaded files
- Homebrew installs fail due to `/opt/homebrew` permissions
- Use `/Library/Developer/CommandLineTools/usr/bin/python3` for Python operations
