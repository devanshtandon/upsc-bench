import { describe, it, expect } from "vitest";
import { gradeAnswer, computeQuizSummary, pickQuizQuestions } from "../quiz";
import type { QuizQuestion, QuizResult, RankYearData } from "../quiz";
import type { RawQuestion } from "../../types";

// ── Helpers ──────────────────────────────────────────────────

function makeQuestion(overrides: Partial<QuizQuestion> = {}): QuizQuestion {
  return {
    id: "gs1_2025_q1",
    question_number: 1,
    question_text: "Test question?",
    options: { a: "A", b: "B", c: "C", d: "D" },
    correct_answer: "b",
    has_image: false,
    image_paths: [],
    image_description: "",
    marks_correct: 2.0,
    marks_wrong: -0.66,
    ...overrides,
  };
}

function makeResult(
  isCorrect: boolean,
  answer: string | null,
  marks: number
): QuizResult {
  return {
    question: makeQuestion(),
    userAnswer: answer,
    isCorrect,
    marksEarned: marks,
  };
}

const mockRankData: RankYearData = {
  total_appeared: 1000000,
  mains_qualified: 15000,
  cutoff_general: 90,
  estimated_topper: 160,
  distribution: [
    { score: 160, rank: 1 },
    { score: 140, rank: 100 },
    { score: 120, rank: 1000 },
    { score: 100, rank: 5000 },
    { score: 90, rank: 15000 },
  ],
};

// ── gradeAnswer ──────────────────────────────────────────────

describe("gradeAnswer", () => {
  it("correct answer", () => {
    const q = makeQuestion({ correct_answer: "b" });
    const result = gradeAnswer(q, "b");
    expect(result.isCorrect).toBe(true);
    expect(result.marksEarned).toBe(2.0);
  });

  it("wrong answer", () => {
    const q = makeQuestion({ correct_answer: "b" });
    const result = gradeAnswer(q, "a");
    expect(result.isCorrect).toBe(false);
    expect(result.marksEarned).toBe(-0.66);
  });

  it("skipped (null)", () => {
    const q = makeQuestion();
    const result = gradeAnswer(q, null);
    expect(result.isCorrect).toBe(false);
    expect(result.marksEarned).toBe(0);
  });
});

// ── computeQuizSummary ───────────────────────────────────────

describe("computeQuizSummary", () => {
  it("perfect score → passes", () => {
    const results: QuizResult[] = Array.from({ length: 5 }, () =>
      makeResult(true, "b", 2.0)
    );
    const summary = computeQuizSummary(results, mockRankData);

    expect(summary.correct).toBe(5);
    expect(summary.wrong).toBe(0);
    expect(summary.skipped).toBe(0);
    // Raw: 5 × 2.0 = 10; extrapolated: 10 × 20 = 200
    expect(summary.rawScore).toBe(10);
    expect(summary.extrapolatedScore).toBe(200);
    expect(summary.passed).toBe(true);
  });

  it("all wrong → fails", () => {
    const results: QuizResult[] = Array.from({ length: 5 }, () =>
      makeResult(false, "a", -0.66)
    );
    const summary = computeQuizSummary(results, mockRankData);

    expect(summary.correct).toBe(0);
    expect(summary.wrong).toBe(5);
    // Raw: 5 × -0.66 = -3.3; extrapolated: -3.3 × 20 = -66
    expect(summary.extrapolatedScore).toBe(-66);
    expect(summary.passed).toBe(false);
  });

  it("mixed → correct extrapolation and rank", () => {
    const results: QuizResult[] = [
      makeResult(true, "b", 2.0),
      makeResult(true, "b", 2.0),
      makeResult(true, "b", 2.0),
      makeResult(false, "a", -0.66),
      makeResult(false, null, 0), // skipped
    ];
    const summary = computeQuizSummary(results, mockRankData);

    expect(summary.correct).toBe(3);
    expect(summary.wrong).toBe(1);
    expect(summary.skipped).toBe(1);
    // Raw: 3×2.0 + 1×(-0.66) + 0 = 5.34; extrapolated: 5.34 × 20 = 106.8
    expect(summary.rawScore).toBe(5.34);
    expect(summary.extrapolatedScore).toBe(106.8);
    expect(summary.passed).toBe(true); // 106.8 > 90
  });
});

// ── pickQuizQuestions ────────────────────────────────────────

describe("pickQuizQuestions", () => {
  function makeRawQuestion(id: string, year: number, paper: string): RawQuestion {
    return {
      id,
      year,
      paper,
      question_number: 1,
      question_text: "Q?",
      options: { a: "A", b: "B", c: "C", d: "D" },
      has_image: false,
      image_paths: [],
      image_description: "",
      correct_answer: "a",
      marks_correct: 2.0,
      marks_wrong: -0.66,
      marks_unanswered: 0,
    };
  }

  it("filters to year=2025, paper=gs1", () => {
    const pool = [
      ...Array.from({ length: 10 }, (_, i) =>
        makeRawQuestion(`gs1_2025_q${i}`, 2025, "gs1")
      ),
      makeRawQuestion("csat_2025_q1", 2025, "csat"),
      makeRawQuestion("gs1_2024_q1", 2024, "gs1"),
    ];
    const picked = pickQuizQuestions(pool);
    expect(picked).toHaveLength(5);
    // All should be gs1 2025 (the filter is internal)
    for (const q of picked) {
      expect(q.id).toMatch(/^gs1_2025/);
    }
  });

  it("returns 5 questions when pool >= 5", () => {
    const pool = Array.from({ length: 20 }, (_, i) =>
      makeRawQuestion(`gs1_2025_q${i}`, 2025, "gs1")
    );
    expect(pickQuizQuestions(pool)).toHaveLength(5);
  });
});
