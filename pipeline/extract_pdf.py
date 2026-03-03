"""Extract structured content from UPSC PDF papers using Reducto AI."""

import json
import os
import requests
from pathlib import Path


REDUCTO_API_URL = "https://platform.reducto.ai/parse"


def extract_pdf(pdf_path: str, output_dir: str) -> dict:
    """Extract markdown and images from a UPSC PDF using Reducto.

    Args:
        pdf_path: Path to the UPSC PDF file.
        output_dir: Directory to save extracted images.

    Returns:
        Dict with 'markdown' (full text) and 'images' (list of saved image paths).
    """
    api_key = os.environ.get("REDUCTO_API_KEY")
    if not api_key:
        raise ValueError("REDUCTO_API_KEY environment variable not set")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with open(pdf_path, "rb") as f:
        response = requests.post(
            REDUCTO_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (Path(pdf_path).name, f, "application/pdf")},
            data={"return_images": "true"},
            timeout=300,
        )
    response.raise_for_status()
    result = response.json()

    # Extract markdown content from result
    blocks = result.get("result", {}).get("blocks", [])
    markdown_parts = []
    for block in blocks:
        content = block.get("content", "")
        if content:
            markdown_parts.append(content)
    markdown = "\n\n".join(markdown_parts)

    # Download and save images
    saved_images = []
    images = result.get("result", {}).get("images", [])
    for i, img_data in enumerate(images):
        img_url = img_data.get("url", "")
        if not img_url:
            continue
        img_response = requests.get(img_url, timeout=60)
        img_response.raise_for_status()

        img_name = img_data.get("name", f"image_{i}.png")
        img_path = os.path.join(output_dir, img_name)
        with open(img_path, "wb") as img_file:
            img_file.write(img_response.content)
        saved_images.append(img_path)

    return {"markdown": markdown, "images": saved_images}


def extract_all_pdfs(pdf_dir: str, images_base_dir: str) -> dict[str, dict]:
    """Extract all UPSC PDFs from a directory structure.

    Expects: pdf_dir/{year}/{filename}.pdf
    Saves images to: images_base_dir/{year}/{paper}/

    Returns:
        Dict mapping pdf filename to extraction results.
    """
    results = {}
    pdf_base = Path(pdf_dir)

    for year_dir in sorted(pdf_base.iterdir()):
        if not year_dir.is_dir():
            continue
        year = year_dir.name

        for pdf_file in sorted(year_dir.glob("*.pdf")):
            paper = "gs1" if "gs" in pdf_file.stem.lower() else "csat"
            img_dir = os.path.join(images_base_dir, year, paper)

            print(f"Extracting {pdf_file.name}...")
            result = extract_pdf(str(pdf_file), img_dir)
            results[pdf_file.name] = result
            print(f"  → {len(result['images'])} images extracted")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract UPSC PDFs via Reducto")
    parser.add_argument("--pdf-dir", default="data/pdfs", help="Directory containing PDFs")
    parser.add_argument("--images-dir", default="data/images", help="Directory to save images")
    parser.add_argument("--output", default="data/processed/raw_extractions.json", help="Output JSON")
    args = parser.parse_args()

    results = extract_all_pdfs(args.pdf_dir, args.images_dir)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved extractions to {args.output}")
