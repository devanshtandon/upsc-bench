// Arena-specific types for the /arena side-by-side comparison feature

export type ArenaPaper = "mains_essay" | "mains_gs1" | "mains_gs2" | "mains_gs3" | "mains_gs4";

export interface ArenaQuestion {
  id: string;
  paper: ArenaPaper;
  question_type: "essay" | "short_answer" | "case_study";
  section: string | null;
  question_number: number;
  question_text: string;
  word_limit: number;
  max_marks: number;
}

// Flexible rubric scores — essays use content_breadth, GS uses content_accuracy
export type ArenaRubricScores = Record<string, number>;

export interface ArenaAnswer {
  text: string;
  word_count: number;
  rubric_scores: ArenaRubricScores | null;
  total_score: number | null;
  feedback: string | null;
}

export type ArenaAnswerMap = Record<string, Record<string, ArenaAnswer>>;

export interface ArenaData {
  questions: ArenaQuestion[];
  answers: ArenaAnswerMap;
}

export interface ArenaPairing {
  questionId: string;
  paper: ArenaPaper;
  modelA: string;
  modelB: string;
}

export type VoteChoice = "A" | "B" | "tie" | "skip";

export interface ArenaRoundResult {
  pairing: ArenaPairing;
  vote: VoteChoice;
  winnerModel: string | null;
}

export type ArenaState =
  | { stage: "comparing"; pairing: ArenaPairing; roundIndex: number; results: ArenaRoundResult[]; revealed: boolean }
  | { stage: "voted"; pairing: ArenaPairing; vote: VoteChoice; roundIndex: number; results: ArenaRoundResult[]; revealed: boolean }
  | { stage: "summary"; results: ArenaRoundResult[] };
