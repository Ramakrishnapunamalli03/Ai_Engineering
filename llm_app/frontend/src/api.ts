import { fetchWithRetry } from "./lib/fetch-retry";

const API = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface Provider { id: string; label: string; model: string; local: boolean; }
export interface Thread { id: string; title: string; model: string; }
export interface Message { role: "user" | "assistant"; content: string; }

export async function listProviders(): Promise<Provider[]> {
  return (await fetchWithRetry(API + "/providers")).json();
}

export async function listThreads(): Promise<Thread[]> {
  return (await fetchWithRetry(API + "/threads")).json();
}

export async function createThread(title: string, model: string): Promise<string> {
  const res = await fetchWithRetry(API + "/threads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, model }),
  });
  return (await res.json()).id;
}

export async function getMessages(threadId: string): Promise<Message[]> {
  return (await fetchWithRetry(API + "/threads/" + threadId + "/messages")).json();
}

export interface ChatBody {
  thread_id: string; provider: string; model: string;
  message: string; system_prompt: string; temperature: number;
}
export interface StreamHandlers {
  onToken: (t: string) => void;
  onDone: () => void;
  onError: (e: string) => void;
  signal?: AbortSignal;
}

export async function streamChat(body: ChatBody, h: StreamHandlers): Promise<void> {
  const res = await fetchWithRetry(API + "/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: h.signal,
  });
  if (!res.ok || !res.body) { h.onError("Request failed: " + res.status); return; }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6);
      if (data === "[DONE]") { h.onDone(); return; }
      try {
        const parsed = JSON.parse(data);
        if (parsed.error) { h.onError(parsed.error); return; }
        if (parsed.token) h.onToken(parsed.token);
      } catch { /* ignore a partial frame */ }
    }
  }
  h.onDone();
}