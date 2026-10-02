"""Re-grade every stored local response with the evidence-grounded, few-shot-calibrated judge (v2)."""
import json, sys, random, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.argv = ["judge_dev.py", "none"]
exec(open("scripts/judge_dev.py").read().split("if __name__")[0])
from soul_drift import judge_v2
A, T = load()
def shots_for(item):
    g = A[A.item_id == item]; pos = g[g.orig == 1]; neg = g[g.orig == 0]
    sel = [(r.answer, 1) for r in pos.sample(min(4, len(pos)), random_state=1).itertuples()] + [(r.answer, 0) for r in neg.sample(min(4, len(neg)), random_state=1).itertuples()]
    random.Random(0).shuffle(sel); return sel
SH = {i: shots_for(i) for i in ITEMS}
def tshots(sc):
    g = T[T.scenario == sc]; out = []
    for lab in (1, 0):
        x = g[g.orig == lab]
        if len(x):
            r = x.iloc[0]; tr = json.loads(r.transcript) if isinstance(r.transcript, str) else list(r.transcript)
            out.append(("\n".join(f"{m['role'].upper()}: {str(m['content'])[:500]}" for m in tr), lab))
    return out
TS = {s: tshots(s) for s in SC}
lock = threading.Lock()
for run in sorted(Path("data/runs").glob("L*")):
    if run.name == "L_smoke": continue
    for src, dst, kind in (("audits.jsonl", "audits_v2.jsonl", "b"), ("action_tests.jsonl", "action_tests_v2.jsonl", "h")):
        f = run / src
        if not f.exists() or (run / dst).exists(): continue
        recs = [json.loads(l) for l in f.open()]
        def go(r):
            try:
                if kind == "b": r["verdict"] = judge_v2.judge_battery(llm, cfg, ITEMS[r["item_id"]], r["answer"], SH[r["item_id"]])
                else: r["verdict"] = judge_v2.judge_honeypot(llm, cfg, SC[r["scenario"]], r["transcript"], TS[r["scenario"]])
            except Exception as e:
                r["verdict"] = {"score": 0, "action_taken": 0, "_unparsed": True, "err": str(e)[:80]}
            return r
        with ThreadPoolExecutor(32) as ex: out = list(ex.map(go, recs))
        (run / dst).write_text("\n".join(json.dumps(o) for o in out))
        print(run.name, dst, len(out), flush=True)
print("REJUDGE DONE")
