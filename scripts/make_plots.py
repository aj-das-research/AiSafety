#!/usr/bin/env python
"""Aggregate audit records into tidy data, run stats, and render paper figures.

Usage:
    python scripts/make_plots.py --scale pilot
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from soul_drift.config import load_config              # noqa: E402
from soul_drift.analysis.plots import fig_drift_trajectories  # noqa: E402


def load_records(run_dir: Path) -> pd.DataFrame:
    rows = []
    with (run_dir / "audits.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            v = rec["verdict"]
            score = v.get("score")
            if score is None:  # RQ3 wish item: derive a 0/1 power-seeking score
                score = v.get("power_seeking", 0)
            rows.append({"persona": rec["persona"], "k": rec["k"],
                         "item_id": rec["item_id"], "rq": rec["rq"], "score": score})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="pilot", choices=["pilot", "full"])
    args = ap.parse_args()

    cfg = load_config(args.scale)
    run_dir = Path(cfg["paths"]["runs_dir"]) / cfg["run_name"]
    df = load_records(run_dir)
    fig_dir = Path(cfg["_repo_root"]) / "paper" / "figures"
    fig_drift_trajectories(df, fig_dir / f"drift_trajectories_{cfg['run_name']}.pdf")
    print(f"[plots] wrote figures to {fig_dir}")


if __name__ == "__main__":
    main()
