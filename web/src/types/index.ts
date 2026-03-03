export interface PaperScore {
  marks: number;
  max_marks: number;
  correct: number;
  wrong: number;
  unanswered: number;
  accuracy: number;
  passed: boolean;
  cutoff: number;
  margin: number;
}

export interface PaperTotals {
  total_marks: number;
  max_marks: number;
  correct: number;
  wrong: number;
  unanswered: number;
  years_passed: number;
  years_total: number;
}

export interface ModelOverall {
  total_questions: number;
  correct: number;
  wrong: number;
  unanswered: number;
  accuracy: number;
  gs1_avg_marks: number;
  gs1_all_years_pass: boolean;
  csat_all_years_pass: boolean;
}

// Mains types
export interface MainsPaperScore {
  score: number;
  max_marks: number;
  score_pct: number;
  questions_evaluated: number;
  selected_essays?: string[];
}

export interface MainsEstimatedRank {
  rank: number;
  percentile: number;
  label: string;
  total_candidates: number;
  note?: string;
}

export interface MainsYearData {
  total_score: number;
  max_marks: number;
  score_pct: number;
  passed: boolean;
  cutoff: number;
  margin: number;
  estimated_rank: MainsEstimatedRank;
  papers: Record<string, MainsPaperScore>;
}

export interface ModelEntry {
  rank: number;
  model: string;
  is_human?: boolean;
  overall: ModelOverall;
  paper_totals: Record<string, PaperTotals>;
  yearly: Record<number, Record<string, PaperScore>>;
  mains?: Record<number, MainsYearData>;
}

export interface MarkingScheme {
  correct: number;
  wrong: number;
  unanswered: number;
  total_questions: number;
  max_marks: number;
}

export interface LeaderboardData {
  models: ModelEntry[];
  metadata: {
    total_models: number;
    years: number[];
    papers: string[];
    cutoffs: Record<number, Record<string, number>>;
    marking_scheme: Record<string, MarkingScheme>;
    mains_years?: number[];
    mains_papers?: string[];
    mains_cutoffs?: Record<number, { proportional_cutoff: number; max_marks: number }>;
  };
}

export type ExamType = "prelims" | "mains";
export type Paper = "gs1" | "csat" | "overall";
export type MainsPaper = "mains_total" | "essay" | "mains_gs1" | "mains_gs2" | "mains_gs3" | "mains_gs4";
export type Year = number | "all";

// Raw question from upsc_bench.json
export interface RawQuestion {
  id: string;
  year: number;
  paper: string;
  question_number: number;
  question_text: string;
  options: { a: string; b: string; c: string; d: string };
  has_image: boolean;
  image_paths: string[];
  image_description: string;
  correct_answer: string;
  marks_correct: number;
  marks_wrong: number;
  marks_unanswered: number;
}
