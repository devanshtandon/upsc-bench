"use client";

import React from "react";
import { MODEL_DISPLAY_NAMES, MODEL_COLORS } from "@/lib/constants";
import { getModelScore } from "@/lib/data";
import type { ModelEntry, Paper, Year } from "@/types";

interface LeaderboardProps {
  models: ModelEntry[];
  year: Year;
  paper: Paper;
  cutoffs?: Record<number, Record<string, number>>;
}

function getRankClass(rank: number): string {
  if (rank === 1) return "gold";
  if (rank === 2) return "silver";
  if (rank === 3) return "bronze";
  return "default";
}

export default function Leaderboard({ models, year, paper, cutoffs }: LeaderboardProps) {
  const maxMarks = models.length > 0
    ? Math.max(...models.map((m) => getModelScore(m, year, paper).marks))
    : 200;

  const showRank = year !== "all" && (paper === "gs1" || paper === "overall");

  // Determine cutoff for current view
  let cutoffMarks: number | null = null;
  let cutoffMaxMarks = 200;
  let cutoffLabel: string | null = null;
  if (year !== "all" && cutoffs) {
    const yearCutoffs = cutoffs[year as number];
    if (yearCutoffs) {
      if (paper === "gs1") {
        cutoffMarks = yearCutoffs.gs1 ?? null;
      } else if (paper === "csat") {
        cutoffMarks = yearCutoffs.csat_qualifying ?? null;
      } else if (paper === "overall") {
        const gs1Val = yearCutoffs.gs1 ?? null;
        const csatVal = yearCutoffs.csat_qualifying ?? null;
        if (gs1Val !== null && csatVal !== null) {
          cutoffMarks = gs1Val + csatVal;
          cutoffMaxMarks = 400;
          cutoffLabel = "Combined Cutoff (GS1 + CSAT Qualifying)";
        }
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
  if (year !== "all" && cutoffs) {
    const yearCutoffs = cutoffs[year as number];
    if (yearCutoffs) {
      gs1Cutoff = yearCutoffs.gs1 ?? null;
      csatCutoff = yearCutoffs.csat_qualifying ?? null;
    }
  }

  const colCount = showRank ? 5 : 4;
  const thClass = "px-3 py-3 text-[11px] font-semibold uppercase tracking-wider";
  const thColor = { color: "rgba(26,17,69,0.4)" };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse" style={{ tableLayout: "fixed" }}>
        <colgroup>
          {/* # | Model | Score | Breakdown | AIR? */}
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
              <th className={`text-center ${thClass} hidden sm:table-cell`} style={thColor}>Est. AIR</th>
            )}
          </tr>
        </thead>
        <tbody className="stagger-children">
          {models.map((model, idx) => {
            const score = getModelScore(model, year, paper);
            const displayName = MODEL_DISPLAY_NAMES[model.model] ?? model.model;
            const color = MODEL_COLORS[model.model] ?? "#1a1145";
            const barWidth = maxMarks > 0 ? (score.marks / score.maxMarks) * 100 : 0;
            const isTop = model.rank === 1;

            // Get estimated rank
            let estimatedRank: { rank: number | null; label: string; percentile: number | null; total_appeared?: number } | null = null;
            if (showRank && typeof year === "number") {
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              const gs1Data = model.yearly[year]?.gs1 as any;
              if (gs1Data?.estimated_rank) {
                estimatedRank = gs1Data.estimated_rank;
              }
            }

            return (
              <React.Fragment key={model.model}>
                {cutoffMarks !== null && cutoffInsertIndex === idx && (
                  <CutoffRow cutoffMarks={cutoffMarks} maxMarks={cutoffMaxMarks} colCount={colCount} paper={paper} label={cutoffLabel} showRank={showRank} />
                )}
                <tr
                  className={`leaderboard-row animate-fade-in-up ${isTop ? "top-rank" : ""}`}
                  style={{ borderBottom: "1px solid rgba(26, 17, 69, 0.06)" }}
                >
                  {/* Rank */}
                  <td className="px-3 py-2.5">
                    <span className={`rank-badge ${getRankClass(model.rank)}`}>
                      {model.rank}
                    </span>
                  </td>

                  {/* Model name */}
                  <td className="px-3 py-2.5">
                    <div className="flex items-center gap-2.5">
                      <div
                        className="w-1.5 h-6 rounded-full flex-shrink-0"
                        style={{ backgroundColor: color }}
                      />
                      <span className="font-semibold text-[15px] truncate" style={{ color: "var(--navy)" }}>
                        {displayName}
                      </span>
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
                      <span className="font-bold text-sm whitespace-nowrap" style={{ color: "var(--navy)", fontVariantNumeric: "tabular-nums" }}>
                        {score.marks.toFixed(1)}
                        <span style={{ color: "rgba(26,17,69,0.3)" }}>/{score.maxMarks}</span>
                      </span>
                    </div>
                  </td>

                  {/* Breakdown */}
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

                  {/* Est. AIR */}
                  {showRank && (
                    <td className="px-3 py-2.5 text-center hidden sm:table-cell">
                      {estimatedRank?.rank ? (
                        <div
                          className="inline-flex flex-col items-center rounded-lg px-2.5 py-1"
                          style={{ backgroundColor: "rgba(255, 153, 51, 0.08)", border: "1px solid rgba(255, 153, 51, 0.15)" }}
                        >
                          <span className="font-bold text-sm" style={{ color: "var(--saffron)" }}>
                            ~{estimatedRank.rank.toLocaleString()}
                          </span>
                          <span className="text-[9px] font-medium" style={{ color: "rgba(255,153,51,0.6)" }}>
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
            <CutoffRow cutoffMarks={cutoffMarks} maxMarks={cutoffMaxMarks} colCount={colCount} paper={paper} label={cutoffLabel} showRank={showRank} />
          )}
        </tbody>
      </table>
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
        {year !== "all" && gs1Cutoff !== null && (
          <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.4)" }}>
            <span style={{ color: "var(--saffron)" }}>To pass ({year}):</span>{" "}
            GS Paper I score must exceed {gs1Cutoff}/200 (General category cutoff).
            {csatCutoff !== null && (
              <> CSAT Paper II is qualifying only — minimum {csatCutoff}/200 ({((csatCutoff / 200) * 100).toFixed(0)}%) required.</>
            )}
          </p>
        )}
        {year === "all" && (
          <p className="text-[10px]" style={{ color: "rgba(26,17,69,0.4)" }}>
            <span style={{ color: "var(--saffron)" }}>Passing criteria:</span>{" "}
            GS Paper I score must exceed the year-specific General category cutoff. CSAT Paper II is qualifying only — minimum 33% (66/200) required.
            Cutoff lines not shown when viewing all years (cutoffs vary by year).
          </p>
        )}
      </div>
    </div>
  );
}

function CutoffRow({
  cutoffMarks,
  maxMarks,
  colCount,
  paper,
  label,
  showRank,
}: {
  cutoffMarks: number;
  maxMarks: number;
  colCount: number;
  paper: Paper;
  label?: string | null;
  showRank: boolean;
}) {
  const barWidth = (cutoffMarks / maxMarks) * 100;
  const displayLabel = label ?? (paper === "csat" ? "CSAT Qualifying Cutoff" : "GS1 General Category Cutoff");

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
      {showRank && <td className="px-3 py-2 hidden sm:table-cell" />}
    </tr>
  );
}
