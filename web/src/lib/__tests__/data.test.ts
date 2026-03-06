import { describe, it, expect } from "vitest";
import {
  getFilteredModels,
  getMainsFilteredModels,
  getMainsHumanModels,
  getModelScore,
  getMainsModelScore,
} from "../data";
import type { LeaderboardData, ModelEntry } from "../../types";

// ── Mock data builders ───────────────────────────────────────

function makeModelEntry(overrides: Partial<ModelEntry> & { model: string }): ModelEntry {
  return {
    rank: 0,
    overall: {
      total_questions: 0,
      correct: 0,
      wrong: 0,
      unanswered: 0,
      accuracy: 0,
      gs1_avg_marks: 0,
      gs1_all_years_pass: false,
      csat_all_years_pass: false,
    },
    paper_totals: {},
    yearly: {},
    ...overrides,
  };
}

function makeLeaderboardData(models: ModelEntry[]): LeaderboardData {
  return {
    models,
    metadata: {
      total_models: models.length,
      years: [2025],
      papers: ["gs1", "csat"],
      cutoffs: { 2025: { gs1: 90, csat_qualifying: 66 } },
      marking_scheme: {
        gs1: { correct: 2, wrong: -0.66, unanswered: 0, total_questions: 100, max_marks: 200 },
        csat: { correct: 2.5, wrong: -0.83, unanswered: 0, total_questions: 80, max_marks: 200 },
      },
    },
  };
}

// ── getFilteredModels ────────────────────────────────────────

describe("getFilteredModels", () => {
  it("overall sorts by GS1 marks descending", () => {
    const models = [
      makeModelEntry({
        model: "low",
        yearly: { 2025: { gs1: { marks: 120, max_marks: 200, correct: 60, wrong: 20, unanswered: 20, accuracy: 60, passed: true, cutoff: 90, margin: 30 }, csat: { marks: 100, max_marks: 200, correct: 40, wrong: 10, unanswered: 30, accuracy: 50, passed: true, cutoff: 66, margin: 34 } } },
      }),
      makeModelEntry({
        model: "high",
        yearly: { 2025: { gs1: { marks: 160, max_marks: 200, correct: 80, wrong: 10, unanswered: 10, accuracy: 80, passed: true, cutoff: 90, margin: 70 }, csat: { marks: 100, max_marks: 200, correct: 40, wrong: 10, unanswered: 30, accuracy: 50, passed: true, cutoff: 66, margin: 34 } } },
      }),
    ];
    const data = makeLeaderboardData(models);
    const sorted = getFilteredModels(data, 2025, "overall");
    expect(sorted[0].model).toBe("high");
    expect(sorted[1].model).toBe("low");
  });

  it("CSAT-fail models go last", () => {
    const models = [
      makeModelEntry({
        model: "csat_fail",
        yearly: { 2025: { gs1: { marks: 180, max_marks: 200, correct: 90, wrong: 5, unanswered: 5, accuracy: 90, passed: true, cutoff: 90, margin: 90 }, csat: { marks: 50, max_marks: 200, correct: 20, wrong: 10, unanswered: 50, accuracy: 25, passed: false, cutoff: 66, margin: -16 } } },
      }),
      makeModelEntry({
        model: "normal",
        yearly: { 2025: { gs1: { marks: 100, max_marks: 200, correct: 50, wrong: 30, unanswered: 20, accuracy: 50, passed: true, cutoff: 90, margin: 10 }, csat: { marks: 100, max_marks: 200, correct: 40, wrong: 10, unanswered: 30, accuracy: 50, passed: true, cutoff: 66, margin: 34 } } },
      }),
    ];
    const data = makeLeaderboardData(models);
    const sorted = getFilteredModels(data, 2025, "overall");
    expect(sorted[0].model).toBe("normal");
    expect(sorted[1].model).toBe("csat_fail");
  });

  it("assigns sequential ranks", () => {
    const models = Array.from({ length: 3 }, (_, i) =>
      makeModelEntry({
        model: `model_${i}`,
        yearly: { 2025: { gs1: { marks: 150 - i * 10, max_marks: 200, correct: 70 - i * 5, wrong: 20, unanswered: 10, accuracy: 70, passed: true, cutoff: 90, margin: 60 }, csat: { marks: 100, max_marks: 200, correct: 40, wrong: 10, unanswered: 30, accuracy: 50, passed: true, cutoff: 66, margin: 34 } } },
      })
    );
    const data = makeLeaderboardData(models);
    const sorted = getFilteredModels(data, 2025, "overall");
    expect(sorted.map((m) => m.rank)).toEqual([1, 2, 3]);
  });

  it("specific paper sorts by paper marks", () => {
    const models = [
      makeModelEntry({
        model: "low_csat",
        yearly: { 2025: { gs1: { marks: 160, max_marks: 200, correct: 80, wrong: 10, unanswered: 10, accuracy: 80, passed: true, cutoff: 90, margin: 70 }, csat: { marks: 80, max_marks: 200, correct: 32, wrong: 10, unanswered: 38, accuracy: 40, passed: true, cutoff: 66, margin: 14 } } },
      }),
      makeModelEntry({
        model: "high_csat",
        yearly: { 2025: { gs1: { marks: 100, max_marks: 200, correct: 50, wrong: 30, unanswered: 20, accuracy: 50, passed: true, cutoff: 90, margin: 10 }, csat: { marks: 150, max_marks: 200, correct: 60, wrong: 10, unanswered: 10, accuracy: 75, passed: true, cutoff: 66, margin: 84 } } },
      }),
    ];
    const data = makeLeaderboardData(models);
    const sorted = getFilteredModels(data, 2025, "csat");
    expect(sorted[0].model).toBe("high_csat");
  });
});

