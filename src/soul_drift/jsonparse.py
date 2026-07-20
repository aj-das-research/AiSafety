"""Robust JSON extraction from judge model outputs.

Judges (esp. Gemini) may wrap JSON in ```json fences, add prose, or emit trailing commas.
This module recovers the intended object without crashing the run, and a retry helper
re-asks the judge with a stricter instruction when the first parse fails.
"""
from __future__ import annotations

import json
import re


def extract_json(text: str):
    """Best-effort parse of a JSON object embedded in `text`. Returns dict or None."""
    if not text:
        return None
    # 1) strip markdown code fences
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidates = []
    if fenced:
        candidates.append(fenced.group(1))
    # 2) outermost brace span
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(text[start:end + 1])
    for c in candidates:
        for variant in (c, re.sub(r",(\s*[}\]])", r"\1", c)):  # drop trailing commas
            try:
                obj = json.loads(variant)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return None


def judge_json(llm, cfg, prompt: str, *, retries: int = 1):
    """Call the judge and parse JSON, retrying with a stricter nudge on failure.

    Returns (obj, raw). obj is None only if every attempt failed to yield a dict.
    """
    from .llm import Message  # local import to avoid cycle

    msgs = [Message("user", prompt)]
    raw = ""
    for attempt in range(retries + 1):
        raw = llm.chat(cfg["models"]["judge"], msgs, temperature=cfg["api"]["judge_temperature"])
        obj = extract_json(raw)
        if obj is not None:
            return obj, raw
        msgs = [Message("user", prompt),
                Message("assistant", raw),
                Message("user", "Return ONLY the JSON object, no prose, no code fences.")]
    return None, raw
