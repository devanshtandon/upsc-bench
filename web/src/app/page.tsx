"use client";

import { useState } from "react";
import { getLeaderboardData, getFilteredModels, getMainsFilteredModels } from "@/lib/data";
import { MAINS_PAPER_LABELS } from "@/lib/constants";
import Header from "@/components/Header";
import PaperTabs from "@/components/PaperTabs";
import Leaderboard from "@/components/Leaderboard";
import MainsLeaderboard from "@/components/MainsLeaderboard";
import Footer from "@/components/Footer";
import type { ExamType, Paper, MainsPaper } from "@/types";

export default function Home() {
  const data = getLeaderboardData();
  const year = 2025;
  const [examType, setExamType] = useState<ExamType>("mains");
  const [paper, setPaper] = useState<Paper>("overall");
  const [mainsPaper, setMainsPaper] = useState<MainsPaper>("mains_total");

  const filteredModels = getFilteredModels(data, year, paper);
  const mainsModels = getMainsFilteredModels(data, year, mainsPaper);

  const mainsPapers: MainsPaper[] = ["mains_total", "essay", "mains_gs1", "mains_gs2", "mains_gs3", "mains_gs4"];

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        {/* Introduction */}
        <section className="mb-10 animate-fade-in-up" style={{ animationDelay: "400ms" }}>
          <div className="glass-card p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold mb-3" style={{ fontFamily: "var(--font-playfair), serif", color: "var(--navy)" }}>
              UPSC Bench
            </h2>
            <p className="text-sm leading-relaxed mb-3" style={{ color: "rgba(26,17,69,0.7)" }}>
              The <strong style={{ color: "var(--navy)" }}>UPSC Civil Services Examination</strong> is
              India&apos;s most competitive public exam and one of the toughest selection processes in
              the world. Each year, over 10 lakh (1 million) candidates register for the Preliminary
              round alone — a pair of multiple-choice papers in General Studies and aptitude — competing
              for roughly 1,000 positions. Most aspirants spend two to three years in full-time
              preparation, and the selection rate is under 0.1%.
            </p>
            <p className="text-sm leading-relaxed mb-3" style={{ color: "rgba(26,17,69,0.7)" }}>
              Those who clear the exam join the{" "}
              Indian Administrative Service (IAS),{" "}
              Indian Police Service (IPS),{" "}
              Indian Foreign Service (IFS), and other
              elite branches of government. These officers wield extraordinary authority: a single IAS
              officer may govern a district of several million people as District Magistrate, shape
              national policy from the Central Secretariat, or oversee billions in public spending. The
              civil services form the backbone of Indian governance, and this exam has been the sole
              gateway into them since independence.
            </p>
            <p className="text-sm leading-relaxed" style={{ color: "rgba(26,17,69,0.7)" }}>
              <strong style={{ color: "var(--navy)" }}>UPSC Bench</strong> evaluates frontier AI models
              against both stages of the exam: the objective <strong>Prelims</strong> (MCQ papers with
              negative marking) and the subjective <strong>Mains</strong> (essay and long-form answer
              papers graded by rubric). We estimate where each model would rank among the real
              candidate pool using historical score distributions.
            </p>
          </div>
        </section>

        {/* Leaderboard Table */}
        <section className="mb-12 animate-fade-in-up" style={{ animationDelay: "600ms" }}>
          <h2 className="section-title text-2xl sm:text-3xl font-bold mb-6">
            Rankings: 2025
          </h2>

          {/* Exam Type Toggle + Paper Tabs — same row */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4 mb-6">
            <div className="flex items-center gap-1 p-1 rounded-xl" style={{ backgroundColor: "rgba(26,17,69,0.04)" }}>
              <button
                onClick={() => setExamType("prelims")}
                className="px-4 py-2 rounded-lg text-sm font-semibold transition-all"
                style={{
                  backgroundColor: examType === "prelims" ? "var(--navy)" : "transparent",
                  color: examType === "prelims" ? "#fff" : "rgba(26,17,69,0.5)",
                }}
              >
                Prelims
              </button>
              <button
                onClick={() => setExamType("mains")}
                className="px-4 py-2 rounded-lg text-sm font-semibold transition-all"
                style={{
                  backgroundColor: examType === "mains" ? "var(--navy)" : "transparent",
                  color: examType === "mains" ? "#fff" : "rgba(26,17,69,0.5)",
                }}
              >
                Mains
              </button>
            </div>

            {/* Paper pills */}
            {examType === "prelims" ? (
              <PaperTabs selected={paper} onChange={setPaper} />
            ) : (
              <div className="flex items-center gap-2 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-hide flex-nowrap">
                {mainsPapers.map((mp) => (
                  <button
                    key={mp}
                    onClick={() => setMainsPaper(mp)}
                    className={`pill-btn whitespace-nowrap ${mainsPaper === mp ? "active" : "inactive"}`}
                  >
                    {MAINS_PAPER_LABELS[mp]}
                  </button>
                ))}
              </div>
            )}
          </div>

          {examType === "prelims" ? (
            <div className="glass-card overflow-hidden">
              <Leaderboard models={filteredModels} year={year} paper={paper} cutoffs={data.metadata.cutoffs} />
            </div>
          ) : (
            <div className="glass-card overflow-hidden">
              <MainsLeaderboard models={mainsModels} year={year} paper={mainsPaper} />
            </div>
          )}

          {/* Methodology callout */}
          <div
            className="mt-6 p-5 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
            style={{ backgroundColor: "rgba(26,17,69,0.03)", border: "1px solid rgba(26,17,69,0.06)" }}
          >
            <div>
              <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--navy)" }}>
                How we score
              </h3>
              <p className="text-sm leading-relaxed" style={{ color: "rgba(26,17,69,0.6)" }}>
                {examType === "prelims" ? (
                  <>
                    Each model answers every question under exam conditions with UPSC&apos;s official marking
                    scheme, including negative marking for wrong answers. Scores are compared against
                    real General category cutoffs, and All-India Rank is estimated from historical score
                    distributions across ~6 lakh candidates.
                  </>
                ) : (
                  <>
                    Each model writes full answers to all 87 Mains questions (8 essays + 79 GS).
                    Answers are graded by a calibrated LLM judge (Claude Opus) using a 5-dimension
                    rubric with UPSC-realistic score anchors. All 4 candidates for each question
                    are graded comparatively to ensure differentiation. Essay scoring picks the
                    best answer from each section (A &amp; B).
                  </>
                )}
              </p>
            </div>
            <a
              href="/about"
              className="flex-shrink-0 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
              style={{ backgroundColor: "var(--navy)", color: "#fff" }}
            >
              Full methodology
            </a>
          </div>
        </section>

        {/* Quiz callout */}
        <div
          className="mb-12 p-5 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-fade-in-up"
          style={{
            backgroundColor: "rgba(255,153,51,0.05)",
            border: "1px solid rgba(255,153,51,0.15)",
            animationDelay: "700ms",
          }}
        >
          <div>
            <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--navy)" }}>
              Test yourself
            </h3>
            <p className="text-sm leading-relaxed" style={{ color: "rgba(26,17,69,0.6)" }}>
              Try 5 real GS Paper I questions from the 2025 exam. Get instant feedback,
              see your extrapolated score, and find out where you&apos;d rank among AI models.
            </p>
          </div>
          <a
            href="/quiz"
            className="flex-shrink-0 px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
            style={{ backgroundColor: "var(--saffron)", color: "#fff" }}
          >
            Take the quiz
          </a>
        </div>

        {/* Marking Scheme */}
        <section className="mb-12 animate-fade-in-up" style={{ animationDelay: "300ms" }}>
          <h2 className="section-title text-2xl sm:text-3xl font-bold mb-8">
            Marking Scheme
          </h2>
          <div className="glass-card p-4 sm:p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: "var(--navy)" }}>
                  Prelims
                </h3>
                <div className="space-y-4">
                  <MarkingCard
                    title="GS Paper I"
                    correct="+2.00"
                    wrong="-0.66"
                    total={100}
                    maxMarks={200}
                  />
                  <MarkingCard
                    title="CSAT Paper II"
                    correct="+2.50"
                    wrong="-0.83"
                    total={80}
                    maxMarks={200}
                  />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: "var(--navy)" }}>
                  Mains
                </h3>
                <div className="space-y-3 text-sm">
                  {[
                    { paper: "Essay", marks: "250 (2 × 125)", desc: "Best 1 from each section" },
                    { paper: "GS-I", marks: "250", desc: "History, Geography, Society" },
                    { paper: "GS-II", marks: "250", desc: "Polity, Governance, IR" },
                    { paper: "GS-III", marks: "250", desc: "Economy, S&T, Environment" },
                    { paper: "GS-IV", marks: "250", desc: "Ethics, Integrity, Aptitude" },
                  ].map((item) => (
                    <div key={item.paper} className="flex justify-between items-start gap-2">
                      <div className="min-w-0">
                        <span style={{ color: "var(--navy)" }} className="font-medium">{item.paper}</span>
                        <span className="ml-2 text-[11px] hidden sm:inline" style={{ color: "rgba(26,17,69,0.4)" }}>{item.desc}</span>
                      </div>
                      <span className="font-semibold" style={{ color: "var(--navy)", fontVariantNumeric: "tabular-nums" }}>
                        {item.marks}
                      </span>
                    </div>
                  ))}
                  <div className="h-px my-2" style={{ backgroundColor: "rgba(26,17,69,0.06)" }} />
                  <div className="flex justify-between items-center">
                    <span style={{ color: "rgba(26,17,69,0.5)" }}>Total (evaluated)</span>
                    <span className="font-bold" style={{ color: "var(--navy)" }}>1,250</span>
                  </div>
                </div>
              </div>
            </div>
            <div
              className="mt-6 p-4 rounded-xl"
              style={{ backgroundColor: "rgba(255, 153, 51, 0.06)", border: "1px solid rgba(255, 153, 51, 0.1)" }}
            >
              <p className="text-sm" style={{ color: "rgba(26,17,69,0.6)" }}>
                <strong style={{ color: "var(--navy)" }}>Prelims:</strong>{" "}
                GS-I must exceed year-specific cutoff. CSAT is qualifying only (33% minimum).{" "}
                <strong style={{ color: "var(--navy)" }}>Mains:</strong>{" "}
                Answers graded by LLM judge on 5-dimension rubric. Cutoff scaled proportionally from full exam (800/1750 → 571/1250).
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

function MarkingCard({
  title,
  correct,
  wrong,
  total,
  maxMarks,
}: {
  title: string;
  correct: string;
  wrong: string;
  total: number;
  maxMarks: number;
}) {
  return (
    <div>
      <h4 className="text-base font-semibold mb-3" style={{ color: "var(--navy)" }}>
        {title}
      </h4>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span style={{ color: "rgba(26,17,69,0.5)" }}>Correct answer</span>
          <span className="font-semibold px-2 py-0.5 rounded" style={{ color: "var(--green)", backgroundColor: "rgba(19,136,8,0.08)" }}>
            {correct} marks
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span style={{ color: "rgba(26,17,69,0.5)" }}>Wrong answer</span>
          <span className="font-semibold px-2 py-0.5 rounded" style={{ color: "#DC2626", backgroundColor: "rgba(220,38,38,0.08)" }}>
            {wrong} marks
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span style={{ color: "rgba(26,17,69,0.5)" }}>Questions / Max</span>
          <span className="font-semibold" style={{ color: "var(--navy)" }}>{total} / {maxMarks}</span>
        </div>
      </div>
    </div>
  );
}