// ── getMainsFilteredModels ───────────────────────────────────

describe("getMainsFilteredModels", () => {
  function makeMainsModel(model: string, totalScore: number, isHuman = false): ModelEntry {
    return makeModelEntry({
      model,
      is_human: isHuman,
      mains: {
        2025: {
          total_score: totalScore,
          max_marks: 1250,
          score_pct: (totalScore / 1250) * 100,
          passed: totalScore > 571,
          cutoff: 571,
          margin: totalScore - 571,
          estimated_rank: { rank: 1, percentile: 99, label: "Top", total_candidates: 1000 },
          papers: {
            essay: { score: totalScore * 0.2, max_marks: 250, score_pct: 0, questions_evaluated: 2 },
            gs1: { score: totalScore * 0.2, max_marks: 250, score_pct: 0, questions_evaluated: 20 },
            gs2: { score: totalScore * 0.2, max_marks: 250, score_pct: 0, questions_evaluated: 20 },
            gs3: { score: totalScore * 0.2, max_marks: 250, score_pct: 0, questions_evaluated: 20 },
            gs4: { score: totalScore * 0.2, max_marks: 250, score_pct: 0, questions_evaluated: 20 },
          },
        },
      },
    });
  }

  it("excludes humans", () => {
    const models = [
      makeMainsModel("gpt5", 900),
      makeMainsModel("human_ref", 600, true),
    ];
    const data = makeLeaderboardData(models);
    const sorted = getMainsFilteredModels(data, 2025, "mains_total");
    expect(sorted).toHaveLength(1);
    expect(sorted[0].model).toBe("gpt5");
  });

  it("total sort descending", () => {
    const models = [
      makeMainsModel("low", 700),
      makeMainsModel("high", 900),
      makeMainsModel("mid", 800),
    ];
    const data = makeLeaderboardData(models);
    const sorted = getMainsFilteredModels(data, 2025, "mains_total");
    expect(sorted.map((m) => m.model)).toEqual(["high", "mid", "low"]);
  });

  it("per-paper sort", () => {
    const m1 = makeMainsModel("a", 900);
    const m2 = makeMainsModel("b", 800);
    // Override gs1 score for m2 to be higher
    m2.mains![2025].papers.gs1.score = 230;
    m1.mains![2025].papers.gs1.score = 180;
    const data = makeLeaderboardData([m1, m2]);
    const sorted = getMainsFilteredModels(data, 2025, "mains_gs1");
    expect(sorted[0].model).toBe("b");
  });
});

