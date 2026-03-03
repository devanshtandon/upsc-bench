"use client";

import { PAPER_LABELS } from "@/lib/constants";
import type { Paper } from "@/types";

interface PaperTabsProps {
  selected: Paper;
  onChange: (paper: Paper) => void;
}

export default function PaperTabs({ selected, onChange }: PaperTabsProps) {
  const papers: Paper[] = ["overall", "gs1", "csat"];

  return (
    <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide flex-nowrap">
      <span className="text-xs font-semibold uppercase tracking-wider mr-1 flex-shrink-0" style={{ color: "rgba(26,17,69,0.4)" }}>
        Paper
      </span>
      {papers.map((paper) => {
        const isActive = selected === paper;
        return (
          <button
            key={paper}
            onClick={() => onChange(paper)}
            className={`pill-btn whitespace-nowrap ${isActive ? "active" : "inactive"}`}
          >
            {PAPER_LABELS[paper]}
          </button>
        );
      })}
    </div>
  );
}
