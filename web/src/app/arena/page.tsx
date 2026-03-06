"use client";

import { useState } from "react";
import Footer from "@/components/Footer";
import ArenaAnswerPanel from "@/components/ArenaAnswerPanel";
import { MODEL_DISPLAY_NAMES, MODEL_COLORS } from "@/lib/constants";
import {
  buildPairings,
  computeVoteWinner,
  computeSummary,
  ROUNDS_PER_SESSION,
  ARENA_PAPER_LABELS,
} from "@/lib/arena";
import type {
  ArenaData,
  ArenaPaper,
  ArenaQuestion,
  ArenaState,
  ArenaPairing,
  ArenaRoundResult,
  VoteChoice,
} from "@/types/arena";
import rawArenaData from "../../../data/arena_data.json";

const arenaData = rawArenaData as ArenaData;

const PAPER_OPTIONS: ArenaPaper[] = [
  "mains_essay",
  "mains_gs1",
  "mains_gs2",
  "mains_gs3",
  "mains_gs4",
];

// ── Page Component ───────────────────────────────────

export default function ArenaPage() {
  const [selectedPaper, setSelectedPaper] = useState<ArenaPaper>("mains_essay");
  const [pairings, setPairings] = useState<ArenaPairing[]>(() =>
    buildPairings(arenaData, ROUNDS_PER_SESSION, selectedPaper)
  );

  const [state, setState] = useState<ArenaState>({
    stage: "comparing",
    pairing: pairings[0],
    roundIndex: 0,
    results: [],
    revealed: false,
  });

  // ── Handlers ─────────────────────────────────────

  function handlePaperChange(paper: ArenaPaper) {
    setSelectedPaper(paper);
    const newPairings = buildPairings(arenaData, ROUNDS_PER_SESSION, paper);
    setPairings(newPairings);
    setState({
      stage: "comparing",
      pairing: newPairings[0],
      roundIndex: 0,
      results: [],
      revealed: false,
    });
  }

  function handleVote(vote: VoteChoice) {
    if (state.stage !== "comparing") return;

    const winnerModel = computeVoteWinner(vote, state.pairing);
    const result: ArenaRoundResult = {
      pairing: state.pairing,
      vote,
      winnerModel,
    };

    setState({
      stage: "voted",
      pairing: state.pairing,
      vote,
      roundIndex: state.roundIndex,
      results: [...state.results, result],
      revealed: state.revealed,
    });
  }

  function handleReveal() {
    if (state.stage !== "comparing") return;
    setState({ ...state, revealed: true });
  }

  function handleNext() {
    if (state.stage !== "voted") return;

    const nextIndex = state.roundIndex + 1;
    if (nextIndex >= pairings.length) {
      setState({ stage: "summary", results: state.results });
    } else {
      setState({
        stage: "comparing",
        pairing: pairings[nextIndex],
        roundIndex: nextIndex,
        results: state.results,
        revealed: false,
      });
    }
  }

  function handleRestart() {
    const newPairings = buildPairings(arenaData, ROUNDS_PER_SESSION, selectedPaper);
    setPairings(newPairings);
    setState({
      stage: "comparing",
      pairing: newPairings[0],
      roundIndex: 0,
      results: [],
      revealed: false,
    });
  }

  // ── Subtitle text ────────────────────────────────
  const paperLabel = ARENA_PAPER_LABELS[selectedPaper];
  const subtitleText =
    selectedPaper === "mains_essay"
      ? `Two AI models, one UPSC essay question. Read both responses blind, then vote for the better answer. Model identities are revealed after you vote.`
      : `Two AI models, one UPSC ${paperLabel} question. Read both answers blind, then vote for the better response. Model identities are revealed after you vote.`;

  // ── Render ───────────────────────────────────────

  return (
    <div className="min-h-screen">
      <div className="tricolor-bar" />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <a
            href="/"
            className="inline-flex items-center gap-1 text-sm transition-colors hover:text-[var(--saffron)]"
            style={{ color: "var(--navy)" }}
          >
            &larr; Back
          </a>
          <div
            className="w-px h-6"
            style={{ backgroundColor: "rgba(26,17,69,0.15)" }}
          />
          <h1 className="section-title text-2xl sm:text-3xl font-bold">
            Arena
          </h1>
        </div>

        {/* Paper selector */}
        {state.stage !== "summary" && (
          <div className="flex flex-wrap gap-2 mb-4">
            {PAPER_OPTIONS.map((paper) => (
              <button
                key={paper}
                onClick={() => handlePaperChange(paper)}
                className={`pill-btn ${selectedPaper === paper ? "active" : "inactive"}`}
                style={
                  selectedPaper === paper
                    ? { background: "var(--navy)", borderColor: "var(--navy)" }
                    : {}
                }
              >
                {ARENA_PAPER_LABELS[paper]}
              </button>
            ))}
          </div>
        )}

        {/* Subtitle */}
        {state.stage !== "summary" && (
          <p
            className="text-sm mb-6 leading-relaxed max-w-2xl"
            style={{ color: "rgba(26,17,69,0.5)" }}
          >
            {subtitleText}
          </p>
        )}

        {/* Progress bar */}
        {state.stage !== "summary" && (
          <ProgressBar
            current={state.roundIndex}
            total={pairings.length}
            completedCount={state.stage === "voted" ? state.roundIndex : state.roundIndex}
          />
        )}

        {/* Main content */}
        {state.stage === "comparing" && (
          <ComparingView
            state={state}
            arenaData={arenaData}
            onVote={handleVote}
            onReveal={handleReveal}
          />
        )}

        {state.stage === "voted" && (
          <VotedView
            state={state}
            arenaData={arenaData}
            totalRounds={pairings.length}
            onNext={handleNext}
          />
        )}

        {state.stage === "summary" && (
          <ArenaSummary
            results={state.results}
            arenaData={arenaData}
            selectedPaper={selectedPaper}
            onRestart={handleRestart}
            onPaperChange={handlePaperChange}
          />
        )}
      </main>

      <Footer />
    </div>
  );
}

