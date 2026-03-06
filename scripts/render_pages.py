#!/usr/bin/env python3
"""Render PDF pages as PNG images at 200 DPI for visual extraction."""

import fitz  # PyMuPDF
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PDFS = [
    {
        "path": os.path.join(BASE, "data/pdfs/2025/gs_paper1_2025.pdf"),
        "output_dir": os.path.join(BASE, "data/parsed/gs1_2025_pages"),
    },
    {
        "path": os.path.join(BASE, "data/pdfs/2025/csat_paper2_2025.pdf"),
        "output_dir": os.path.join(BASE, "data/parsed/csat_2025_pages"),
    },
]

DPI = 200

def render_pdf(pdf_path, output_dir):
    doc = fitz.open(pdf_path)
    count = doc.page_count
    print(f"Rendering {pdf_path} ({count} pages) at {DPI} DPI...")
    os.makedirs(output_dir, exist_ok=True)

    for i, page in enumerate(doc):
        mat = fitz.Matrix(DPI / 72, DPI / 72)
        pix = page.get_pixmap(matrix=mat)
        out_path = os.path.join(output_dir, f"page_{i+1:02d}.png")
        pix.save(out_path)
        print(f"  Saved {out_path} ({pix.width}x{pix.height})")

    doc.close()
    return count

if __name__ == "__main__":
    total = 0
    for pdf in PDFS:
        count = render_pdf(pdf["path"], pdf["output_dir"])
        total += count
    print(f"\nDone. Rendered {total} pages total.")
