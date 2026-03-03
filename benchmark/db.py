"""SQLite database operations for UPSC Bench results."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    config_path TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT DEFAULT 'running',
    total_questions INTEGER DEFAULT 0,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    paper TEXT NOT NULL,
    question_number INTEGER NOT NULL,
    raw_output TEXT,
    extracted_answer TEXT,
    correct_answer TEXT,
    result TEXT NOT NULL,
    marks REAL NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(run_id),
    UNIQUE(run_id, question_id)
);

CREATE TABLE IF NOT EXISTS mains_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER,
    paper TEXT,
    question_number INTEGER,
    question_text TEXT,
    word_limit INTEGER,
    max_marks REAL,
    raw_output TEXT,
    word_count INTEGER,
    rubric_scores TEXT,
    total_score REAL,
    feedback TEXT,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(run_id),
    UNIQUE(run_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_results_run ON results(run_id);
CREATE INDEX IF NOT EXISTS idx_results_model ON results(model);
CREATE INDEX IF NOT EXISTS idx_results_year_paper ON results(year, paper);
CREATE INDEX IF NOT EXISTS idx_mains_results_run ON mains_results(run_id);
CREATE INDEX IF NOT EXISTS idx_mains_results_model ON mains_results(model);
CREATE INDEX IF NOT EXISTS idx_mains_results_year_paper ON mains_results(year, paper);
"""


class BenchmarkDB:
    """SQLite database for storing benchmark results."""

    def __init__(self, db_path: str = "db/benchmark_results.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def create_run(self, run_id: str, model: str, config_path: str = "",
                   metadata: dict | None = None) -> str:
        """Create a new benchmark run entry."""
        from datetime import datetime, timezone
        self.conn.execute(
            "INSERT INTO runs (run_id, model, config_path, started_at, metadata) "
            "VALUES (?, ?, ?, ?, ?)",
            (run_id, model, config_path,
             datetime.now(timezone.utc).isoformat(),
             json.dumps(metadata or {})),
        )
        self.conn.commit()
        return run_id

    def complete_run(self, run_id: str, total_questions: int):
        """Mark a run as completed."""
        from datetime import datetime, timezone
        self.conn.execute(
            "UPDATE runs SET status='completed', completed_at=?, total_questions=? "
            "WHERE run_id=?",
            (datetime.now(timezone.utc).isoformat(), total_questions, run_id),
        )
        self.conn.commit()

    def save_result(self, run_id: str, question: dict, raw_output: str,
                    grading: dict, marks: float, usage: dict):
        """Save a single question result."""
        self.conn.execute(
            "INSERT OR REPLACE INTO results "
            "(run_id, question_id, model, year, paper, question_number, "
            "raw_output, extracted_answer, correct_answer, result, marks, "
            "prompt_tokens, completion_tokens) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                question["id"],
                "",  # model filled from run
                question["year"],
                question["paper"],
                question["question_number"],
                raw_output,
                grading["extracted_answer"],
                grading["correct_answer"],
                grading["result"],
                marks,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
            ),
        )
        self.conn.commit()

    def get_run_results(self, run_id: str) -> list[dict]:
        """Get all results for a run."""
        rows = self.conn.execute(
            "SELECT * FROM results WHERE run_id = ? ORDER BY year, paper, question_number",
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_run_summary(self, run_id: str) -> dict:
        """Get summary statistics for a run."""
        row = self.conn.execute(
            "SELECT "
            "  COUNT(*) as total, "
            "  SUM(CASE WHEN result='correct' THEN 1 ELSE 0 END) as correct, "
            "  SUM(CASE WHEN result='wrong' THEN 1 ELSE 0 END) as wrong, "
            "  SUM(CASE WHEN result='unanswered' THEN 1 ELSE 0 END) as unanswered, "
            "  SUM(marks) as total_marks "
            "FROM results WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        return dict(row) if row else {}

    def close(self):
        self.conn.close()

    # --- Mains methods ---

    def save_mains_result(self, run_id: str, question: dict, raw_output: str,
                          word_count: int, usage: dict):
        """Save a single Mains question answer (pre-grading)."""
        self.conn.execute(
            "INSERT OR REPLACE INTO mains_results "
            "(run_id, question_id, model, year, paper, question_number, "
            "question_text, word_limit, max_marks, raw_output, word_count, "
            "prompt_tokens, completion_tokens) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                question["id"],
                "",  # model filled from run
                question.get("year"),
                question.get("paper"),
                question.get("question_number"),
                question.get("question_text", ""),
                question.get("word_limit"),
                question.get("max_marks"),
                raw_output,
                word_count,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
            ),
        )
        self.conn.commit()

    def update_mains_grading(self, run_id: str, question_id: str,
                             rubric_scores: dict, total_score: float,
                             feedback: str):
        """Update a Mains result with judge scores."""
        self.conn.execute(
            "UPDATE mains_results SET rubric_scores=?, total_score=?, feedback=? "
            "WHERE run_id=? AND question_id=?",
            (json.dumps(rubric_scores), total_score, feedback,
             run_id, question_id),
        )
        self.conn.commit()

    def get_mains_results(self, run_id: str) -> list[dict]:
        """Get all Mains results for a run."""
        rows = self.conn.execute(
            "SELECT * FROM mains_results WHERE run_id = ? "
            "ORDER BY year, paper, question_number",
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]
