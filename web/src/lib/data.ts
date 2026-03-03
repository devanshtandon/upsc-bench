import leaderboardJson from "../../data/leaderboard.json";
import type { LeaderboardData, ModelEntry, Paper, MainsPaper } from "../types";

export function getLeaderboardData(): LeaderboardData {
  return leaderboardJson as LeaderboardData;
}

export function getFilteredModels(
  data: LeaderboardData,
  year: number,
  paper: Paper
): ModelEntry[] {
  let models = [...data.models];

  if (paper !== "overall") {
    models = models
      .filter((m) => m.yearly[year]?.[paper])
      .sort((a, b) => {
        const aScore = a.yearly[year]?.[paper]?.marks ?? 0;
        const bScore = b.yearly[year]?.[paper]?.marks ?? 0;
        return bScore - aScore;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  } else {
    // Prelims Rank: sort by GS1 marks, CSAT-fail models last
    models = models
      .filter((m) => m.yearly[year]?.gs1)
      .sort((a, b) => {
        const aCsatPass = (a.yearly[year]?.csat?.passed) ? 1 : 0;
        const bCsatPass = (b.yearly[year]?.csat?.passed) ? 1 : 0;
        if (aCsatPass !== bCsatPass) return bCsatPass - aCsatPass;
        const aGs1 = a.yearly[year]?.gs1?.marks ?? 0;
        const bGs1 = b.yearly[year]?.gs1?.marks ?? 0;
        return bGs1 - aGs1;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  }

  return models;
}

export function getMainsFilteredModels(
  data: LeaderboardData,
  year: number,
  paper: MainsPaper
): ModelEntry[] {
  let models = data.models.filter((m) => m.mains?.[year]);

  if (paper === "mains_total") {
    models = models
      .sort((a, b) => {
        const aScore = a.mains![year].total_score;
        const bScore = b.mains![year].total_score;
        return bScore - aScore;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  } else {
    const paperKey = paper === "essay" ? "essay" : paper.replace("mains_", "");
    models = models
      .sort((a, b) => {
        const aScore = a.mains![year].papers[paperKey]?.score ?? 0;
        const bScore = b.mains![year].papers[paperKey]?.score ?? 0;
        return bScore - aScore;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  }

  return models;
}

export function getModelScore(
  model: ModelEntry,
  year: number,
  paper: Paper
): { marks: number; maxMarks: number; passed: boolean; accuracy: number; correct: number; wrong: number; unanswered: number } {
  if (paper === "overall") {
    // Prelims Rank: show GS1 marks only
    const gs1Data = model.yearly[year]?.gs1;
    if (!gs1Data) return { marks: 0, maxMarks: 200, passed: false, accuracy: 0, correct: 0, wrong: 0, unanswered: 0 };
    const csatData = model.yearly[year]?.csat;
    const csatPassed = csatData?.passed ?? false;
    const total = gs1Data.correct + gs1Data.wrong + gs1Data.unanswered;
    return {
      marks: gs1Data.marks,
      maxMarks: gs1Data.max_marks,
      passed: gs1Data.passed && csatPassed,
      accuracy: total > 0 ? Math.round((gs1Data.correct / total) * 10000) / 100 : 0,
      correct: gs1Data.correct,
      wrong: gs1Data.wrong,
      unanswered: gs1Data.unanswered,
    };
  }

  // Specific paper
  const score = model.yearly[year]?.[paper];
  if (!score) return { marks: 0, maxMarks: 0, passed: false, accuracy: 0, correct: 0, wrong: 0, unanswered: 0 };
  return {
    marks: score.marks,
    maxMarks: score.max_marks,
    passed: score.passed,
    accuracy: score.accuracy,
    correct: score.correct,
    wrong: score.wrong,
    unanswered: score.unanswered,
  };
}

export function getMainsModelScore(
  model: ModelEntry,
  year: number,
  paper: MainsPaper
): { score: number; maxMarks: number; scorePct: number; passed: boolean } {
  const mainsData = model.mains?.[year];
  if (!mainsData) return { score: 0, maxMarks: 0, scorePct: 0, passed: false };

  if (paper === "mains_total") {
    return {
      score: mainsData.total_score,
      maxMarks: mainsData.max_marks,
      scorePct: mainsData.score_pct,
      passed: mainsData.passed,
    };
  }

  const paperKey = paper === "essay" ? "essay" : paper.replace("mains_", "");
  const paperData = mainsData.papers[paperKey];
  if (!paperData) return { score: 0, maxMarks: 0, scorePct: 0, passed: false };

  return {
    score: paperData.score,
    maxMarks: paperData.max_marks,
    scorePct: paperData.score_pct,
    passed: mainsData.passed,
  };
}
