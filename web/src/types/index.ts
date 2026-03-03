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

export interface ModelEntry {
  rank: number;
  model: string;
  overall: ModelOverall;
  paper_totals: Record<string, PaperTotals>;
  yearly: Record<number, Record<string, PaperScore>>;
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
  };
}

export type Paper = "gs1" | "csat" | "overall";
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
