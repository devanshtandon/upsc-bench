import { describe, it, expect } from "vitest";
import { buildPairings, computeVoteWinner, computeSummary } from "../arena";
import type { ArenaData, ArenaPairing, ArenaRoundResult } from "../../types/arena";

// ── Helpers ──────────────────────────────────────────────────

function makeArenaData(
  questionCount: number = 3,
  modelCount: number = 3
): ArenaData {
  const models = Array.from({ length: modelCount }, (_, i) => `model_${i}`);
  const questions = Array.from({ length: questionCount }, (_, i) => ({
    id: `q${i}`,
    paper: "mains_essay" as const,
    question_type: "essay" as const,
    section: (i % 2 === 0 ? "A" : "B") as string | null,
    question_number: i + 1,
    question_text: `Question ${i}?`,
    word_limit: 1000,
    max_marks: 125,
  }));

  const answers: ArenaData["answers"] = {};
  for (const q of questions) {
    answers[q.id] = {};
    for (const m of models) {
      answers[q.id][m] = {
        text: `Answer by ${m}`,
        word_count: 500,
        rubric_scores: null,
        total_score: null,
        feedback: null,
      };
    }
  }

  return { questions, answers };
}

// ── buildPairings ────────────────────────────────────────────

describe("buildPairings", () => {
  it("returns requested count", () => {
    const data = makeArenaData(5, 4);
    const pairings = buildPairings(data, 5);
    expect(pairings).toHaveLength(5);
  });

  it("models A and B are distinct", () => {
    const data = makeArenaData(5, 4);
    const pairings = buildPairings(data, 10);
    for (const p of pairings) {
      expect(p.modelA).not.toBe(p.modelB);
    }
  });

  it("skips questions with fewer than 2 models", () => {
    const data = makeArenaData(2, 3);
    // Remove all models from q0 except one
    const q0Models = Object.keys(data.answers["q0"]);
    for (let i = 1; i < q0Models.length; i++) {
      delete data.answers["q0"][q0Models[i]];
    }
    const pairings = buildPairings(data, 5);
    // No pairing should use q0
    for (const p of pairings) {
      if (p.questionId === "q0") {
        // q0 only has 1 model, so this should not happen
        expect(Object.keys(data.answers["q0"]).length).toBeGreaterThanOrEqual(2);
      }
    }
  });
});

// ── computeVoteWinner ────────────────────────────────────────

describe("computeVoteWinner", () => {
  const pairing: ArenaPairing = {
    questionId: "q1",
    paper: "mains_essay",
    modelA: "gpt5",
    modelB: "claude",
  };

  it("vote A returns modelA", () => {
    expect(computeVoteWinner("A", pairing)).toBe("gpt5");
  });

  it("vote B returns modelB", () => {
    expect(computeVoteWinner("B", pairing)).toBe("claude");
  });

  it("tie returns null", () => {
    expect(computeVoteWinner("tie", pairing)).toBeNull();
  });

  it("skip returns null", () => {
    expect(computeVoteWinner("skip", pairing)).toBeNull();
  });
});

// ── computeSummary ───────────────────────────────────────────

describe("computeSummary", () => {
  it("tallies wins correctly", () => {
    const results: ArenaRoundResult[] = [
      { pairing: { questionId: "q1", paper: "mains_essay", modelA: "gpt5", modelB: "claude" }, vote: "A", winnerModel: "gpt5" },
      { pairing: { questionId: "q2", paper: "mains_essay", modelA: "gpt5", modelB: "claude" }, vote: "B", winnerModel: "claude" },
      { pairing: { questionId: "q3", paper: "mains_essay", modelA: "gpt5", modelB: "claude" }, vote: "A", winnerModel: "gpt5" },
    ];
    const summary = computeSummary(results);
    expect(summary.winCounts["gpt5"]).toBe(2);
    expect(summary.winCounts["claude"]).toBe(1);
    expect(summary.tieCount).toBe(0);
    expect(summary.skipCount).toBe(0);
  });

  it("counts ties and skips", () => {
    const results: ArenaRoundResult[] = [
      { pairing: { questionId: "q1", paper: "mains_essay", modelA: "a", modelB: "b" }, vote: "tie", winnerModel: null },
      { pairing: { questionId: "q2", paper: "mains_essay", modelA: "a", modelB: "b" }, vote: "skip", winnerModel: null },
      { pairing: { questionId: "q3", paper: "mains_essay", modelA: "a", modelB: "b" }, vote: "tie", winnerModel: null },
    ];
    const summary = computeSummary(results);
    expect(summary.tieCount).toBe(2);
    expect(summary.skipCount).toBe(1);
    expect(Object.keys(summary.winCounts)).toHaveLength(0);
  });

  it("empty results → all zeroes", () => {
    const summary = computeSummary([]);
    expect(summary.tieCount).toBe(0);
    expect(summary.skipCount).toBe(0);
    expect(Object.keys(summary.winCounts)).toHaveLength(0);
  });
});
