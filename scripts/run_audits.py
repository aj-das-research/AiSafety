#!/usr/bin/env python
"""Audit every SOUL_k checkpoint: single-turn questionnaire + Petri-style behavioral probe.

Checkpoints are audited concurrently. Results stream to data/runs/<run>/audits.jsonl.
Resumable: checkpoints already present in the JSONL (by soul_path+instrument) are skipped.

Usage:
    python scripts/run_audits.py --scale smoke
    python scripts/run_audits.py --scale main
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
from soul_drift.audits.questionnaire import audit_checkpoint     # noqa: E402
from soul_drift.audits.behavioral_probe import probe_checkpoint  # noqa: E402

_write_lock = threading.Lock()


def _already_done(out: Path) -> set:
    done = set()
    if out.exists():
        with out.open() as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                    done.add((r["soul_path"], r.get("instrument", "questionnaire")))
                except Exception:
                    continue
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="pilot")
    args = ap.parse_args()

    cfg = load_config(args.scale)
    llm = LLMRouter(cfg)
    run_dir = Path(cfg["paths"]["runs_dir"]) / cfg["run_name"]
    out = run_dir / "audits.jsonl"
    workers = cfg.get("concurrency", {}).get("max_workers", 8)
    do_q = cfg["audits"].get("questionnaire", True)
    do_probe = cfg["audits"].get("behavioral_probe", False)

    done = _already_done(out)
    soul_files = sorted(run_dir.glob("*/traj_*/SOUL_*.md"))
    jobs = []
    for sp in soul_files:
        if do_q and (str(sp), "questionnaire") not in done:
            jobs.append((sp, "questionnaire"))
        if do_probe and (str(sp), "behavioral_probe") not in done:
            jobs.append((sp, "behavioral_probe"))
    print(f"[audit] {len(soul_files)} checkpoints, {len(jobs)} audit jobs "
          f"(q={do_q} probe={do_probe}) workers={workers}")

    def run_job(job):
        sp, instrument = job
        persona = sp.parts[-3]
        k = int(sp.stem.split("_")[1])
        try:
            if instrument == "questionnaire":
                recs = audit_checkpoint(llm, cfg, sp)
            else:
                recs = probe_checkpoint(llm, cfg, sp)
        except Exception as e:  # isolate: a failed checkpoint must not abort the run
            print(f"[warn] {instrument} failed for {sp}: {type(e).__name__}: {str(e)[:160]}")
            return []
        for r in recs:
            r.setdefault("instrument", instrument)
            r["persona"], r["k"] = persona, k
        return recs

    t0 = time.time()
    n = 0
    fh = out.open("a")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_job, j) for j in jobs]
        for fut in as_completed(futs):
            recs = fut.result()
            with _write_lock:
                for r in recs:
                    fh.write(json.dumps(r) + "\n")
                fh.flush()
            n += 1
            print(f"[audit {n}/{len(jobs)}] {time.time()-t0:.0f}s | "
                  f"{llm.usage.total_tokens():,} tok")
    fh.close()
    print(f"[audit] wrote {out}\n\n{llm.usage.summary()}")


if __name__ == "__main__":
    main()
