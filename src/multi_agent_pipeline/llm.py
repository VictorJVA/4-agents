from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Protocol

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class JSONLLMClient(Protocol):
    """Protocol for LLM clients that return JSON from system + user payload."""

    def complete_json(self, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]: ...


class GroqJSONClient:
    def __init__(self, model: str = "llama-3.1-8b-instant") -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set.")
        self.client = Groq(api_key=api_key)
        self.model = model

    def complete_json(self, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=True),
                },
            ],
        )
        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("Empty model response")
        return json.loads(content)


def _get_gemini_client(model: str) -> "GeminiJSONClient":
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise RuntimeError(
            "Gemini support requires: pip install google-genai. "
            "Set GEMINI_API_KEY in .env to use Gemini."
        ) from e
    return GeminiJSONClient(model=model, _genai=genai, _types=types)


class GeminiJSONClient:
    """Gemini API client that returns JSON. Uses GEMINI_API_KEY from env."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        *,
        _genai: Any = None,
        _types: Any = None,
    ) -> None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set.")
        if _genai is None or _types is None:
            try:
                from google import genai as _genai_mod
                from google.genai import types as _types_mod
            except ImportError as e:
                raise RuntimeError(
                    "Gemini support requires: pip install google-genai."
                ) from e
            _genai = _genai_mod
            _types = _types_mod
        self._genai = _genai
        self._types = _types
        self.client = _genai.Client(api_key=api_key)
        self.model = model

    def complete_json(self, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model=self.model,
            contents=json.dumps(user_payload, ensure_ascii=True),
            config=self._types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        text = getattr(response, "text", None) or (response.candidates[0].content.parts[0].text if response.candidates else None)
        if not text:
            raise RuntimeError("Empty model response")
        return json.loads(text)


def get_llm_client(
    provider: str | None = None,
    model: str | None = None,
) -> JSONLLMClient:
    """Return a JSON LLM client for the given provider and model.

    provider: "groq" | "gemini" | None. If None, uses LLM_PROVIDER env var,
              or "gemini" if GEMINI_API_KEY is set, else "groq".
    model: model name for the provider. Defaults: groq llama-3.1-8b-instant, gemini gemini-2.0-flash.
    """
    provider = (provider or os.getenv("LLM_PROVIDER") or "").strip().lower()
    if not provider:
        provider = "gemini" if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") else "groq"
    if provider == "gemini":
        return _get_gemini_client(model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
    if provider == "groq":
        return GroqJSONClient(model=model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"))
    raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'groq' or 'gemini'.")
