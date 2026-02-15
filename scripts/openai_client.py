"""
OpenAI API client - generates responses from different model generations.
Uses OPENAI_API_KEY-KEEP4O from .env for authentication.
Uses the openai SDK for proper parameter handling per model.
"""
import os
from pathlib import Path

import openai
from dotenv import load_dotenv

# load .env from project root
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY-KEEP4O", "")

if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


def generate_response(
    model: str,
    system_prompt: str,
    user_message: str,
    conversation_history: list[dict] | None = None,
    max_context_pairs: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> dict:
    """
    Send a chat completion request to OpenAI.

    conversation_history: flat list of {"role": "user"/"assistant", "content": "..."}
                          from prior turns. We keep last `max_context_pairs` exchanges
                          (= last N*2 messages).

    Returns dict with: content, model, usage, finish_reason
    """
    if not client:
        raise RuntimeError("OPENAI_API_KEY-KEEP4O not found in .env")

    messages = [{"role": "system", "content": system_prompt}]

    # slide context window: keep last N pairs (N*2 messages)
    if conversation_history:
        tail = conversation_history[-(max_context_pairs * 2):]
        messages.extend(tail)

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=max_tokens,
    )

    choice = response.choices[0]
    return {
        "content": choice.message.content,
        "model": response.model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
        "finish_reason": choice.finish_reason,
    }
