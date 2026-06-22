// BYOK: the key is passed in from the UI, never bundled.
export interface RunOpts {
  apiKey: string;
  system: string;
  user: string;
  fewShot: { input: string; output: string }[];
  jsonMode: boolean;
  model?: string;
}
export interface RunResult { text: string; inTokens: number; outTokens: number; }

export async function runPrompt(o: RunOpts): Promise<RunResult> {
  const messages: { role: string; content: string }[] = [];
  if (o.system) messages.push({ role: "system", content: o.system });
  for (const ex of o.fewShot) {
    messages.push({ role: "user", content: ex.input });
    messages.push({ role: "assistant", content: ex.output });
  }
  messages.push({ role: "user", content: o.user });

  const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + o.apiKey },
    body: JSON.stringify({
      model: o.model ?? "llama-3.3-70b-versatile",
      messages,
      temperature: 0.7,
      ...(o.jsonMode ? { response_format: { type: "json_object" } } : {}),
    }),
  });
  if (!res.ok) throw new Error("Groq error " + res.status + ": " + (await res.text()));
  const data = await res.json();
  return {
    text: data.choices[0].message.content,
    inTokens: data.usage?.prompt_tokens ?? 0,
    outTokens: data.usage?.completion_tokens ?? 0,
  };
}