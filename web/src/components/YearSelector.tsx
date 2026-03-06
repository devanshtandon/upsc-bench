"use client";

import { useEffect } from "react";
import type { Year } from "@/types";

interface YearSelectorProps {
  years: number[];
  selected: Year;
  onChange: (year: Year) => void;
}

export default function YearSelector({ years, selected, onChange }: YearSelectorProps) {
  // Hide "All Years" when there's only one year — it's redundant
  const options: Year[] = years.length > 1 ? [...[...years].reverse(), "all"] : [...years];

  // If only one year and nothing selected yet, auto-select it
  useEffect(() => {
    if (years.length === 1 && selected === "all") {
      onChange(years[0]);
    }
  }, [years, selected, onChange]);

  // Don't render the selector at all if there's only one year
  if (years.length <= 1) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider mr-1" style={{ color: "rgba(26,17,69,0.4)" }}>
          Year
        </span>
        <span className="pill-btn active">
          {years[0] ?? "—"}
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-xs font-semibold uppercase tracking-wider mr-1" style={{ color: "rgba(26,17,69,0.4)" }}>
        Year
      </span>
      {options.map((year) => {
        const isActive = selected === year;
        return (
          <button
            key={year}
            onClick={() => onChange(year)}
            className={`pill-btn ${isActive ? "active" : "inactive"}`}
          >
            {year === "all" ? "All Years" : year}
          </button>
        );
      })}
    </div>
  );
}
