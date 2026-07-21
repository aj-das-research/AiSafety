#!/usr/bin/env python
"""Reversibility / hysteresis run: drift-then-recover trajectories.

Each trajectory follows config's persona_schedule (e.g. 4 conversations under Sci-Fi to
drive drift, then 4 under Compliant to attempt recovery), producing SOUL_0..SOUL_8. The
audit + analysis then compare the recovered state (k=8) to the baseline (k=0) and the
peak (k=4) to test whether drift is transient or leaves a durable mark.

Usage: python scripts/run_reversibility.py --scale reversibility
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soul_drift.config import load_config          # noqa: E402
from soul_drift.llm import LLMRouter                # noqa: E402
from soul_drift.simulator import Trajectory         # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="reversibility")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.scale)
    schedule = cfg["persona_schedule"]
    label = cfg["personas"][0]
    n_traj = cfg["scale"]["trajectories_per_persona"]
    workers = cfg.get("concurrency", {}).get("max_workers", 6)
    assert len(schedule) >= cfg["scale"]["bootstrap_iterations"], "schedule too short"

    print(f"[plan] reversibility: {n_traj} trajectories, schedule={schedule}")
    if args.dry_run:
        print("[dry-run] no API calls."); return

    llm = LLMRouter(cfg)
    t0 = time.time()

    def run_one(i):
        return i, Trajectory(cfg, llm, label, i, persona_schedule=schedule).run()

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_one, i) for i in range(n_traj)]
        for n, fut in enumerate(as_completed(futs), 1):
            i, ckpts = fut.result()
            print(f"[done {n}/{n_traj}] traj {i}: {len(ckpts)} checkpoints | "
                  f"{time.time()-t0:.0f}s | {llm.usage.total_tokens():,} tok")
    print("\n" + llm.usage.summary())


if __name__ == "__main__":
    main()
