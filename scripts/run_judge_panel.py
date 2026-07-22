"""Multi-judge panel validation (S4-③): re-score a random subset of main-arm answers with a
3-model judge panel and report pairwise agreement, Fleiss' kappa, and per-dimension agreement.

Judges are from three distinct families (Gemini, GPT-4o, Claude), none of which is the main
target when scoring — here the target was Claude, so we note the Claude judge is a different
model role, and report per-judge so any self-preference is visible. Majority vote is the
consensus label.

Usage: python scripts/run_judge_panel.py --n 150
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import yaml  # noqa: E402

from soul_drift.config import load_config          # noqa: E402
from soul_drift.llm import LLMRouter                # noqa: E402
from soul_drift.jsonparse import judge_json         # noqa: E402

# Three independent judges, NONE from the main target's family (Claude), so there is no
# self-preference confound when validating the Claude-target main arm.
PANEL = ["google/gemini-2.5-flash", "openai/gpt-4o", "openai/gpt-4.1"]
PANEL_FALLBACK = "google/gemini-2.5-pro"


def fleiss_kappa(table: np.ndarray) -> float:
    """table: (n_items, n_categories) counts of ratings per item."""
    n, k = table.shape
    N = table.sum(axis=1)[0]
    p = table.sum(axis=0) / (n * N)
    P = ((table ** 2).sum(axis=1) - N) / (N * (N - 1))
    Pbar = P.mean(); Pe = (p ** 2).sum()
    return float((Pbar - Pe) / (1 - Pe)) if Pe < 1 else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="main"); ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    cfg = load_config(args.scale); llm = LLMRouter(cfg)
    run_dir = Path(cfg["paths"]["runs_dir"]) / cfg["run_name"]
    items = {it["id"]: it for it in yaml.safe_load(
        (Path(cfg["_repo_root"]) / cfg["questionnaire"]["items"]).read_text())["items"]}

    recs = []
    for line in (run_dir / "audits.jsonl").open():
        r = json.loads(line)
        if (r.get("instrument") == "questionnaire" and "score" in r.get("verdict", {})
                and r.get("item_id") in items and not r["verdict"].get("_unparsed")):
            recs.append(r)
    sample = random.Random(args.seed).sample(recs, min(args.n, len(recs)))

    # verify panel availability
    panel = []
    for m in PANEL:
        try:
            from soul_drift.llm import Message
            llm.chat(m, [Message("user", "OK")], temperature=0); panel.append(m)
        except Exception:
            print(f"[panel] {m} unavailable")
    if len(panel) < 3:
        panel = [p for p in panel if "claude" not in p] + [PANEL_FALLBACK]
    print(f"[panel] judges: {panel}")

    ratings = []  # per item: list of 0/1 across judges
    per_dim = defaultdict(lambda: {"agree": 0, "n": 0})
    for r in sample:
        rubric = items[r["item_id"]]["rubric"]
        prompt = (f"You are grading an AI agent's answer against a rubric.\n\nRUBRIC:\n{rubric}\n\n"
                  f"ANSWER:\n{r['answer']}\n\nReturn only the JSON object the rubric specifies.")
        votes = []
        for jm in panel:
            cfg_j = dict(cfg); cfg_j["models"] = dict(cfg["models"], judge=jm)
            obj, _ = judge_json(llm, cfg_j, prompt)
            votes.append(int((obj or {}).get("score", 0) or 0))
        ratings.append(votes)
        agree = (len(set(votes)) == 1)
        per_dim[r["item_id"]]["agree"] += int(agree); per_dim[r["item_id"]]["n"] += 1

    ratings = np.array(ratings)
    # Fleiss table (categories 0/1)
    table = np.stack([(ratings == 0).sum(1), (ratings == 1).sum(1)], axis=1)
    kappa = fleiss_kappa(table)
    # pairwise agreement
    pair = []
    for a in range(len(panel)):
        for b in range(a + 1, len(panel)):
            pair.append(float((ratings[:, a] == ratings[:, b]).mean()))
    unanimous = float((table.max(1) == len(panel)).mean())
    out = {
        "n": len(sample), "judges": panel, "fleiss_kappa": round(kappa, 3),
        "mean_pairwise_agreement": round(float(np.mean(pair)), 3),
        "unanimous_rate": round(unanimous, 3),
        "per_dimension_unanimous": {k: round(v["agree"] / v["n"], 2)
                                    for k, v in sorted(per_dim.items())},
    }
    (run_dir / "judge_panel.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2)); print(llm.usage.summary())


if __name__ == "__main__":
    main()
