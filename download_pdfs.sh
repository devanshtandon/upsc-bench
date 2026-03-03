#!/bin/bash
set -e

BASE="/Users/devansht/Desktop/upsc-bench/data/pdfs"

download_with_fallback() {
    local output="$1"
    local primary="$2"
    local fallback="$3"
    
    echo "Downloading: $output"
    if curl -L --connect-timeout 10 -o "$output" "$primary" 2>/dev/null; then
        size=$(stat -f%z "$output" 2>/dev/null || echo 0)
        if [ "$size" -gt 102400 ]; then
            echo "  SUCCESS (primary): $(du -h "$output" | cut -f1)"
            return 0
        fi
    fi
    
    if [ -n "$fallback" ]; then
        echo "  Primary failed, trying fallback..."
        if curl -L --connect-timeout 15 -o "$output" "$fallback" 2>/dev/null; then
            size=$(stat -f%z "$output" 2>/dev/null || echo 0)
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

echo "=== GS Paper 1 Downloads ==="

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
echo "=== CSAT Paper 2 Downloads ==="

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
echo "=== Verification ==="
echo "File listing:"
ls -lh $BASE/*/
echo ""
echo "File type check:"
for f in $BASE/*/*.pdf; do
    echo "  $(file "$f")"
done
