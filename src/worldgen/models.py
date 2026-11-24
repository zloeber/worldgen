from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ModelConfig:
    model: str
    api_base: str | None = None


def resolve_model_config(model: str | None, api_base: str | None) -> ModelConfig | None:
    selected = (model or "").strip()
    if not selected:
        return None
    base = (api_base or "").strip()
    if not base:
        base = (os.environ.get("OLLAMA_API_BASE") or os.environ.get("OPENAI_API_BASE") or "").strip()
    return ModelConfig(model=selected, api_base=base or None)


def parse_model_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match is None:
            raise ValueError("model response was not JSON")
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError("model response JSON must be an object")
    return payload


def complete_with_litellm(config: ModelConfig, prompt: str) -> dict[str, Any]:
    import litellm

    kwargs: dict[str, Any] = {
        "model": config.model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if config.api_base:
        kwargs["api_base"] = config.api_base
    response = litellm.completion(**kwargs)
    content = response.choices[0].message.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    if not isinstance(content, str) or not content.strip():
        raise ValueError("model response content was empty")
    return parse_model_json(content)
