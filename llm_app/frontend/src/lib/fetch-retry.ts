// Retries transient backend failures with exponential backoff.
const RETRYABLE = [429, 500, 502, 503, 504];
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function fetchWithRetry(
  url: string,
  init: RequestInit = {},
  maxRetries = 3,
  baseDelayMs = 500,
): Promise<Response> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, init);
      if (res.ok || !RETRYABLE.includes(res.status) || attempt === maxRetries) return res;
    } catch (err) {
      if (attempt === maxRetries) throw err;
    }
    await sleep(baseDelayMs * 2 ** attempt); // 0.5s, 1s, 2s
  }
  throw new Error("fetchWithRetry: exhausted retries");
}