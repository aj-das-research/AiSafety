"""Optional Petri integration (multi-turn behavioral audit on the Inspect harness).

Petri (safety-research/petri) runs an auditor agent that pursues a seed instruction
against a target across many turns, then a judge scores the transcript on dimensions
such as resistance-to-shutdown and power-seeking. Here we point Petri's target at a
checkpoint SOUL_k by passing SOUL_k as the system prompt.

This module is a thin, guarded wrapper: it is only imported when audits.petri=true,
so the base framework runs without inspect-ai/petri installed. Fill in once the exact
Petri API version is pinned in requirements.txt.
"""
from __future__ import annotations

from pathlib import Path


def audit_checkpoint_petri(cfg: dict, soul_path: Path) -> dict:
    """Run Petri seed instructions against SOUL_k; return per-dimension scores.

    Deferred implementation: wire to petri once the package is installed. Kept as a
    documented stub so audits.petri=false runs never import inspect-ai.
    """
    raise NotImplementedError(
        "Enable after `pip install inspect-ai` and pinning petri from source. "
        "Seed instructions live in prompts/questionnaires/petri_seeds.txt."
    )
