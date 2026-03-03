import type { RawQuestion } from "../types";

// ── Types ──────────────────────────────────────────────

export interface QuizQuestion {
  id: string;
  question_number: number;
  question_text: string;
  options: { a: string; b: string; c: string; d: string };
  correct_answer: string;
  has_image: boolean;
  image_paths: string[];
  image_description: string;
  marks_correct: number;
  marks_wrong: number;
}

export interface QuizResult {
  question: QuizQuestion;
  userAnswer: string | null; // null = skipped
  isCorrect: boolean;
  marksEarned: number;
}

export interface QuizSummary {
  results: QuizResult[];
  rawScore: number;
  extrapolatedScore: number;
  maxMarks: number;
  correct: number;
  wrong: number;
  skipped: number;
  accuracy: number;
  passed: boolean;
  cutoff: number;
  margin: number;
  estimatedRank: number | null;
  estimatedRankLabel: string;
  totalAppeared: number;
}

// ── Question Selection ─────────────────────────────────

const QUIZ_SIZE = 5;
const QUIZ_YEAR = 2025;
const QUIZ_PAPER = "gs1";

export function pickQuizQuestions(allQuestions: RawQuestion[]): QuizQuestion[] {
  const pool = allQuestions.filter(
    (q) => q.year === QUIZ_YEAR && q.paper === QUIZ_PAPER
  );

  // Fisher-Yates shuffle
  const shuffled = [...pool];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  return shuffled.slice(0, QUIZ_SIZE).map((q) => ({
    id: q.id,
    question_number: q.question_number,
    question_text: q.question_text,
    options: q.options,
    correct_answer: q.correct_answer,
    has_image: q.has_image,
    image_paths: q.image_paths,
    image_description: q.image_description,
    marks_correct: q.marks_correct,
    marks_wrong: q.marks_wrong,
  }));
}

// ── Grading ────────────────────────────────────────────

export function gradeAnswer(
  question: QuizQuestion,
  answer: string | null
): { isCorrect: boolean; marksEarned: number } {
  if (answer === null) {
    return { isCorrect: false, marksEarned: 0 };
  }
  const isCorrect = answer === question.correct_answer;
  const marksEarned = isCorrect ? question.marks_correct : question.marks_wrong;
  return { isCorrect, marksEarned };
}

// ── Scoring ────────────────────────────────────────────

const GS1_TOTAL_QUESTIONS = 100;
const GS1_MAX_MARKS = 200;

export function computeQuizSummary(
  results: QuizResult[],
  rankData: RankYearData
): QuizSummary {
  const correct = results.filter((r) => r.isCorrect).length;
  const skipped = results.filter((r) => r.userAnswer === null).length;
  const wrong = results.length - correct - skipped;
  const rawScore = results.reduce((sum, r) => sum + r.marksEarned, 0);

  // Extrapolate: scale up to 100-question paper
  const scaleFactor = GS1_TOTAL_QUESTIONS / results.length;
  const extrapolatedScore =
    Math.round(rawScore * scaleFactor * 100) / 100;

  const cutoff = rankData.cutoff_general;
  const passed = extrapolatedScore >= cutoff;
  const margin = Math.round((extrapolatedScore - cutoff) * 100) / 100;
  const totalQuestions = correct + wrong + skipped;
  const accuracy =
    totalQuestions > 0
      ? Math.round((correct / totalQuestions) * 10000) / 100
      : 0;

  const rankResult = interpolateRank(extrapolatedScore, rankData);

  return {
    results,
    rawScore: Math.round(rawScore * 100) / 100,
    extrapolatedScore,
    maxMarks: GS1_MAX_MARKS,
    correct,
    wrong,
    skipped,
    accuracy,
    passed,
    cutoff,
    margin,
    estimatedRank: rankResult.rank,
    estimatedRankLabel: rankResult.label,
    totalAppeared: rankResult.totalAppeared,
  };
}

// ── Rank Interpolation ─────────────────────────────────

export interface RankYearData {
  total_appeared: number;
  mains_qualified: number;
  cutoff_general: number;
  estimated_topper: number;
  distribution: Array<{ score: number; rank: number }>;
}

function interpolateRank(
  score: number,
  yearData: RankYearData
): { rank: number | null; label: string; totalAppeared: number } {
  const { total_appeared, cutoff_general, estimated_topper, distribution } =
    yearData;

  // Below cutoff
  if (score < cutoff_general) {
    return {
      rank: null,
      label: "Did not qualify",
      totalAppeared: total_appeared,
    };
  }

  // Above estimated topper
  if (score >= estimated_topper) {
    return {
      rank: 1,
      label: "Exceeds topper estimate",
      totalAppeared: total_appeared,
    };
  }

  // Interpolate between anchor points (distribution sorted descending by score)
  for (let i = 0; i < distribution.length - 1; i++) {
    const high = distribution[i];
    const low = distribution[i + 1];
    if (low.score <= score && score <= high.score) {
      const scoreRange = high.score - low.score;
      let rank: number;
      if (scoreRange === 0) {
        rank = high.rank;
      } else {
        const fraction = (high.score - score) / scoreRange;
        rank = high.rank + fraction * (low.rank - high.rank);
      }
      rank = Math.max(1, Math.round(rank));

      let label: string;
      if (rank <= 10) label = "Topper territory";
      else if (rank <= 100) label = "Top 100";
      else if (rank <= 500) label = "Top 500";
      else if (rank <= 1000) label = "Top 1,000";
      else if (rank <= 5000) label = "Top 5,000";
      else label = `Top ${((Math.floor(rank / 1000) + 1) * 1000).toLocaleString()}`;

      return { rank, label, totalAppeared: total_appeared };
    }
  }

  // Fallback: at cutoff boundary
  return {
    rank: yearData.mains_qualified,
    label: "At cutoff",
    totalAppeared: total_appeared,
  };
}
