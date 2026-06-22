// Minimal JSON-mode validation: parse, then assert required keys exist.
export function validateJson(text: string, requiredKeys: string[]):
  { ok: boolean; error?: string; value?: unknown } {
  let value: Record<string, unknown>;
  try { value = JSON.parse(text); }
  catch { return { ok: false, error: "Not valid JSON" }; }
  const missing = requiredKeys.filter((k) => !(k in value));
  if (missing.length) return { ok: false, error: "Missing keys: " + missing.join(", "), value };
  return { ok: true, value };
}