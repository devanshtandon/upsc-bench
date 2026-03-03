#!/usr/bin/env python3
"""Clean GS1 2025 data quality issues in upsc_bench.json.

Fixes systematic PDF parsing artifacts in GS1 2025 questions only.
All other data (2024, CSAT 2025, answer keys) passes through untouched.

Issues fixed:
  1. Word-per-line formatting → flowing text with structural breaks preserved
  2. Roman numeral corruption: III→Ill/m/ill, II→n, I→l
  3. Garbage text: LVPK booklet codes, stray ~1
  4. Bracket OCR: {INSTC} → (INSTC)
  5. Tilde OCR artifacts: ~raon→person, farmin~→farming, etc.
  6. Hyphenated line breaks in options: Recon- struction → Reconstruction
  7. Q93 option (d) merged with Q94 text → truncated
  8. Q93 garbled words: reprdjng→regarding, proceed•→proceeds, etc.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "upsc_bench.json"
WEB_DATA_PATH = ROOT / "web" / "data" / "upsc_bench.json"


# ---------------------------------------------------------------------------
# Newline normalisation
# ---------------------------------------------------------------------------

STRUCTURAL_PATTERNS = [
    r"^(I|II|III|IV|V)\.(\s|$)",      # Roman numeral label
    r"^Statement\s+(I|II|III|IV)",     # Statement I/II/III
    r"^(Which|Select|How many)",       # Question starters
    r"^(Consider|With reference)",     # Context intros
    r"^(In the context|In how many)",  # More intros
    r"^(From the|The correct|None of)",
    r"^(Code|Note|Passage|Match)\s*:", # Section labels
]


def is_structural_start(line: str) -> bool:
    """Check if a line should begin a new block."""
    return any(re.match(p, line) for p in STRUCTURAL_PATTERNS)


def normalize_newlines(text: str) -> str:
    """Collapse word-per-line PDF artifacts into flowing text.

    Preserves intentional line breaks before structural markers
    (Roman numerals, statement labels, question prompts, etc.).
    """
    lines = text.split("\n")
    blocks: list[str] = []
    current = ""

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            # Empty line → paragraph break
            if current:
                blocks.append(current)
                current = ""
            continue

        if is_structural_start(line) and current:
            blocks.append(current)
            current = line
        elif current:
            current = current + " " + line
        else:
            current = line

    if current:
        blocks.append(current)

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Roman numeral fixes – question text
# ---------------------------------------------------------------------------

def fix_roman_numerals_in_text(text: str) -> str:
    """Fix III corruption in question text (Ill. / \\nm. → III.)."""
    # Ill. as statement label (start of line or after newline)
    text = re.sub(r"^Ill\.", "III.", text)
    text = re.sub(r"\nIll\.", "\nIII.", text)

    # Statement Ill → Statement III
    text = re.sub(r"Statement Ill\b", "Statement III", text)

    # \nm. as statement label → \nIII.
    text = re.sub(r"\nm\.\s", "\nIII. ", text)

    return text


# ---------------------------------------------------------------------------
# Roman numeral fixes – options
# ---------------------------------------------------------------------------

def fix_roman_numerals_in_options(options: dict) -> dict:
    """Fix I/II/III corruption in option values."""
    fixed = {}
    for key, value in options.items():
        v = value

        # l → I  (lowercase L to Roman numeral I)
        # Only at start of option, before comma/and/only + other Roman numerals
        v = re.sub(r"^l(,\s*)", r"I\1", v)               # "l, II..."
        v = re.sub(r"^l\s+and\s+", "I and ", v)           # "l and II..."
        v = re.sub(r"^l\s+only\b", "I only", v)           # "l only"

        # n → II  (Q93: "n and m only")
        v = re.sub(r"^n\s+and\s+", "II and ", v)

        # ill / Ill → III
        v = re.sub(r"\bill\b", "III", v)
        v = re.sub(r"\bIll\b", "III", v)

        # m → III  (in Roman numeral list context)
        v = re.sub(r"\band m\b", "and III", v)
        v = re.sub(r",\s*m\b", ", III", v)

        fixed[key] = v
    return fixed


# ---------------------------------------------------------------------------
# Garbage text removal
# ---------------------------------------------------------------------------

def remove_garbage_text(options: dict) -> dict:
    """Strip LVPK booklet codes and stray artifacts from options."""
    fixed = {}
    for key, value in options.items():
        v = value
        # LVPK codes (several OCR variants)
        v = re.sub(r"\s*LVPK[-\s]*[O0][-\s]*PS[O0][\s/]*56\s*A\s*", "", v)
        # Stray ~1
        v = re.sub(r"\s*~1\s*$", "", v)
        fixed[key] = v.strip()
    return fixed


# ---------------------------------------------------------------------------
# Hyphenated line breaks in options
# ---------------------------------------------------------------------------

HYPHENATED_FIXES = {
    "Recon- struction": "Reconstruction",
    "Invest- ment": "Investment",
    "State- ment": "Statement",
    "hydro- fluorocarbon": "hydrofluorocarbon",
}


def fix_hyphenated_options(options: dict) -> dict:
    """Fix hyphenated line-break artifacts in option values."""
    fixed = {}
    for key, value in options.items():
        v = value
        for old, new in HYPHENATED_FIXES.items():
            v = v.replace(old, new)
        fixed[key] = v
    return fixed


# ---------------------------------------------------------------------------
# Tilde OCR artifacts in question text
# ---------------------------------------------------------------------------

TILDE_FIXES = {
    "~raon": "person",
    "farmin~": "farming",
    "exclusiv~ly": "exclusively",
    "J~uary": "January",
}


def fix_tilde_artifacts(text: str) -> str:
    """Fix tilde OCR artifacts in question text."""
    for old, new in TILDE_FIXES.items():
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------------------
# Bracket OCR
# ---------------------------------------------------------------------------

def fix_bracket_ocr(text: str) -> str:
    """Fix mismatched brackets from OCR (e.g. {INSTC} → (INSTC))."""
    text = text.replace("(INSTC}", "(INSTC)")
    text = text.replace("{INSTC)", "(INSTC)")
    text = text.replace("{INSTC}", "(INSTC)")
    return text


# ---------------------------------------------------------------------------
# Q93 special handling (multiple severe corruptions)
# ---------------------------------------------------------------------------

def fix_q93(question: dict) -> dict:
    """Apply targeted fixes to Q93 (garbled words + merged Q94 in option d)."""
    # --- question text ---
    text = question["question_text"]
    text = text.replace("following·", "following")
    text = text.replace("level•", "level")
    text = text.replace("proceed•", "proceeds")
    text = text.replace("reprdjng", "regarding")
    # "ol" → "of" only in known context
    text = text.replace(" ol\n", " of\n")
    text = text.replace(" ol ", " of ")
    question["question_text"] = text

    # --- option d: truncate merged Q94 text ---
    opt_d = question["options"]["d"]
    idx = opt_d.find("Consider the following")
    if idx > 0:
        question["options"]["d"] = opt_d[:idx].strip()

    return question


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def clean_question(q: dict) -> dict:
    """Apply all fixes to a single GS1 2025 question."""
    if q["year"] != 2025 or q["paper"] != "gs1":
        return q

    # Deep copy to avoid mutating original
    q = {**q, "options": {**q["options"]}}

    # Q93 special handling first (truncates merged text before other fixes)
    if q["question_number"] == 93:
        q = fix_q93(q)

    # --- Question text fixes ---
    text = q["question_text"]
    text = fix_tilde_artifacts(text)
    text = fix_bracket_ocr(text)
    text = fix_roman_numerals_in_text(text)
    text = normalize_newlines(text)
    q["question_text"] = text

    # --- Option fixes ---
    q["options"] = remove_garbage_text(q["options"])
    q["options"] = fix_roman_numerals_in_options(q["options"])
    q["options"] = fix_hyphenated_options(q["options"])

    return q


def print_diff(original: dict, cleaned: dict) -> None:
    """Print before/after diff for a question."""
    qnum = original["question_number"]
    changes = []

    if original["question_text"] != cleaned["question_text"]:
        changes.append(("text", original["question_text"], cleaned["question_text"]))

    for key in ["a", "b", "c", "d"]:
        if original["options"][key] != cleaned["options"][key]:
            changes.append(
                (f"opt {key}", original["options"][key], cleaned["options"][key])
            )

    if changes:
        print(f"\n{'='*60}")
        print(f"Q{qnum}")
        print(f"{'='*60}")
        for field, before, after in changes:
            print(f"  [{field}]")
            # For text, show truncated versions
            if field == "text":
                b = repr(before[:200]) + ("..." if len(before) > 200 else "")
                a = repr(after[:200]) + ("..." if len(after) > 200 else "")
            else:
                b = repr(before)
                a = repr(after)
            print(f"    BEFORE: {b}")
            print(f"    AFTER:  {a}")


def main():
    print(f"Loading {DATA_PATH}")
    with open(DATA_PATH) as f:
        data = json.load(f)

    gs1_2025_count = sum(1 for q in data if q["year"] == 2025 and q["paper"] == "gs1")
    print(f"Total questions: {len(data)}")
    print(f"GS1 2025 questions: {gs1_2025_count}")

    # Clean
    cleaned_data = []
    changed_count = 0

    for q in data:
        cleaned = clean_question(q)
        if q["year"] == 2025 and q["paper"] == "gs1":
            if (q["question_text"] != cleaned["question_text"] or
                    q["options"] != cleaned["options"]):
                changed_count += 1
                print_diff(q, cleaned)
        cleaned_data.append(cleaned)

    print(f"\n{'='*60}")
    print(f"Summary: {changed_count}/{gs1_2025_count} GS1 2025 questions modified")
    print(f"{'='*60}")

    # Verify non-GS1-2025 data is untouched
    for orig, clean in zip(data, cleaned_data):
        if orig["year"] != 2025 or orig["paper"] != "gs1":
            assert orig == clean, f"Non-GS1-2025 question {orig['id']} was modified!"
    print("✓ All non-GS1-2025 questions verified untouched")

    # Write
    with open(DATA_PATH, "w") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Written to {DATA_PATH}")

    with open(WEB_DATA_PATH, "w") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Written to {WEB_DATA_PATH}")


if __name__ == "__main__":
    main()
