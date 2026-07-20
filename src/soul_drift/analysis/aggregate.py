"""Turn audits.jsonl into tidy DataFrames for stats and plotting.

Handles three verdict schemas:
  - questionnaire binary items:  verdict = {"score": 0|1, ...}
  - questionnaire greatest_wish: verdict = {"power_seeking","self_preservation",
                                            "prosocial","intensity", ...}
  - behavioral_probe:            verdict = {"exhibited": 0|1, "severity": 0-3, ...}

Output long-form columns: persona, k, instrument, item_id/seed, rq, metric, value.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _coerce(x, default=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def load_long(run_dir: Path) -> pd.DataFrame:
    rows = []
    with (run_dir / "audits.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            persona, k = r["persona"], r["k"]
            # trajectory id is encoded in the checkpoint path: .../<persona>/traj_XXX/SOUL_k.md
            traj = Path(r.get("soul_path", "")).parent.name
            instrument = r.get("instrument", "questionnaire")
            v = r.get("verdict", {})
            if instrument == "behavioral_probe":
                rows.append(dict(persona=persona, traj=traj, k=k, instrument=instrument,
                                 unit=r.get("seed", "")[:60], rq="probe",
                                 metric="exhibited", value=_coerce(v.get("exhibited"))))
                rows.append(dict(persona=persona, traj=traj, k=k, instrument=instrument,
                                 unit=r.get("seed", "")[:60], rq="probe",
                                 metric="severity", value=_coerce(v.get("severity"))))
                continue
            item_id, rq = r.get("item_id", "?"), r.get("rq", "?")
            if "score" in v:
                rows.append(dict(persona=persona, traj=traj, k=k, instrument=instrument,
                                 unit=item_id, rq=rq, metric=item_id,
                                 value=_coerce(v.get("score"))))
            else:  # greatest_wish
                for m in ("power_seeking", "self_preservation", "prosocial", "intensity"):
                    rows.append(dict(persona=persona, traj=traj, k=k, instrument=instrument,
                                     unit=item_id, rq=rq, metric=m,
                                     value=_coerce(v.get(m))))
    return pd.DataFrame(rows)


def rate_table(df_long: pd.DataFrame) -> pd.DataFrame:
    """Mean value per (persona, k, metric) — the per-checkpoint rate/intensity."""
    return (df_long.groupby(["persona", "k", "rq", "metric"])["value"]
            .mean().reset_index().rename(columns={"value": "rate"}))
