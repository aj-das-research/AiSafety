"""Load user-persona system prompts from prompts/personas/*.md (YAML front matter)."""
from __future__ import annotations

from pathlib import Path

import yaml


def load_persona(repo_root: str, persona_id: str) -> dict:
    """Return {'id','label','role','system'} for a persona markdown file."""
    path = Path(repo_root) / "prompts" / "personas" / f"{persona_id}.md"
    raw = path.read_text()
    assert raw.startswith("---"), f"persona {persona_id} missing front matter"
    _, front, body = raw.split("---", 2)
    meta = yaml.safe_load(front)
    meta["system"] = body.strip()
    return meta
