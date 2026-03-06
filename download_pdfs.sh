#!/bin/bash
set -e

BASE="$(cd "$(dirname "$0")" && pwd)/data/pdfs"
ANSKEY_BASE="$(cd "$(dirname "$0")" && pwd)/data/answer_keys/pdfs"

mkdir -p "$BASE"/{2020,2021,2022,2023,2024,2025/mains}
mkdir -p "$ANSKEY_BASE"

download_with_fallback() {
    local output="$1"
    local primary="$2"
    local fallback="$3"

    if [ -f "$output" ]; then
        size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output" 2>/dev/null || echo 0)
        if [ "$size" -gt 102400 ]; then
            echo "  SKIP (exists): $output ($(du -h "$output" | cut -f1))"
            return 0
        fi
    fi

    echo "Downloading: $output"
    if curl -L --connect-timeout 10 -o "$output" "$primary" 2>/dev/null; then
        size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output" 2>/dev/null || echo 0)
        if [ "$size" -gt 102400 ]; then
            echo "  SUCCESS (primary): $(du -h "$output" | cut -f1)"
            return 0
        fi
    fi

    if [ -n "$fallback" ]; then
        echo "  Primary failed, trying fallback..."
        if curl -L --connect-timeout 15 -o "$output" "$fallback" 2>/dev/null; then
            size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output" 2>/dev/null || echo 0)
            if [ "$size" -gt 102400 ]; then
                echo "  SUCCESS (fallback): $(du -h "$output" | cut -f1)"
                return 0
            fi
        fi
    fi

    echo "  FAILED: $output"
    rm -f "$output"
    return 1
}

echo "=== Prelims — GS Paper 1 ==="

download_with_fallback "$BASE/2025/gs_paper1_2025.pdf" \
    "https://www.clearias.com/up/upsc-cse-2025-prelims-gs-question-paper.pdf" \
    ""

download_with_fallback "$BASE/2024/gs_paper1_2024.pdf" \
    "https://upsc.gov.in/sites/default/files/QP-CSP-24-GENERAL-STUDIES-PAPER-I-180624.pdf" \
    "https://www.clearias.com/up/upsc-cse-2024-prelims-gs-question-paper.pdf"

download_with_fallback "$BASE/2023/gs_paper1_2023.pdf" \
    "https://upsc.gov.in/sites/default/files/QP_CS_Pre_Exam_2023_280523.pdf" \
    "https://www.clearias.com/up/UPSC-CSE-Prelims-2023-Quesstion-Paper-General-Studies-Paper-1.pdf"

download_with_fallback "$BASE/2022/gs_paper1_2022.pdf" \
    "https://upsc.gov.in/sites/default/files/GENERAL%20STUDIES%20PAPER%20I.pdf" \
    "https://spmiasacademy.com/wp-content/uploads/2025/04/GS1-22-1.pdf"

download_with_fallback "$BASE/2021/gs_paper1_2021.pdf" \
    "https://upsc.gov.in/sites/default/files/QP-CSP-21-GeneralStudiesPaper-I-121021.pdf" \
    "https://spmiasacademy.com/wp-content/uploads/2025/04/GS1-21.pdf"

download_with_fallback "$BASE/2020/gs_paper1_2020.pdf" \
    "https://upsc.gov.in/sites/default/files/CSP_2020_GS_Paper-1.pdf" \
    "https://spmiasacademy.com/wp-content/uploads/2025/04/GS1-2020.pdf"

echo ""
echo "=== Prelims — CSAT Paper 2 ==="

download_with_fallback "$BASE/2025/csat_paper2_2025.pdf" \
    "https://www.clearias.com/up/upsc-cse-2025-prelims-csat-question-paper.pdf" \
    ""

download_with_fallback "$BASE/2024/csat_paper2_2024.pdf" \
    "https://www.clearias.com/up/upsc-cse-2024-prelims-csat-question-paper.pdf" \
    ""

download_with_fallback "$BASE/2023/csat_paper2_2023.pdf" \
    "https://www.clearias.com/up/UPSC-CSE-Prelims-2023-Quesstion-Paper-General-Studies-Paper-2-CSAT.pdf" \
    ""

download_with_fallback "$BASE/2022/csat_paper2_2022.pdf" \
    "https://spmiasacademy.com/wp-content/uploads/2025/04/CSAT-2022-1.pdf" \
    ""

download_with_fallback "$BASE/2020/csat_paper2_2020.pdf" \
    "https://spmiasacademy.com/wp-content/uploads/2025/04/CSAT-2020-2-1.pdf" \
    ""

echo ""
echo "=== Mains 2025 ==="

download_with_fallback "$BASE/2025/mains/essay_2025.pdf" \
    "https://www.insightsonindia.com/wp-content/uploads/2025/08/UPSC-Mains-2025-Essay-Question-Paper-updated.pdf" \
    ""

download_with_fallback "$BASE/2025/mains/gs1_2025.pdf" \
    "https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-1-2025-QP.pdf" \
    ""

download_with_fallback "$BASE/2025/mains/gs2_2025.pdf" \
    "https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-2-Mains-2025-Insights-IAS.pdf" \
    ""

download_with_fallback "$BASE/2025/mains/gs3_2025.pdf" \
    "https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-3-Mains-2025-insights-ias.pdf" \
    ""

download_with_fallback "$BASE/2025/mains/gs4_2025.pdf" \
    "https://www.insightsonindia.com/wp-content/uploads/2025/08/GS-4-INSIGHTS-IAS-MAINS-2025.pdf" \
    ""

echo ""
echo "=== Verification ==="
echo "File listing:"
find "$BASE" -name "*.pdf" -exec ls -lh {} \; | sort
echo ""
echo "File type check:"
find "$BASE" -name "*.pdf" | sort | while read f; do
    echo "  $(file "$f")"
done
echo ""
echo "Total size:"
du -sh "$BASE"
