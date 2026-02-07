# UPSC Bench

**Can AI pass India's toughest exam?**

An LLM evaluation benchmark based on India's UPSC Civil Services Preliminary Examination. Ranks frontier LLMs using real UPSC marking scheme, compares against actual cutoffs, and presents results on a leaderboard.

## Dataset

- **Scope**: Prelims only — GS Paper I + CSAT Paper II
- **Years**: 2020–2024 (~900 total questions)
- **Scoring**: Real UPSC scheme: +2 correct, −0.66 wrong, 0 unanswered
- **Grading**: Deterministic string match (no LLM grader needed)

## Models Evaluated

| Model | Provider |
|-------|----------|
| GPT-4o | OpenAI |
| Claude Opus 4 | Anthropic |
| Claude Sonnet 4 | Anthropic |
| Gemini 2.5 Pro | Google |
| Gemini 2.0 Flash | Google |
| DeepSeek R1 | DeepSeek |

## Setup

```bash
# Install Python dependencies
uv sync

# Copy environment template
cp .env.example .env
# Fill in your API keys

# Run the benchmark
python benchmark/runner.py --config config/claude_opus.yaml

# Generate leaderboard
python scripts/generate_leaderboard.py

# Run the frontend
cd web && npm install && npm run dev
```

## Project Structure

```
upsc-bench/
├── data/           # UPSC question dataset
├── pipeline/       # PDF → JSON data pipeline
├── benchmark/      # Evaluation harness
├── config/         # Model configs (YAML)
├── results/        # Benchmark results
├── scripts/        # Utility scripts
├── db/             # SQLite database
└── web/            # Next.js leaderboard frontend
```

## Scoring

- GS Paper I: +2.0 per correct, −0.66 per wrong, 0 unanswered
- CSAT Paper II: +2.5 per correct, −0.83 per wrong, 0 unanswered
- Pass/Fail: Compared against year-specific General category cutoffs

## Disclaimer

This is an independent research project. Not affiliated with UPSC or the Government of India.