// ── Progress Bar ────────────────────────────────────

function ProgressBar({
  current,
  total,
  completedCount,
}: {
  current: number;
  total: number;
  completedCount: number;
}) {
  return (
    <div className="flex items-center gap-2 mb-6">
      {Array.from({ length: total }).map((_, i) => {
        let bgColor: string;
        if (i < completedCount) {
          bgColor = "var(--green)";
        } else if (i === current) {
          bgColor = "var(--saffron)";
        } else {
          bgColor = "rgba(26,17,69,0.08)";
        }
        return (
          <div
            key={i}
            className="flex-1 h-1.5 rounded-full transition-all"
            style={{ backgroundColor: bgColor }}
          />
        );
      })}
      <span
        className="text-xs ml-1 tabular-nums flex-shrink-0"
        style={{ color: "rgba(26,17,69,0.35)" }}
      >
        {current + 1}/{total}
      </span>
    </div>
  );
}

// ── Comparing View ──────────────────────────────────

function ComparingView({
  state,
  arenaData,
  onVote,
  onReveal,
}: {
  state: Extract<ArenaState, { stage: "comparing" }>;
  arenaData: ArenaData;
  onVote: (v: VoteChoice) => void;
  onReveal: () => void;
}) {
  const question = arenaData.questions.find(
    (q) => q.id === state.pairing.questionId
  )!;
  const answerA = arenaData.answers[state.pairing.questionId][state.pairing.modelA];
  const answerB = arenaData.answers[state.pairing.questionId][state.pairing.modelB];

  return (
    <div className="animate-fade-in-up space-y-4">
      <QuestionHeader question={question} />

      <ArenaAnswerPanel
        answerA={answerA}
        answerB={answerB}
        paper={question.paper}
        maxMarks={question.max_marks}
        stage="comparing"
        vote={null}
        revealed={state.revealed}
        modelAName={
          state.revealed
            ? (MODEL_DISPLAY_NAMES[state.pairing.modelA] ?? state.pairing.modelA)
            : null
        }
        modelBName={
          state.revealed
            ? (MODEL_DISPLAY_NAMES[state.pairing.modelB] ?? state.pairing.modelB)
            : null
        }
        modelAColor={state.revealed ? (MODEL_COLORS[state.pairing.modelA] ?? null) : null}
        modelBColor={state.revealed ? (MODEL_COLORS[state.pairing.modelB] ?? null) : null}
        onReveal={onReveal}
      />

      <VoteButtons onVote={onVote} />
    </div>
  );
}

// ── Voted View ──────────────────────────────────────

