import type { Metadata } from "next";
import { Playfair_Display, DM_Sans } from "next/font/google";
import "./globals.css";

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  display: "swap",
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "UPSC Bench — Can AI Pass India's Toughest Exam?",
  description:
    "LLM evaluation benchmark based on India's UPSC Civil Services Preliminary Examination. Ranking frontier AI models against real UPSC cutoffs.",
  openGraph: {
    title: "UPSC Bench — Can AI Pass India's Toughest Exam?",
    description:
      "Ranking frontier LLMs on India's UPSC Civil Services Exam with real marking scheme and cutoffs.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${playfair.variable} ${dmSans.variable} antialiased page-bg`}
        style={{ fontFamily: "var(--font-dm-sans), system-ui, sans-serif" }}
      >
        {children}
      </body>
    </html>
  );
}
