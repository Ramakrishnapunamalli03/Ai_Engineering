"""
Multi-provider LLM abstraction.
Usage: python providers.py
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai as genai

# Load .env from parent folder
load_dotenv("../.env")


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int


def chat_openai(messages, model="gpt-4o-mini", temperature=0.7):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    return LLMResponse(
        content=response.choices[0].message.content,
        model=model,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
    )


def chat_anthropic(messages, model="claude-sonnet-4-0", temperature=0.7):
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    system = next(
        (m["content"] for m in messages if m["role"] == "system"),
        ""
    )

    user_messages = [
        m for m in messages
        if m["role"] != "system"
    ]

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=user_messages,
        temperature=temperature,
    )

    return LLMResponse(
        content=response.content[0].text,
        model=model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


def chat_google(messages, model="gemini-2.5-flash", temperature=0.7):
    genai.configure(
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    gmodel = genai.GenerativeModel(model)

    prompt = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in messages
    )

    response = gmodel.generate_content(
        prompt,
        generation_config={
            "temperature": temperature
        },
    )

    return LLMResponse(
        content=response.text,
        model=model,
        input_tokens=response.usage_metadata.prompt_token_count,
        output_tokens=response.usage_metadata.candidates_token_count,
    )


def chat_groq(messages,
              model="llama-3.3-70b-versatile",
              temperature=0.7):

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    return LLMResponse(
        content=response.choices[0].message.content,
        model=model,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
    )


def chat_ollama(messages,
                model="phi3",
                temperature=0.7,
                base_url="http://localhost:11434/v1"):

    client = OpenAI(
        base_url=base_url,
        api_key="ollama-local",
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    usage = getattr(response, "usage", None)

    return LLMResponse(
        content=response.choices[0].message.content,
        model=model,
        input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
        output_tokens=getattr(usage, "completion_tokens", 0) or 0,
    )


def chat(provider, messages, **kwargs):
    providers = {
        "openai": chat_openai,
        "anthropic": chat_anthropic,
        "google": chat_google,
        "groq": chat_groq,
        "ollama": chat_ollama,
    }

    if provider not in providers:
        raise ValueError(
            f"Unknown provider: {provider}"
        )

    return providers[provider](
        messages,
        **kwargs
    )

def chat_with_fallback(messages: list, preference=("openai", "anthropic", "groq")):
    last_error = None
    for provider in preference:
        try:
            return chat(provider, messages)
        except Exception as e:
            print(f"  [{provider}] failed: {e} — trying next")
            last_error = e
    raise RuntimeError(f"All providers failed. Last error: {last_error}")

# In production: instrument this with a circuit breaker so you stop calling
# a degraded provider for ~30s after N consecutive failures. Libraries like
# pybreaker or tenacity handle this cleanly.


if __name__ == "__main__":

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Be concise."
        },
        {
            "role": "user",
            "content": "What is Python in one sentence?"
        }
    ]

    try:
        result = chat_with_fallback(
            messages,
            preference=(
                "openai",
                "anthropic",
                "groq",
                "ollama",
            )
        )

        print("\nProvider Used:", result.model)
        print("Response:")
        print(result.content)
        print(
            f"\nTokens: "
            f"{result.input_tokens} in / "
            f"{result.output_tokens} out"
        )

    except Exception as e:
        print(f"\nAll providers failed: {e}")