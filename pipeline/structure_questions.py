"""Structure raw markdown from UPSC PDFs into question JSON schema using LLM."""

import json
import os
from pathlib import Path

import litellm


STRUCTURING_PROMPT = """You are a UPSC exam question parser. Given raw markdown text extracted from a UPSC Preliminary Examination paper, extract ALL questions into structured JSON.

For each question, output a JSON object with these fields:
- question_number: integer
- question_text: the full question text (preserve formatting, include "Consider the following statements:" preambles)
- options: object with keys "a", "b", "c", "d" mapping to option text
- has_image: boolean, true if the question references a figure/map/diagram/image
- image_description: if has_image is true, describe what the referenced image shows based on context clues

Rules:
- Preserve exact question text, including numbered statements within questions
- Options may be labeled (a), (b), (c), (d) or (1), (2), (3), (4) — normalize to a/b/c/d
- Some questions have "Which of the statements given above..." patterns — include the full text
- For passage-based questions, include the full passage in question_text
- Output a JSON array of question objects, nothing else

Raw markdown:
{markdown_chunk}"""


def structure_questions(
    markdown: str,
    year: int,
    paper: str,
    model: str = "anthropic/claude-sonnet-4-20250514",
) -> list[dict]:
    """Use an LLM to structure raw markdown into question JSON.

    Args:
        markdown: Raw markdown text from PDF extraction.
        year: Exam year (e.g., 2024).
        paper: Paper type ("gs1" or "csat").
        model: LiteLLM model identifier.

    Returns:
        List of structured question dicts.
    """
    # Split markdown into chunks if very long (to stay within context limits)
    max_chunk_len = 30000
    chunks = []
    if len(markdown) > max_chunk_len:
        # Split at double newlines near the limit
        words = markdown.split("\n\n")
        current_chunk = []
        current_len = 0
        for para in words:
            if current_len + len(para) > max_chunk_len and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_len = len(para)
            else:
                current_chunk.append(para)
                current_len += len(para)
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
    else:
        chunks = [markdown]

    all_questions = []
    for chunk in chunks:
        prompt = STRUCTURING_PROMPT.format(markdown_chunk=chunk)
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        raw_output = response.choices[0].message.content
        try:
            parsed = json.loads(raw_output)
            # Handle both {"questions": [...]} and [...] formats
            questions = parsed if isinstance(parsed, list) else parsed.get("questions", [])
            all_questions.extend(questions)
        except json.JSONDecodeError:
            print(f"Warning: Failed to parse LLM output for {year}/{paper} chunk")
            continue

    # Add metadata to each question
    structured = []
    for q in all_questions:
        qnum = q.get("question_number", 0)
        structured.append({
            "id": f"{paper}_{year}_q{qnum:03d}",
            "year": year,
            "paper": paper,
            "question_number": qnum,
            "question_text": q.get("question_text", ""),
            "options": q.get("options", {}),
            "correct_answer": "",  # Filled in by merge_answer_keys
            "answer_source": "",
            "has_image": q.get("has_image", False),
            "image_paths": [],  # Filled in later
            "image_description": q.get("image_description", ""),
            "marks_correct": 2.0 if paper == "gs1" else 2.5,
            "marks_wrong": -0.66 if paper == "gs1" else -0.83,
            "marks_unanswered": 0.0,
            "source_pdf": "",
            "source_page": 0,
        })

    return structured


def structure_all(
    extractions_path: str,
    output_dir: str,
    model: str = "anthropic/claude-sonnet-4-20250514",
) -> list[dict]:
    """Structure all extracted PDFs into question JSON files.

    Args:
        extractions_path: Path to raw_extractions.json from extract_pdf.py.
        output_dir: Directory to save per-paper JSON files.
        model: LiteLLM model to use for structuring.

    Returns:
        List of all structured questions.
    """
    with open(extractions_path) as f:
        extractions = json.load(f)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    all_questions = []

    for filename, data in extractions.items():
        # Parse year and paper from filename like "gs_paper1_2024.pdf"
        parts = filename.replace(".pdf", "").split("_")
        year = int([p for p in parts if p.isdigit() and len(p) == 4][0])
        paper = "gs1" if "gs" in filename.lower() else "csat"

        print(f"Structuring {filename} ({year}/{paper})...")
        questions = structure_questions(data["markdown"], year, paper, model)

        # Save individual file
        out_path = os.path.join(output_dir, f"{paper}_{year}.json")
        with open(out_path, "w") as f:
            json.dump(questions, f, indent=2)
        print(f"  → {len(questions)} questions structured")

        all_questions.extend(questions)

    return all_questions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Structure UPSC questions from raw markdown")
    parser.add_argument("--extractions", default="data/processed/raw_extractions.json")
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--model", default="anthropic/claude-sonnet-4-20250514")
    args = parser.parse_args()

    questions = structure_all(args.extractions, args.output_dir, args.model)
    print(f"Total: {len(questions)} questions structured")
