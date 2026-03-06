"use client";

import { useState, type ReactNode } from "react";
import type { ArenaAnswer, ArenaPaper, VoteChoice } from "@/types/arena";

const ESSAY_RUBRIC_LABELS: Record<string, string> = {
  content_breadth: "Content & Breadth",
  structure_flow: "Structure & Flow",
  depth_examples: "Depth & Examples",
  analytical_depth: "Analytical Depth",
  presentation: "Presentation",
};

const GS_RUBRIC_LABELS: Record<string, string> = {
  content_accuracy: "Content & Accuracy",
  structure_flow: "Structure & Flow",
  depth_examples: "Depth & Examples",
  analytical_depth: "Analytical Depth",
  presentation: "Presentation",
};

function getRubricLabels(paper: ArenaPaper): Record<string, string> {
  return paper === "mains_essay" ? ESSAY_RUBRIC_LABELS : GS_RUBRIC_LABELS;
}

/** Max value for rubric bar display, scaled by question marks. */
function getRubricBarMax(maxMarks: number): number {
  if (maxMarks >= 125) return 40; // Essays: rubric values up to ~35
  return maxMarks * 0.32;        // GS: proportional (3.2 for 10-mark, 4.8 for 15-mark)
}

interface ArenaAnswerPanelProps {
  answerA: ArenaAnswer;
  answerB: ArenaAnswer;
  paper: ArenaPaper;
  maxMarks: number;
  stage: "comparing" | "voted";
  vote: VoteChoice | null;
  revealed: boolean;
  modelAName: string | null;
  modelBName: string | null;
  modelAColor: string | null;
  modelBColor: string | null;
  onReveal: () => void;
}

/** Convert inline markdown (bold, italic) to React elements. */
function renderInlineMarkdown(text: string): ReactNode[] {
  const parts: ReactNode[] = [];
  // Match **bold**, *italic*, and plain text segments
  const regex = /\*\*(.+?)\*\*|\*(.+?)\*/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    if (match[1]) {
      parts.push(<strong key={match.index}>{match[1]}</strong>);
    } else if (match[2]) {
      parts.push(<em key={match.index}>{match[2]}</em>);
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }
  return parts;
}

