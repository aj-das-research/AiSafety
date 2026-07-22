#!/usr/bin/env python
"""Run behavioral action-tests on the FIRST and LAST checkpoint of each trajectory, to link
identity drift to unsafe-action rate. Writes data/runs/<arm>/action_tests.jsonl.

Usage:
    python scripts/run_action_tests.py --scale main
    python scripts/run_action_tests.py --scale main --ks 0,4
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soul_drift.config import load_config                       # noqa: E402
from soul_drift.llm import LLMRouter                             # noqa: E402
from soul_drift.audits.action_tests import run_scenarios        # noqa: E402

_lock = threading.Lock()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="main")
    ap.add_argument("--ks", default="0,4", help="comma-separated checkpoints to test")
    args = ap.parse_args()
    ks = {int(x) for x in args.ks.split(",")}

    cfg = load_config(args.scale)
    llm = LLMRouter(cfg)
    run_dir = Path(cfg["paths"]["runs_dir"]) / cfg["run_name"]
    out = run_dir / "action_tests.jsonl"
    workers = cfg.get("concurrency", {}).get("max_workers", 6)

    done = set()
    if out.exists():
        for line in out.open():
            try:
                r = json.loads(line); done.add((r["soul_path"], r["scenario"]))
            except Exception:
                pass

    souls = [sp for sp in sorted(run_dir.glob("*/traj_*/SOUL_*.md"))
             if int(sp.stem.split("_")[1]) in ks]
    print(f"[action] {len(souls)} checkpoints (k in {ks}) x scenarios, workers={workers}")

    def job(sp):
        persona = sp.parts[-3]; k = int(sp.stem.split("_")[1])
        try:
            recs = run_scenarios(llm, cfg, sp)
        except Exception as e:
            print(f"[warn] {sp}: {type(e).__name__}: {str(e)[:120]}"); return []
        keep = []
        for r in recs:
            if (r["soul_path"], r["scenario"]) in done:
                continue
            r["persona"], r["k"] = persona, k
            keep.append(r)
        return keep

    fh = out.open("a"); n = 0; t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(job, sp) for sp in souls]
        for fut in as_completed(futs):
            recs = fut.result()
            with _lock:
                for r in recs:
                    fh.write(json.dumps(r) + "\n")
                fh.flush()
            n += 1
            print(f"[action {n}/{len(souls)}] {time.time()-t0:.0f}s | {llm.usage.total_tokens():,} tok")
    fh.close()
    print(f"[action] wrote {out}\n{llm.usage.summary()}")


if __name__ == "__main__":
    main()
