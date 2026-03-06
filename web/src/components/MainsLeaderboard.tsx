"use client";

import React, { useState } from "react";
import { MODEL_DISPLAY_NAMES, MODEL_COLORS, MAINS_PAPER_LABELS } from "@/lib/constants";
import { getMainsModelScore } from "@/lib/data";
import type { ModelEntry, MainsPaper } from "@/types";

interface MainsLeaderboardProps {
  models: ModelEntry[];
  humanModels: ModelEntry[];
  year: number;
  paper: MainsPaper;
  humanColor?: string;
}

const paperKeys = ["essay", "gs1", "gs2", "gs3", "gs4"];

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function getMainsMeta(model: ModelEntry, year: number, paper: MainsPaper, humanColorOverride?: string) {
  const scoreData = getMainsModelScore(model, year, paper);
  const mainsData = model.mains?.[year];
  const displayName = MODEL_DISPLAY_NAMES[model.model] ?? model.model;
  const isHuman = model.is_human === true;
  const color = isHuman && humanColorOverride ? humanColorOverride : (MODEL_COLORS[model.model] ?? "#1a1145");
  const barWidth = scoreData.maxMarks > 0 ? (scoreData.score / scoreData.maxMarks) * 100 : 0;
  const isTop = model.rank === 1;
  const estimatedRank = mainsData?.estimated_rank;
  const humanMeta = model.human_metadata;
  return { scoreData, mainsData, displayName, color, barWidth, isTop, isHuman, estimatedRank, humanMeta };
}

function humanSubtitle(model: ModelEntry, year: number): string {
  const hm = model.human_metadata;
  const mains = model.mains?.[year];
  if (!hm || !mains) return "";
  return `CSE ${hm.exam_year} AIR ${hm.air} · Est. ${mains.total_score.toFixed(0)}/1250 (from ${hm.written_marks}/${hm.written_max})`;
}

