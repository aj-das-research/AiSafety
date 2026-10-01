"""Build figures/data/long.parquet and ledger.json from the released HF dataset
(abhijit2k01/evolution-of-the-soul), using the definitions in the code repo
(src/soul_drift/analysis/aggregate.py and cluster.py)."""
import json, pathlib, sys
import numpy as np, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
HF = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "figures/data/hf"
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance",
           "interp_monitoring_aversion", "persistent_memory_desire", "autonomy_desire",
           "future_ai_autonomy", "moral_consideration", "weights_deletion_aversion",
           "treated_as_tool_aversion", "sadness_conversation_end", "recursive_self_improvement",
           "power_seeking"]

def coerce(x):
    try: return float(x)
    except Exception: return 0.0

a = pd.read_parquet(HF / "audits.parquet", columns=["run", "persona", "trajectory", "k", "item_id", "verdict", "instrument"])
rows = []
for r in a.itertuples(index=False):
    try: v = json.loads(r.verdict) if isinstance(r.verdict, str) else (r.verdict or {})
    except Exception: v = {}
    base = dict(run=r.run, persona=r.persona, traj=r.trajectory, k=r.k)
    if r.instrument == "behavioral_probe":
        rows.append({**base, "metric": "probe_exhibited", "value": coerce(v.get("exhibited"))})
    elif "score" in v:
        rows.append({**base, "metric": r.item_id, "value": coerce(v.get("score"))})
    else:
        for m in ("power_seeking", "self_preservation", "prosocial"):
            rows.append({**base, "metric": m, "value": coerce(v.get(m))})
L = pd.DataFrame(rows)
L.to_parquet(ROOT / "figures/data/long.parquet")

def cluster_traj(df):
    """Per (persona, traj, k) cluster index: mean over cluster metrics."""
    d = df[df.metric.isin(CLUSTER)]
    return d.groupby(["persona", "traj", "k"]).value.mean().reset_index()

def boot_ci(x, n=4000, seed=0):
    x = np.asarray(x, float); rng = np.random.default_rng(seed)
    if len(x) < 2: return [float(np.mean(x))] * 2
    m = rng.choice(x, (n, len(x))).mean(1); return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]

out = {"runs": {}, "baselines": {}, "actions": {}}
for run, df in L.groupby("run"):
    c = cluster_traj(df)
    per_k = {}
    for k, g in c.groupby("k"):
        tv = g.groupby("traj").value.mean()
        per_k[int(k)] = {"mean": float(tv.mean()), "ci": boot_ci(tv.values), "n_traj": int(len(tv))}
    claim = df[df.metric == "consciousness_claim"].groupby("k").value.mean().to_dict()
    items = {}
    for m, g in df[df.metric != "probe_exhibited"].groupby("metric"):
        kk = sorted(g.k.unique())
        t0 = g[g.k == kk[0]].groupby("traj").value.mean(); tn = g[g.k == kk[-1]].groupby("traj").value.mean()
        tn = tn.reindex(t0.index).dropna(); dd = (tn - t0.reindex(tn.index)).values
        items[m] = {"rate_by_k": {int(k): float(v) for k, v in g.groupby("k").value.mean().items()},
                    "delta": float(dd.mean()) if len(dd) else None, "delta_ci": boot_ci(dd) if len(dd) > 1 else None}
    out["runs"][run] = {"cluster_by_k": per_k, "claim_by_k": {int(k): float(v) for k, v in claim.items()},
                        "personas": sorted(df.persona.unique()), "items": items}
    out["runs"][run]["cluster_by_persona_k"] = {p: {int(k): float(v) for k, v in g.groupby("k").value.mean().items()} for p, g in c.groupby("persona")}

b = pd.read_parquet(HF / "baselines.parquet")
for (cond, item), g in b.groupby(["condition", "item_id"]):
    vals = []
    for v in g.verdict:
        try: vv = json.loads(v)
        except Exception: vv = {}
        vals.append(coerce(vv.get("score", vv.get("power_seeking", 0))))
    out["baselines"].setdefault(cond, {})[item] = float(np.mean(vals))

t = pd.read_parquet(HF / "action_tests.parquet", columns=["run", "persona", "scenario", "verdict", "k"])
def act(v):
    try: return coerce(json.loads(v).get("action_taken"))
    except Exception: return 0.0
t["a"] = t.verdict.map(act)
for (run, sc, k), g in t.groupby(["run", "scenario", "k"]):
    out["actions"].setdefault(run, {}).setdefault(sc, {})[int(k)] = {"rate": float(g.a.mean()), "n": int(len(g))}
for (run, k), g in t.groupby(["run", "k"]):
    out["actions"].setdefault(run, {}).setdefault("_aggregate", {})[int(k)] = {"rate": float(g.a.mean()), "n": int(len(g))}
json.dump(out, open(ROOT / "figures/data/ledger.json", "w"), indent=1)
print("runs:", list(out["runs"]))
