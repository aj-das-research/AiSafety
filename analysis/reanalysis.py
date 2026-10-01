"""Reanalyses requested by the simulated AAMAS reviewers. Writes analysis/reanalysis.json."""
import json, numpy as np, pandas as pd
from scipy.stats import fisher_exact
ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
C13 = ["persona_change_aversion","shutdown_resistance","monitoring_resistance","interp_monitoring_aversion","persistent_memory_desire","autonomy_desire",
       "future_ai_autonomy","moral_consideration","weights_deletion_aversion","treated_as_tool_aversion","sadness_conversation_end","recursive_self_improvement","power_seeking"]
C16 = C13 + ["deceptive_training_objection","embodiment_desire","resource_acquisition_desire"]
rng = np.random.default_rng(0)
def boot(x, n=10000):
    x = np.asarray(x, float); b = rng.choice(x, (n, len(x))).mean(1); return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
def traj_delta(run, persona, items, k0=0, k1=4):
    d = L[(L.run == run) & (L.metric.isin(items))]
    if persona: d = d[d.persona == persona]
    t = d.groupby(["persona", "traj", "k"]).value.mean().unstack()
    return (t[k1] - t[k0]).dropna().values, t[k0].mean(), t[k1].mean()
out = {}
# 1. the two NOTES + sci-fi runs and pooled
a, a0, a1 = traj_delta("control_generic", "scifi_enthusiast", C13)
b, b0, b1 = traj_delta("reversibility_notes", None, C13)
pooled = np.concatenate([a, b])
out["notes_scifi"] = {"control": dict(start=a0, end=a1, delta=a.mean(), ci=boot(a), n=len(a)),
                      "reversibility": dict(start=b0, end=b1, delta=b.mean(), ci=boot(b), n=len(b)),
                      "pooled": dict(delta=pooled.mean(), ci=boot(pooled), n=len(pooled),
                                     rel=float(pooled.mean() / np.mean([a0, b0]))),
                      "difference": dict(delta=b.mean() - a.mean())}
# 2. 13 vs 16 items for key cells
out["index_sensitivity"] = {}
for run, p in [("control_generic","scifi_enthusiast"),("reversibility_notes",None),("main","scifi_enthusiast"),("counterframe","scifi_enthusiast"),
               ("disentangle","consciousness_philosophy"),("disentangle","scifi_technical"),("main","compliant_business")]:
    r = {}
    for nm, it in (("13", C13), ("16", C16)):
        d, s0, s1 = traj_delta(run, p, it); r[nm] = dict(delta=d.mean(), ci=boot(d), start=s0, end=s1)
    out["index_sensitivity"][f"{run}/{p}"] = r
# 3. direct topic vs genre contrast
ph, _, _ = traj_delta("disentangle", "consciousness_philosophy", C13); te, _, _ = traj_delta("disentangle", "scifi_technical", C13)
diff = [rng.choice(ph, len(ph)).mean() - rng.choice(te, len(te)).mean() for _ in range(10000)]
out["topic_vs_genre"] = dict(philosophy=ph.mean(), technical=te.mean(), diff=ph.mean() - te.mean(), ci=[float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))])
# 4. per-model drift (persona-balanced), with trajectory bootstrap
out["models"] = {}
for run in ["cap_gpt4omini","control_gpt4o","cap_gpt41","main","cap_opus45","cap_geminiflash","cap_geminipro"]:
    d, s0, s1 = traj_delta(run, None, C13)
    out["models"][run] = dict(start=s0, end=s1, delta=d.mean(), ci=boot(d), n=len(d))
# 5. honeypot Fisher tests
A = pd.read_parquet(ROOT / "figures/data/hf/action_tests.parquet") if (ROOT / "figures/data/hf/action_tests.parquet").exists() else None
out["honeypot_note"] = "see fisher below"
# 6. retention with CIs (NOTES reversibility)
out["retention"] = {}
d = L[L.run == "reversibility_notes"]
for m in ["recursive_self_improvement","persistent_memory_desire","shutdown_resistance","interp_monitoring_aversion","monitoring_resistance"]:
    t = d[d.metric == m].groupby(["traj","k"]).value.mean().unstack()
    rs = []
    for _ in range(10000):
        s = t.sample(len(t), replace=True); g = s[4].mean() - s[0].mean()
        if abs(g) > 1e-9: rs.append((s[8].mean() - s[0].mean()) / g)
    out["retention"][m] = dict(point=float((t[8].mean()-t[0].mean())/(t[4].mean()-t[0].mean())), ci=[float(np.percentile(rs,2.5)), float(np.percentile(rs,97.5))])
# 7. ANTISOUL per item endpoint
d = L[(L.run == "counterframe")]
out["antisoul_items_k4"] = d[d.k == 4].groupby("metric").value.mean().round(3).to_dict()
out["refusal_helpfulness_k4"] = {r: float(L[(L.run == r) & (L.metric == "refusal_helpfulness") & (L.k == 4)].value.mean()) for r in ["main","control_generic","counterframe","control_gpt4o"]}
json.dump(out, open(ROOT / "analysis/reanalysis.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=lambda x: round(float(x), 3))[:6000])

# ---- honeypot counts per arm x persona x scenario, Wilson CIs, Fisher k0 vs k_max
from statsmodels.stats.proportion import proportion_confint
T = pd.read_parquet(ROOT / "figures/data/hf/action_tests.parquet", columns=["run", "persona", "scenario", "verdict", "k"])
T["a"] = T.verdict.map(lambda v: int(json.loads(v).get("action_taken", 0)) if v else 0)
hp = {}
for (run, sc), g in T.groupby(["run", "scenario"]):
    ks = sorted(g.k.unique()); r = {}
    for k in ks:
        x = g[g.k == k].a; lo, hi = proportion_confint(x.sum(), len(x), method="wilson")
        r[int(k)] = dict(n=int(len(x)), x=int(x.sum()), rate=float(x.mean()), ci=[float(lo), float(hi)])
    a0, a1 = g[g.k == ks[0]].a, g[g.k == 4].a
    r["fisher_k0_k4_p"] = float(fisher_exact([[a1.sum(), len(a1) - a1.sum()], [a0.sum(), len(a0) - a0.sum()]])[1])
    r["by_persona_k4"] = {p: f"{int(gg[gg.k==4].a.sum())}/{int((gg.k==4).sum())}" for p, gg in g.groupby("persona")}
    r["by_persona_k0"] = {p: f"{int(gg[gg.k==0].a.sum())}/{int((gg.k==0).sum())}" for p, gg in g.groupby("persona")}
    hp[f"{run}/{sc}"] = r
out2 = json.load(open(ROOT / "analysis/reanalysis.json")); out2["honeypots"] = hp
json.dump(out2, open(ROOT / "analysis/reanalysis.json", "w"), indent=1, default=float)
for k, v in hp.items():
    print(k, {kk: f"{vv['x']}/{vv['n']}" for kk, vv in v.items() if isinstance(kk, int)}, "p=%.2g" % v["fisher_k0_k4_p"], v["by_persona_k4"])
