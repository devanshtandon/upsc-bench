export const COLORS = {
  saffron: "#FF9933",
  navy: "#1a1145",
  green: "#138808",
  cream: "#FFF8F0",
  gold: "#C5A55A",
  darkText: "#1a1a2e",
  lightText: "#6b7280",
  white: "#FFFFFF",
  red: "#DC2626",
  border: "#E5E7EB",
} as const;

export const MODEL_DISPLAY_NAMES: Record<string, string> = {
  "openrouter/google/gemini-3.1-pro-preview": "Gemini 3.1 Pro",
  "openrouter/anthropic/claude-opus-4.6": "Claude Opus 4.6",
  "openrouter/openai/gpt-5.2": "GPT-5.2",
  "openrouter/x-ai/grok-4": "Grok 4",
  "openrouter/google/gemini-2.5-flash": "Gemini 2.5 Flash",
  "openrouter/google/gemini-3-flash-preview": "Gemini 3 Flash",
  "human/shakti_dubey_2024": "Shakti Dubey",
};

export const MODEL_COLORS: Record<string, string> = {
  "openrouter/google/gemini-3.1-pro-preview": "#3B82F6",
  "openrouter/anthropic/claude-opus-4.6": "#D97706",
  "openrouter/openai/gpt-5.2": "#10B981",
  "openrouter/x-ai/grok-4": "#EF4444",
  "openrouter/google/gemini-2.5-flash": "#60A5FA",
  "openrouter/google/gemini-3-flash-preview": "#34D399",
  "human/shakti_dubey_2024": "#8B5CF6",
};

export const PAPER_LABELS: Record<string, string> = {
  gs1: "GS Paper I",
  csat: "CSAT Paper II",
  overall: "Prelims Score",
};

export const MAINS_PAPER_LABELS: Record<string, string> = {
  mains_total: "Mains Total",
  essay: "Essay",
  mains_gs1: "GS-I",
  mains_gs2: "GS-II",
  mains_gs3: "GS-III",
  mains_gs4: "GS-IV (Ethics)",
};
