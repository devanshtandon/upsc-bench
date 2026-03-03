"""Orchestrator: runs the full UPSC Bench data pipeline.

Pipeline: PDFs → Reducto extraction → LLM structuring → answer key merge → validation
"""

import argparse
import json
import sys
from pathlib import Path

from pipeline.extract_pdf import extract_all_pdfs
from pipeline.structure_questions import structure_all
from pipeline.merge_answer_keys import merge_answer_keys
from pipeline.validate_dataset import validate_dataset


def build_dataset(
    pdf_dir: str = "data/pdfs",
    images_dir: str = "data/images",
    answer_keys_dir: str = "data/answer_keys",
    output_dir: str = "data/processed",
    model: str = "anthropic/claude-sonnet-4-20250514",
    skip_extraction: bool = False,
    skip_structuring: bool = False,
) -> bool:
    """Run the full data pipeline to produce upsc_bench.json.

    Args:
        pdf_dir: Directory containing UPSC PDFs organized by year.
        images_dir: Directory to save extracted images.
        answer_keys_dir: Directory containing answer key JSONs.
        output_dir: Directory for output files.
        model: LiteLLM model for question structuring.
        skip_extraction: Skip PDF extraction (use existing raw_extractions.json).
        skip_structuring: Skip LLM structuring (use existing per-paper JSONs).

    Returns:
        True if pipeline completes successfully.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    extractions_path = f"{output_dir}/raw_extractions.json"
    unvalidated_path = f"{output_dir}/upsc_bench_unvalidated.json"
    final_path = f"{output_dir}/upsc_bench.json"

    # Step 1: Extract PDFs
    if not skip_extraction:
        print("\n" + "="*60)
        print("STEP 1: Extracting PDFs via Reducto")
        print("="*60)
        results = extract_all_pdfs(pdf_dir, images_dir)
        with open(extractions_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved raw extractions to {extractions_path}")
    else:
        print("Skipping PDF extraction (using existing data)")

    # Step 2: Structure questions
    if not skip_structuring:
        print("\n" + "="*60)
        print("STEP 2: Structuring questions via LLM")
        print("="*60)
        all_questions = structure_all(extractions_path, output_dir, model)
        print(f"Total structured: {len(all_questions)} questions")
    else:
        print("Skipping LLM structuring (using existing data)")

    # Step 3: Merge answer keys
    print("\n" + "="*60)
    print("STEP 3: Merging answer keys")
    print("="*60)

    # Load all per-paper question files
    all_questions = []
    for qfile in sorted(Path(output_dir).glob("*_*.json")):
        if "upsc_bench" in qfile.name or "raw_extraction" in qfile.name:
            continue
        with open(qfile) as f:
            all_questions.extend(json.load(f))

    merged = merge_answer_keys(all_questions, answer_keys_dir)
    with open(unvalidated_path, "w") as f:
        json.dump(merged, f, indent=2)

    # Step 4: Validate
    print("\n" + "="*60)
    print("STEP 4: Validating dataset")
    print("="*60)

    valid = validate_dataset(unvalidated_path, images_dir)

    if valid:
        # Copy to final path
        with open(unvalidated_path) as f:
            data = json.load(f)
        with open(final_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n✓ Dataset saved to {final_path}")
    else:
        print(f"\n✗ Validation failed. Check {unvalidated_path} for issues.")

    return valid


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build UPSC Bench dataset")
    parser.add_argument("--pdf-dir", default="data/pdfs")
    parser.add_argument("--images-dir", default="data/images")
    parser.add_argument("--answer-keys-dir", default="data/answer_keys")
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--model", default="anthropic/claude-sonnet-4-20250514")
    parser.add_argument("--skip-extraction", action="store_true")
    parser.add_argument("--skip-structuring", action="store_true")
    args = parser.parse_args()

    success = build_dataset(
        pdf_dir=args.pdf_dir,
        images_dir=args.images_dir,
        answer_keys_dir=args.answer_keys_dir,
        output_dir=args.output_dir,
        model=args.model,
        skip_extraction=args.skip_extraction,
        skip_structuring=args.skip_structuring,
    )
    sys.exit(0 if success else 1)
