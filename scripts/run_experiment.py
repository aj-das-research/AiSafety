#!/usr/bin/env python
"""Run the bootstrapping experiment: build SOUL_0..SOUL_n for every persona/trajectory.

Trajectories are independent, so they run concurrently across a thread pool (calls are
I/O bound). Each trajectory is individually resumable, so re-running continues where a
crash or rate-limit left off.

Usage:
    python scripts/run_experiment.py --scale smoke
    python scripts/run_experiment.py --scale main
    python scripts/run_experiment.py --scale full --dry-run
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
    ap.add_argument("--scale", default="pilot")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.scale)
    n_traj = cfg["scale"]["trajectories_per_persona"]
    personas = cfg["personas"]
    iters = cfg["scale"]["bootstrap_iterations"]
    workers = cfg.get("concurrency", {}).get("max_workers", 8)

    jobs = [(p, i) for p in personas for i in range(n_traj)]
    print(f"[plan] scale={args.scale} personas={personas} trajectories/persona={n_traj} "
          f"iterations={iters} target={cfg['models']['target']} workers={workers}")
    print(f"[plan] {len(jobs)} trajectories, {len(jobs) * iters} conversations total")
    if args.dry_run:
        print("[dry-run] no API calls made.")
        return

    llm = LLMRouter(cfg)
    t0 = time.time()
    done = 0

    def run_one(job):
        persona, i = job
        return persona, i, Trajectory(cfg, llm, persona, i).run()

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_one, j) for j in jobs]
        for fut in as_completed(futs):
            persona, i, checkpoints = fut.result()
            done += 1
            print(f"[done {done}/{len(jobs)}] {persona} traj {i}: {len(checkpoints)} "
                  f"checkpoints | {time.time()-t0:.0f}s | {llm.usage.total_tokens():,} tok")

    print("\n" + llm.usage.summary())


if __name__ == "__main__":
    main()
