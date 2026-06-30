import { useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface Citation { file_path: string; start_line: number; end_line: number; }

export default function App() {
  const [q, setQ] = useState("How does retrieval merge BM25 and dense results?");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [busy, setBusy] = useState(false);

  async function ask() {
    setBusy(true); setAnswer(""); setCitations([]);
    const res = await fetch(API + "/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();
    setAnswer(data.answer); setCitations(data.citations); setBusy(false);
  }

  return (
    <div style={{ fontFamily: "system-ui", maxWidth: 760, margin: "0 auto", padding: 16 }}>
      <h1>Ask Your Docs</h1>
      <div style={{ display: "flex", gap: 8 }}>
        <input style={{ flex: 1 }} value={q} onChange={(e) => setQ(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && ask()} />
        <button onClick={ask} disabled={busy}>{busy ? "…" : "Ask"}</button>
      </div>
      <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p>
      {citations.length > 0 && (
        <div>
          <h3>Citations</h3>
          <ul>
            {citations.map((c, i) => (
              <li key={i}><code>{c.file_path}:{c.start_line}-{c.end_line}</code></li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}