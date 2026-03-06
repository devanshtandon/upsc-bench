"""Tests for benchmark/db.py — SQLite operations for benchmark results."""

from __future__ import annotations

import json

import pytest

from benchmark.db import BenchmarkDB


@pytest.fixture
def db(tmp_path) -> BenchmarkDB:
    """Create a fresh in-memory-like DB in a temp directory."""
    db_path = str(tmp_path / "test.db")
    database = BenchmarkDB(db_path)
    yield database
    database.close()


@pytest.fixture
def sample_question() -> dict:
    return {
        "id": "gs1_2025_q1",
        "year": 2025,
        "paper": "gs1",
        "question_number": 1,
        "question_text": "Capital of India?",
        "word_limit": None,
        "max_marks": 2.0,
    }


@pytest.fixture
def sample_grading() -> dict:
    return {
        "extracted_answer": "b",
        "correct_answer": "b",
        "result": "correct",
    }


# ── Run lifecycle ─────────────────────────────────────────────


class TestRunLifecycle:
    def test_create_complete_run(self, db):
        run_id = db.create_run("run-001", "test-model", "config.yaml")
        assert run_id == "run-001"

        db.complete_run("run-001", total_questions=10)
        # Verify via direct SQL
        row = db.conn.execute(
            "SELECT status, total_questions FROM runs WHERE run_id='run-001'"
        ).fetchone()
        assert row["status"] == "completed"
        assert row["total_questions"] == 10


# ── Prelims results ──────────────────────────────────────────


class TestPrelimsResults:
    def test_save_and_get(self, db, sample_question, sample_grading):
        db.create_run("run-001", "gpt5")
        db.save_result(
            "run-001", sample_question, "The answer is B",
            sample_grading, marks=2.0, usage={"prompt_tokens": 100},
            model="gpt5",
        )
        results = db.get_run_results("run-001")
        assert len(results) == 1
        assert results[0]["question_id"] == "gs1_2025_q1"
        assert results[0]["result"] == "correct"
        assert results[0]["marks"] == 2.0

    def test_run_summary(self, db, sample_question, sample_grading):
        db.create_run("run-001", "gpt5")

        # 2 correct, 1 wrong
        for i, result_type in enumerate(["correct", "correct", "wrong"]):
            q = {**sample_question, "id": f"q{i}", "question_number": i}
            g = {**sample_grading, "result": result_type}
            marks = 2.0 if result_type == "correct" else -0.66
            db.save_result("run-001", q, "output", g, marks, {}, model="gpt5")

        summary = db.get_run_summary("run-001")
        assert summary["total"] == 3
        assert summary["correct"] == 2
        assert summary["wrong"] == 1
        assert summary["total_marks"] == pytest.approx(3.34, abs=0.01)

    def test_unique_constraint_replaces(self, db, sample_question, sample_grading):
        """INSERT OR REPLACE should update, not error on duplicate question_id."""
        db.create_run("run-001", "gpt5")
        db.save_result(
            "run-001", sample_question, "First attempt",
            sample_grading, marks=2.0, usage={}, model="gpt5",
        )
        # Save again with different output
        db.save_result(
            "run-001", sample_question, "Second attempt",
            {**sample_grading, "result": "wrong"}, marks=-0.66,
            usage={}, model="gpt5",
        )
        results = db.get_run_results("run-001")
        assert len(results) == 1
        assert results[0]["result"] == "wrong"  # replaced

    def test_model_field_saved(self, db, sample_question, sample_grading):
        db.create_run("run-001", "gpt5")
        db.save_result(
            "run-001", sample_question, "output",
            sample_grading, 2.0, {}, model="gpt5",
        )
        results = db.get_run_results("run-001")
        assert results[0]["model"] == "gpt5"


# ── Mains results ─────────────────────────────────────────────


class TestMainsResults:
    def test_save_and_get(self, db, sample_question):
        db.create_run("run-001", "gpt5")
        db.save_mains_result(
            "run-001", sample_question, "Long essay response...",
            word_count=250, usage={"prompt_tokens": 500},
            model="gpt5",
        )
        results = db.get_mains_results("run-001")
        assert len(results) == 1
        assert results[0]["word_count"] == 250
        assert results[0]["model"] == "gpt5"

    def test_update_grading(self, db, sample_question):
        db.create_run("run-001", "gpt5")
        db.save_mains_result(
            "run-001", sample_question, "Essay text",
            word_count=200, usage={}, model="gpt5",
        )

        rubric = {"content": 8, "structure": 7, "depth": 9}
        db.update_mains_grading(
            "run-001", "gs1_2025_q1",
            rubric_scores=rubric, total_score=24.0,
            feedback="Well structured answer.",
        )

        results = db.get_mains_results("run-001")
        assert results[0]["total_score"] == 24.0
        assert results[0]["feedback"] == "Well structured answer."
        assert json.loads(results[0]["rubric_scores"]) == rubric
