import leaderboardJson from "../../data/leaderboard.json";
import type { LeaderboardData, ModelEntry, Paper, Year } from "../types";

export function getLeaderboardData(): LeaderboardData {
  return leaderboardJson as LeaderboardData;
}

export function getFilteredModels(
  data: LeaderboardData,
  year: Year,
  paper: Paper
): ModelEntry[] {
  let models = [...data.models];

  // Re-rank based on filter
  if (year !== "all" && paper !== "overall") {
    models = models
      .filter((m) => m.yearly[year]?.[paper])
      .sort((a, b) => {
        const aScore = a.yearly[year]?.[paper]?.marks ?? 0;
        const bScore = b.yearly[year]?.[paper]?.marks ?? 0;
        return bScore - aScore;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  } else if (year !== "all") {
    // Specific year, overall = Prelims Rank: sort by GS1 marks, CSAT-fail models last
    models = models
      .sort((a, b) => {
        const aCsatPass = (a.yearly[year]?.csat?.passed) ? 1 : 0;
        const bCsatPass = (b.yearly[year]?.csat?.passed) ? 1 : 0;
        if (aCsatPass !== bCsatPass) return bCsatPass - aCsatPass;
        const aGs1 = a.yearly[year]?.gs1?.marks ?? 0;
        const bGs1 = b.yearly[year]?.gs1?.marks ?? 0;
        return bGs1 - aGs1;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  } else if (paper !== "overall") {
    // All years, specific paper
    models = models
      .sort((a, b) => {
        const aTotal = a.paper_totals[paper]?.total_marks ?? 0;
        const bTotal = b.paper_totals[paper]?.total_marks ?? 0;
        return bTotal - aTotal;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  } else {
    // All years + overall: rank by GS1 avg marks, CSAT-fail models last
    models = models
      .sort((a, b) => {
        const aCsatPass = a.overall.csat_all_years_pass ? 1 : 0;
        const bCsatPass = b.overall.csat_all_years_pass ? 1 : 0;
        if (aCsatPass !== bCsatPass) return bCsatPass - aCsatPass;
        return b.overall.gs1_avg_marks - a.overall.gs1_avg_marks;
      })
      .map((m, i) => ({ ...m, rank: i + 1 }));
  }

  return models;
}

export function getModelScore(
  model: ModelEntry,
  year: Year,
  paper: Paper
): { marks: number; maxMarks: number; passed: boolean; accuracy: number; correct: number; wrong: number; unanswered: number } {
  if (year === "all" && paper === "overall") {
    // Prelims Rank (all years): show GS1 average marks
    const gs1Totals = model.paper_totals.gs1;
    if (!gs1Totals) return { marks: 0, maxMarks: 200, passed: false, accuracy: 0, correct: 0, wrong: 0, unanswered: 0 };
    const years = gs1Totals.years_total || 1;
    const total = gs1Totals.correct + gs1Totals.wrong + gs1Totals.unanswered;
    return {
      marks: Math.round((gs1Totals.total_marks / years) * 100) / 100,
      maxMarks: gs1Totals.max_marks / years,
      passed: model.overall.gs1_all_years_pass && model.overall.csat_all_years_pass,
      accuracy: total > 0 ? Math.round((gs1Totals.correct / total) * 10000) / 100 : 0,
      correct: Math.round(gs1Totals.correct / years),
      wrong: Math.round(gs1Totals.wrong / years),
      unanswered: Math.round(gs1Totals.unanswered / years),
    };
  }

  if (year === "all" && paper !== "overall") {
    const pt = model.paper_totals[paper];
    if (!pt) return { marks: 0, maxMarks: 0, passed: false, accuracy: 0, correct: 0, wrong: 0, unanswered: 0 };
    const years = pt.years_total || 1;
    const total = pt.correct + pt.wrong + pt.unanswered;
    return {
      marks: Math.round((pt.total_marks / years) * 100) / 100,
      maxMarks: pt.max_marks / years,
      passed: pt.years_passed === pt.years_total,
      accuracy: total > 0 ? Math.round((pt.correct / total) * 10000) / 100 : 0,
      correct: Math.round(pt.correct / years),
      wrong: Math.round(pt.wrong / years),
      unanswered: Math.round(pt.unanswered / years),
    };
  }

  if (year !== "all" && paper === "overall") {
    // Prelims Rank (specific year): show GS1 marks only
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

  // Specific year + specific paper
  const score = model.yearly[year as number]?.[paper];
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
