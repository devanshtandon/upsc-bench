"use client";

import { useState, useMemo } from "react";
import Footer from "@/components/Footer";
import QuestionCard from "@/components/QuestionCard";
import {
  pickQuizQuestions,
  gradeAnswer,
  computeQuizSummary,
} from "@/lib/quiz";
import type { QuizResult, QuizSummary, RankYearData } from "@/lib/quiz";
import type { RawQuestion } from "@/types";
import { MODEL_DISPLAY_NAMES, MODEL_COLORS } from "@/lib/constants";
import allQuestions from "../../../data/upsc_bench.json";
import rankMappingData from "../../../data/rank_mapping.json";
import leaderboardData from "../../../data/leaderboard.json";

// ── State Types ──────────────────────────────────────

type QuizState =
  | {
      stage: "question";
      qIndex: number;
      results: QuizResult[];
      showFeedback: boolean;
      lastAnswer: string | null;
    }
  | { stage: "results"; summary: QuizSummary };

// ── Page Component ───────────────────────────────────

export default function QuizPage() {
  const [quizKey, setQuizKey] = useState(0);
  const questions = useMemo(
    () => pickQuizQuestions(allQuestions as RawQuestion[]),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [quizKey]
  );

  const [state, setState] = useState<QuizState>({
    stage: "question",
    qIndex: 0,
    results: [],
    showFeedback: false,
    lastAnswer: null,
  });

  const rankYear = (rankMappingData as Record<string, RankYearData>)["2025"];

  // ── Handlers ─────────────────────────────────────

  function handleAnswer(answer: string) {
    if (state.stage !== "question" || state.showFeedback) return;
    setState({ ...state, showFeedback: true, lastAnswer: answer });
  }

  function handleSkip() {
    if (state.stage !== "question" || state.showFeedback) return;
    setState({ ...state, showFeedback: true, lastAnswer: null });
  }

  function handleNext() {
    if (state.stage !== "question" || !state.showFeedback) return;

    const question = questions[state.qIndex];
    const { isCorrect, marksEarned } = gradeAnswer(question, state.lastAnswer);
    const result: QuizResult = {
      question,
      userAnswer: state.lastAnswer,
      isCorrect,
      marksEarned,
    };
    const newResults = [...state.results, result];

    if (state.qIndex >= questions.length - 1) {
      // All questions done
      const summary = computeQuizSummary(newResults, rankYear);
      setState({ stage: "results", summary });
    } else {
      setState({
        stage: "question",
        qIndex: state.qIndex + 1,
        results: newResults,
        showFeedback: false,
        lastAnswer: null,
      });
    }
  }

  function handleRestart() {
    setQuizKey((k) => k + 1);
    setState({
      stage: "question",
      qIndex: 0,
      results: [],
      showFeedback: false,
      lastAnswer: null,
    });
  }

  // ── Render ───────────────────────────────────────

  return (
    <div className="min-h-screen">
      <div className="tricolor-bar" />

      <main className="max-w-2xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
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
          <h1 className="section-title text-3xl font-bold">UPSC Quiz</h1>
        </div>

        {/* Subtitle */}
        {state.stage === "question" && (
          <p
            className="text-sm mb-6 leading-relaxed"
            style={{ color: "rgba(26,17,69,0.5)" }}
          >
            5 random questions from GS Paper I, 2025. Answer each question or
            skip it — just like the real UPSC Prelims.
          </p>
        )}

        {/* Progress dots */}
        {state.stage === "question" && (
          <ProgressDots
            current={state.qIndex}
            total={questions.length}
            results={state.results}
          />
        )}

        {/* Question */}
        {state.stage === "question" && (
          <QuestionCard
            question={questions[state.qIndex]}
            qIndex={state.qIndex}
            total={questions.length}
            showFeedback={state.showFeedback}
            lastAnswer={state.lastAnswer}
            onAnswer={handleAnswer}
            onSkip={handleSkip}
            onNext={handleNext}
          />
        )}

        {/* Results */}
        {state.stage === "results" && (
          <ResultsScreen
            summary={state.summary}
            onRestart={handleRestart}
          />
        )}
      </main>

      <Footer />
    </div>
  );
}

// ── Progress Dots ────────────────────────────────────

function ProgressDots({
  current,
  total,
  results,
}: {
  current: number;
  total: number;
  results: QuizResult[];
}) {
  return (
    <div className="flex items-center gap-2 mb-6">
      {Array.from({ length: total }).map((_, i) => {
        let bgColor: string;
        if (i < results.length) {
          // Completed question
          bgColor = results[i].isCorrect
            ? "var(--green)"
            : results[i].userAnswer === null
              ? "rgba(26,17,69,0.2)"
              : "#DC2626";
        } else if (i === current) {
          bgColor = "var(--saffron)";
        } else {
          bgColor = "rgba(26,17,69,0.1)";
        }

        return (
          <div
            key={i}
            className="flex-1 h-1.5 rounded-full transition-all"
            style={{ backgroundColor: bgColor }}
          />
        );
      })}
    </div>
  );
}

