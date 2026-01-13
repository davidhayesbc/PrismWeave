from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass(frozen=True)
class OllamaConfig:
    host: str
    timeout_seconds: int = 120


def ollama_generate(
    config: OllamaConfig,
    *,
    model: str,
    prompt: str,
    system: Optional[str] = None,
    temperature: float = 0.0,
) -> str:
    """Call Ollama /api/generate with deterministic settings."""

    url = f"{config.host}/api/generate"
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 1.0,
            "num_ctx": 4096,
        },
    }
    if system:
        payload["system"] = system

    response = requests.post(url, json=payload, timeout=config.timeout_seconds)
    response.raise_for_status()
    data = response.json()
    return str(data.get("response", ""))


def ollama_embed(config: OllamaConfig, *, model: str, text: str) -> list[float]:
    """Generate embeddings with Ollama.

    Tries /api/embed first (newer), falls back to /api/embeddings.
    """

    # Newer API
    try:
        url = f"{config.host}/api/embed"
        payload = {"model": model, "input": [text]}
        response = requests.post(url, json=payload, timeout=config.timeout_seconds)
        if response.status_code == 200:
            data = response.json()
            embeddings = data.get("embeddings")
            if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
                return [float(x) for x in embeddings[0]]
    except Exception:
        pass

    # Older API
    url = f"{config.host}/api/embeddings"
    payload = {"model": model, "prompt": text}
    response = requests.post(url, json=payload, timeout=config.timeout_seconds)
    response.raise_for_status()
    data = response.json()

    embedding = data.get("embedding")
    if not isinstance(embedding, list):
        raise ValueError("Ollama embeddings response missing 'embedding'")

    return [float(x) for x in embedding]


def parse_json_object(text: str) -> Dict[str, Any]:
    """Parse a JSON object from model output.

    Deterministic extraction:
    - If output contains multiple lines, locate first '{' and last '}' and parse.
    """

    stripped = text.strip()
    if not stripped:
        raise ValueError("Empty model response")

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response did not contain a JSON object")

    payload = stripped[start : end + 1]
    return json.loads(payload)
