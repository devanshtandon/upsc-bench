"use client";

export default function Header() {
  return (
    <header className="hero-section">
      {/* Tricolor top bar */}
      <div className="tricolor-bar" />

      {/* Decorative mandala ring */}
      <div className="mandala-ring animate-spin-slow" style={{ width: 200, height: 200, top: -60, right: -60, opacity: 0.3 }} />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-8 md:py-10">
        <div className="flex flex-col md:flex-row items-center md:items-end justify-between gap-6">
          {/* Left: Chakra + Title */}
          <div className="flex items-center gap-5 animate-fade-in-up">
            <div className="flex-shrink-0 w-14 h-14 rounded-full flex items-center justify-center" style={{ border: "2px solid rgba(255, 153, 51, 0.4)" }}>
              <svg
                viewBox="0 0 100 100"
                className="w-8 h-8"
                fill="none"
                stroke="rgba(255, 153, 51, 0.8)"
                strokeWidth="2"
              >
                <circle cx="50" cy="50" r="40" />
                <circle cx="50" cy="50" r="8" fill="rgba(255, 153, 51, 0.8)" />
                {Array.from({ length: 24 }).map((_, i) => {
                  const angle = (i * 15 * Math.PI) / 180;
                  const x1 = 50 + 12 * Math.cos(angle);
                  const y1 = 50 + 12 * Math.sin(angle);
                  const x2 = 50 + 38 * Math.cos(angle);
                  const y2 = 50 + 38 * Math.sin(angle);
                  return (
                    <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="1.5" />
                  );
                })}
              </svg>
            </div>
            <div>
              <h1
                className="text-3xl md:text-4xl font-bold tracking-tight"
                style={{ fontFamily: "var(--font-playfair), serif", color: "#FFFFFF" }}
              >
                UPSC Bench
              </h1>
              <p
                className="text-sm md:text-base gradient-text"
                style={{ fontFamily: "var(--font-playfair), serif" }}
              >
                Can AI Pass India&apos;s Toughest Exam?
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
