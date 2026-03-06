// Arena logic: pairing generation, vote computation, summary aggregation

import type { ArenaData, ArenaPairing, ArenaRoundResult, VoteChoice } from "@/types/arena";
import { shuffle } from "./utils";

export const ROUNDS_PER_SESSION = 5;

/**
 * Generate randomized pairings for an arena session.
 * Each round picks a question, then two distinct models that both
 * have answers for that question.
 */
export function buildPairings(
  data: ArenaData,
  count: number = ROUNDS_PER_SESSION
): ArenaPairing[] {
  const questions = shuffle(data.questions);
  const pairings: ArenaPairing[] = [];

  for (let attempt = 0; pairings.length < count && attempt < count * 3; attempt++) {
    const question = questions[attempt % questions.length];
    const questionAnswers = data.answers[question.id];
    if (!questionAnswers) continue;

    // Get models that have answers for this specific question
    const models = Object.keys(questionAnswers);
    if (models.length < 2) continue;

    // Fisher-Yates pick 2 distinct models
    const shuffled = shuffle(models);
    pairings.push({
      questionId: question.id,
      modelA: shuffled[0],
      modelB: shuffled[1],
    });
  }

  return pairings;
}

/**
 * Determine which model won based on the user's vote.
 */
export function computeVoteWinner(
  vote: VoteChoice,
  pairing: ArenaPairing
): string | null {
  if (vote === "A") return pairing.modelA;
  if (vote === "B") return pairing.modelB;
  return null;
}

/**
 * Aggregate results from a session into win counts.
 */
export function computeSummary(results: ArenaRoundResult[]): {
  winCounts: Record<string, number>;
  tieCount: number;
  skipCount: number;
} {
  const winCounts: Record<string, number> = {};
  let tieCount = 0;
  let skipCount = 0;

  for (const r of results) {
    if (r.vote === "skip") {
      skipCount++;
    } else if (r.vote === "tie") {
      tieCount++;
    } else if (r.winnerModel) {
      winCounts[r.winnerModel] = (winCounts[r.winnerModel] ?? 0) + 1;
    }
  }

  return { winCounts, tieCount, skipCount };
}
