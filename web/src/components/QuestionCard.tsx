"use client";

import type { QuizQuestion } from "@/lib/quiz";

interface QuestionCardProps {
  question: QuizQuestion;
  qIndex: number;
  total: number;
  showFeedback: boolean;
  lastAnswer: string | null;
  onAnswer: (answer: string) => void;
  onSkip: () => void;
  onNext: () => void;
}

const OPTION_LABELS: Record<string, string> = {
  a: "A",
  b: "B",
  c: "C",
  d: "D",
};

export default function QuestionCard({
  question,
  qIndex,
  total,
  showFeedback,
  lastAnswer,
  onAnswer,
  onSkip,
  onNext,
}: QuestionCardProps) {
  const isLast = qIndex === total - 1;

  return (
    <div className="glass-card p-6 animate-fade-in-up">
      {/* Question header */}
      <div className="flex items-center justify-between mb-4">
        <span
          className="text-xs font-semibold uppercase tracking-wider"
          style={{ color: "rgba(26,17,69,0.4)" }}
        >
          Question {qIndex + 1} of {total}
        </span>
        <span
          className="text-xs px-2 py-0.5 rounded-full"
          style={{
            backgroundColor: "rgba(255,153,51,0.08)",
            color: "var(--saffron)",
            fontWeight: 600,
          }}
        >
          Q{question.question_number}
        </span>
      </div>

      {/* Question text */}
      <div className="mb-6">
        {question.question_text
          .split("\n")
          .filter((line: string) => line.trim() !== "")
          .map((line: string, i: number) => (
            <p
              key={i}
              className="text-sm leading-relaxed mb-2 last:mb-0"
              style={{ color: "var(--navy)" }}
            >
              {line}
            </p>
          ))}
      </div>

      {/* Image placeholder (for future use) */}
      {question.has_image && question.image_paths.length > 0 && (
        <div
          className="mb-4 p-4 rounded-lg text-center"
          style={{
            backgroundColor: "rgba(26,17,69,0.04)",
            border: "1px dashed rgba(26,17,69,0.15)",
          }}
        >
          <p
            className="text-xs"
            style={{ color: "rgba(26,17,69,0.4)" }}
          >
            [Image: {question.image_description || "Visual content — refer to original paper"}]
          </p>
        </div>
      )}

      {/* Options */}
      <div className="space-y-2.5 mb-5">
        {(["a", "b", "c", "d"] as const).map((key) => {
          const isCorrect = key === question.correct_answer;
          const isUserAnswer = key === lastAnswer;

          let style: React.CSSProperties;
          let extraClass = "";

          if (showFeedback) {
            if (isCorrect) {
              style = {
                backgroundColor: "rgba(19,136,8,0.08)",
                borderColor: "var(--green)",
                color: "var(--green)",
              };
            } else if (isUserAnswer) {
              style = {
                backgroundColor: "rgba(220,38,38,0.08)",
                borderColor: "#DC2626",
                color: "#DC2626",
              };
            } else {
              style = { opacity: 0.35 };
            }
          } else {
            style = {};
            extraClass = "inactive";
          }

          return (
            <button
              key={key}
              onClick={() => !showFeedback && onAnswer(key)}
              disabled={showFeedback}
              className={`pill-btn ${extraClass} w-full text-left flex items-start gap-3 !rounded-xl !py-3 !px-4`}
              style={{
                ...style,
                cursor: showFeedback ? "default" : "pointer",
              }}
            >
              <span
                className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                style={{
                  backgroundColor: showFeedback
                    ? "transparent"
                    : "rgba(26,17,69,0.06)",
                  color: showFeedback ? "inherit" : "var(--navy)",
                }}
              >
                {OPTION_LABELS[key]}
              </span>
              <span className="text-sm leading-relaxed">
                {question.options[key]}
              </span>
              {showFeedback && isCorrect && (
                <span className="ml-auto flex-shrink-0" style={{ color: "var(--green)" }}>
                  ✓
                </span>
              )}
              {showFeedback && isUserAnswer && !isCorrect && (
                <span className="ml-auto flex-shrink-0" style={{ color: "#DC2626" }}>
                  ✗
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Feedback banner */}
      {showFeedback && (
        <div
          className="mb-4 p-3 rounded-xl text-sm font-medium animate-fade-in-up"
          style={{
            backgroundColor:
              lastAnswer === null
                ? "rgba(26,17,69,0.04)"
                : lastAnswer === question.correct_answer
                  ? "rgba(19,136,8,0.08)"
                  : "rgba(220,38,38,0.06)",
            color:
              lastAnswer === null
                ? "rgba(26,17,69,0.5)"
                : lastAnswer === question.correct_answer
                  ? "var(--green)"
                  : "#DC2626",
          }}
        >
          {lastAnswer === null
            ? "Skipped — no marks awarded."
            : lastAnswer === question.correct_answer
              ? `Correct! +${question.marks_correct.toFixed(2)} marks`
              : `Wrong. −${Math.abs(question.marks_wrong).toFixed(2)} marks. The correct answer is ${OPTION_LABELS[question.correct_answer]}.`}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        {!showFeedback ? (
          <>
            <button
              onClick={onSkip}
              className="text-sm transition-colors"
              style={{ color: "rgba(26,17,69,0.4)" }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.color = "var(--saffron)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.color = "rgba(26,17,69,0.4)")
              }
            >
              Skip (0 marks)
            </button>
            <span
              className="text-[10px]"
              style={{ color: "rgba(26,17,69,0.3)" }}
            >
              +{question.marks_correct.toFixed(1)} correct · −{Math.abs(question.marks_wrong).toFixed(2)} wrong
            </span>
          </>
        ) : (
          <>
            <div />
            <button
              onClick={onNext}
              className="pill-btn active !px-6"
              style={{
                background: "var(--saffron)",
                borderColor: "var(--saffron)",
              }}
            >
              {isLast ? "See Results" : "Next Question →"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
