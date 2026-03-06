# Data Sources

All question papers used in UPSC Bench are sourced from publicly available PDFs. This document records the provenance of every data file in the repository.

## Prelims Question Papers

| File | Year | Paper | Source | Fallback |
|------|------|-------|--------|----------|
| `data/pdfs/2025/gs_paper1_2025.pdf` | 2025 | GS Paper I | ClearIAS | — |
| `data/pdfs/2025/csat_paper2_2025.pdf` | 2025 | CSAT Paper II | ClearIAS | — |
| `data/pdfs/2024/gs_paper1_2024.pdf` | 2024 | GS Paper I | [UPSC.gov.in](https://upsc.gov.in/sites/default/files/QP-CSP-24-GENERAL-STUDIES-PAPER-I-180624.pdf) | [ClearIAS](https://www.clearias.com/up/upsc-cse-2024-prelims-gs-question-paper.pdf) |
| `data/pdfs/2024/csat_paper2_2024.pdf` | 2024 | CSAT Paper II | [ClearIAS](https://www.clearias.com/up/upsc-cse-2024-prelims-csat-question-paper.pdf) | — |
| `data/pdfs/2023/gs_paper1_2023.pdf` | 2023 | GS Paper I | [UPSC.gov.in](https://upsc.gov.in/sites/default/files/QP_CS_Pre_Exam_2023_280523.pdf) | [ClearIAS](https://www.clearias.com/up/UPSC-CSE-Prelims-2023-Quesstion-Paper-General-Studies-Paper-1.pdf) |
| `data/pdfs/2022/gs_paper1_2022.pdf` | 2022 | GS Paper I | [UPSC.gov.in](https://upsc.gov.in/sites/default/files/GENERAL%20STUDIES%20PAPER%20I.pdf) | [SPM IAS Academy](https://spmiasacademy.com/wp-content/uploads/2025/04/GS1-22-1.pdf) |

**Note:** UPSC.gov.in is the official source but is often geo-restricted to India. Coaching institute mirrors (ClearIAS, SPM IAS Academy) host identical copies of the publicly released papers.

## Mains Question Papers (2025)

All Mains 2025 papers sourced from [Insights on India (InsightsIAS)](https://www.insightsonindia.com/), a leading UPSC coaching institute.

| File | Paper | Source URL |
|------|-------|-----------|
| `data/pdfs/2025/mains/essay_2025.pdf` | Essay | [InsightsIAS](https://www.insightsonindia.com/wp-content/uploads/2025/08/UPSC-Mains-2025-Essay-Question-Paper-updated.pdf) |
| `data/pdfs/2025/mains/gs1_2025.pdf` | GS Paper I | [InsightsIAS](https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-1-2025-QP.pdf) |
| `data/pdfs/2025/mains/gs2_2025.pdf` | GS Paper II | [InsightsIAS](https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-2-Mains-2025-Insights-IAS.pdf) |
| `data/pdfs/2025/mains/gs3_2025.pdf` | GS Paper III | [InsightsIAS](https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-3-Mains-2025-insights-ias.pdf) |
| `data/pdfs/2025/mains/gs4_2025.pdf` | GS Paper IV (Ethics) | [InsightsIAS](https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-4-INSIGHTS-IAS-MAINS-2025.pdf) |

## Answer Keys

| File | Year | Paper | Source |
|------|------|-------|--------|
| `data/answer_keys/gs1_2025.json` | 2025 | GS Paper I | Vision IAS / coaching consensus |
| `data/answer_keys/csat_2025.json` | 2025 | CSAT Paper II | Vision IAS / coaching consensus |
| `data/answer_keys/gs1_2024.json` | 2024 | GS Paper I | Vision IAS / coaching consensus |
| `data/answer_keys/csat_2024.json` | 2024 | CSAT Paper II | Vision IAS / coaching consensus |

Raw answer key PDFs are stored in `data/answer_keys/pdfs/`.

**Note:** UPSC does not release official answer keys for Prelims. All answer keys are from coaching institutes and represent the community consensus. For disputed questions (where coaching institutes disagree), we follow the majority answer.

## Processed Dataset

| File | Description |
|------|-------------|
| `data/processed/upsc_bench.json` | 357 Prelims questions (2024 + 2025, GS1 + CSAT) — extracted from PDFs via multimodal LLM pipeline |
| `data/mains_questions/mains_2025.json` | 87 Mains 2025 questions (Essay + GS1-4) — transcribed from coaching institute reproductions |

## Data Pipeline

Prelims questions are extracted from PDFs using:
1. `pipeline/extract_pdf.py` — PDF → page images
2. `pipeline/structure_questions.py` — LLM-based question structuring (handles OCR artifacts, image-based questions)
3. `pipeline/merge_answer_keys.py` — Merge extracted questions with answer keys
4. `pipeline/validate_dataset.py` — Consistency checks
5. `pipeline/build_dataset.py` — Orchestrates the full pipeline

Mains questions were manually transcribed from coaching institute PDFs and structured into JSON.

## Re-downloading PDFs

If you need to re-download any missing PDFs:

```bash
bash download_pdfs.sh
```

This script skips files that already exist locally and tries fallback URLs if the primary source is unavailable.
