#!/bin/bash
# Run all models on 2025 questions only.
# Creates temporary configs with filter_years: [2025] and separate output files.
# After running, use scripts/combine_results.py to merge with 2024 results.

set -e

cd "$(dirname "$0")/.."

MODELS=("claude_opus" "gemini_3_pro" "gemini_flash" "gpt5" "grok4")

for model in "${MODELS[@]}"; do
    config="config/${model}.yaml"
    config_2025="config/${model}_2025.yaml"

    if [ ! -f "$config" ]; then
        echo "Config not found: $config, skipping"
        continue
    fi

    # Create 2025-specific config
    sed -e 's|output_filepath: "results/raw/results_'"${model}"'.json"|output_filepath: "results/raw/results_'"${model}"'_2025.json"|' \
        -e 's|filter_years: null|filter_years: [2025]|' \
        "$config" > "$config_2025"

    echo "Running $model on 2025 questions..."
    PYTHONPATH=. /Library/Developer/CommandLineTools/usr/bin/python3 -m benchmark.runner --config "$config_2025"

    # Clean up temp config
    rm "$config_2025"

    echo "Done: $model"
    echo "---"
done

echo ""
echo "All models complete. Run: PYTHONPATH=. python3 scripts/combine_results.py"
