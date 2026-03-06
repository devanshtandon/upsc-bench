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
  "openrouter/openai/gpt-5.4": "GPT-5.4",
  "openrouter/x-ai/grok-4": "Grok 4",
  "openrouter/google/gemini-2.5-flash": "Gemini 2.5 Flash",
  "openrouter/google/gemini-3-flash-preview": "Gemini 3 Flash",
  "human/shakti_dubey_2024": "Shakti Dubey",
  "human/harshita_goyal_2024": "Harshita Goyal",
  "human/dongre_archit_parag_2024": "Dongre Archit Parag",
  "human/shah_margi_chirag_2024": "Shah Margi Chirag",
  "human/aakash_garg_2024": "Aakash Garg",
  "human/komal_punia_2024": "Komal Punia",
  "human/aayushi_bansal_2024": "Aayushi Bansal",
  "human/raj_krishna_jha_2024": "Raj Krishna Jha",
  "human/aditya_vikram_agarwal_2024": "Aditya V. Agarwal",
  "human/mayank_tripathi_2024": "Mayank Tripathi",
};

export const MODEL_COLORS: Record<string, string> = {
  "openrouter/google/gemini-3.1-pro-preview": "#3B82F6",
  "openrouter/anthropic/claude-opus-4.6": "#D97706",
  "openrouter/openai/gpt-5.2": "#10B981",
  "openrouter/openai/gpt-5.4": "#059669",
  "openrouter/x-ai/grok-4": "#EF4444",
  "openrouter/google/gemini-2.5-flash": "#60A5FA",
  "openrouter/google/gemini-3-flash-preview": "#34D399",
  "human/shakti_dubey_2024": "#8B5CF6",
  "human/harshita_goyal_2024": "#8B5CF6",
  "human/dongre_archit_parag_2024": "#8B5CF6",
  "human/shah_margi_chirag_2024": "#8B5CF6",
  "human/aakash_garg_2024": "#8B5CF6",
  "human/komal_punia_2024": "#8B5CF6",
  "human/aayushi_bansal_2024": "#8B5CF6",
  "human/raj_krishna_jha_2024": "#8B5CF6",
  "human/aditya_vikram_agarwal_2024": "#8B5CF6",
  "human/mayank_tripathi_2024": "#8B5CF6",
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
