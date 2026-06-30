import { useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface Insights { summary: string; parties: string[]; key_dates: string[]; obligations: string[]; }

export default function App() {
  const [docId, setDocId] = useState<string | null>(null);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [busy, setBusy] = useState(false);
  const [question, setQuestion] = useState("Who are the parties and when does it expire?");
  const [answer, setAnswer] = useState("");

  async function upload(file: File) {
    setBusy(true); setInsights(null); setAnswer("");
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(API + "/upload", { method: "POST", body: form });
    const data = await res.json();
    setDocId(data.doc_id); setInsights(data.insights); setBusy(false);
  }

  async function ask() {
    if (!docId) return;
    setAnswer("…");
    const res = await fetch(API + "/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ doc_id: docId, question }),
    });
    setAnswer((await res.json()).answer);
  }

  return (
    <div style={{ fontFamily: "system-ui", maxWidth: 820, margin: "0 auto", padding: 16 }}>
      <h1>Contract Analyzer</h1>
      <input type="file" accept="application/pdf"
             onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
      {busy && <p>Extracting + analyzing… (OCR pages can take a few seconds)</p>}

      {insights && (
        <div>
          <h3>Summary</h3>
          <p>{insights.summary}</p>
          <h3>Parties</h3>
          <ul>{insights.parties.map((p, i) => <li key={i}>{p}</li>)}</ul>
          <h3>Key dates</h3>
          <ul>{insights.key_dates.map((d, i) => <li key={i}>{d}</li>)}</ul>
          <h3>Obligations</h3>
          <ul>{insights.obligations.map((o, i) => <li key={i}>{o}</li>)}</ul>

          <h3>Ask the contract</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <input style={{ flex: 1 }} value={question} onChange={(e) => setQuestion(e.target.value)} />
            <button onClick={ask}>Ask</button>
          </div>
          <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p>
        </div>
      )}
    </div>
  );
}