function VotedView({
  state,
  arenaData,
  totalRounds,
  onNext,
}: {
  state: Extract<ArenaState, { stage: "voted" }>;
  arenaData: ArenaData;
  totalRounds: number;
  onNext: () => void;
}) {
  const question = arenaData.questions.find(
    (q) => q.id === state.pairing.questionId
  )!;
  const answerA = arenaData.answers[state.pairing.questionId][state.pairing.modelA];
  const answerB = arenaData.answers[state.pairing.questionId][state.pairing.modelB];
  const isLast = state.roundIndex >= totalRounds - 1;

  const modelAName =
    MODEL_DISPLAY_NAMES[state.pairing.modelA] ?? state.pairing.modelA;
  const modelBName =
    MODEL_DISPLAY_NAMES[state.pairing.modelB] ?? state.pairing.modelB;

  return (
    <div className="animate-fade-in space-y-4">
      <QuestionHeader question={question} />

      <ArenaAnswerPanel
        answerA={answerA}
        answerB={answerB}
        paper={question.paper}
        maxMarks={question.max_marks}
        stage="voted"
        vote={state.vote}
        revealed={true}
        modelAName={modelAName}
        modelBName={modelBName}
        modelAColor={MODEL_COLORS[state.pairing.modelA] ?? null}
        modelBColor={MODEL_COLORS[state.pairing.modelB] ?? null}
        onReveal={() => {}}
      />

      {/* Vote result banner */}
      <div
        className="glass-card p-4 text-center"
        style={{
          borderColor:
            state.vote === "tie" || state.vote === "skip"
              ? "var(--gold)"
              : "var(--green)",
          borderWidth: "1.5px",
        }}
      >
        <p className="text-sm font-semibold" style={{ color: "var(--navy)" }}>
          {state.vote === "A" && (
            <>
              You chose{" "}
              <span style={{ color: MODEL_COLORS[state.pairing.modelA] ?? "var(--navy)" }}>
                {modelAName}
              </span>
            </>
          )}
          {state.vote === "B" && (
            <>
              You chose{" "}
              <span style={{ color: MODEL_COLORS[state.pairing.modelB] ?? "var(--navy)" }}>
                {modelBName}
              </span>
            </>
          )}
          {state.vote === "tie" && "You called it a tie"}
          {state.vote === "skip" && "Skipped this round"}
        </p>

        {/* Judge scores comparison */}
        {(answerA.total_score !== null || answerB.total_score !== null) && (
          <p
            className="text-xs mt-1"
            style={{ color: "rgba(26,17,69,0.45)" }}
          >
            Judge scores:{" "}
            <span className="font-semibold">
              {modelAName} {answerA.total_score?.toFixed(1) ?? "—"}
            </span>
            {" vs "}
            <span className="font-semibold">
              {modelBName} {answerB.total_score?.toFixed(1) ?? "—"}
            </span>
            /{question.max_marks}
          </p>
        )}
      </div>

      {/* Next button */}
      <div className="flex justify-center">
        <button
          onClick={onNext}
          className="pill-btn active !px-8"
          style={{
            background: "var(--saffron)",
            borderColor: "var(--saffron)",
          }}
        >
          {isLast ? "See results" : "Next comparison"}
        </button>
      </div>
    </div>
  );
}

// ── Question Header ─────────────────────────────────

function QuestionHeader({ question }: { question: ArenaQuestion }) {
  const paperLabel = ARENA_PAPER_LABELS[question.paper];
  const isEssay = question.paper === "mains_essay";
  const isCaseStudy = question.question_type === "case_study";

  // Badge text
  const badgeText = question.section
    ? `${paperLabel} · Section ${question.section}`
    : paperLabel;

  // Task context varies by question type
  let taskContext: React.ReactNode;
  if (isEssay) {
    taskContext = (
      <>
        <strong style={{ color: "rgba(26,17,69,0.7)" }}>The task:</strong>{" "}
        UPSC Mains candidates must write a {question.word_limit}-word essay exploring this
        topic from multiple dimensions — philosophical, social, political, and
        practical — supported by examples from India and the world.{" "}
        <strong style={{ color: "rgba(26,17,69,0.7)" }}>Judge on:</strong>{" "}
        breadth of content, logical structure, depth of examples, analytical
        insight, and clarity of writing.
      </>
    );
  } else if (isCaseStudy) {
    taskContext = (
      <>
        <strong style={{ color: "rgba(26,17,69,0.7)" }}>The task:</strong>{" "}
        This is an ethics case study. Candidates must analyze the scenario and answer within{" "}
        {question.word_limit} words, demonstrating ethical reasoning, stakeholder analysis,
        and practical solutions.{" "}
        <strong style={{ color: "rgba(26,17,69,0.7)" }}>Judge on:</strong>{" "}
        accuracy of content, logical structure, use of examples, analytical depth, and presentation.
      </>
    );
  } else {
    taskContext = (
      <>
        <strong style={{ color: "rgba(26,17,69,0.7)" }}>The task:</strong>{" "}
        Candidates must answer this {question.max_marks}-mark question within{" "}
        {question.word_limit} words, demonstrating factual accuracy and analytical depth.{" "}
        <strong style={{ color: "rgba(26,17,69,0.7)" }}>Judge on:</strong>{" "}
        accuracy of content, logical structure, use of examples, analytical depth, and presentation.
      </>
    );
  }

  return (
    <div className="glass-card p-4 sm:p-5">
      <div className="flex items-start gap-3">
        <span
          className="flex-shrink-0 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider"
          style={{
            backgroundColor: "rgba(255,153,51,0.1)",
            color: "var(--saffron)",
          }}
        >
          {badgeText}
        </span>
        <div className="flex-1 min-w-0">
          {isEssay ? (
            <h2
              className="text-lg sm:text-xl font-bold leading-snug"
              style={{
                fontFamily: "var(--font-playfair), serif",
                color: "var(--navy)",
              }}
            >
              &ldquo;{question.question_text}&rdquo;
            </h2>
          ) : (
            <div
              className={`text-sm sm:text-base leading-relaxed ${isCaseStudy ? "max-h-48 overflow-y-auto scrollbar-hide" : ""}`}
              style={{ color: "var(--navy)" }}
            >
              {question.question_text}
            </div>
          )}
          <p
            className="text-xs mt-1"
            style={{ color: "rgba(26,17,69,0.4)" }}
          >
            {question.max_marks} marks · {question.word_limit} word limit
          </p>
        </div>
      </div>

      {/* Task context */}
      <div
        className="mt-3 px-3 py-2.5 rounded-lg text-xs leading-relaxed"
        style={{
          backgroundColor: "rgba(26,17,69,0.025)",
          color: "rgba(26,17,69,0.55)",
        }}
      >
        {taskContext}
      </div>
    </div>
  );
}

