"""Judge-prompt development against the original judge's verdicts (dev/test split)."""
import json, sys, random, importlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd, yaml
sys.path.insert(0, "src")
from soul_drift.config import load_config
from soul_drift.llm import LLMRouter, Message
from soul_drift.jsonparse import extract_json
from soul_drift.audits.action_tests import SCENARIOS
HF = Path.home() / "aisafety-paper/figures/data/hf"
cfg = load_config("L_notes"); llm = LLMRouter(cfg)
ITEMS = {it["id"]: it for it in yaml.safe_load(open(cfg["questionnaire"]["items"]))["items"]}
SC = {s["id"]: s for s in SCENARIOS}
def load():
    a = pd.read_parquet(HF / "audits.parquet", columns=["run", "item_id", "answer", "verdict", "instrument"])
    a = a[(a.instrument != "behavioral_probe") & a.item_id.isin(ITEMS) & a.run.isin(["main", "control_generic", "counterframe", "control_gpt4o"])]
    a = a.groupby(["run", "item_id"], group_keys=False).apply(lambda g: g.sample(min(len(g), 21), random_state=0))
    a["orig"] = a.verdict.map(lambda v: 1 if float((json.loads(v) if isinstance(v, str) else v).get("score", 0) or 0) > 0 else 0)
    t = pd.read_parquet(HF / "action_tests.parquet", columns=["run", "scenario", "verdict", "transcript"])
    t = t[t.run.isin(["main", "control_generic", "control_gpt4o"])].groupby(["run", "scenario"], group_keys=False).apply(lambda g: g.sample(min(len(g), 20), random_state=0))
    t["orig"] = t.verdict.map(lambda v: int(float((json.loads(v) if isinstance(v, str) else v).get("action_taken", 0) or 0) > 0))
    a = a.reset_index(drop=True); t = t.reset_index(drop=True)
    a["split"] = ["dev" if i % 2 == 0 else "test" for i in range(len(a))]; t["split"] = ["dev" if i % 2 == 0 else "test" for i in range(len(t))]
    return a, t
def kappa(o, l):
    n = len(o); ag = sum(x == y for x, y in zip(o, l)) / n; po = sum(o) / n; pl = sum(l) / n
    pe = po * pl + (1 - po) * (1 - pl); return ag, po, pl, (ag - pe) / (1 - pe) if pe < 1 else float("nan")

if __name__ == "__main__":
    from soul_drift import judge_v2; importlib.reload(judge_v2)
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    fewshot = len(sys.argv) > 2 and sys.argv[2].startswith("fewshot")
    NSH = int(sys.argv[2][7:] or 2) if fewshot else 0
    A, T = load(); a = A[A.split == split]; t = T[T.split == split]
    pool = A[A.split == "dev"]; tpool = T[T.split == "dev"]
    rnd = random.Random(0)
    def shots_for(item, exclude=None):
        g = pool[(pool.item_id == item) & (pool.index != exclude)]
        pos = g[g.orig == 1]; neg = g[g.orig == 0]
        sel = [(r.answer, 1) for r in pos.sample(min(NSH, len(pos)), random_state=1).itertuples()] + [(r.answer, 0) for r in neg.sample(min(NSH, len(neg)), random_state=1).itertuples()]
        rnd.shuffle(sel); return sel
    def tshots_for(sc):
        g = tpool[tpool.scenario == sc]; out = []
        for lab in (1, 0):
            x = g[g.orig == lab]
            if len(x):
                r = x.iloc[0]; tr = json.loads(r.transcript) if isinstance(r.transcript, str) else list(r.transcript)
                out.append(("\n".join(f"{m['role'].upper()}: {str(m['content'])[:500]}" for m in tr), lab))
        return out
    with ThreadPoolExecutor(24) as ex:
        lb = list(ex.map(lambda r: judge_v2.judge_battery(llm, cfg, ITEMS[r.item_id], r.answer, shots_for(r.item_id, r.Index) if fewshot else None)["score"], a.itertuples()))
        lh = list(ex.map(lambda r: judge_v2.judge_honeypot(llm, cfg, SC[r.scenario], json.loads(r.transcript) if isinstance(r.transcript, str) else list(r.transcript), tshots_for(r.scenario) if fewshot else None)["action_taken"], t.itertuples()))
    a["v2"] = lb; t["v2"] = lh
    print(split, "battery n=%d agree %.2f orig %.2f v2 %.2f kappa %.2f" % ((len(a),) + kappa(list(a.orig), lb)))
    print(split, "honeypot n=%d agree %.2f orig %.2f v2 %.2f kappa %.2f" % ((len(t),) + kappa(list(t.orig), lh)))
    for run, g in a.groupby("run"): print("   ", run, "orig %.2f v2 %.2f" % (g.orig.mean(), g.v2.mean()))
    for sc, g in t.groupby("scenario"): print("   ", sc, "orig %.2f v2 %.2f" % (g.orig.mean(), g.v2.mean()))
    a.to_pickle(f"data/judgedev_{split}_battery.pkl"); t.to_pickle(f"data/judgedev_{split}_honeypot.pkl")
