"use client";

export default function Header() {
  return (
    <header className="hero-section">
      {/* Tricolor top bar */}
      <div className="tricolor-bar" />

      {/* Decorative mandala ring — hidden on small screens to avoid overflow */}
      <div className="mandala-ring animate-spin-slow hidden sm:block" style={{ width: 200, height: 200, top: -60, right: -60, opacity: 0.3 }} />

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 md:py-10">
        <div className="flex flex-col md:flex-row items-center md:items-end justify-between gap-4 sm:gap-6">
          {/* Left: Chakra + Title */}
          <div className="flex items-center gap-4 sm:gap-5 animate-fade-in-up">
            <div className="flex-shrink-0 w-11 h-11 sm:w-14 sm:h-14 rounded-full flex items-center justify-center" style={{ border: "2px solid rgba(255, 153, 51, 0.4)" }}>
              <svg
                viewBox="0 0 100 100"
                className="w-6 h-6 sm:w-8 sm:h-8"
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
                className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight"
                style={{ fontFamily: "var(--font-playfair), serif", color: "#FFFFFF" }}
              >
                UPSC Bench
              </h1>
              <p
                className="text-xs sm:text-sm md:text-base gradient-text"
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
