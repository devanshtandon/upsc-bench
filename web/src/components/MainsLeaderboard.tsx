"use client";

import React from "react";
import { MODEL_DISPLAY_NAMES, MODEL_COLORS, MAINS_PAPER_LABELS } from "@/lib/constants";
import { getMainsModelScore } from "@/lib/data";
import type { ModelEntry, MainsPaper } from "@/types";

interface MainsLeaderboardProps {
  models: ModelEntry[];
  year: number;
  paper: MainsPaper;
}

export default function MainsLeaderboard({ models, year, paper }: MainsLeaderboardProps) {
  const showPaperBreakdown = paper === "mains_total";
  const thClass = "px-3 py-3 text-[11px] font-semibold uppercase tracking-wider";
  const thColor = { color: "rgba(26,17,69,0.4)" };
  const paperKeys = ["essay", "gs1", "gs2", "gs3", "gs4"];

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse" style={{ tableLayout: "fixed" }}>
        <colgroup>
          <col style={{ width: "44px" }} />
          <col />
          <col style={{ width: showPaperBreakdown ? "18%" : "28%" }} />
          {showPaperBreakdown && <col style={{ width: "32%" }} />}
          <col style={{ width: "100px" }} />
        </colgroup>
        <thead>
          <tr style={{ borderBottom: "2px solid rgba(26, 17, 69, 0.1)" }}>
            <th className={`text-left ${thClass}`} style={thColor}>#</th>
            <th className={`text-left ${thClass}`} style={thColor}>Model</th>
            <th className={`text-left ${thClass}`} style={thColor}>Score</th>
            {showPaperBreakdown && (
              <th className={`text-center ${thClass} hidden sm:table-cell`} style={thColor}>Paper Breakdown</th>
            )}
            <th className={`text-center ${thClass} hidden sm:table-cell`} style={thColor}>Est. AIR</th>
          </tr>
        </thead>
        <tbody className="stagger-children">
          {models.map((model) => {
            const scoreData = getMainsModelScore(model, year, paper);
            const mainsData = model.mains?.[year];
            const displayName = MODEL_DISPLAY_NAMES[model.model] ?? model.model;
            const color = MODEL_COLORS[model.model] ?? "#1a1145";
            const barWidth = scoreData.maxMarks > 0 ? (scoreData.score / scoreData.maxMarks) * 100 : 0;
            const isTop = model.rank === 1;
            const isHuman = model.is_human === true;
            const estimatedRank = mainsData?.estimated_rank;

            return (
              <tr
                key={model.model}
                className={`leaderboard-row animate-fade-in-up ${isTop && !isHuman ? "top-rank" : ""}`}
                style={{
                  borderBottom: "1px solid rgba(26, 17, 69, 0.06)",
                  ...(isHuman ? { backgroundColor: "rgba(139, 92, 246, 0.04)" } : {}),
                }}
              >
                {/* Rank */}
                <td className="px-3 py-2.5">
                  {isHuman ? (
                    <span className="inline-flex items-center justify-center w-7 h-7 rounded-full text-sm" style={{ backgroundColor: "rgba(139,92,246,0.1)", color: "#8B5CF6" }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                    </span>
                  ) : (
                    <span className={`rank-badge ${model.rank === 1 ? "gold" : model.rank === 2 ? "silver" : model.rank === 3 ? "bronze" : "default"}`}>
                      {model.rank}
                    </span>
                  )}
                </td>

                {/* Model name */}
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2.5">
                    <div
                      className="w-1.5 h-6 rounded-full flex-shrink-0"
                      style={{ backgroundColor: color }}
                    />
                    <div>
                      <span className="font-semibold text-[15px] truncate block" style={{ color: isHuman ? "#8B5CF6" : "var(--navy)" }}>
                        {displayName}
                      </span>
                      {isHuman && (
                        <span className="text-[10px] font-medium" style={{ color: "rgba(139,92,246,0.6)" }}>
                          CSE 2024 AIR 1 · Written 843/1750
                        </span>
                      )}
                    </div>
                  </div>
                </td>

                {/* Score */}
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 min-w-0 max-w-[52px]">
                      <div className="w-full h-1.5 rounded-full" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>
                        <div
                          className="score-fill"
                          style={{
                            width: `${barWidth}%`,
                            height: "6px",
                            background: `linear-gradient(90deg, ${color}, ${color}dd)`,
                          }}
                        />
                      </div>
                    </div>
                    <div>
                      <span className="font-bold text-sm whitespace-nowrap block" style={{ color: isHuman ? "#8B5CF6" : "var(--navy)", fontVariantNumeric: "tabular-nums" }}>
                        {scoreData.score.toFixed(1)}
                        <span style={{ color: isHuman ? "rgba(139,92,246,0.3)" : "rgba(26,17,69,0.3)" }}>/{scoreData.maxMarks}</span>
                      </span>
                      <span className="text-[11px] font-medium whitespace-nowrap" style={{ color: scoreData.passed ? "#16a34a" : "#dc2626" }}>
                        {scoreData.scorePct.toFixed(0)}%{" "}
                        {scoreData.passed ? "✓ Pass" : "✗ Fail"}
                      </span>
                    </div>
                  </div>
                </td>

                {/* Paper Breakdown */}
                {showPaperBreakdown && (
                  <td className="px-3 py-2.5 hidden sm:table-cell">
                    <div className="flex gap-1.5">
                      {paperKeys.map((pk) => {
                        const pd = mainsData?.papers[pk];
                        if (!pd) return null;
                        const pct = pd.max_marks > 0 ? (pd.score / pd.max_marks) * 100 : 0;
                        return (
                          <div
                            key={pk}
                            className="flex flex-col items-center flex-1 min-w-0"
                            title={`${MAINS_PAPER_LABELS[pk === "essay" ? "essay" : `mains_${pk}`] ?? pk}: ${pd.score.toFixed(0)}/${pd.max_marks}`}
                          >
                            <div className="w-full h-1 rounded-full mb-0.5" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>
                              <div
                                className="h-full rounded-full"
                                style={{
                                  width: `${pct}%`,
                                  backgroundColor: color,
                                  opacity: 0.7,
                                }}
                              />
                            </div>
                            <span className="text-[9px] font-medium" style={{ color: isHuman ? "rgba(139,92,246,0.4)" : "rgba(26,17,69,0.4)", fontVariantNumeric: "tabular-nums" }}>
                              {pd.score.toFixed(0)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                    <div className="flex gap-1.5 mt-0.5">
                      {paperKeys.map((pk) => (
                        <span key={pk} className="flex-1 text-center text-[8px]" style={{ color: "rgba(26,17,69,0.25)" }}>
                          {pk === "essay" ? "Ess" : pk.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </td>
                )}

                {/* Est. AIR */}
                <td className="px-3 py-2.5 text-center hidden sm:table-cell">
                  {estimatedRank ? (
                    <div
                      className="inline-flex flex-col items-center rounded-lg px-2.5 py-1"
                      style={{
                        backgroundColor: isHuman ? "rgba(139,92,246,0.08)" : "rgba(255, 153, 51, 0.08)",
                        border: isHuman ? "1px solid rgba(139,92,246,0.15)" : "1px solid rgba(255, 153, 51, 0.15)",
                      }}
                    >
                      <span className="font-bold text-sm" style={{ color: isHuman ? "#8B5CF6" : "var(--saffron)" }}>
                        ~{estimatedRank.rank.toLocaleString()}
                      </span>
                      <span className="text-[9px] font-medium" style={{ color: isHuman ? "rgba(139,92,246,0.5)" : "rgba(255,153,51,0.6)" }}>
                        of {(estimatedRank.total_candidates / 1000).toFixed(1)}K
                      </span>
                    </div>
                  ) : (
                    <span className="text-sm" style={{ color: "rgba(26,17,69,0.3)" }}>—</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {/* Footnotes */}
      <div className="px-4 py-3 space-y-1">
        {showPaperBreakdown && (
          <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.35)" }}>
            Paper breakdown: Essay (250) · GS-I (250) · GS-II (250) · GS-III (250) · GS-IV (250). Essay scored as best 1 from each section (A &amp; B).
          </p>
        )}
        <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.3)" }}>
          Est. AIR = Estimated All-India Rank among ~14.5K Mains candidates. Scores graded by LLM-as-judge (rubric-based).
        </p>
        <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.4)" }}>
          <span style={{ color: "var(--saffron)" }}>To pass (2025):</span>{" "}
          Mains written score must exceed proportional cutoff of ~571/1250 (scaled from 800/1750 full exam cutoff).
        </p>
        <p className="text-[10px]" style={{ color: "rgba(139,92,246,0.5)" }}>
          <span style={{ color: "#8B5CF6" }}>Human reference:</span>{" "}
          Shakti Dubey (CSE 2024 AIR 1, written 843/1750). Essay+GS scores estimated — UPSC does not publish paper-wise marks. Optional paper (~300/500) excluded from our benchmark.
        </p>
      </div>
    </div>
  );
}
