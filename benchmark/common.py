"""Shared utility functions for UPSC Bench pipeline.

Consolidates load_cutoffs, load_config, load_questions, and load_rubric
which were previously duplicated across scorer, mains_scorer, runner,
mains_runner, generate_leaderboard, and grade_mains.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_cutoffs(cutoffs_path: str = "config/cutoffs.yaml") -> dict:
    """Load historical UPSC cutoff marks and marking scheme."""
    with open(cutoffs_path) as f:
        return yaml.safe_load(f)


def load_config(config_path: str) -> dict:
    """Load YAML config for a benchmark run."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_questions(
    input_path: str,
    filter_years: list[int] | None = None,
    filter_papers: list[str] | None = None,
    max_questions: int | None = None,
) -> list[dict]:
    """Load and filter questions from the dataset.

    Works for both Prelims and Mains question files.
    """
    with open(input_path) as f:
        questions = json.load(f)

    if filter_years:
        questions = [q for q in questions if q["year"] in filter_years]
    if filter_papers:
        questions = [q for q in questions if q["paper"] in filter_papers]
    if max_questions:
        questions = questions[:max_questions]

    return questions


def load_rubric(judge_path: str = "config/judge.yaml") -> dict:
    """Load grading rubric configuration."""
    with open(judge_path) as f:
        return yaml.safe_load(f)


def load_model_registry(registry_path: str = "config/models.yaml") -> dict:
    """Load the model registry."""
    with open(registry_path) as f:
        return yaml.safe_load(f)


def resolve_model_config(model_key: str, exam_type: str = "prelims",
                         registry_path: str = "config/models.yaml") -> dict:
    """Resolve a model key + exam type into a full config dict.

    Constructs the equivalent of the old per-model YAML config by
    combining the model registry entry with exam-type defaults.

    Args:
        model_key: Key from models.yaml (e.g., 'gpt5', 'claude_opus').
        exam_type: Either 'prelims' or 'mains'.
        registry_path: Path to models.yaml.

    Returns:
        Config dict compatible with runner.py / mains_runner.py.

    Raises:
        KeyError: If model_key is not found in the registry.
    """
    registry = load_model_registry(registry_path)
    models = registry["models"]
    defaults = registry["defaults"][exam_type]

    if model_key not in models:
        available = ", ".join(sorted(models.keys()))
        raise KeyError(f"Unknown model '{model_key}'. Available: {available}")

    model_entry = models[model_key]

    # Derive output filepath from model key and exam type
    if exam_type == "prelims":
        output_filepath = f"{defaults['output_dir']}/results_{model_key}.json"
    else:
        output_filepath = f"{defaults['output_dir']}/mains_answers_{model_key}.json"

    return {
        "input_filepath": defaults["input"],
        "output_filepath": output_filepath,
        "dbfilepath": defaults["db"],
        "filter_years": None,
        "filter_papers": None,
        "max_questions": None,
        "model": {
            "name": model_entry["name"],
            "temperature": model_entry.get("temperature", defaults["temperature"]),
            "max_tokens": model_entry.get("max_tokens", defaults["max_tokens"]),
            "supports_vision": model_entry.get("supports_vision", defaults["supports_vision"]),
        },
    }
