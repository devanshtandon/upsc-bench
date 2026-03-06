"""Shared fixtures for UPSC Bench tests."""

from __future__ import annotations

import json

import pytest
import yaml


# ── Cutoff / config fixtures ──────────────────────────────────

@pytest.fixture
def sample_cutoffs() -> dict:
    """Minimal cutoff data matching config/cutoffs.yaml structure."""
    return {
        "cutoffs": {
            2025: {"gs1": 90.0, "csat_qualifying": 66},
            2024: {"gs1": 87.98, "csat_qualifying": 66},
        },
        "mains_cutoffs": {
            2025: {"total": 800, "max_marks": 1750},
        },
    }


@pytest.fixture
def cutoffs_yaml(tmp_path, sample_cutoffs) -> str:
    """Write sample cutoffs to a temp YAML file and return path."""
    path = tmp_path / "cutoffs.yaml"
    path.write_text(yaml.dump(sample_cutoffs))
    return str(path)


@pytest.fixture
def model_registry(tmp_path) -> str:
    """Write a minimal model registry YAML and return path."""
    registry = {
        "models": {
            "test_model": {
                "name": "openrouter/test/model-v1",
                "temperature": 0.3,
                "supports_vision": False,
            },
            "vision_model": {
                "name": "openrouter/test/vision-v1",
                "supports_vision": True,
                "max_tokens": 2048,
            },
        },
        "defaults": {
            "prelims": {
                "input": "data/processed/upsc_bench.json",
                "output_dir": "results/raw",
                "db": "db/benchmark.db",
                "temperature": 0.0,
                "max_tokens": 1024,
                "supports_vision": True,
            },
            "mains": {
                "input": "data/mains_questions/mains_2025.json",
                "output_dir": "results/raw",
                "db": "db/mains_benchmark.db",
                "temperature": 0.7,
                "max_tokens": 4096,
                "supports_vision": False,
            },
        },
    }
    path = tmp_path / "models.yaml"
    path.write_text(yaml.dump(registry))
    return str(path)


# ── Question fixtures ─────────────────────────────────────────

@pytest.fixture
def sample_questions() -> list[dict]:
    """Minimal question list covering both years and papers."""
    return [
        {
            "id": "gs1_2025_q1", "year": 2025, "paper": "gs1",
            "question_number": 1, "question_text": "Capital of India?",
            "options": {"a": "Mumbai", "b": "Delhi", "c": "Kolkata", "d": "Chennai"},
            "has_image": False, "image_paths": [], "image_description": "",
            "correct_answer": "b", "marks_correct": 2.0,
            "marks_wrong": -0.66, "marks_unanswered": 0.0,
        },
        {
            "id": "gs1_2025_q2", "year": 2025, "paper": "gs1",
            "question_number": 2, "question_text": "Largest state?",
            "options": {"a": "UP", "b": "MP", "c": "Rajasthan", "d": "Maharashtra"},
            "has_image": False, "image_paths": [], "image_description": "",
            "correct_answer": "c", "marks_correct": 2.0,
            "marks_wrong": -0.66, "marks_unanswered": 0.0,
        },
        {
            "id": "csat_2025_q1", "year": 2025, "paper": "csat",
            "question_number": 1, "question_text": "2 + 2 = ?",
            "options": {"a": "3", "b": "4", "c": "5", "d": "6"},
            "has_image": False, "image_paths": [], "image_description": "",
            "correct_answer": "b", "marks_correct": 2.5,
            "marks_wrong": -0.83, "marks_unanswered": 0.0,
        },
        {
            "id": "gs1_2024_q1", "year": 2024, "paper": "gs1",
            "question_number": 1, "question_text": "First PM of India?",
            "options": {"a": "Gandhi", "b": "Nehru", "c": "Patel", "d": "Ambedkar"},
            "has_image": False, "image_paths": [], "image_description": "",
            "correct_answer": "b", "marks_correct": 2.0,
            "marks_wrong": -0.66, "marks_unanswered": 0.0,
        },
    ]


@pytest.fixture
def questions_json(tmp_path, sample_questions) -> str:
    """Write sample questions to a temp JSON file and return path."""
    path = tmp_path / "questions.json"
    path.write_text(json.dumps(sample_questions))
    return str(path)


# ── Rank mapping fixture ──────────────────────────────────────

@pytest.fixture
def sample_rank_data() -> dict:
    """Rank mapping data for testing estimate_rank."""
    return {
        "2025": {
            "total_appeared": 1000000,
            "mains_qualified": 15000,
            "cutoff_general": 90.0,
            "estimated_topper": 160.0,
            "distribution": [
                {"score": 160, "rank": 1},
                {"score": 140, "rank": 100},
                {"score": 120, "rank": 1000},
                {"score": 100, "rank": 5000},
                {"score": 90, "rank": 15000},
            ],
        },
    }