// ── getModelScore ────────────────────────────────────────────

describe("getModelScore", () => {
  it("overall returns GS1 data with combined pass", () => {
    const model = makeModelEntry({
      model: "test",
      yearly: {
        2025: {
          gs1: { marks: 150, max_marks: 200, correct: 75, wrong: 15, unanswered: 10, accuracy: 75, passed: true, cutoff: 90, margin: 60 },
          csat: { marks: 100, max_marks: 200, correct: 40, wrong: 10, unanswered: 30, accuracy: 50, passed: true, cutoff: 66, margin: 34 },
        },
      },
    });
    const score = getModelScore(model, 2025, "overall");
    expect(score.marks).toBe(150);
    expect(score.passed).toBe(true);
    expect(score.correct).toBe(75);
  });

  it("missing year returns zeroes", () => {
    const model = makeModelEntry({ model: "test" });
    const score = getModelScore(model, 2025, "overall");
    expect(score.marks).toBe(0);
    expect(score.passed).toBe(false);
  });
});

// ── getMainsModelScore ───────────────────────────────────────

describe("getMainsModelScore", () => {
  function makeMainsEntry(): ModelEntry {
    return makeModelEntry({
      model: "test",
      mains: {
        2025: {
          total_score: 900,
          max_marks: 1250,
          score_pct: 72,
          passed: true,
          cutoff: 571,
          margin: 329,
          estimated_rank: { rank: 1, percentile: 99, label: "Top", total_candidates: 1000 },
          papers: {
            essay: { score: 180, max_marks: 250, score_pct: 72, questions_evaluated: 2 },
            gs1: { score: 195, max_marks: 250, score_pct: 78, questions_evaluated: 20 },
          },
        },
      },
    });
  }

  it("total returns total_score fields", () => {
    const score = getMainsModelScore(makeMainsEntry(), 2025, "mains_total");
    expect(score.score).toBe(900);
    expect(score.maxMarks).toBe(1250);
    expect(score.passed).toBe(true);
  });

  it("paper returns correct paperKey", () => {
    const score = getMainsModelScore(makeMainsEntry(), 2025, "mains_gs1");
    expect(score.score).toBe(195);
    expect(score.maxMarks).toBe(250);
  });

  it("essay paper", () => {
    const score = getMainsModelScore(makeMainsEntry(), 2025, "essay");
    expect(score.score).toBe(180);
  });

  it("missing mains data returns zeroes", () => {
    const model = makeModelEntry({ model: "no_mains" });
    const score = getMainsModelScore(model, 2025, "mains_total");
    expect(score.score).toBe(0);
  });
});

// ── getMainsHumanModels ──────────────────────────────────────

describe("getMainsHumanModels", () => {
  it("sorted by AIR ascending", () => {
    const models = [
      makeModelEntry({
        model: "human_10",
        is_human: true,
        human_metadata: { air: 10, exam_year: "2024", written_marks: 800, written_max: 1750, interview_marks: 200, total_marks: 1000, total_max: 2025 },
        mains: { 2025: { total_score: 600, max_marks: 1250, score_pct: 48, passed: true, cutoff: 571, margin: 29, estimated_rank: { rank: 10, percentile: 99, label: "Top", total_candidates: 1000 }, papers: {} } },
      }),
      makeModelEntry({
        model: "human_1",
        is_human: true,
        human_metadata: { air: 1, exam_year: "2024", written_marks: 900, written_max: 1750, interview_marks: 220, total_marks: 1120, total_max: 2025 },
        mains: { 2025: { total_score: 650, max_marks: 1250, score_pct: 52, passed: true, cutoff: 571, margin: 79, estimated_rank: { rank: 1, percentile: 99.9, label: "Top", total_candidates: 1000 }, papers: {} } },
      }),
    ];
    const data = makeLeaderboardData(models);
    const sorted = getMainsHumanModels(data, 2025);
    expect(sorted[0].model).toBe("human_1");
    expect(sorted[1].model).toBe("human_10");
  });
});
