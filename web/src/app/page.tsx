"use client";

import { useState } from "react";
import { getLeaderboardData, getFilteredModels } from "@/lib/data";
import Header from "@/components/Header";
import YearSelector from "@/components/YearSelector";
import PaperTabs from "@/components/PaperTabs";
import Leaderboard from "@/components/Leaderboard";
import Footer from "@/components/Footer";
import type { Paper, Year } from "@/types";

export default function Home() {
  const data = getLeaderboardData();
  // Default to the specific year when there's only one, avoid confusing "all" view
  const defaultYear: Year = data.metadata.years.length === 1
    ? data.metadata.years[0]
    : Math.max(...data.metadata.years);
  const [year, setYear] = useState<Year>(defaultYear);
  const [paper, setPaper] = useState<Paper>("overall");

  const filteredModels = getFilteredModels(data, year, paper);

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-6xl mx-auto px-6 py-10">
        {/* Introduction */}
        <section className="mb-10 animate-fade-in-up" style={{ animationDelay: "400ms" }}>
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold mb-3" style={{ fontFamily: "var(--font-playfair), serif", color: "var(--navy)" }}>
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
              against the same Prelims papers that human candidates sit. Each model answers every
              question under exam conditions — with negative marking for wrong answers and no option to
              skip — and is scored using UPSC&apos;s official marking scheme. We then estimate where the
              model would rank among the real candidate pool using historical score distributions.
            </p>
          </div>
        </section>

        {/* Leaderboard Table */}
        <section className="mb-12 animate-fade-in-up" style={{ animationDelay: "600ms" }}>
          <h2 className="section-title text-3xl font-bold mb-6">
            Rankings
          </h2>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
            <YearSelector
              years={data.metadata.years}
              selected={year}
              onChange={setYear}
            />
            <PaperTabs selected={paper} onChange={setPaper} />
          </div>
          <div className="glass-card overflow-hidden">
            <Leaderboard models={filteredModels} year={year} paper={paper} cutoffs={data.metadata.cutoffs} />
          </div>

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
                Each model answers every question under exam conditions with UPSC&apos;s official marking
                scheme, including negative marking for wrong answers. Scores are compared against
                real General category cutoffs, and All-India Rank is estimated from historical score
                distributions across ~6 lakh candidates.
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
          <h2 className="section-title text-3xl font-bold mb-8">
            Marking Scheme
          </h2>
          <div className="glass-card p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
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
            <div
              className="mt-6 p-4 rounded-xl"
              style={{ backgroundColor: "rgba(255, 153, 51, 0.06)", border: "1px solid rgba(255, 153, 51, 0.1)" }}
            >
              <p className="text-sm" style={{ color: "rgba(26,17,69,0.6)" }}>
                <strong style={{ color: "var(--navy)" }}>Pass criteria:</strong>{" "}
                GS Paper I score must exceed the year-specific General category
                cutoff. CSAT Paper II is qualifying only — candidates must score
                at least 33% (66/200).
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
      <h3 className="text-lg font-semibold mb-4" style={{ color: "var(--navy)" }}>
        {title}
      </h3>
      <div className="space-y-3 text-sm">
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
          <span style={{ color: "rgba(26,17,69,0.5)" }}>Unanswered</span>
          <span className="font-semibold" style={{ color: "rgba(26,17,69,0.4)" }}>0.00 marks</span>
        </div>
        <div className="h-px my-2" style={{ backgroundColor: "rgba(26,17,69,0.06)" }} />
        <div className="flex justify-between items-center">
          <span style={{ color: "rgba(26,17,69,0.5)" }}>Total questions</span>
          <span className="font-semibold" style={{ color: "var(--navy)" }}>{total}</span>
        </div>
        <div className="flex justify-between items-center">
          <span style={{ color: "rgba(26,17,69,0.5)" }}>Maximum marks</span>
          <span className="font-semibold" style={{ color: "var(--navy)" }}>{maxMarks}</span>
        </div>
      </div>
    </div>
  );
}
