// USD per 1K tokens. Ollama is local, so it's free.
const PRICING: Record<string, { in: number; out: number }> = {
  "gpt-4o-mini":                { in: 0.00015,  out: 0.0006 },
  "claude-3-5-sonnet-20241022": { in: 0.003,    out: 0.015  },
  "gemini-1.5-flash":           { in: 0.000075, out: 0.0003 },
  "llama-3.3-70b-versatile":    { in: 0.00059,  out: 0.00079 },
  "phi3":                         { in: 0,        out: 0 },
};

export const estimateTokens = (text: string) => Math.ceil(text.length / 4);

export function estimateCost(model: string, inTok: number, outTok: number): number {
  const p = PRICING[model];
  if (!p) return 0;
  return (inTok / 1000) * p.in + (outTok / 1000) * p.out;
}