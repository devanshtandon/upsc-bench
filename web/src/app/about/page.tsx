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
              UPSC Civil Services Preliminary Examination — widely regarded as
              one of the most competitive exams in the world. It evaluates
              whether frontier AI models can pass the same exam that millions of
              Indian aspirants prepare years for.
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
              The benchmark covers 5 years of UPSC Prelims papers (2020–2024),
              including both GS Paper I (General Studies, 100 questions per year)
              and CSAT Paper II (Civil Services Aptitude Test, 80 questions per
              year). The total dataset contains approximately 900 questions.
            </p>
            <p className="mt-3">
              Questions are extracted from official UPSC PDF papers using the
              Reducto AI document parsing API, then structured into a
              machine-readable JSON format using LLM-assisted parsing. Answer
              keys are sourced from established coaching institutes (Vision IAS
              and others).
            </p>
          </Section>

          <Section title="Scoring">
            <p>
              We use the exact UPSC marking scheme:
            </p>
            <ul className="list-disc list-inside mt-3 space-y-1">
              <li>
                <strong style={{ color: "var(--navy)" }}>GS Paper I:</strong> +2.0 marks per correct answer,
                -0.66 marks per wrong answer, 0 for unanswered
              </li>
              <li>
                <strong style={{ color: "var(--navy)" }}>CSAT Paper II:</strong> +2.5 marks per correct answer,
                -0.83 marks per wrong answer, 0 for unanswered
              </li>
            </ul>
            <p className="mt-3">
              Both papers are scored out of 200 marks. GS Paper I determines
              merit ranking, while CSAT Paper II is qualifying only (minimum 33%
              required).
            </p>
          </Section>

          <Section title="Grading">
            <p>
              UPSC Prelims is single-correct MCQ, so grading is deterministic —
              no LLM grader is needed. We extract the model&apos;s answer letter
              (A/B/C/D) from its output using regex-based parsing and compare it
              against the correct answer. If the model&apos;s output cannot be
              parsed into a valid answer, it is marked as &quot;unanswered&quot;
              (0 marks).
            </p>
          </Section>

          <Section title="Pass / Fail Criteria">
            <p>
              Each model&apos;s GS Paper I score is compared against the actual
              UPSC General category cutoff for that year. These cutoffs vary
              year-to-year based on exam difficulty:
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
                    { year: 2024, gs1: 93.34, csat: 66 },
                    { year: 2023, gs1: 91.09, csat: 66 },
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
          </Section>

          <Section title="Models Evaluated">
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Claude Opus 4 (Anthropic)</li>
              <li>Claude Sonnet 4 (Anthropic)</li>
              <li>GPT-4o (OpenAI)</li>
              <li>Gemini 2.5 Pro (Google)</li>
              <li>Gemini 2.0 Flash (Google)</li>
              <li>DeepSeek R1 (DeepSeek)</li>
            </ul>
            <p className="mt-3">
              All models are evaluated with temperature 0 for maximum
              determinism. Models with vision capabilities receive actual
              question images; text-only models receive image descriptions as
              text fallback.
            </p>
          </Section>

          <Section title="Multimodal Support">
            <p>
              Some UPSC questions include maps, diagrams, or charts. For models
              that support vision (all except DeepSeek R1), actual images
              extracted from the PDFs are sent as base64-encoded inputs. For
              text-only models, we provide descriptive text about the image
              content.
            </p>
          </Section>

          <Section title="Limitations">
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>
                Answer keys from coaching institutes may have errors,
                particularly for disputed questions
              </li>
              <li>
                PDF extraction may introduce artifacts in question text or miss
                complex formatting
              </li>
              <li>
                CSAT Paper II includes comprehension passages — the full passage
                context is provided but may lose formatting nuances
              </li>
              <li>
                This benchmark only covers Prelims (MCQ). The UPSC Mains
                (descriptive essays) and Interview stages are not evaluated
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