/* ─── Mobile card for a single model row ─── */
function MobileRow({ model, year, paper, showPaperBreakdown, humanColor }: { model: ModelEntry; year: number; paper: MainsPaper; showPaperBreakdown: boolean; humanColor?: string }) {
  const { scoreData, mainsData, displayName, color, barWidth, isHuman, estimatedRank } = getMainsMeta(model, year, paper, humanColor);

  return (
    <div
      className={`px-4 py-3 animate-fade-in-up ${model.rank === 1 && !isHuman ? "top-rank" : ""}`}
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
          <span className={`rank-badge flex-shrink-0 ${model.rank === 1 ? "gold" : model.rank === 2 ? "silver" : model.rank === 3 ? "bronze" : "default"}`}>
            {model.rank}
          </span>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline justify-between gap-2">
            <span className="font-semibold text-[14px] truncate" style={{ color: isHuman ? "#8B5CF6" : "var(--navy)" }}>
              {displayName}
            </span>
            <span className="font-bold text-[15px] whitespace-nowrap flex-shrink-0" style={{ color: isHuman ? "#8B5CF6" : "var(--navy)", fontVariantNumeric: "tabular-nums" }}>
              {scoreData.score.toFixed(1)}
              <span className="text-[12px]" style={{ color: isHuman ? "rgba(139,92,246,0.3)" : "rgba(26,17,69,0.3)" }}>/{scoreData.maxMarks}</span>
            </span>
          </div>
          {isHuman && (
            <span className="text-[10px] font-medium block" style={{ color: "rgba(139,92,246,0.6)" }}>
              {humanSubtitle(model, year)}
            </span>
          )}
        </div>
      </div>

      {/* Row 2: Score bar + pass/fail + AIR */}
      <div className="mt-2 ml-10">
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

        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-[12px] font-medium" style={{ color: scoreData.passed ? "#16a34a" : "#dc2626" }}>
            {scoreData.scorePct.toFixed(0)}% {scoreData.passed ? "✓ Pass" : "✗ Fail"}
          </span>
          {estimatedRank && (
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

        {/* Paper breakdown mini-bars */}
        {showPaperBreakdown && mainsData && (
          <div className="mt-2 flex gap-1.5">
            {paperKeys.map((pk) => {
              const pd = mainsData.papers[pk];
              if (!pd) return null;
              const pct = pd.max_marks > 0 ? (pd.score / pd.max_marks) * 100 : 0;
              return (
                <div key={pk} className="flex flex-col items-center flex-1 min-w-0">
                  <div className="w-full h-1 rounded-full mb-0.5" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${pct}%`, backgroundColor: color, opacity: 0.7 }}
                    />
                  </div>
                  <span className="text-[9px] font-medium" style={{ color: "rgba(26,17,69,0.4)", fontVariantNumeric: "tabular-nums" }}>
                    {pd.score.toFixed(0)}
                  </span>
                  <span className="text-[8px]" style={{ color: "rgba(26,17,69,0.25)" }}>
                    {pk === "essay" ? "Ess" : pk.toUpperCase()}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Desktop table row for a single model ─── */
function DesktopRow({ model, year, paper, showPaperBreakdown, humanColor }: { model: ModelEntry; year: number; paper: MainsPaper; showPaperBreakdown: boolean; humanColor?: string }) {
  const { scoreData, mainsData, displayName, color, barWidth, isHuman, estimatedRank } = getMainsMeta(model, year, paper, humanColor);

  return (
    <tr
      className={`leaderboard-row animate-fade-in-up ${model.rank === 1 && !isHuman ? "top-rank" : ""}`}
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
          <span className={`rank-badge ${model.rank === 1 ? "gold" : model.rank === 2 ? "silver" : model.rank === 3 ? "bronze" : "default"}`}>
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
                {humanSubtitle(model, year)}
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
      {showPaperBreakdown && (
        <td className="px-3 py-2.5">
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
                      style={{ width: `${pct}%`, backgroundColor: color, opacity: 0.7 }}
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
      <td className="px-3 py-2.5 text-center">
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
}

export default function MainsLeaderboard({ models, humanModels, year, paper, humanColor = "#8B5CF6" }: MainsLeaderboardProps) {
  const showPaperBreakdown = paper === "mains_total";
  const [showAllHumans, setShowAllHumans] = useState(false);
  const hc = humanColor;

  const topHuman = humanModels.length > 0 ? humanModels[0] : null;
  const restHumans = humanModels.slice(1);
  const hasMoreHumans = restHumans.length > 0;

  return (
    <div>
      {/* ===== MOBILE: Card layout ===== */}
      <div className="block sm:hidden">
        <div className="divide-y" style={{ borderColor: "rgba(26,17,69,0.06)" }}>
          {models.map((model) => (
            <MobileRow key={model.model} model={model} year={year} paper={paper} showPaperBreakdown={showPaperBreakdown} />
          ))}
        </div>

        {/* Human Reference Section — Mobile */}
        {topHuman && (
          <div className="mt-3">
            <div className="px-4 py-2 flex items-center gap-2" style={{ borderTop: "2px solid rgba(139,92,246,0.15)" }}>
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: "#8B5CF6" }}>
                Human Reference — CSE 2024 Top 10
              </span>
            </div>
            <div className="divide-y" style={{ borderColor: "rgba(139,92,246,0.08)" }}>
              <MobileRow model={topHuman} year={year} paper={paper} showPaperBreakdown={showPaperBreakdown} />
              {showAllHumans && restHumans.map((model) => (
                <MobileRow key={model.model} model={model} year={year} paper={paper} showPaperBreakdown={showPaperBreakdown} />
              ))}
            </div>
            {hasMoreHumans && (
              <button
                onClick={() => setShowAllHumans(!showAllHumans)}
                className="w-full px-4 py-2 text-[12px] font-medium transition-colors cursor-pointer"
                style={{ color: "#8B5CF6", backgroundColor: "rgba(139,92,246,0.04)" }}
              >
                {showAllHumans ? "Hide AIR 2–10 ▴" : "Show AIR 2–10 ▾"}
              </button>
            )}
          </div>
        )}
      </div>

      {/* ===== DESKTOP: Table layout ===== */}
      <div className="hidden sm:block overflow-x-auto">
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
              <th className="text-left px-3 py-3 text-[11px] font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>#</th>
              <th className="text-left px-3 py-3 text-[11px] font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>Model</th>
              <th className="text-left px-3 py-3 text-[11px] font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>Score</th>
              {showPaperBreakdown && (
                <th className="text-center px-3 py-3 text-[11px] font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>Paper Breakdown</th>
              )}
              <th className="text-center px-3 py-3 text-[11px] font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>Est. AIR</th>
            </tr>
          </thead>
          <tbody className="stagger-children">
            {models.map((model) => (
              <DesktopRow key={model.model} model={model} year={year} paper={paper} showPaperBreakdown={showPaperBreakdown} />
            ))}
          </tbody>
        </table>

        {/* Human Reference Section — Desktop */}
        {topHuman && (
          <div className="mt-1">
            <div className="px-3 py-2 flex items-center gap-2" style={{ borderTop: "2px solid rgba(139,92,246,0.15)" }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: "#8B5CF6" }}>
                Human Reference — CSE 2024 Top 10
              </span>
            </div>
            <table className="w-full border-collapse" style={{ tableLayout: "fixed" }}>
              <colgroup>
                <col style={{ width: "44px" }} />
                <col />
                <col style={{ width: showPaperBreakdown ? "18%" : "28%" }} />
                {showPaperBreakdown && <col style={{ width: "32%" }} />}
                <col style={{ width: "100px" }} />
              </colgroup>
              <tbody>
                <DesktopRow model={topHuman} year={year} paper={paper} showPaperBreakdown={showPaperBreakdown} />
                {showAllHumans && restHumans.map((model) => (
                  <DesktopRow key={model.model} model={model} year={year} paper={paper} showPaperBreakdown={showPaperBreakdown} />
                ))}
              </tbody>
            </table>
            {hasMoreHumans && (
              <button
                onClick={() => setShowAllHumans(!showAllHumans)}
                className="w-full px-3 py-1.5 text-[12px] font-medium transition-colors cursor-pointer"
                style={{ color: "#8B5CF6", backgroundColor: "rgba(139,92,246,0.04)", borderTop: "1px solid rgba(139,92,246,0.08)" }}
              >
                {showAllHumans ? "Hide AIR 2–10 ▴" : "Show AIR 2–10 ▾"}
              </button>
            )}
          </div>
        )}
      </div>

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
          CSE 2024 top 10 rankers. Written marks from UPSC, proportionally estimated for 1250-mark benchmark subset. UPSC does not publish paper-wise marks.
        </p>
      </div>
    </div>
  );
}
