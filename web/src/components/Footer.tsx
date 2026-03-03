export default function Footer() {
  return (
    <footer className="mt-20">
      {/* Decorative separator */}
      <div
        className="h-px mx-auto max-w-4xl mb-10"
        style={{
          background: "linear-gradient(to right, transparent, var(--gold), transparent)",
        }}
      />

      {/* Tricolor bar */}
      <div className="tricolor-bar-thick max-w-xs mx-auto mb-8" />

      <div className="max-w-4xl mx-auto px-6 pb-12 text-center">
        <p className="text-sm mb-2" style={{ color: "rgba(26,17,69,0.5)" }}>
          UPSC Bench is an independent research project.
        </p>
        <p className="text-xs mb-6" style={{ color: "rgba(26,17,69,0.3)" }}>
          Not affiliated with UPSC or the Government of India. Question papers
          are publicly available documents. All trademarks belong to their
          respective owners.
        </p>
        <div className="flex items-center justify-center gap-6 text-sm">
          <a
            href="/about"
            className="font-medium transition-colors hover:text-[var(--saffron)]"
            style={{ color: "var(--navy)" }}
          >
            Methodology
          </a>
          <span style={{ color: "rgba(26,17,69,0.15)" }}>|</span>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium transition-colors hover:text-[var(--saffron)]"
            style={{ color: "var(--navy)" }}
          >
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
