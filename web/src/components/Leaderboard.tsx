"use client";

import React from "react";
import { MODEL_DISPLAY_NAMES, MODEL_COLORS } from "@/lib/constants";
import { getModelScore } from "@/lib/data";
import type { ModelEntry, Paper } from "@/types";

interface LeaderboardProps {
  models: ModelEntry[];
  year: number;
  paper: Paper;
  cutoffs?: Record<number, Record<string, number>>;
}

function getRankClass(rank: number): string {
  if (rank === 1) return "gold";
  if (rank === 2) return "silver";
  if (rank === 3) return "bronze";
  return "default";
}

function getModelMeta(model: ModelEntry, year: number, paper: Paper) {
  const score = getModelScore(model, year, paper);
  const displayName = MODEL_DISPLAY_NAMES[model.model] ?? model.model;
  const color = MODEL_COLORS[model.model] ?? "#1a1145";
  const barWidth = score.maxMarks > 0 ? (score.marks / score.maxMarks) * 100 : 0;
  const isTop = model.rank === 1;
  const isHuman = model.is_human === true;

  const showRank = paper === "gs1" || paper === "overall";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let estimatedRank: { rank: number | null; label: string; percentile: number | null; total_appeared?: number } | null = null;
  if (showRank) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const gs1Data = model.yearly[year]?.gs1 as any;
    if (gs1Data?.estimated_rank) {
      estimatedRank = gs1Data.estimated_rank;
    }
  }

  let csatInfo: { passed: boolean; marks: number } | null = null;
  if (paper === "overall") {
    const csatData = model.yearly[year]?.csat;
    if (csatData) {
      csatInfo = { passed: csatData.passed, marks: csatData.marks };
    }
  }

  return { score, displayName, color, barWidth, isTop, isHuman, estimatedRank, csatInfo };
}

