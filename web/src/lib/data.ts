import leaderboardJson from "../../data/leaderboard.json";
import type { LeaderboardData, ModelEntry, Paper, Year, PaperScore } from "../types";

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
    // Specific year, overall (sum both papers)
    models = models
      .sort((a, b) => {
        const aMarks = Object.values(a.yearly[year] ?? {}).reduce(
          (sum: number, s) => sum + (s as PaperScore).marks,
          0
        );
        const bMarks = Object.values(b.yearly[year] ?? {}).reduce(
          (sum: number, s) => sum + (s as PaperScore).marks,
          0
        );
        return bMarks - aMarks;
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
    // All years + overall: rank by overall accuracy
    models = models
      .sort((a, b) => {
        const aAcc = a.overall.accuracy;
        const bAcc = b.overall.accuracy;
        if (bAcc !== aAcc) return bAcc - aAcc;
        // Tiebreaker: average combined marks across years
        return getAllYearsOverallMarks(b) - getAllYearsOverallMarks(a);
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
    // Average combined marks (GS1 + CSAT) across all years
    const avgMarks = getAllYearsOverallMarks(model);
    const numYears = Object.keys(model.yearly).length || 1;
    const maxPerYear = Object.values(model.yearly)[0]
      ? Object.values(Object.values(model.yearly)[0]).reduce(
          (sum, s) => sum + (s as PaperScore).max_marks, 0)
      : 400;
    return {
      marks: avgMarks,
      maxMarks: maxPerYear,
      passed: model.overall.gs1_all_years_pass && model.overall.csat_all_years_pass,
      accuracy: model.overall.accuracy,
      correct: Math.round(model.overall.correct / numYears),
      wrong: Math.round(model.overall.wrong / numYears),
      unanswered: Math.round(model.overall.unanswered / numYears),
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
    const yearData = model.yearly[year] ?? {};
    const marks = Object.values(yearData).reduce(
      (sum, s) => sum + (s as PaperScore).marks,
      0
    );
    const maxMarks = Object.values(yearData).reduce(
      (sum, s) => sum + (s as PaperScore).max_marks,
      0
    );
    const correct = Object.values(yearData).reduce(
      (sum, s) => sum + (s as PaperScore).correct,
      0
    );
    const wrong = Object.values(yearData).reduce(
      (sum, s) => sum + (s as PaperScore).wrong,
      0
    );
    const unansweredCount = Object.values(yearData).reduce(
      (sum, s) => sum + (s as PaperScore).unanswered,
      0
    );
    const total = Object.values(yearData).reduce(
      (sum, s) =>
        sum +
        (s as PaperScore).correct +
        (s as PaperScore).wrong +
        (s as PaperScore).unanswered,
      0
    );
    const allPassed = Object.values(yearData).every(
      (s) => (s as PaperScore).passed
    );
    return {
      marks: Math.round(marks * 100) / 100,
      maxMarks,
      passed: allPassed,
      accuracy: total > 0 ? Math.round((correct / total) * 10000) / 100 : 0,
      correct,
      wrong,
      unanswered: unansweredCount,
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

/** Average combined marks (all papers) per year across all years. */
function getAllYearsOverallMarks(model: ModelEntry): number {
  const years = Object.values(model.yearly);
  if (years.length === 0) return 0;
  const totalMarks = years.reduce((sum, yearPapers) => {
    const yearSum = Object.values(yearPapers).reduce(
      (s, p) => s + (p as PaperScore).marks, 0
    );
    return sum + yearSum;
  }, 0);
  return Math.round((totalMarks / years.length) * 100) / 100;
}
