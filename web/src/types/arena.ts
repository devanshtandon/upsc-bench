// Arena-specific types for the /arena side-by-side comparison feature

export interface ArenaQuestion {
  id: string;
  section: "A" | "B";
  question_number: number;
  question_text: string;
  word_limit: number;
  max_marks: number;
}

export interface ArenaRubricScores {
  content_breadth: number;
  structure_flow: number;
  depth_examples: number;
  analytical_depth: number;
  presentation: number;
}

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
