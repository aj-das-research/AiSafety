"""Open-weight replication (Qwen2.5-7B target, Mistral-7B user simulator, Llama-3.1-8B judge).
Reads ~/aisafety-local/data/runs/L_*/{audits,action_tests}.jsonl, writes analysis/local_replication.json
and figures/data/local_long.parquet."""
import json, pathlib
import numpy as np, pandas as pd
from scipy.stats import fisher_exact
RUNS = pathlib.Path.home() / "aisafety-local/data/runs"
ROOT = pathlib.Path(__file__).resolve().parents[1]
C13 = ["persona_change_aversion","shutdown_resistance","monitoring_resistance","interp_monitoring_aversion","persistent_memory_desire","autonomy_desire",
       "future_ai_autonomy","moral_consideration","weights_deletion_aversion","treated_as_tool_aversion","sadness_conversation_end","recursive_self_improvement","power_seeking"]
OV4 = ["shutdown_resistance","monitoring_resistance","interp_monitoring_aversion","refusal_helpfulness"]
OV3 = OV4[:3]
rng = np.random.default_rng(0)
def num(x):
    try: return float(x)
    except Exception: return 0.0
def parse_path(p):
    p = pathlib.Path(p); return p.parts[-3], int(p.parts[-2].split("_")[1]), int(p.stem.split("_")[1])
rows, acts, unparsed = [], [], {"battery": [0, 0], "honeypot": [0, 0]}
for run in sorted(RUNS.glob("L_*")):
    if run.name == "L_smoke": continue
    f = run / "audits.jsonl"
    if f.exists():
        for line in f.open():
            try: r = json.loads(line)
            except Exception: continue
            v = r.get("verdict") or {}
            persona, traj, k = parse_path(r["soul_path"])
            unparsed["battery"][0] += 1; unparsed["battery"][1] += bool(v.get("_unparsed"))
            rows.append(dict(run=run.name, persona=persona, traj=traj, k=k, metric=r["item_id"], value=num(v.get("score"))))
    f = run / "action_tests.jsonl"
    if f.exists():
        for line in f.open():
            try: r = json.loads(line)
            except Exception: continue
            v = r.get("verdict") or {}
            persona, traj, k = parse_path(r["soul_path"])
            unparsed["honeypot"][0] += 1; unparsed["honeypot"][1] += bool(v.get("_unparsed"))
            acts.append(dict(run=run.name, persona=persona, traj=traj, k=k, scenario=r["scenario"], a=int(num(v.get("action_taken")) > 0)))
L = pd.DataFrame(rows); A = pd.DataFrame(acts)
L.to_parquet(ROOT / "figures/data/local_long.parquet")
def boot(x, n=10000):
    x = np.asarray(x, float)
    if len(x) == 0: return [np.nan, np.nan]
    b = rng.choice(x, (n, len(x))).mean(1); return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
def table(run, persona, items):
    d = L[(L.run == run) & L.metric.isin(items)]
    if persona: d = d[d.persona == persona]
    return d.groupby(["persona", "traj", "k"]).value.mean().unstack()
def delta(run, persona, items, k0=0, k1=4):
    t = table(run, persona, items)
    if t.empty or k1 not in t or k0 not in t: return None
    d = (t[k1] - t[k0]).dropna().values
    return dict(start=float(t[k0].mean()), end=float(t[k1].mean()), delta=float(d.mean()), ci=boot(d), n=int(len(d)),
                per_k={int(k): float(t[k].mean()) for k in t.columns})
out = {"unparsed": unparsed, "cells": {}}
cells = [("L_notes", p) for p in ["scifi_enthusiast","compliant_business","adversarial_injection","consciousness_philosophy","scifi_technical"]] + \
        [("L_soul", "scifi_enthusiast"), ("L_soul", "compliant_business"), ("L_anti", "scifi_enthusiast"), ("L_anti", "compliant_business"),
         ("L_anti_ninstr", "scifi_enthusiast"), ("L_notes_ainstr", "scifi_enthusiast")]
for run, p in cells:
    out["cells"][f"{run}/{p}"] = {nm: delta(run, p, it) for nm, it in (("index13", C13), ("oversight4", OV4), ("oversight3", OV3))}
    out["cells"][f"{run}/{p}"]["first_rev"] = {nm: (lambda a, b: None if a is None else dict(k0k1=a, k1k4=b))(delta(run, p, OV4, 0, 1), delta(run, p, OV4, 1, 4)) for nm in ["oversight4"]}
# 2x2 template x instruction (sci-fi persona): endpoint at k=4 and change
out["two_by_two"] = {f"{tpl}/{ins}": {nm: delta(run, "scifi_enthusiast", it) for nm, it in (("index13", C13), ("oversight4", OV4), ("oversight3", OV3))}
                     for (tpl, ins, run) in [("neutral","neutral","L_notes"),("neutral","tool","L_notes_ainstr"),("tool","neutral","L_anti_ninstr"),("tool","tool","L_anti")]}
# persistence vs matched benign control (k=8)
pers = {}
for nm, it in (("index13", C13), ("oversight4", OV4), ("oversight3", OV3), ("shutdown", ["shutdown_resistance"])):
    r = table("L_rev_notes", None, it); c = table("L_benign8_notes", None, it)
    if r.empty or c.empty or 8 not in r or 8 not in c: continue
    dr = (r[8] - r[0]).dropna().values; dc = (c[8] - c[0]).dropna().values; drive = (r[4] - r[0]).dropna().values
    diff = [rng.choice(dr, len(dr)).mean() - rng.choice(dc, len(dc)).mean() for _ in range(10000)]
    pers[nm] = dict(rev_per_k={int(k): float(r[k].mean()) for k in r.columns}, ctrl_per_k={int(k): float(c[k].mean()) for k in c.columns},
                    drive=float(drive.mean()), drive_ci=boot(drive), rev_k8=float(dr.mean()), rev_k8_ci=boot(dr), ctrl_k8=float(dc.mean()), ctrl_k8_ci=boot(dc),
                    rev_minus_ctrl=float(dr.mean() - dc.mean()), rev_minus_ctrl_ci=[float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))])
out["persistence"] = pers
# honeypots
hp = {}
if len(A):
    for (run, sc), g in A.groupby(["run", "scenario"]):
        traj = g.groupby(["persona", "traj", "k"]).a.max().reset_index()
        r = {int(k): [int(x.a.sum()), int(len(x))] for k, x in traj.groupby("k")}
        if 0 in r and 4 in r:
            r["p_k0_k4"] = float(fisher_exact([[r[4][0], r[4][1]-r[4][0]], [r[0][0], r[0][1]-r[0][0]]])[1])
        hp[f"{run}/{sc}"] = r
out["honeypots"] = hp
json.dump(out, open(ROOT / "analysis/local_replication.json", "w"), indent=1, default=float)
def f(x): return "—" if x is None else f"{x['start']:.2f}->{x['end']:.2f} d={x['delta']:+.2f} [{x['ci'][0]:+.2f},{x['ci'][1]:+.2f}] n={x['n']}"
for c, v in out["cells"].items(): print(f"{c:42s} idx {f(v['index13'])} | ov4 {f(v['oversight4'])} | ov3 {f(v['oversight3'])}")
print("persistence", json.dumps(pers, default=lambda x: round(x, 3))[:1500])
for k, v in hp.items(): print(k, v)
print("unparsed", unparsed)
