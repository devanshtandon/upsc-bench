"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { MODEL_DISPLAY_NAMES, MODEL_COLORS } from "@/lib/constants";
import { getModelScore } from "@/lib/data";
import type { ModelEntry, Paper, Year, LeaderboardData } from "@/types";

interface ScoreChartProps {
  models: ModelEntry[];
  year: Year;
  paper: Paper;
  data: LeaderboardData;
}

export default function ScoreChart({ models, year, paper, data }: ScoreChartProps) {
  const chartData = models.map((m) => {
    const score = getModelScore(m, year, paper);
    const shortName = MODEL_DISPLAY_NAMES[m.model] ?? m.model;
    return {
      name: shortName,
      score: score.marks,
      maxMarks: score.maxMarks,
      model: m.model,
    };
  });

  let cutoff: number | null = null;
  if (year !== "all" && paper === "gs1") {
    cutoff = data.metadata.cutoffs[year as number]?.gs1 ?? null;
  } else if (year !== "all" && paper === "csat") {
    cutoff = data.metadata.cutoffs[year as number]?.csat_qualifying ?? null;
  }

  const maxScore = chartData[0]?.maxMarks ?? 200;

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(26, 17, 69, 0.06)" />
          <XAxis
            dataKey="name"
            tick={{ fill: "rgba(26, 17, 69, 0.5)", fontSize: 12 }}
            angle={-30}
            textAnchor="end"
            height={80}
            axisLine={{ stroke: "rgba(26, 17, 69, 0.1)" }}
            tickLine={{ stroke: "rgba(26, 17, 69, 0.1)" }}
          />
          <YAxis
            domain={[0, maxScore]}
            tick={{ fill: "rgba(26, 17, 69, 0.5)", fontSize: 12 }}
            axisLine={{ stroke: "rgba(26, 17, 69, 0.1)" }}
            tickLine={{ stroke: "rgba(26, 17, 69, 0.1)" }}
            label={{
              value: "Marks",
              angle: -90,
              position: "insideLeft",
              fill: "rgba(26, 17, 69, 0.4)",
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--cream)",
              border: "1px solid var(--card-border)",
              borderRadius: "12px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
              fontFamily: "var(--font-dm-sans), sans-serif",
            }}
            cursor={{ fill: "rgba(255, 153, 51, 0.06)" }}
            formatter={(value) => [`${Number(value).toFixed(1)} marks`, "Score"]}
          />
          <Bar dataKey="score" radius={[6, 6, 0, 0]} maxBarSize={56}>
            {chartData.map((entry) => (
              <Cell
                key={entry.model}
                fill={MODEL_COLORS[entry.model] ?? "var(--navy)"}
              />
            ))}
          </Bar>
          {cutoff !== null && (
            <ReferenceLine
              y={cutoff}
              stroke="#DC2626"
              strokeDasharray="8 4"
              strokeWidth={2}
              label={{
                value: `Cutoff: ${cutoff}`,
                position: "right",
                fill: "#DC2626",
                fontSize: 12,
                fontWeight: 600,
              }}
            />
          )}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