export default function Leaderboard({ models, year, paper, cutoffs }: LeaderboardProps) {
  const showRank = paper === "gs1" || paper === "overall";

  // Determine cutoff for current view
  let cutoffMarks: number | null = null;
  if (cutoffs) {
    const yearCutoffs = cutoffs[year];
    if (yearCutoffs) {
      if (paper === "gs1" || paper === "overall") {
        cutoffMarks = yearCutoffs.gs1 ?? null;
      } else if (paper === "csat") {
        cutoffMarks = yearCutoffs.csat_qualifying ?? null;
      }
    }
  }

  // Find where to insert cutoff row
  let cutoffInsertIndex = -1;
  if (cutoffMarks !== null) {
    for (let i = 0; i < models.length; i++) {
      const score = getModelScore(models[i], year, paper);
      if (score.marks < cutoffMarks) {
        cutoffInsertIndex = i;
        break;
      }
    }
    if (cutoffInsertIndex === -1) cutoffInsertIndex = models.length;
  }

  // Resolve cutoff values for the footnote
  let gs1Cutoff: number | null = null;
  let csatCutoff: number | null = null;
  if (cutoffs) {
    const yearCutoffs = cutoffs[year];
    if (yearCutoffs) {
      gs1Cutoff = yearCutoffs.gs1 ?? null;
      csatCutoff = yearCutoffs.csat_qualifying ?? null;
    }
  }

  return (
    <div>
      {/* ===== MOBILE: Card layout ===== */}
      <div className="block sm:hidden">
        <div className="divide-y" style={{ borderColor: "rgba(26,17,69,0.06)" }}>
          {models.map((model, idx) => {
            const { score, displayName, color, barWidth, isTop, isHuman, estimatedRank, csatInfo } = getModelMeta(model, year, paper);
            return (
              <React.Fragment key={model.model}>
                {cutoffMarks !== null && cutoffInsertIndex === idx && (
                  <MobileCutoffRow cutoffMarks={cutoffMarks} maxMarks={200} paper={paper} />
                )}
                <div
                  className={`px-4 py-3 animate-fade-in-up ${isTop && !isHuman ? "top-rank" : ""}`}
                  style={isHuman ? { backgroundColor: "rgba(139, 92, 246, 0.04)" } : undefined}
                >
                  {/* Row 1: Rank + Name + Score */}
                  <div className="flex items-center gap-3">
                    {isHuman ? (
                      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full flex-shrink-0" style={{ backgroundColor: "rgba(139,92,246,0.1)", color: "#8B5CF6" }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                          <circle cx="12" cy="7" r="4" />
                        </svg>
                      </span>
                    ) : (
                      <span className={`rank-badge flex-shrink-0 ${getRankClass(model.rank)}`}>
                        {model.rank}
                      </span>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline justify-between gap-2">
                        <span className="font-semibold text-[14px] truncate" style={{ color: isHuman ? "#8B5CF6" : "var(--navy)" }}>
                          {displayName}
                        </span>
                        <span className="font-bold text-[15px] whitespace-nowrap flex-shrink-0" style={{ color: isHuman ? "#8B5CF6" : "var(--navy)", fontVariantNumeric: "tabular-nums" }}>
                          {score.marks.toFixed(1)}
                          <span className="text-[12px]" style={{ color: isHuman ? "rgba(139,92,246,0.3)" : "rgba(26,17,69,0.3)" }}>/{score.maxMarks}</span>
                        </span>
                      </div>
                      {isHuman && (
                        <span className="text-[10px] font-medium block" style={{ color: "rgba(139,92,246,0.6)" }}>
                          CSE 2024 AIR 1 (est.)
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Row 2: Score bar + breakdown + extras */}
                  <div className="mt-2 ml-10">
                    {/* Full-width score bar */}
                    <div className="w-full h-1.5 rounded-full mb-2" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>
                      <div
                        className="score-fill"
                        style={{
                          width: `${barWidth}%`,
                          height: "6px",
                          background: `linear-gradient(90deg, ${color}, ${color}dd)`,
                        }}
                      />
                    </div>

                    {/* Breakdown + CSAT + AIR in a flex row */}
                    <div className="flex items-center gap-3 flex-wrap">
                      <div className="flex items-center gap-2 text-[12px] font-medium" style={{ fontVariantNumeric: "tabular-nums" }}>
                        <span style={{ color: "#16a34a" }}>{score.correct}✓</span>
                        <span style={{ color: "#dc2626" }}>{score.wrong}✗</span>
                        <span style={{ color: "rgba(26,17,69,0.35)" }}>{score.unanswered}–</span>
                      </div>
                      {csatInfo && (
                        <span
                          className="text-[11px] font-medium"
                          style={{ color: csatInfo.passed ? "#16a34a" : "#dc2626" }}
                        >
                          CSAT {csatInfo.passed ? "✓" : "✗"} {csatInfo.marks.toFixed(1)}
                        </span>
                      )}
                      {showRank && estimatedRank?.rank && (
                        <span
                          className="text-[11px] font-semibold ml-auto px-2 py-0.5 rounded-md"
                          style={{
                            backgroundColor: isHuman ? "rgba(139,92,246,0.08)" : "rgba(255,153,51,0.08)",
                            color: isHuman ? "#8B5CF6" : "var(--saffron)",
                          }}
                        >
                          AIR ~{estimatedRank.rank.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </React.Fragment>
            );
          })}
          {cutoffMarks !== null && cutoffInsertIndex === models.length && (
            <MobileCutoffRow cutoffMarks={cutoffMarks} maxMarks={200} paper={paper} />
          )}
        </div>
      </div>

      {/* ===== DESKTOP: Table layout ===== */}
      <div className="hidden sm:block overflow-x-auto">
        <DesktopTable
          models={models}
          year={year}
          paper={paper}
          showRank={showRank}
          cutoffMarks={cutoffMarks}
          cutoffInsertIndex={cutoffInsertIndex}
        />
      </div>

      {/* Footnotes */}
      <div className="px-4 py-3 space-y-1">
        <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.35)" }}>
          <span style={{ color: "#16a34a" }}>✓</span> Correct
          {" · "}
          <span style={{ color: "#dc2626" }}>✗</span> Wrong
          {" · "}
          <span>–</span> Not attempted (scored 0, no negative marking)
        </p>
        {showRank && (
          <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.3)" }}>
            Est. AIR = Estimated All-India Rank among ~6 lakh Prelims candidates. Based on coaching institute data.
          </p>
        )}
        {gs1Cutoff !== null && (
          <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.4)" }}>
            <span style={{ color: "var(--saffron)" }}>To pass ({year}):</span>{" "}
            GS Paper I score must exceed {gs1Cutoff}/200 (General category cutoff).
            {csatCutoff !== null && (
              <> CSAT Paper II is qualifying only — minimum {csatCutoff}/200 ({((csatCutoff / 200) * 100).toFixed(0)}%) required.</>
            )}
          </p>
        )}
        <p className="text-[10px]" style={{ color: "rgba(139,92,246,0.5)" }}>
          <span style={{ color: "#8B5CF6" }}>Human reference:</span>{" "}
          Shakti Dubey (CSE 2024 AIR 1). Prelims scores are estimated — UPSC does not publish individual Prelims marks.
        </p>
      </div>
    </div>
  );
}

/* ===== Desktop table (unchanged layout, extracted for clarity) ===== */
function DesktopTable({
  models, year, paper, showRank, cutoffMarks, cutoffInsertIndex,
}: {
  models: ModelEntry[];
  year: number;
  paper: Paper;
  showRank: boolean;
  cutoffMarks: number | null;
  cutoffInsertIndex: number;
}) {
  const colCount = showRank ? 5 : 4;
  const thClass = "px-3 py-3 text-[11px] font-semibold uppercase tracking-wider";
  const thColor = { color: "rgba(26,17,69,0.4)" };

  return (
    <table className="w-full border-collapse" style={{ tableLayout: "fixed" }}>
      <colgroup>
        <col style={{ width: "44px" }} />
        <col />
        <col style={{ width: showRank ? "22%" : "30%" }} />
        <col style={{ width: showRank ? "18%" : "22%" }} />
        {showRank && <col style={{ width: "100px" }} />}
      </colgroup>
      <thead>
        <tr style={{ borderBottom: "2px solid rgba(26, 17, 69, 0.1)" }}>
          <th className={`text-left ${thClass}`} style={thColor}>#</th>
          <th className={`text-left ${thClass}`} style={thColor}>Model</th>
          <th className={`text-left ${thClass}`} style={thColor}>Score</th>
          <th className={`text-center ${thClass}`} style={thColor}>Breakdown</th>
          {showRank && (
            <th className={`text-center ${thClass}`} style={thColor}>Est. AIR</th>
          )}
        </tr>
      </thead>
      <tbody className="stagger-children">
        {models.map((model, idx) => {
          const { score, displayName, color, barWidth, isTop, isHuman, estimatedRank, csatInfo } = getModelMeta(model, year, paper);

          return (
            <React.Fragment key={model.model}>
              {cutoffMarks !== null && cutoffInsertIndex === idx && (
                <CutoffRow cutoffMarks={cutoffMarks} maxMarks={200} colCount={colCount} paper={paper} showRank={showRank} />
              )}
              <tr
                className={`leaderboard-row animate-fade-in-up ${isTop && !isHuman ? "top-rank" : ""}`}
                style={{
                  borderBottom: "1px solid rgba(26, 17, 69, 0.06)",
                  ...(isHuman ? { backgroundColor: "rgba(139, 92, 246, 0.04)" } : {}),
                }}
              >
                <td className="px-3 py-2.5">
                  {isHuman ? (
                    <span className="inline-flex items-center justify-center w-7 h-7 rounded-full text-sm" style={{ backgroundColor: "rgba(139,92,246,0.1)", color: "#8B5CF6" }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                    </span>
                  ) : (
                    <span className={`rank-badge ${getRankClass(model.rank)}`}>
                      {model.rank}
                    </span>
                  )}
                </td>
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-1.5 h-6 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
                    <div>
                      <span className="font-semibold text-[15px] truncate block" style={{ color: isHuman ? "#8B5CF6" : "var(--navy)" }}>
                        {displayName}
                      </span>
                      {isHuman && (
                        <span className="text-[10px] font-medium" style={{ color: "rgba(139,92,246,0.6)" }}>
                          CSE 2024 AIR 1 (est.)
                        </span>
                      )}
                    </div>
                  </div>
                </td>
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
                        {score.marks.toFixed(1)}
                        <span style={{ color: isHuman ? "rgba(139,92,246,0.3)" : "rgba(26,17,69,0.3)" }}>/{score.maxMarks}</span>
                      </span>
                      {csatInfo && (
                        <span className="text-[11px] font-medium whitespace-nowrap" style={{ color: csatInfo.passed ? "#16a34a" : "#dc2626" }}>
                          CSAT {csatInfo.passed ? "✓" : "✗"} {csatInfo.marks.toFixed(1)}
                        </span>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-3 py-2.5">
                  <div
                    className="inline-grid text-sm font-medium"
                    style={{
                      gridTemplateColumns: "auto auto 6px auto auto 6px auto auto",
                      columnGap: "2px",
                      fontVariantNumeric: "tabular-nums",
                      justifyItems: "end",
                    }}
                  >
                    <span className="text-right" style={{ color: "#16a34a", minWidth: "2ch" }}>{score.correct}</span>
                    <span style={{ color: "#16a34a" }}>✓</span>
                    <span />
                    <span className="text-right" style={{ color: "#dc2626", minWidth: "2ch" }}>{score.wrong}</span>
                    <span style={{ color: "#dc2626" }}>✗</span>
                    <span />
                    <span className="text-right" style={{ color: "rgba(26,17,69,0.35)", minWidth: "2ch" }}>{score.unanswered}</span>
                    <span style={{ color: "rgba(26,17,69,0.35)" }}>–</span>
                  </div>
                </td>
                {showRank && (
                  <td className="px-3 py-2.5 text-center">
                    {estimatedRank?.rank ? (
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
                          of {estimatedRank.total_appeared
                            ? `${(estimatedRank.total_appeared / 100000).toFixed(estimatedRank.total_appeared % 100000 === 0 ? 0 : 1)}L`
                            : "6L"}
                        </span>
                      </div>
                    ) : (
                      <span className="text-sm" style={{ color: "rgba(26,17,69,0.3)" }}>—</span>
                    )}
                  </td>
                )}
              </tr>
            </React.Fragment>
          );
        })}
        {cutoffMarks !== null && cutoffInsertIndex === models.length && (
          <CutoffRow cutoffMarks={cutoffMarks} maxMarks={200} colCount={colCount} paper={paper} showRank={showRank} />
        )}
      </tbody>
    </table>
  );
}

/* ===== Cutoff row — desktop table ===== */
function CutoffRow({
  cutoffMarks,
  maxMarks,
  colCount,
  paper,
  showRank,
}: {
  cutoffMarks: number;
  maxMarks: number;
  colCount: number;
  paper: Paper;
  showRank: boolean;
}) {
  const barWidth = (cutoffMarks / maxMarks) * 100;
  const displayLabel = paper === "csat" ? "CSAT Qualifying Cutoff" : "GS1 General Category Cutoff";

  return (
    <tr
      style={{
        borderTop: "2px dashed rgba(255, 153, 51, 0.5)",
        borderBottom: "2px dashed rgba(255, 153, 51, 0.5)",
        backgroundColor: "rgba(255, 153, 51, 0.04)",
      }}
    >
      <td className="px-3 py-2">
        <span
          className="inline-flex items-center justify-center w-7 h-7 rounded-full text-sm font-bold"
          style={{ backgroundColor: "rgba(255,153,51,0.1)", color: "var(--saffron)" }}
        >
          —
        </span>
      </td>
      <td className="px-3 py-2">
        <div className="flex items-center gap-2.5">
          <div
            className="w-1.5 h-6 rounded-full flex-shrink-0"
            style={{ backgroundColor: "var(--saffron)", opacity: 0.5 }}
          />
          <span className="font-semibold text-sm truncate" style={{ color: "var(--saffron)" }}>
            {displayLabel}
          </span>
        </div>
      </td>
      <td className="px-3 py-2">
        <div className="flex items-center gap-2">
          <div className="flex-1 min-w-0 max-w-[52px]">
            <div className="w-full h-1.5 rounded-full" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>
              <div
                style={{
                  width: `${barWidth}%`,
                  height: "6px",
                  borderRadius: "9999px",
                  background: "repeating-linear-gradient(90deg, var(--saffron) 0px, var(--saffron) 4px, transparent 4px, transparent 8px)",
                  opacity: 0.5,
                }}
              />
            </div>
          </div>
          <span className="font-bold text-sm whitespace-nowrap" style={{ color: "var(--saffron)" }}>
            {cutoffMarks.toFixed(1)}
            <span style={{ color: "rgba(255,153,51,0.4)" }}>/{maxMarks}</span>
          </span>
        </div>
      </td>
      <td className="px-3 py-2" />
      {showRank && <td className="px-3 py-2" />}
    </tr>
  );
}

/* ===== Cutoff row — mobile card ===== */
function MobileCutoffRow({
  cutoffMarks,
  maxMarks,
  paper,
}: {
  cutoffMarks: number;
  maxMarks: number;
  paper: Paper;
}) {
  const barWidth = (cutoffMarks / maxMarks) * 100;
  const displayLabel = paper === "csat" ? "CSAT Qualifying Cutoff" : "General Category Cutoff";

  return (
    <div
      className="px-4 py-2.5"
      style={{
        borderTop: "2px dashed rgba(255, 153, 51, 0.5)",
        borderBottom: "2px dashed rgba(255, 153, 51, 0.5)",
        backgroundColor: "rgba(255, 153, 51, 0.04)",
      }}
    >
      <div className="flex items-center gap-3">
        <span
          className="inline-flex items-center justify-center w-7 h-7 rounded-full text-sm font-bold flex-shrink-0"
          style={{ backgroundColor: "rgba(255,153,51,0.1)", color: "var(--saffron)" }}
        >
          —
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline justify-between gap-2">
            <span className="font-semibold text-[13px] truncate" style={{ color: "var(--saffron)" }}>
              {displayLabel}
            </span>
            <span className="font-bold text-[14px] whitespace-nowrap flex-shrink-0" style={{ color: "var(--saffron)", fontVariantNumeric: "tabular-nums" }}>
              {cutoffMarks.toFixed(1)}
              <span className="text-[11px]" style={{ color: "rgba(255,153,51,0.4)" }}>/{maxMarks}</span>
            </span>
          </div>
        </div>
      </div>
      <div className="mt-1.5 ml-10">
        <div className="w-full h-1.5 rounded-full" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>
          <div
            style={{
              width: `${barWidth}%`,
              height: "6px",
              borderRadius: "9999px",
              background: "repeating-linear-gradient(90deg, var(--saffron) 0px, var(--saffron) 4px, transparent 4px, transparent 8px)",
              opacity: 0.5,
            }}
          />
        </div>
      </div>
    </div>
  );
}