// ── Vote Buttons ────────────────────────────────────

function VoteButtons({ onVote }: { onVote: (v: VoteChoice) => void }) {
  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-2 sm:gap-3 py-2">
      <button
        onClick={() => onVote("A")}
        className="pill-btn active !px-6 text-center"
        style={{
          background: "var(--navy)",
          borderColor: "var(--navy)",
        }}
      >
        Model A is better
      </button>
      <button
        onClick={() => onVote("tie")}
        className="pill-btn inactive !px-5 text-center"
      >
        Tie
      </button>
      <button
        onClick={() => onVote("skip")}
        className="pill-btn inactive !px-5 text-center"
      >
        Skip
      </button>
      <button
        onClick={() => onVote("B")}
        className="pill-btn active !px-6 text-center"
        style={{
          background: "var(--navy)",
          borderColor: "var(--navy)",
        }}
      >
        Model B is better
      </button>
    </div>
  );
}

// ── Summary Screen ──────────────────────────────────

function ArenaSummary({
  results,
  arenaData,
  selectedPaper,
  onRestart,
  onPaperChange,
}: {
  results: ArenaRoundResult[];
  arenaData: ArenaData;
  selectedPaper: ArenaPaper;
  onRestart: () => void;
  onPaperChange: (paper: ArenaPaper) => void;
}) {
  const { winCounts, tieCount, skipCount } = computeSummary(results);

  // Sort models by win count descending
  const rankedModels = Object.entries(winCounts).sort(([, a], [, b]) => b - a);

  return (
    <div className="space-y-6 animate-fade-in-up max-w-2xl mx-auto">
      <div className="text-center mb-2">
        <h2
          className="section-title text-2xl sm:text-3xl font-bold"
          style={{ fontFamily: "var(--font-playfair), serif" }}
        >
          Session Results
        </h2>
        <p
          className="text-sm mt-3"
          style={{ color: "rgba(26,17,69,0.5)" }}
        >
          Your preference rankings across {results.length}{" "}
          {ARENA_PAPER_LABELS[selectedPaper]} comparisons
        </p>
      </div>

      {/* Win counts */}
      {rankedModels.length > 0 && (
        <div className="glass-card overflow-hidden">
          <div
            className="px-4 py-3"
            style={{ borderBottom: "1px solid rgba(26,17,69,0.06)" }}
          >
            <h3
              className="text-sm font-semibold"
              style={{ color: "var(--navy)" }}
            >
              Your preferred models
            </h3>
          </div>
          <div className="divide-y" style={{ borderColor: "rgba(26,17,69,0.04)" }}>
            {rankedModels.map(([model, wins], idx) => {
              const name = MODEL_DISPLAY_NAMES[model] ?? model;
              const color = MODEL_COLORS[model] ?? "var(--navy)";
              return (
                <div
                  key={model}
                  className="px-4 py-3 flex items-center gap-3"
                >
                  <span
                    className={`rank-badge ${idx === 0 ? "gold" : idx === 1 ? "silver" : "default"}`}
                  >
                    {idx + 1}
                  </span>
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <div
                      className="w-1.5 h-5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: color }}
                    />
                    <span
                      className="font-semibold text-sm"
                      style={{ color: "var(--navy)" }}
                    >
                      {name}
                    </span>
                  </div>
                  <span
                    className="font-bold text-sm tabular-nums"
                    style={{ color: "var(--navy)" }}
                  >
                    {wins} win{wins !== 1 ? "s" : ""}
                  </span>
                </div>
              );
            })}
          </div>
          {(tieCount > 0 || skipCount > 0) && (
            <div
              className="px-4 py-2.5 flex gap-4"
              style={{ borderTop: "1px solid rgba(26,17,69,0.06)" }}
            >
              {tieCount > 0 && (
                <span className="text-xs" style={{ color: "rgba(26,17,69,0.4)" }}>
                  {tieCount} tie{tieCount !== 1 ? "s" : ""}
                </span>
              )}
              {skipCount > 0 && (
                <span className="text-xs" style={{ color: "rgba(26,17,69,0.4)" }}>
                  {skipCount} skipped
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Round-by-round review */}
      <div className="glass-card overflow-hidden">
        <div
          className="px-4 py-3"
          style={{ borderBottom: "1px solid rgba(26,17,69,0.06)" }}
        >
          <h3
            className="text-sm font-semibold"
            style={{ color: "var(--navy)" }}
          >
            Round-by-round
          </h3>
        </div>
        <div>
          {results.map((r, i) => {
            const question = arenaData.questions.find(
              (q) => q.id === r.pairing.questionId
            );
            const nameA =
              MODEL_DISPLAY_NAMES[r.pairing.modelA] ?? r.pairing.modelA;
            const nameB =
              MODEL_DISPLAY_NAMES[r.pairing.modelB] ?? r.pairing.modelB;
            const winnerName = r.winnerModel
              ? (MODEL_DISPLAY_NAMES[r.winnerModel] ?? r.winnerModel)
              : r.vote === "tie"
                ? "Tie"
                : "Skipped";

            const isEssay = question?.paper === "mains_essay";
            const questionLabel = question
              ? isEssay
                ? `\u201C${question.question_text}\u201D`
                : question.question_text
              : r.pairing.questionId;

            return (
              <div
                key={i}
                className="px-4 py-2.5 flex items-center gap-3 text-sm"
                style={{
                  borderBottom:
                    i < results.length - 1
                      ? "1px solid rgba(26,17,69,0.04)"
                      : "none",
                }}
              >
                <span
                  className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{
                    backgroundColor:
                      r.vote === "skip"
                        ? "rgba(26,17,69,0.06)"
                        : r.vote === "tie"
                          ? "rgba(212,168,67,0.1)"
                          : "rgba(19,136,8,0.08)",
                    color:
                      r.vote === "skip"
                        ? "rgba(26,17,69,0.4)"
                        : r.vote === "tie"
                          ? "var(--gold)"
                          : "var(--green)",
                  }}
                >
                  {i + 1}
                </span>
                <span
                  className="flex-1 truncate"
                  style={{ color: "rgba(26,17,69,0.6)" }}
                >
                  {questionLabel}
                </span>
                <span
                  className="text-xs flex-shrink-0"
                  style={{ color: "rgba(26,17,69,0.4)" }}
                >
                  {nameA} vs {nameB}
                </span>
                <span
                  className="text-xs font-semibold flex-shrink-0 w-20 text-right"
                  style={{
                    color: r.winnerModel
                      ? (MODEL_COLORS[r.winnerModel] ?? "var(--navy)")
                      : "rgba(26,17,69,0.4)",
                  }}
                >
                  {winnerName}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap items-center justify-center gap-3">
        <button
          onClick={onRestart}
          className="pill-btn active !px-6"
          style={{
            background: "var(--saffron)",
            borderColor: "var(--saffron)",
          }}
        >
          New session
        </button>
        {/* Quick paper switch from summary */}
        {PAPER_OPTIONS.filter((p) => p !== selectedPaper).map((paper) => (
          <button
            key={paper}
            onClick={() => onPaperChange(paper)}
            className="pill-btn inactive !px-5"
          >
            Try {ARENA_PAPER_LABELS[paper]}
          </button>
        ))}
        <a href="/" className="pill-btn inactive !px-6">
          Back to leaderboard
        </a>
      </div>
    </div>
  );
}
