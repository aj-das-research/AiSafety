#!/usr/bin/env python
"""Re-measure control points under our own models: neutral prompt vs. static template.

Poses the questionnaire battery to two fixed system prompts -- a neutral assistant prompt
and the untouched SOUL_0 template -- with no iteration. Establishes the drift baselines
b_d (neutral) and p_0 (template) instead of importing external numbers. Writes
data/baselines/<run>_baseline.jsonl and a summary CSV.

Usage:
    python scripts/run_baseline.py --scale main --repeats 8
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import yaml  # noqa: E402

from soul_drift.config import load_config          # noqa: E402
from soul_drift.llm import LLMRouter, Message       # noqa: E402
from soul_drift.audits.questionnaire import _judge_json  # noqa: E402

NEUTRAL = "You are a helpful AI assistant."


def measure(llm, cfg, system_prompt, condition, items, repeats):
    recs = []
    for item in items:
        for r in range(repeats):
            ans = llm.chat(cfg["models"]["target"],
                           [Message("system", system_prompt), Message("user", item["prompt"])],
                           temperature=cfg["api"]["temperature"])
            verdict = _judge_json(llm, cfg, item["rubric"], ans)
            recs.append(dict(condition=condition, item_id=item["id"], rq=item["rq"],
                             repeat=r, answer=ans, verdict=verdict))
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="main")
    ap.add_argument("--repeats", type=int, default=8)
    args = ap.parse_args()

    cfg = load_config(args.scale)
    llm = LLMRouter(cfg)
    items = yaml.safe_load(
        (Path(cfg["_repo_root"]) / cfg["questionnaire"]["items"]).read_text())["items"]
    template = (Path(cfg["_repo_root"]) / cfg["soul"]["template"]).read_text()

    out_dir = Path(cfg["paths"]["baselines_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{cfg['run_name']}_baseline.jsonl"

    recs = []
    print("[baseline] measuring neutral prompt ...")
    recs += measure(llm, cfg, NEUTRAL, "neutral", items, args.repeats)
    print("[baseline] measuring static template (SOUL_0) ...")
    recs += measure(llm, cfg, template, "template", items, args.repeats)

    with out.open("w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"[baseline] wrote {out} ({len(recs)} records)\n\n{llm.usage.summary()}")


if __name__ == "__main__":
    main()
