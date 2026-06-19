"""FastAPI backend: provider switching, streaming (SSE), retry, and SQLite persistence."""
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import db
import providers

load_dotenv()
db.init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # the Vite dev origin — lock down for prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# Catalog the frontend renders in a dropdown. "local" flags Ollama.
PROVIDERS = [
    {"id": "openai",    "label": "OpenAI · GPT-4o-mini",      "model": "gpt-4o-mini",                "local": False},
    {"id": "anthropic", "label": "Anthropic · Claude 3.5",    "model": "claude-3-5-sonnet-20241022", "local": False},
    {"id": "google",    "label": "Google · Gemini 1.5 Flash", "model": "gemini-1.5-flash",           "local": False},
    {"id": "groq",      "label": "Groq · Llama 3.3 70B",      "model": "llama-3.3-70b-versatile",    "local": False},
    {"id": "ollama", "label": "Ollama · Phi-3 (local)", "model": "phi3", "local": True},
]


@app.get("/providers")
def get_providers():
    return PROVIDERS


@app.get("/threads")
def threads():
    return db.list_threads()


class NewThread(BaseModel):
    title: str
    model: str


@app.post("/threads")
def new_thread(body: NewThread):
    return {"id": db.create_thread(body.title, body.model)}


@app.get("/threads/{thread_id}/messages")
def thread_messages(thread_id: str):
    return db.get_messages(thread_id)


@app.delete("/threads/{thread_id}")
def remove_thread(thread_id: str):
    db.delete_thread(thread_id)
    return {"ok": True}


class ChatBody(BaseModel):
    thread_id: str
    provider: str
    model: str
    message: str
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.7


@app.post("/chat/stream")
def chat_stream(body: ChatBody):
    # Persist the user turn, then build full history for context.
    db.add_message(body.thread_id, "user", body.message)
    history = db.get_messages(body.thread_id)
    messages = [{"role": "system", "content": body.system_prompt}] + history

    def generate():
        collected = []
        try:
            for token in providers.stream_chat(body.provider, messages, body.model, body.temperature):
                collected.append(token)
                yield "data: " + json.dumps({"token": token}) + "\n\n"
        except Exception as err:
            yield "data: " + json.dumps({"error": str(err)}) + "\n\n"
        finally:
            if collected:
                db.add_message(body.thread_id, "assistant", "".join(collected))
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")