// ── Results Screen ───────────────────────────────────

function ResultsScreen({
  summary,
  onRestart,
}: {
  summary: QuizSummary;
  onRestart: () => void;
}) {
  // Build comparison data: user + AI models
  const aiModels = leaderboardData.models
    .map((m) => {
      const gs1 = (m.yearly as Record<string, Record<string, { marks: number; max_marks: number }>>)["2025"]?.gs1;
      if (!gs1) return null;
      return {
        name: MODEL_DISPLAY_NAMES[m.model] ?? m.model,
        color: MODEL_COLORS[m.model] ?? "#1a1145",
        marks: gs1.marks,
        maxMarks: gs1.max_marks,
        isUser: false,
      };
    })
    .filter(Boolean) as Array<{
    name: string;
    color: string;
    marks: number;
    maxMarks: number;
    isUser: boolean;
  }>;

  const userEntry = {
    name: "You",
    color: "#FF9933",
    marks: summary.extrapolatedScore,
    maxMarks: summary.maxMarks,
    isUser: true,
  };

  const allEntries = [...aiModels, userEntry].sort(
    (a, b) => b.marks - a.marks
  );

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Score card */}
      <div className="glass-card p-6">
        <h2
          className="text-xl font-bold mb-4"
          style={{
            fontFamily: "var(--font-playfair), serif",
            color: "var(--navy)",
          }}
        >
          Your Results
        </h2>

        <div className="grid grid-cols-3 gap-4 mb-5">
          <div className="text-center">
            <div
              className="text-2xl font-bold"
              style={{ color: "var(--navy)" }}
            >
              {summary.extrapolatedScore.toFixed(1)}
              <span
                className="text-sm font-normal"
                style={{ color: "rgba(26,17,69,0.3)" }}
              >
                /{summary.maxMarks}
              </span>
            </div>
            <div
              className="text-[11px] mt-1"
              style={{ color: "rgba(26,17,69,0.4)" }}
            >
              Est. Score
            </div>
          </div>

          <div className="text-center">
            <div
              className="text-2xl font-bold"
              style={{
                color: summary.passed ? "var(--green)" : "#DC2626",
              }}
            >
              {summary.passed ? "PASS" : "FAIL"}
            </div>
            <div
              className="text-[11px] mt-1"
              style={{ color: "rgba(26,17,69,0.4)" }}
            >
              vs {summary.cutoff}/200 cutoff
            </div>
          </div>

          <div className="text-center">
            {summary.estimatedRank !== null ? (
              <>
                <div
                  className="text-2xl font-bold"
                  style={{ color: "var(--saffron)" }}
                >
                  ~{summary.estimatedRank.toLocaleString()}
                </div>
                <div
                  className="text-[11px] mt-1"
                  style={{ color: "rgba(26,17,69,0.4)" }}
                >
                  Est. AIR of{" "}
                  {(summary.totalAppeared / 100000).toFixed(0)}L
                </div>
              </>
            ) : (
              <>
                <div
                  className="text-2xl font-bold"
                  style={{ color: "rgba(26,17,69,0.3)" }}
                >
                  —
                </div>
                <div
                  className="text-[11px] mt-1"
                  style={{ color: "rgba(26,17,69,0.4)" }}
                >
                  Below cutoff
                </div>
              </>
            )}
          </div>
        </div>

        {/* Breakdown pills */}
        <div className="flex items-center justify-center gap-4 text-sm">
          <span
            className="px-3 py-1 rounded-full font-semibold"
            style={{
              backgroundColor: "rgba(19,136,8,0.08)",
              color: "var(--green)",
            }}
          >
            {summary.correct} correct
          </span>
          <span
            className="px-3 py-1 rounded-full font-semibold"
            style={{
              backgroundColor: "rgba(220,38,38,0.08)",
              color: "#DC2626",
            }}
          >
            {summary.wrong} wrong
          </span>
          <span
            className="px-3 py-1 rounded-full font-semibold"
            style={{
              backgroundColor: "rgba(26,17,69,0.04)",
              color: "rgba(26,17,69,0.4)",
            }}
          >
            {summary.skipped} skipped
          </span>
        </div>
      </div>

      {/* Question-by-question review */}
      <div className="glass-card overflow-hidden">
        <div className="px-4 py-3" style={{ borderBottom: "1px solid rgba(26,17,69,0.06)" }}>
          <h3
            className="text-sm font-semibold"
            style={{ color: "var(--navy)" }}
          >
            Question Review
          </h3>
        </div>
        <div>
          {summary.results.map((r, i) => (
            <div
              key={r.question.id}
              className="px-4 py-2.5 flex items-center gap-3 text-sm"
              style={{
                borderBottom:
                  i < summary.results.length - 1
                    ? "1px solid rgba(26,17,69,0.04)"
                    : "none",
              }}
            >
              <span
                className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                style={{
                  backgroundColor: r.isCorrect
                    ? "rgba(19,136,8,0.08)"
                    : r.userAnswer === null
                      ? "rgba(26,17,69,0.06)"
                      : "rgba(220,38,38,0.1)",
                  color: r.isCorrect
                    ? "var(--green)"
                    : r.userAnswer === null
                      ? "rgba(26,17,69,0.4)"
                      : "#DC2626",
                }}
              >
                {r.isCorrect ? "✓" : r.userAnswer === null ? "–" : "✗"}
              </span>
              <span
                className="flex-1 truncate"
                style={{ color: "rgba(26,17,69,0.7)" }}
              >
                Q{r.question.question_number}
              </span>
              <span
                className="text-xs"
                style={{ color: "rgba(26,17,69,0.4)" }}
              >
                {r.userAnswer
                  ? r.userAnswer.toUpperCase()
                  : "—"}
                {" → "}
                {r.question.correct_answer.toUpperCase()}
              </span>
              <span
                className="text-xs font-semibold tabular-nums w-14 text-right"
                style={{
                  color: r.isCorrect
                    ? "var(--green)"
                    : r.userAnswer === null
                      ? "rgba(26,17,69,0.3)"
                      : "#DC2626",
                }}
              >
                {r.marksEarned > 0 ? "+" : ""}
                {r.marksEarned.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* AI Comparison */}
      <div className="glass-card overflow-hidden">
        <div className="px-4 py-3" style={{ borderBottom: "1px solid rgba(26,17,69,0.06)" }}>
          <h3
            className="text-sm font-semibold"
            style={{ color: "var(--navy)" }}
          >
            How you compare — GS Paper I, 2025
          </h3>
        </div>
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr
              style={{
                borderBottom: "2px solid rgba(26,17,69,0.1)",
              }}
            >
              <th
                className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider"
                style={{ color: "rgba(26,17,69,0.4)" }}
              >
                #
              </th>
              <th
                className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider"
                style={{ color: "rgba(26,17,69,0.4)" }}
              >
                Model
              </th>
              <th
                className="px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wider"
                style={{ color: "rgba(26,17,69,0.4)" }}
              >
                Score
              </th>
            </tr>
          </thead>
          <tbody>
            {allEntries.map((entry, idx) => (
              <tr
                key={entry.name}
                className={`leaderboard-row ${entry.isUser ? "top-rank" : ""}`}
                style={{
                  borderBottom: "1px solid rgba(26,17,69,0.06)",
                  ...(entry.isUser
                    ? {
                        background:
                          "linear-gradient(90deg, rgba(255,153,51,0.1) 0%, rgba(255,153,51,0.03) 100%)",
                      }
                    : {}),
                }}
              >
                <td className="px-4 py-2.5">
                  <span
                    className={`rank-badge ${idx === 0 ? "gold" : idx === 1 ? "silver" : idx === 2 ? "bronze" : "default"}`}
                  >
                    {idx + 1}
                  </span>
                </td>
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-2.5">
                    <div
                      className="w-1.5 h-6 rounded-full flex-shrink-0"
                      style={{ backgroundColor: entry.color }}
                    />
                    <span
                      className="font-semibold"
                      style={{
                        color: entry.isUser
                          ? "var(--saffron)"
                          : "var(--navy)",
                      }}
                    >
                      {entry.name}
                      {entry.isUser && (
                        <span
                          className="ml-2 text-[10px] font-normal px-1.5 py-0.5 rounded"
                          style={{
                            backgroundColor: "rgba(255,153,51,0.12)",
                            color: "var(--saffron)",
                          }}
                        >
                          extrapolated
                        </span>
                      )}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-2.5 text-right">
                  <span
                    className="font-bold"
                    style={{
                      color: entry.isUser
                        ? "var(--saffron)"
                        : "var(--navy)",
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {entry.marks.toFixed(1)}
                    <span
                      style={{
                        color: entry.isUser
                          ? "rgba(255,153,51,0.4)"
                          : "rgba(26,17,69,0.3)",
                      }}
                    >
                      /{entry.maxMarks}
                    </span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-4 py-2.5">
          <p
            className="text-[10px]"
            style={{ color: "rgba(26,17,69,0.3)" }}
          >
            Your score is extrapolated from {summary.results.length} questions to
            a full {summary.maxMarks}-mark paper. AI models answered all 100
            questions. CSAT Paper II assumed qualifying (66+/200).
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={onRestart}
          className="pill-btn active !px-6"
          style={{
            background: "var(--saffron)",
            borderColor: "var(--saffron)",
          }}
        >
          Try Again
        </button>
        <a href="/" className="pill-btn inactive !px-6">
          Back to Leaderboard
        </a>
      </div>
    </div>
  );
}
