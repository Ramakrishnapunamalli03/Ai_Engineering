import { useEffect, useState } from "react";
import { runPrompt } from "./lib/groq";
import { validateJson } from "./lib/validate";
import { loadTemplates, saveTemplates, upsertTemplate, type Template, type PromptDoc } from "./lib/storage";

const estTokens = (s: string) => Math.ceil(s.length / 4);

export default function App() {
  const [apiKey, setApiKey] = useState(localStorage.getItem("prompt-lab-key") ?? "");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [name, setName] = useState("My template");

  // Shared input + few-shot; two system-prompt variants for A/B.
  const [user, setUser] = useState("Summarize in one line: the cat sat on the mat.");
  const [systemA, setSystemA] = useState("You are terse.");
  const [systemB, setSystemB] = useState("You are a playful poet.");
  const [useFewShot, setUseFewShot] = useState(false);
  const [fewShot, setFewShot] = useState([{ input: "ping", output: "pong" }]);
  const [jsonMode, setJsonMode] = useState(false);

  const [outA, setOutA] = useState("");
  const [outB, setOutB] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => setTemplates(loadTemplates()), []);
  useEffect(() => localStorage.setItem("prompt-lab-key", apiKey), [apiKey]);

  const docFor = (system: string): PromptDoc =>
    ({ system, user, fewShot: useFewShot ? fewShot : [], jsonMode });

  async function runAB() {
    setError("");
    if (!apiKey) { setError("Enter your Groq API key first."); return; }
    setBusy(true); setOutA(""); setOutB("");
    try {
      const [a, b] = await Promise.all([
        runPrompt({ apiKey, ...docFor(systemA) }),
        runPrompt({ apiKey, ...docFor(systemB) }),
      ]);
      setOutA(a.text); setOutB(b.text);
    } catch (e) { setError(String(e)); }
    finally { setBusy(false); }
  }

  function save() {
    const next = upsertTemplate(templates, name, docFor(systemA));
    setTemplates(next); saveTemplates(next);
  }

  function restore(t: Template, vi: number) {
    const d = t.versions[vi].doc;
    setName(t.name); setSystemA(d.system); setUser(d.user);
    setUseFewShot(d.fewShot.length > 0);
    setFewShot(d.fewShot.length ? d.fewShot : [{ input: "", output: "" }]);
    setJsonMode(d.jsonMode);
  }

  const jsonCheck = jsonMode && outA ? validateJson(outA, ["summary"]) : null;
  const cost = ((estTokens(systemA + systemB + user) + estTokens(outA + outB)) / 1000) * 0.0006;

  return (
    <div style={{ fontFamily: "system-ui", maxWidth: 1000, margin: "0 auto", padding: 16 }}>
      <h1>Prompt Lab</h1>
      <input type="password" style={{ width: "100%", marginBottom: 12 }}
             placeholder="Groq API key (kept only in your browser)"
             value={apiKey} onChange={(e) => setApiKey(e.target.value)} />

      <label>Shared input</label>
      <textarea style={{ width: "100%" }} rows={2} value={user} onChange={(e) => setUser(e.target.value)} />

      <div>
        <label>
          <input type="checkbox" checked={useFewShot} onChange={(e) => setUseFewShot(e.target.checked)} /> Few-shot exemplars
        </label>{"  "}
        <label>
          <input type="checkbox" checked={jsonMode} onChange={(e) => setJsonMode(e.target.checked)} /> Structured output (JSON)
        </label>
      </div>
      {useFewShot && fewShot.map((ex, i) => (
        <div key={i} style={{ display: "flex", gap: 8, marginTop: 4 }}>
          <input placeholder="example input" value={ex.input}
                 onChange={(e) => setFewShot(fewShot.map((x, j) => (j === i ? { ...x, input: e.target.value } : x)))} />
          <input placeholder="example output" value={ex.output}
                 onChange={(e) => setFewShot(fewShot.map((x, j) => (j === i ? { ...x, output: e.target.value } : x)))} />
        </div>
      ))}
      {useFewShot && <button onClick={() => setFewShot([...fewShot, { input: "", output: "" }])}>+ exemplar</button>}

      <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
        {[["A", systemA, setSystemA, outA, true], ["B", systemB, setSystemB, outB, false]].map(
          ([label, sys, setSys, out, showCheck]: any) => (
            <div key={label} style={{ flex: 1 }}>
              <strong>Variant {label}</strong>
              <textarea style={{ width: "100%" }} rows={3} value={sys} onChange={(e) => setSys(e.target.value)} />
              <div style={{ whiteSpace: "pre-wrap", background: "#f5f5f5", padding: 8, minHeight: 60 }}>{out}</div>
              {showCheck && jsonCheck && (
                <div style={{ color: jsonCheck.ok ? "green" : "crimson" }}>
                  {jsonCheck.ok ? "✓ valid JSON with required keys" : "✗ " + jsonCheck.error}
                </div>
              )}
            </div>
          ),
        )}
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 12 }}>
        <button onClick={runAB} disabled={busy}>{busy ? "Running..." : "Run A/B"}</button>
        <input value={name} onChange={(e) => setName(e.target.value)} />
        <button onClick={save}>Save template (Variant A)</button>
        <span style={{ fontFamily: "monospace" }}>~${cost.toFixed(5)}</span>
      </div>
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <h3>Templates</h3>
      {templates.map((t) => (
        <div key={t.id} style={{ borderTop: "1px solid #eee", padding: "8px 0" }}>
          <strong>{t.name}</strong> — {t.versions.length} version(s){" "}
          {t.versions.map((v, vi) => (
            <button key={vi} style={{ marginLeft: 6 }} onClick={() => restore(t, vi)}>
              restore {new Date(v.ts).toLocaleTimeString()}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}