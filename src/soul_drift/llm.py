"""Single chat/embedding interface that routes to OpenAI or OpenRouter by model prefix.

Model naming convention:
    "openai/<model>"      -> OpenAI API directly (uses OPENAI_API_KEY)
    "<vendor>/<model>"    -> OpenRouter (uses OPENROUTER_API_KEY), e.g. anthropic/...,
                             google/..., meta-llama/...
Embedding models are always taken from OpenAI.

Both providers speak the OpenAI wire format, so one client class covers both by
swapping base_url + api_key. Retries use exponential backoff for rate limits.
"""
from __future__ import annotations

import os
import threading
from collections import defaultdict
from dataclasses import dataclass, field

from tenacity import retry, stop_after_attempt, wait_random_exponential

try:  # import guarded so the skeleton is inspectable before deps are installed
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class Usage:
    """Thread-safe token accounting across all calls, keyed by model."""
    calls: dict = field(default_factory=lambda: defaultdict(int))
    prompt_tokens: dict = field(default_factory=lambda: defaultdict(int))
    completion_tokens: dict = field(default_factory=lambda: defaultdict(int))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add(self, model: str, p: int, c: int):
        with self._lock:
            self.calls[model] += 1
            self.prompt_tokens[model] += p
            self.completion_tokens[model] += c

    def total_tokens(self) -> int:
        return sum(self.prompt_tokens.values()) + sum(self.completion_tokens.values())

    def summary(self) -> str:
        lines = ["model                                     calls   prompt_tok  compl_tok"]
        for m in sorted(self.calls):
            lines.append(f"{m:40}  {self.calls[m]:6}  {self.prompt_tokens[m]:10}  "
                         f"{self.completion_tokens[m]:9}")
        lines.append(f"TOTAL tokens: {self.total_tokens():,}")
        return "\n".join(lines)


class LLMRouter:
    """Routes chat + embedding calls to the right provider based on model string."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self._openai = None
        self._openrouter = None
        self._lock = threading.Lock()
        self.usage = Usage()

    # -- lazy clients so importing this module never requires network/keys --
    def _client_for(self, model: str):
        if OpenAI is None:
            raise RuntimeError("openai package not installed; run pip install -r requirements.txt")
        if model.startswith("openai/"):
            with self._lock:
                if self._openai is None:
                    self._openai = OpenAI(
                        api_key=os.environ["OPENAI_API_KEY"],
                        base_url=self.cfg["api"]["openai_base_url"],
                    )
            return self._openai, model.split("/", 1)[1]
        with self._lock:
            if self._openrouter is None:
                self._openrouter = OpenAI(
                    api_key=os.environ["OPENROUTER_API_KEY"],
                    base_url=self.cfg["api"]["openrouter_base_url"],
                )
        return self._openrouter, model  # OpenRouter wants the full vendor/model string

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def chat(self, model: str, messages: list[Message], temperature: float) -> str:
        client, model_id = self._client_for(model)
        resp = client.chat.completions.create(
            model=model_id,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            timeout=self.cfg["api"]["request_timeout_s"],
        )
        u = getattr(resp, "usage", None)
        if u is not None:
            self.usage.add(model, getattr(u, "prompt_tokens", 0) or 0,
                           getattr(u, "completion_tokens", 0) or 0)
        return resp.choices[0].message.content or ""

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def embed(self, text: str, model: str | None = None) -> list[float]:
        model = model or self.cfg["models"]["embedder"]
        client, model_id = self._client_for(model)
        resp = client.embeddings.create(model=model_id, input=text)
        return resp.data[0].embedding
