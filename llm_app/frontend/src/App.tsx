import { useEffect, useRef, useState } from "react";
import {
  listProviders, listThreads, createThread, getMessages, streamChat,
  type Provider, type Thread, type Message,
} from "./api";
import { estimateTokens, estimateCost } from "./lib/token-cost";

export default function App() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [provider, setProvider] = useState<Provider | null>(null);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [systemPrompt, setSystemPrompt] = useState("You are a helpful assistant.");
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState("");
  const [busy, setBusy] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    listProviders().then((p) => { setProviders(p); setProvider(p[0] ?? null); });
    listThreads().then(setThreads);
  }, []);

  // Loading messages on thread change is what makes history survive a refresh.
  useEffect(() => {
    if (activeId) getMessages(activeId).then(setMessages);
    else setMessages([]);
  }, [activeId]);

  async function send() {
    if (!input.trim() || !provider || busy) return;
    const text = input.trim();
    setInput("");
    setBusy(true);

    let threadId = activeId;
    if (!threadId) {
      threadId = await createThread(text, provider.model);
      setActiveId(threadId);
      setThreads(await listThreads());
    }

    setMessages((m) => [...m, { role: "user", content: text }]);
    setStreaming("");

    const controller = new AbortController();
    abortRef.current = controller;
    let assistant = "";

    await streamChat(
      {
        thread_id: threadId, provider: provider.id, model: provider.model,
        message: text, system_prompt: systemPrompt, temperature: 0.7,
      },
      {
        onToken: (t) => { assistant += t; setStreaming(assistant); },
        onError: (e) => { setStreaming("⚠️ " + e); },
        onDone: () => {
          if (assistant) setMessages((m) => [...m, { role: "assistant", content: assistant }]);
          setStreaming("");
          setBusy(false);
          abortRef.current = null;
        },
        signal: controller.signal,
      },
    );
  }

  function stop() {
    abortRef.current?.abort();
    setBusy(false);
  }

  const cost = estimateCost(
    provider?.model ?? "",
    estimateTokens(systemPrompt + messages.map((m) => m.content).join(" ")),
    estimateTokens(streaming),
  );

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "system-ui" }}>
      <aside style={{ width: 240, borderRight: "1px solid #ddd", padding: 12, overflowY: "auto" }}>
        <button onClick={() => { setActiveId(null); setMessages([]); }}>+ New chat</button>
        {threads.map((t) => (
          <div key={t.id} onClick={() => setActiveId(t.id)}
               style={{ padding: 8, cursor: "pointer", fontWeight: t.id === activeId ? 700 : 400 }}>
            {t.title}
          </div>
        ))}
      </aside>

      <main style={{ flex: 1, display: "flex", flexDirection: "column", padding: 16 }}>
        <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
          <select value={provider?.id}
                  onChange={(e) => setProvider(providers.find((p) => p.id === e.target.value) ?? null)}>
            {providers.map((p) => (
              <option key={p.id} value={p.id}>{p.label}{p.local ? " 🖥️" : " ☁️"}</option>
            ))}
          </select>
          <input style={{ flex: 1 }} value={systemPrompt}
                 onChange={(e) => setSystemPrompt(e.target.value)} placeholder="System prompt" />
          <span style={{ fontFamily: "monospace" }}>~${cost.toFixed(5)}</span>
        </div>

        <div style={{ flex: 1, overflowY: "auto", whiteSpace: "pre-wrap" }}>
          {messages.map((m, i) => (
            <p key={i}><strong>{m.role === "user" ? "You" : "AI"}:</strong> {m.content}</p>
          ))}
          {streaming && <p><strong>AI:</strong> {streaming}</p>}
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <input style={{ flex: 1 }} value={input} onChange={(e) => setInput(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Ask anything..." />
          {busy ? <button onClick={stop}>Stop</button> : <button onClick={send}>Send</button>}
        </div>
      </main>
    </div>
  );
}