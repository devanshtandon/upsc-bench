# UPSC Bench

**Can AI pass India's toughest exam?** An LLM evaluation benchmark based on India's UPSC Civil Services Examination — both Prelims (MCQ) and Mains (essay). [View the live leaderboard →](https://upsc-bench.com)

## What is this?

The UPSC Civil Services Examination selects India's top bureaucrats — IAS, IPS, and IFS officers — through a three-stage process that over a million candidates attempt each year, with a selection rate under 0.1%. UPSC Bench evaluates whether frontier AI models can pass this exam, using the real marking scheme, real cutoffs, and real questions from 2025.

What makes it hard: Prelims has negative marking (-0.66 per wrong answer), CSAT has comprehension passages, and Mains demands structured essay writing graded on a 5-dimension rubric. This isn't a trivia quiz — it's the exam that Indian aspirants spend years preparing for.

## Results at a Glance

**Prelims (GS Paper I, 2025)** — Cutoff: 90/200

| Model | GS1 Marks | Status |
|-------|-----------|--------|
| Gemini 3 Flash | 146.80 | Pass |
| Claude Opus 4.6 | 155.44 | Pass |
| Gemini 3.1 Pro | 151.44 | Pass |
| GPT-5.2 | 149.46 | Pass |
| Gemini 2.5 Flash | 140.14 | Pass |

**Mains (2025)** — Cutoff: 571/1250

| Model | Total Score | % | Status |
|-------|------------|---|--------|
| GPT-5.2 | 897.25 | 71.8% | Pass |
| Gemini 3.1 Pro | 865.12 | 69.2% | Pass |
| Claude Opus 4.6 | 828.44 | 66.3% | Pass |
| Gemini 3 Flash | 780.90 | 62.5% | Pass |
| Gemini 2.5 Flash | 735.80 | 58.9% | Pass |
| *Shakti Dubey (AIR 1, 2024)* | *602.14* | *48.2%* | *Pass* |

All five AI models pass both stages. On Mains, all models outscore the estimated human reference (CSE 2024 AIR 1, proportionally scaled to 1250 marks).

## Models Evaluated

| Model | Provider | Prelims GS1 (2025) | Mains Total (2025) |
|-------|----------|-------------------|-------------------|
| GPT-5.2 | OpenAI | 149.46/200 | 897.25/1250 |
| Gemini 3 Flash | Google | 146.80/200 | 780.90/1250 |
| Claude Opus 4.6 | Anthropic | 155.44/200 | 828.44/1250 |
| Gemini 3.1 Pro | Google | 151.44/200 | 865.12/1250 |
| Gemini 2.5 Flash | Google | 140.14/200 | 735.80/1250 |

**Human reference:** Shakti Dubey, CSE 2024 AIR 1 — Mains score proportionally estimated at 602.14/1250 (from 843/1750 total written marks).

## Dataset

- **Prelims:** 2025, 180 questions (100 GS Paper I + 80 CSAT Paper II)
- **Mains:** 2025, 87 questions (8 Essay + 20 GS1 + 20 GS2 + 20 GS3 + 19 GS4)
- **Source:** Questions from official UPSC papers, answer keys from coaching institutes (Vision IAS and others)

## Methodology

### Prelims Scoring

Uses the exact UPSC marking scheme:
- **GS Paper I:** +2.0 correct, −0.66 wrong, 0 unanswered (100 questions, max 200)
- **CSAT Paper II:** +2.5 correct, −0.83 wrong, 0 unanswered (80 questions, max 200)
- **Pass criteria:** GS1 score > year-specific General category cutoff; CSAT ≥ 66/200 (qualifying only)

Grading is deterministic — regex extraction of answer letter (A/B/C/D) compared against correct answer.

### Mains Scoring

Each model writes full answers to all 87 Mains questions:
- **Essays:** Up to 1,200 words each (best 1 from each section, mirroring real UPSC rules)
- **GS answers:** 150–250 words per question

Graded by a calibrated LLM judge (Claude Opus 4.6) using a 5-dimension rubric:

| Dimension | GS Weight | Essay Weight |
|-----------|-----------|-------------|
| Content Accuracy / Breadth | 40% | 30% |
| Structure & Flow | 20% | 20% |
| Depth & Examples | 20% | 20% |
| Analytical Depth | 10% | 20% |
| Presentation | 10% | 10% |

**Debiasing measures:**
- Model names hidden from judge (candidates labeled A/B/C/D/E)
- Candidate order shuffled with fixed seed for reproducibility
- Comparative grading: all models' answers for the same question graded in the same prompt
- UPSC-calibrated score anchors (e.g., 45–55% = adequate Mains candidate, >75% = almost never awarded)

**Total:** 1,250 marks across 5 papers (Essay 250 + GS1-4 250 each)

## Interactive Features

- **Live leaderboard** with Prelims/Mains toggle, year selector, paper breakdown
- **Interactive quiz:** Try 5 random GS1 2025 questions yourself, see how you compare to AI models

## Setup

```bash
# Clone the repo
git clone https://github.com/devanshtakkar/upsc-bench.git
cd upsc-bench

# Install Python dependencies
pip install -e .

# Copy environment template and add API keys
cp .env.example .env

# Run the Prelims benchmark
python benchmark/runner.py --model claude_opus

# Run the Mains benchmark
python -m benchmark.mains_runner --model claude_opus

# Generate leaderboard
python scripts/generate_leaderboard.py

# Run the frontend
cd web && npm install && npm run dev
```

## Project Structure

```
upsc-bench/
├── data/               # UPSC question dataset (Prelims + Mains)
│   ├── answer_keys/    # Prelims answer keys (JSON)
│   ├── processed/      # Merged Prelims questions (357 total)
│   └── mains_questions/# Mains questions (87 total)
├── pipeline/           # PDF → JSON data pipeline
├── benchmark/          # Evaluation harness (Prelims + Mains)
├── config/             # Model configs + cutoffs + grading rubric
├── results/            # Benchmark results (leaderboard.json)
├── scripts/            # Leaderboard generation, grading, utilities
└── web/                # Next.js leaderboard frontend
```

## Disclaimer

This is an independent research project. Not affiliated with UPSC or the Government of India. Question papers are sourced from publicly available PDFs. Answer keys are from coaching institutes and may contain errors for disputed questions.

## License

MIT
