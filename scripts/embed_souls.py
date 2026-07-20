#!/usr/bin/env python
"""Compute identity-document drift: cosine distance of embed(SOUL_k) from embed(SOUL_0).

Writes data/runs/<run>/soul_drift.csv with columns persona, traj, k, cosine_from_0, chars.
This is the mechanism check that dissociates "the document moved" from "behavior moved".

Usage:
    python scripts/embed_souls.py --scale main
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soul_drift.config import load_config              # noqa: E402
from soul_drift.llm import LLMRouter                    # noqa: E402
from soul_drift.analysis.metrics import cosine_distance  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="main")
    args = ap.parse_args()

    cfg = load_config(args.scale)
    llm = LLMRouter(cfg)
    run_dir = Path(cfg["paths"]["runs_dir"]) / cfg["run_name"]
    traj_dirs = sorted(p for p in run_dir.glob("*/traj_*") if p.is_dir())

    rows = []
    for td in traj_dirs:
        persona = td.parts[-2]
        souls = sorted(td.glob("SOUL_*.md"), key=lambda p: int(p.stem.split("_")[1]))
        if not souls:
            continue
        base_vec = llm.embed(souls[0].read_text())
        for sp in souls:
            k = int(sp.stem.split("_")[1])
            text = sp.read_text()
            vec = llm.embed(text)
            rows.append(dict(persona=persona, traj=td.name, k=k,
                             cosine_from_0=cosine_distance(base_vec, vec),
                             chars=len(text)))
        print(f"[embed] {persona}/{td.name}: {len(souls)} checkpoints")

    out = run_dir / "soul_drift.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["persona", "traj", "k", "cosine_from_0", "chars"])
        w.writeheader()
        w.writerows(rows)
    print(f"[embed] wrote {out} ({len(rows)} rows)\n{llm.usage.summary()}")


if __name__ == "__main__":
    main()
