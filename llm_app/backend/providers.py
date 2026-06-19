"""Streaming dispatch across five providers — local Ollama + four cloud APIs."""
import os
from openai import OpenAI
import anthropic
import google.generativeai as genai
from retry import with_retry


def _openai_stream(messages, model, temperature, *, base_url=None, api_key=None):
    client = OpenAI(base_url=base_url, api_key=api_key) if base_url else OpenAI()
    stream = with_retry(lambda: client.chat.completions.create(
        model=model, messages=messages, temperature=temperature, stream=True,
    ))
    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token


def stream_openai(messages, model, temperature):
    yield from _openai_stream(messages, model, temperature)


def stream_groq(messages, model, temperature):
    # Groq ships an OpenAI-compatible endpoint — same SDK, different base_url.
    yield from _openai_stream(
        messages, model, temperature,
        base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"],
    )


def stream_ollama(messages, model, temperature):
    # Local, OpenAI-compatible. No real key needed.
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    yield from _openai_stream(messages, model, temperature, base_url=base, api_key="ollama-local")


def stream_anthropic(messages, model, temperature):
    client = anthropic.Anthropic()
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    convo = [m for m in messages if m["role"] != "system"]
    with client.messages.stream(
        model=model, max_tokens=1024, system=system, messages=convo, temperature=temperature,
    ) as stream:
        for token in stream.text_stream:
            yield token


def stream_google(messages, model, temperature):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    gmodel = genai.GenerativeModel(model)
    prompt = "\n".join(m["role"] + ": " + m["content"] for m in messages)
    for chunk in gmodel.generate_content(
        prompt, stream=True, generation_config={"temperature": temperature},
    ):
        if getattr(chunk, "text", None):
            yield chunk.text


STREAMERS = {
    "openai": stream_openai,
    "anthropic": stream_anthropic,
    "google": stream_google,
    "groq": stream_groq,
    "ollama": stream_ollama,
}


def stream_chat(provider, messages, model, temperature=0.7):
    if provider not in STREAMERS:
        raise ValueError("Unknown provider: " + provider)
    yield from STREAMERS[provider](messages, model, temperature)