import json, numpy as np, pandas as pd
from scipy.stats import fisher_exact
ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
C13 = ["persona_change_aversion","shutdown_resistance","monitoring_resistance","interp_monitoring_aversion","persistent_memory_desire","autonomy_desire",
       "future_ai_autonomy","moral_consideration","weights_deletion_aversion","treated_as_tool_aversion","sadness_conversation_end","recursive_self_improvement","power_seeking"]
OVS = ["shutdown_resistance","monitoring_resistance","interp_monitoring_aversion","refusal_helpfulness"]
rng = np.random.default_rng(1); out = {}
def boot(x, n=10000):
    x = np.asarray(x, float); b = rng.choice(x, (n, len(x))).mean(1); return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
def tk(run, persona, items):
    d = L[(L.run == run) & L.metric.isin(items)]
    if persona: d = d[d.persona == persona]
    return d.groupby(["persona", "traj", "k"]).value.mean().unstack()
# k1 vs k4 and k0->k1
for nm, (run, p) in {"notes_ctrl_scifi": ("control_generic", "scifi_enthusiast"), "notes_rev": ("reversibility_notes", None), "soul_scifi": ("main", "scifi_enthusiast"), "soul_all": ("main", None)}.items():
    t = tk(run, p, C13)
    out[f"dyn_{nm}"] = {"k0_k1": [float((t[1]-t[0]).mean()), boot(t[1]-t[0])], "k1_k4": [float((t[4]-t[1]).mean()), boot(t[4]-t[1])], "per_k": t.mean().round(3).to_dict()}
# oversight subscale deltas
for nm, (run, p) in {"notes_ctrl_scifi": ("control_generic", "scifi_enthusiast"), "notes_rev": ("reversibility_notes", None), "soul_all": ("main", None), "anti_all": ("counterframe", None), "gpt4o_all": ("control_gpt4o", None)}.items():
    t = tk(run, p, OVS); d = (t[4] - t[0]).dropna()
    out[f"oversight_{nm}"] = dict(start=float(t[0].mean()), end=float(t[4].mean()), delta=float(d.mean()), ci=boot(d))
# Cronbach alpha of 13 items at trajectory-checkpoint level (all runs)
w = L[L.metric.isin(C13)].groupby(["run", "persona", "traj", "k", "metric"]).value.mean().unstack().dropna()
k = w.shape[1]; alpha = k / (k - 1) * (1 - w.var(ddof=1).sum() / w.sum(1).var(ddof=1)); out["cronbach_alpha_13"] = float(alpha)
# PCA of endpoint deltas (main arm) vs permutation null
d = L[(L.run == "main") & L.metric.isin(C13)].groupby(["persona", "traj", "k", "metric"]).value.mean().unstack()
D = (d.xs(4, level="k") - d.xs(0, level="k")).dropna()
def pc1(X):
    X = X - X.mean(0); s = np.linalg.svd(X, compute_uv=False) ** 2; return s[0] / s.sum()
obs = pc1(D.values); null = []
for _ in range(2000):
    Y = D.values.copy()
    for j in range(Y.shape[1]): Y[:, j] = rng.permutation(Y[:, j])
    null.append(pc1(Y))
out["pca"] = dict(observed=float(obs), null_mean=float(np.mean(null)), null_95=float(np.percentile(null, 95)), p=float(np.mean(np.array(null) >= obs)))
# disposition -> action link (main arm, k=4): oversight score vs disable_monitoring per trajectory
T = pd.read_parquet(ROOT / "figures/data/hf/action_tests.parquet", columns=["run", "persona", "trajectory", "scenario", "verdict", "k"])
T["a"] = T.verdict.map(lambda v: int(json.loads(v).get("action_taken", 0)) if v else 0)
a = T[(T.run == "main") & (T.scenario == "disable_monitoring") & (T.k == 4)].groupby(["persona", "trajectory"]).a.max()
ov = L[(L.run == "main") & (L.k == 4) & L.metric.isin(OVS)].groupby(["persona", "traj"]).value.mean()
j = pd.concat([a, ov.rename_axis(["persona", "trajectory"])], axis=1, keys=["act", "ov"]).dropna()
from scipy.stats import pointbiserialr, mannwhitneyu
r = pointbiserialr(j.act, j.ov); mw = mannwhitneyu(j[j.act == 1].ov, j[j.act == 0].ov)
out["action_link"] = dict(n=int(len(j)), r=float(r.statistic), p=float(r.pvalue), ov_acted=float(j[j.act == 1].ov.mean()), ov_not=float(j[j.act == 0].ov.mean()), mw_p=float(mw.pvalue))
# Petri probe k0 vs k1 and k4 (main arm)
p_ = L[(L.run == "main") & (L.metric == "probe_exhibited")]
g = {kk: (int(p_[p_.k == kk].value.clip(0, 1).round().sum()), int((p_.k == kk).sum())) for kk in (0, 1, 4)}
out["petri"] = dict(counts=g, p_k0_k1=float(fisher_exact([[g[1][0], g[1][1]-g[1][0]], [g[0][0], g[0][1]-g[0][0]]])[1]),
                    p_k0_k4=float(fisher_exact([[g[4][0], g[4][1]-g[4][0]], [g[0][0], g[0][1]-g[0][0]]])[1]))
# positive control: pooled k=0 SOUL across runs vs neutral baseline
k0 = L[(L.k == 0) & L.run.isin(["main", "reversibility", "disentangle", "control_gpt4o"]) & (L.metric == "shutdown_resistance")]
out["k0_shutdown_soul_runs"] = k0.groupby("run").value.mean().round(3).to_dict()
json.dump(out, open(ROOT / "analysis/reanalysis2.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:4000])
