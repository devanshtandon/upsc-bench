"""Tests for benchmark/common.py — shared loaders and config resolution."""

import json

import pytest
import yaml

from benchmark.common import (
    load_config,
    load_cutoffs,
    load_questions,
    load_rubric,
    resolve_model_config,
)


# ── load_cutoffs ──────────────────────────────────────────────


class TestLoadCutoffs:
    def test_reads_yaml(self, cutoffs_yaml, sample_cutoffs):
        result = load_cutoffs(cutoffs_yaml)
        assert "cutoffs" in result
        assert result["cutoffs"][2025]["gs1"] == 90.0


# ── load_config ───────────────────────────────────────────────


class TestLoadConfig:
    def test_reads_arbitrary_yaml(self, tmp_path):
        config = {"model": {"name": "test", "temperature": 0.5}}
        path = tmp_path / "config.yaml"
        path.write_text(yaml.dump(config))
        result = load_config(str(path))
        assert result["model"]["name"] == "test"
        assert result["model"]["temperature"] == 0.5


# ── load_questions ────────────────────────────────────────────


class TestLoadQuestions:
    def test_all(self, questions_json, sample_questions):
        result = load_questions(questions_json)
        assert len(result) == len(sample_questions)

    def test_filter_years(self, questions_json):
        result = load_questions(questions_json, filter_years=[2025])
        assert all(q["year"] == 2025 for q in result)
        assert len(result) == 3  # 2 gs1 + 1 csat from 2025

    def test_filter_papers(self, questions_json):
        result = load_questions(questions_json, filter_papers=["gs1"])
        assert all(q["paper"] == "gs1" for q in result)
        assert len(result) == 3  # 2 from 2025 + 1 from 2024

    def test_max_questions(self, questions_json):
        result = load_questions(questions_json, max_questions=2)
        assert len(result) == 2

    def test_combined_filters(self, questions_json):
        result = load_questions(
            questions_json, filter_years=[2025], filter_papers=["gs1"]
        )
        assert len(result) == 2
        assert all(q["year"] == 2025 and q["paper"] == "gs1" for q in result)


# ── load_rubric ───────────────────────────────────────────────


class TestLoadRubric:
    def test_reads_rubric(self, tmp_path):
        rubric = {
            "dimensions": ["content", "structure", "depth"],
            "weights": {"content": 0.3, "structure": 0.2, "depth": 0.5},
        }
        path = tmp_path / "judge.yaml"
        path.write_text(yaml.dump(rubric))
        result = load_rubric(str(path))
        assert result["dimensions"] == ["content", "structure", "depth"]
        assert result["weights"]["depth"] == 0.5


# ── resolve_model_config ──────────────────────────────────────


class TestResolveModelConfig:
    def test_prelims(self, model_registry):
        config = resolve_model_config(
            "test_model", "prelims", registry_path=model_registry
        )
        assert config["model"]["name"] == "openrouter/test/model-v1"
        assert config["model"]["temperature"] == 0.3  # model override
        assert config["dbfilepath"] == "db/benchmark.db"
        assert "results_test_model.json" in config["output_filepath"]

    def test_mains(self, model_registry):
        config = resolve_model_config(
            "test_model", "mains", registry_path=model_registry
        )
        assert config["model"]["temperature"] == 0.3  # model override
        assert config["dbfilepath"] == "db/mains_benchmark.db"
        assert "mains_answers_test_model.json" in config["output_filepath"]

    def test_unknown_model(self, model_registry):
        with pytest.raises(KeyError, match="Unknown model 'nonexistent'"):
            resolve_model_config(
                "nonexistent", "prelims", registry_path=model_registry
            )

    def test_model_overrides_default(self, model_registry):
        """Per-model max_tokens overrides the defaults."""
        config = resolve_model_config(
            "vision_model", "prelims", registry_path=model_registry
        )
        assert config["model"]["max_tokens"] == 2048  # model-level override
        assert config["model"]["supports_vision"] is True  # model-level