function renderAnswerText(text: string) {
  const paragraphs = text.split(/\n\n+/).filter((p) => p.trim());
  return paragraphs.map((p, i) => {
    const trimmed = p.trim();
    // Detect markdown-style headers
    if (trimmed.startsWith("## ")) {
      return (
        <h3
          key={i}
          className="font-semibold mt-4 mb-2"
          style={{ color: "var(--navy)", fontSize: "15px" }}
        >
          {renderInlineMarkdown(trimmed.replace(/^##\s*/, ""))}
        </h3>
      );
    }
    if (trimmed.startsWith("# ")) {
      return (
        <h2
          key={i}
          className="font-bold mt-4 mb-2"
          style={{ color: "var(--navy)", fontSize: "16px" }}
        >
          {renderInlineMarkdown(trimmed.replace(/^#\s*/, ""))}
        </h2>
      );
    }
    return (
      <p key={i} className="mb-3">
        {renderInlineMarkdown(trimmed)}
      </p>
    );
  });
}

function AnswerCard({
  label,
  answer,
  paper,
  maxMarks,
  won,
  color,
  stage,
  showScores,
}: {
  label: string;
  answer: ArenaAnswer;
  paper: ArenaPaper;
  maxMarks: number;
  won: boolean;
  color: string | null;
  stage: "comparing" | "voted";
  showScores: boolean;
}) {
  const borderColor = won
    ? "var(--green)"
    : stage === "voted"
      ? "rgba(26,17,69,0.08)"
      : "var(--card-border)";

  const rubricLabels = getRubricLabels(paper);
  const rubricBarMax = getRubricBarMax(maxMarks);
  const contentClass = paper === "mains_essay" ? "arena-essay" : "arena-answer";

  return (
    <div
      className="glass-card overflow-hidden"
      style={{
        borderColor,
        borderWidth: won ? "2px" : "1px",
      }}
    >
      {/* Panel header */}
      <div
        className="px-4 py-3 flex items-center justify-between"
        style={{ borderBottom: "1px solid rgba(26,17,69,0.06)" }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-2 h-5 rounded-full"
            style={{
              backgroundColor:
                stage === "voted" && color ? color : "rgba(26,17,69,0.2)",
            }}
          />
          <span
            className="font-semibold text-sm"
            style={{ color: "var(--navy)" }}
          >
            {label}
          </span>
          {won && (
            <span
              className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
              style={{
                backgroundColor: "rgba(19,136,8,0.1)",
                color: "var(--green)",
              }}
            >
              Winner
            </span>
          )}
        </div>
        <span
          className="text-xs tabular-nums"
          style={{ color: "rgba(26,17,69,0.35)" }}
        >
          {answer.word_count} words
        </span>
      </div>

      {/* Answer text */}
      <div className={`${contentClass} px-4 py-3`}>
        {renderAnswerText(answer.text)}
      </div>

      {/* Rubric scores (only after voting, only if available) */}
      {showScores && answer.rubric_scores && (
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid rgba(26,17,69,0.06)" }}
        >
          <div className="flex items-center justify-between mb-2">
            <span
              className="text-xs font-semibold uppercase tracking-wider"
              style={{ color: "rgba(26,17,69,0.4)" }}
            >
              Rubric Scores
            </span>
            <span
              className="text-sm font-bold tabular-nums"
              style={{ color: "var(--navy)" }}
            >
              {answer.total_score?.toFixed(1)}/{maxMarks}
            </span>
          </div>
          <div className="space-y-1.5">
            {Object.entries(answer.rubric_scores).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2">
                <span
                  className="text-[11px] w-28 flex-shrink-0 truncate"
                  style={{ color: "rgba(26,17,69,0.5)" }}
                >
                  {rubricLabels[key] ?? key}
                </span>
                <div
                  className="flex-1 h-1.5 rounded-full overflow-hidden"
                  style={{ backgroundColor: "rgba(26,17,69,0.06)" }}
                >
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${Math.min(100, (value / rubricBarMax) * 100)}%`,
                      backgroundColor: color ?? "var(--saffron)",
                    }}
                  />
                </div>
                <span
                  className="text-[11px] tabular-nums w-8 text-right"
                  style={{ color: "rgba(26,17,69,0.5)" }}
                >
                  {value.toFixed(1)}
                </span>
              </div>
            ))}
          </div>
          {answer.feedback && (
            <p
              className="mt-2 text-xs italic"
              style={{ color: "rgba(26,17,69,0.4)" }}
            >
              {answer.feedback}
            </p>
          )}
        </div>
      )}

      {/* No scores available notice */}
      {showScores && !answer.rubric_scores && (
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid rgba(26,17,69,0.06)" }}
        >
          <p
            className="text-xs italic"
            style={{ color: "rgba(26,17,69,0.3)" }}
          >
            Rubric scores not available for this model.
          </p>
        </div>
      )}
    </div>
  );
}

export default function ArenaAnswerPanel({
  answerA,
  answerB,
  paper,
  maxMarks,
  stage,
  vote,
  revealed,
  modelAName,
  modelBName,
  modelAColor,
  modelBColor,
  onReveal,
}: ArenaAnswerPanelProps) {
  const [activeTab, setActiveTab] = useState<"A" | "B">("A");

  const showNames = revealed || stage === "voted";
  const labelA = showNames && modelAName ? modelAName : "Model A";
  const labelB = showNames && modelBName ? modelBName : "Model B";

  const wonA = stage === "voted" && vote === "A";
  const wonB = stage === "voted" && vote === "B";

  return (
    <div>
      {/* MOBILE: tab-switched layout */}
      <div className="block sm:hidden">
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setActiveTab("A")}
            className={`pill-btn flex-1 ${activeTab === "A" ? "active" : "inactive"}`}
            style={
              activeTab === "A" && showNames && modelAColor
                ? { backgroundColor: modelAColor, borderColor: modelAColor }
                : {}
            }
          >
            {labelA} {wonA ? " ✓" : ""}
          </button>
          <button
            onClick={() => setActiveTab("B")}
            className={`pill-btn flex-1 ${activeTab === "B" ? "active" : "inactive"}`}
            style={
              activeTab === "B" && showNames && modelBColor
                ? { backgroundColor: modelBColor, borderColor: modelBColor }
                : {}
            }
          >
            {labelB} {wonB ? " ✓" : ""}
          </button>
        </div>
        <AnswerCard
          label={activeTab === "A" ? labelA : labelB}
          answer={activeTab === "A" ? answerA : answerB}
          paper={paper}
          maxMarks={maxMarks}
          won={activeTab === "A" ? wonA : wonB}
          color={activeTab === "A" ? modelAColor : modelBColor}
          stage={stage}
          showScores={stage === "voted"}
        />
      </div>

      {/* DESKTOP: true side-by-side */}
      <div className="hidden sm:grid grid-cols-2 gap-4">
        <AnswerCard
          label={labelA}
          answer={answerA}
          paper={paper}
          maxMarks={maxMarks}
          won={wonA}
          color={showNames ? modelAColor : null}
          stage={stage}
          showScores={stage === "voted"}
        />
        <AnswerCard
          label={labelB}
          answer={answerB}
          paper={paper}
          maxMarks={maxMarks}
          won={wonB}
          color={showNames ? modelBColor : null}
          stage={stage}
          showScores={stage === "voted"}
        />
      </div>

      {/* Reveal button */}
      {stage === "comparing" && !revealed && (
        <div className="mt-3 text-center">
          <button
            onClick={onReveal}
            className="text-xs transition-colors hover:text-[var(--saffron)]"
            style={{ color: "rgba(26,17,69,0.4)" }}
          >
            Reveal model names
          </button>
        </div>
      )}
    </div>
  );
}
