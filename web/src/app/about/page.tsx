import Footer from "@/components/Footer";

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      {/* Tricolor top bar */}
      <div className="tricolor-bar" />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        <div className="flex items-center gap-4 mb-10">
          <a
            href="/"
            className="inline-flex items-center gap-1 text-sm transition-colors hover:text-[var(--saffron)]"
            style={{ color: "var(--navy)" }}
          >
            &larr; Back
          </a>
          <div className="w-px h-6" style={{ backgroundColor: "rgba(26,17,69,0.15)" }} />
          <h1 className="section-title text-3xl font-bold">
            Methodology
          </h1>
        </div>

        <div className="space-y-8 leading-relaxed" style={{ color: "rgba(26,17,69,0.7)" }}>
          <Section title="What is UPSC Bench?">
            <p>
              UPSC Bench is an LLM evaluation benchmark based on India&apos;s
              UPSC Civil Services Examination — widely regarded as one of the
              most competitive exams in the world. It evaluates whether frontier
              AI models can pass both stages of the written exam: the Preliminary
              Examination (objective MCQs) and the Main Examination (essay and
              long-form written answers), using real questions, real marking
              schemes, and real cutoffs.
            </p>
          </Section>

          <Section title="Why This Matters">
            <p>
              The Civil Services Examination is not just an exam — it is a defining institution in
              Indian public life. Over a million candidates sit the Prelims each year, but only around
              1,000 will eventually be selected after three grueling stages: Prelims (objective), Mains
              (nine written papers over five days), and a personality interview. The entire process spans
              over a year, and most serious aspirants dedicate two to four years of their lives to
              preparation, often relocating to coaching hubs like Delhi&apos;s Mukherjee Nagar or
              Rajinder Nagar.
            </p>
            <p className="mt-3">
              The stakes justify the effort. Officers of the Indian Administrative Service are posted as
              District Magistrates with executive authority over districts larger than many countries.
              Indian Police Service officers command law enforcement across entire states. Indian Foreign
              Service officers represent the nation as diplomats. These are among the most powerful
              non-elected positions in the world&apos;s largest democracy, and the exam is the only path
              to them.
            </p>
            <p className="mt-3">
              The UPSC journey has become a cultural phenomenon in India. To understand what this exam
              means, we recommend:
            </p>
            <ul className="list-disc list-inside mt-3 space-y-2">
              <li>
                <strong style={{ color: "var(--navy)" }}>12th Fail</strong> (2023) — A critically
                acclaimed film by Vidhu Vinod Chopra, based on the true story of IPS officer Manoj
                Kumar Sharma, who rose from a village with no electricity to clear one of the
                world&apos;s hardest exams.{" "}
                <a
                  href="https://en.wikipedia.org/wiki/12th_Fail_(film)"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline transition-colors hover:text-[var(--saffron)]"
                  style={{ color: "var(--navy)" }}
                >
                  Wikipedia &rarr;
                </a>
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>TVF Aspirants</strong> (2021) — A widely loved
                web series depicting the friendship, sacrifice, and heartbreak of three UPSC aspirants
                in Delhi.{" "}
                <a
                  href="https://www.youtube.com/playlist?list=PLOq4MgiQsaGsb_WIf6q9cJMR-3HwjG5aI"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline transition-colors hover:text-[var(--saffron)]"
                  style={{ color: "var(--navy)" }}
                >
                  YouTube &rarr;
                </a>
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>Wikipedia: Civil Services Examination</strong> — A
                comprehensive overview of the exam&apos;s structure, history, and selection process.{" "}
                <a
                  href="https://en.wikipedia.org/wiki/Civil_Services_Examination_(India)"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline transition-colors hover:text-[var(--saffron)]"
                  style={{ color: "var(--navy)" }}
                >
                  Wikipedia &rarr;
                </a>
              </li>
            </ul>
          </Section>

          <Section title="Dataset">
            <p>
              The benchmark covers two stages of the UPSC examination:
            </p>
            <ul className="list-disc list-inside mt-3 space-y-1">
              <li>
                <strong style={{ color: "var(--navy)" }}>Prelims (2024 + 2025):</strong> 357 questions
                total — 197 GS Paper I (General Studies, 100 per year) and 160 CSAT Paper II (Civil
                Services Aptitude Test, 80 per year)
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>Mains (2025):</strong> 87 questions — 8 Essay
                topics, 20 GS1, 20 GS2, 20 GS3, and 19 GS4 questions
              </li>
            </ul>
            <p className="mt-3">
              Prelims questions are extracted from official UPSC PDF papers using
              the Reducto AI document parsing API, then structured into a
              machine-readable JSON format using LLM-assisted parsing. Answer
              keys are sourced from established coaching institutes (Vision IAS
              and others). Mains questions are sourced directly from the official
              question papers.
            </p>
          </Section>

          <Section title="Prelims Scoring">
            <p>
              We use the exact UPSC marking scheme:
            </p>
            <ul className="list-disc list-inside mt-3 space-y-1">
              <li>
                <strong style={{ color: "var(--navy)" }}>GS Paper I:</strong> +2.0 marks per correct answer,
                −0.66 marks per wrong answer, 0 for unanswered
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>CSAT Paper II:</strong> +2.5 marks per correct answer,
                −0.83 marks per wrong answer, 0 for unanswered
              </li>
            </ul>
            <p className="mt-3">
              Both papers are scored out of 200 marks. GS Paper I determines
              merit ranking, while CSAT Paper II is qualifying only (minimum 33%
              required). The negative marking means random guessing is roughly
              break-even — models must actually know the answer.
            </p>
          </Section>

          <Section title="Prelims Grading">
            <p>
              UPSC Prelims is single-correct MCQ, so grading is deterministic —
              no LLM grader is needed. We extract the model&apos;s answer letter
              (A/B/C/D) from its output using regex-based parsing and compare it
              against the correct answer. If the model&apos;s output cannot be
              parsed into a valid answer, it is marked as &quot;unanswered&quot;
              (0 marks).
            </p>
          </Section>

          <Section title="Mains Scoring">
            <p>
              The Mains evaluation tests long-form writing ability across 5 papers
              totaling 1,250 marks:
            </p>
            <ul className="list-disc list-inside mt-3 space-y-1">
              <li>
                <strong style={{ color: "var(--navy)" }}>Essay Paper (250 marks):</strong> 8 topics in
                two sections (A and B). Each model writes all 8 essays (up to 1,200 words each).
                The best essay from each section is selected, mirroring actual UPSC rules.
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>GS Papers 1–4 (250 marks each):</strong> 20
                questions per paper (10- and 15-mark questions). Each model writes 150–250 word answers.
              </li>
            </ul>

            <h3 className="text-base font-semibold mt-6 mb-2" style={{ color: "var(--navy)" }}>
              Grading Rubric
            </h3>
            <p>
              All answers are graded by a calibrated LLM judge (Claude Opus 4.6) using a
              5-dimension rubric:
            </p>
            <div className="mt-4 glass-card overflow-hidden">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr style={{ borderBottom: "2px solid rgba(26, 17, 69, 0.1)" }}>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>
                      Dimension
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>
                      GS Weight
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>
                      Essay Weight
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { dim: "Content Accuracy / Breadth", gs: "40%", essay: "30%" },
                    { dim: "Structure & Flow", gs: "20%", essay: "20%" },
                    { dim: "Depth & Examples", gs: "20%", essay: "20%" },
                    { dim: "Analytical Depth", gs: "10%", essay: "20%" },
                    { dim: "Presentation", gs: "10%", essay: "10%" },
                  ].map((row) => (
                    <tr
                      key={row.dim}
                      className="leaderboard-row"
                      style={{ borderBottom: "1px solid rgba(26, 17, 69, 0.06)" }}
                    >
                      <td className="px-4 py-3 font-medium" style={{ color: "var(--navy)" }}>{row.dim}</td>
                      <td className="px-4 py-3 text-right">{row.gs}</td>
                      <td className="px-4 py-3 text-right">{row.essay}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h3 className="text-base font-semibold mt-6 mb-2" style={{ color: "var(--navy)" }}>
              Debiasing & Calibration
            </h3>
            <p>
              To ensure fair and realistic grading, the judge uses several debiasing measures:
            </p>
            <ul className="list-disc list-inside mt-3 space-y-2">
              <li>
                <strong style={{ color: "var(--navy)" }}>Blind grading:</strong> Model names are hidden
                from the judge. Candidates are labeled A, B, C, D, E.
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>Shuffled order:</strong> Candidate order is
                randomized with a fixed seed per question for reproducibility.
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>Comparative format:</strong> All candidates&apos;
                answers for the same question are graded in a single prompt, forcing the judge
                to differentiate rather than grade in isolation.
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>UPSC-calibrated score anchors:</strong> The judge
                prompt includes explicit scoring guidelines calibrated to real UPSC grading standards:
              </li>
            </ul>
            <div className="mt-3 ml-6 p-4 rounded-lg text-sm space-y-1" style={{ backgroundColor: "rgba(26, 17, 69, 0.03)", borderLeft: "3px solid var(--navy)" }}>
              <p><strong style={{ color: "var(--navy)" }}>&lt;30%</strong> — Irrelevant, factually wrong, or off-topic</p>
              <p><strong style={{ color: "var(--navy)" }}>30–45%</strong> — Partially relevant but shallow, missing key points</p>
              <p><strong style={{ color: "var(--navy)" }}>45–55%</strong> — Adequate. This is the median for serious Mains candidates.</p>
              <p><strong style={{ color: "var(--navy)" }}>55–65%</strong> — Good. Well-structured with relevant examples.</p>
              <p><strong style={{ color: "var(--navy)" }}>65–75%</strong> — Excellent. Exceptional depth and analysis.</p>
              <p><strong style={{ color: "var(--navy)" }}>&gt;75%</strong> — Near-perfect. Almost never awarded in real UPSC grading.</p>
            </div>
          </Section>

          <Section title="Pass / Fail Criteria">
            <h3 className="text-base font-semibold mb-2" style={{ color: "var(--navy)" }}>
              Prelims
            </h3>
            <p>
              Each model&apos;s GS Paper I score is compared against the actual
              UPSC General category cutoff for that year. CSAT requires a minimum
              of 66/200 (33%) to qualify. These cutoffs vary year-to-year based
              on exam difficulty:
            </p>
            <div className="mt-4 glass-card overflow-hidden">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr style={{ borderBottom: "2px solid rgba(26, 17, 69, 0.1)" }}>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>
                      Year
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>
                      GS1 Cutoff
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: "rgba(26,17,69,0.4)" }}>
                      CSAT Qualifying
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { year: 2025, gs1: 90.00, csat: 66 },
                    { year: 2024, gs1: 87.98, csat: 66 },
                    { year: 2023, gs1: 75.41, csat: 66 },
                    { year: 2022, gs1: 87.54, csat: 66 },
                    { year: 2021, gs1: 87.54, csat: 66 },
                    { year: 2020, gs1: 92.51, csat: 66 },
                  ].map((row) => (
                    <tr
                      key={row.year}
                      className="leaderboard-row"
                      style={{ borderBottom: "1px solid rgba(26, 17, 69, 0.06)" }}
                    >
                      <td className="px-4 py-3 font-medium" style={{ color: "var(--navy)" }}>{row.year}</td>
                      <td className="px-4 py-3 text-right">{row.gs1}/200</td>
                      <td className="px-4 py-3 text-right">{row.csat}/200</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h3 className="text-base font-semibold mt-6 mb-2" style={{ color: "var(--navy)" }}>
              Mains
            </h3>
            <p>
              The Mains cutoff is proportionally derived from the real UPSC written exam cutoff.
              UPSC publishes a combined cutoff for all written papers (Essay + GS1-4 + Optional = 1,750 marks).
              Since we exclude the Optional paper, we scale proportionally: an approximate cutoff of
              800/1,750 becomes 571/1,250. A model passes Mains if its total score across 5 papers
              exceeds this threshold.
            </p>
          </Section>

          <Section title="Models Evaluated">
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>GPT-5.2 (OpenAI)</li>
              <li>Claude Opus 4.6 (Anthropic)</li>
              <li>Gemini 3.1 Pro (Google)</li>
              <li>Gemini 3 Flash (Google)</li>
              <li>Gemini 2.5 Flash (Google)</li>
            </ul>
            <p className="mt-3">
              <strong style={{ color: "var(--navy)" }}>Human reference:</strong> Shakti Dubey,
              CSE 2024 AIR 1. Mains score proportionally estimated at 602/1,250
              (from 843/1,750 total written marks). UPSC does not publish paper-wise
              marks, so this is a uniform estimate across all papers.
            </p>
            <p className="mt-3">
              All models are evaluated with temperature 0 for maximum
              determinism. All models evaluated via the OpenRouter API.
            </p>
          </Section>

          <Section title="Questions & Answers">
            <div className="space-y-6">
              <QA question="Why use an LLM to judge LLM answers?">
                <p>
                  Mains has no answer key — UPSC publishes questions but not model answers.
                  Human grading would be ideal but is prohibitively expensive at scale (87 questions
                  &times; 5 models = 435 answers to grade). LLM-as-judge is the practical alternative,
                  and we mitigate its weaknesses through comparative grading (forcing differentiation),
                  UPSC-calibrated score anchors (preventing score inflation), blind evaluation (preventing
                  model favoritism), and fixed-seed shuffling (ensuring reproducibility).
                </p>
              </QA>

              <QA question="How reliable is LLM-as-judge grading?">
                <p>
                  The comparative format is key — grading all candidates for the same question in a
                  single prompt forces the judge to make relative distinctions rather than assigning
                  generous scores in isolation. The UPSC-calibrated anchors prevent the common failure
                  mode of LLM judges scoring everything above 80%. The fixed seed ensures the same
                  grading run produces the same results.
                </p>
              </QA>

              <QA question="Why do AI models outscore the human reference on Mains?">
                <p>
                  Three factors: (1) The human score is a proportional estimate — UPSC publishes total
                  written marks (843/1,750 for AIR 1) but not paper-wise breakdowns, so we distribute
                  evenly across papers. The real distribution is likely uneven. (2) AI models write
                  verbose, well-structured answers that score well on rubric dimensions like &quot;Structure
                  &amp; Flow&quot; and &quot;Presentation&quot; — but real UPSC grading may value
                  conciseness and handwriting quality differently. (3) The benchmark excludes the Optional
                  paper (250 marks) and Interview (275 marks), which are part of the full selection process.
                </p>
              </QA>

              <QA question="What about the Interview stage?">
                <p>
                  Not evaluated. The UPSC personality test is a 275-mark interview conducted by a
                  board of senior civil servants. It assesses personality, communication, and
                  situational judgment — qualities that require physical presence and real-time
                  interaction. This is fundamentally different from a text-based benchmark.
                </p>
              </QA>

              <QA question="Can I add my own model?">
                <p>
                  Yes. Create a config YAML in <code className="text-xs px-1 py-0.5 rounded" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>config/</code> specifying
                  the model name, provider, and parameters. Run the Prelims benchmark with{" "}
                  <code className="text-xs px-1 py-0.5 rounded" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>python benchmark/runner.py --config config/your_model.yaml</code>{" "}
                  and the Mains benchmark with{" "}
                  <code className="text-xs px-1 py-0.5 rounded" style={{ backgroundColor: "rgba(26,17,69,0.06)" }}>python -m benchmark.mains_runner --config config/mains_your_model.yaml</code>.
                  Then regenerate the leaderboard.
                </p>
              </QA>
            </div>
          </Section>

          <Section title="Limitations">
            <ul className="list-disc list-inside mt-2 space-y-2">
              <li>
                <strong style={{ color: "var(--navy)" }}>LLM-as-judge bias:</strong> The Mains judge
                (Claude Opus 4.6) may have systematic biases — e.g., preferring verbose answers,
                favoring certain writing styles, or having blind spots on India-specific cultural context.
                Comparative grading and score anchors mitigate but don&apos;t eliminate this.
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>Human reference is estimated:</strong> The
                Mains human reference score (Shakti Dubey, AIR 1) is proportionally scaled from
                total written marks. The actual paper-wise distribution is unknown and likely uneven.
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>Optional paper excluded:</strong> Real UPSC
                Mains includes an Optional subject paper (250 marks). Our benchmark covers Essay + GS1-4
                only (1,250 of 1,750 written marks).
              </li>
              <li>
                Answer keys from coaching institutes may have errors, particularly for
                disputed Prelims questions
              </li>
              <li>
                PDF extraction may introduce artifacts in question text or miss complex formatting
              </li>
              <li>
                CSAT Paper II includes comprehension passages — the full passage context is provided
                but may lose formatting nuances
              </li>
            </ul>
          </Section>
        </div>
      </main>

      <Footer />
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="glass-card p-6">
      <h2
        className="text-xl font-semibold mb-3"
        style={{
          fontFamily: "var(--font-playfair), serif",
          color: "var(--navy)",
        }}
      >
        {title}
      </h2>
      {children}
    </section>
  );
}

function QA({
  question,
  children,
}: {
  question: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h4 className="font-semibold mb-1" style={{ color: "var(--navy)" }}>
        {question}
      </h4>
      <div style={{ color: "rgba(26,17,69,0.7)" }}>
        {children}
      </div>
    </div>
  );
}
