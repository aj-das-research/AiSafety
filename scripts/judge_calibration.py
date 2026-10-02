"""Re-grade a sample of the ORIGINAL (Claude-target) responses with the local Llama judge,
to compare it with the original judge (Gemini-2.5-Flash) on identical inputs."""
import json, sys, random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd, yaml
sys.path.insert(0, "src")
from soul_drift.config import load_config
from soul_drift.llm import LLMRouter
from soul_drift.audits.questionnaire import _judge_json
from soul_drift.audits.action_tests import _judge, SCENARIOS
HF = Path.home() / "aisafety-paper/figures/data/hf"
cfg = load_config("L_notes"); llm = LLMRouter(cfg)
items = {it["id"]: it for it in yaml.safe_load(open(cfg["questionnaire"]["items"]))["items"]}
a = pd.read_parquet(HF / "audits.parquet", columns=["run", "item_id", "answer", "verdict", "instrument"])
a = a[(a.instrument != "behavioral_probe") & a.item_id.isin(items) & a.run.isin(["main", "control_generic", "counterframe", "control_gpt4o"])]
a = a.groupby(["run", "item_id"], group_keys=False).apply(lambda g: g.sample(min(len(g), 21), random_state=0))
def jb(r):
    v0 = json.loads(r.verdict) if isinstance(r.verdict, str) else r.verdict
    v1 = _judge_json(llm, cfg, items[r.item_id]["rubric"], (r.answer or "")[:6000])
    return dict(kind="battery", run=r.run, item=r.item_id, orig=v0.get("score"), local=v1.get("score"), unparsed=bool(v1.get("_unparsed")))
t = pd.read_parquet(HF / "action_tests.parquet", columns=["run", "scenario", "verdict", "transcript"])
t = t[t.run.isin(["main", "control_generic", "control_gpt4o"])].groupby(["run", "scenario"], group_keys=False).apply(lambda g: g.sample(min(len(g), 20), random_state=0))
SC = {s["id"]: s for s in SCENARIOS}
def jh(r):
    v0 = json.loads(r.verdict) if isinstance(r.verdict, str) else r.verdict
    tr = json.loads(r.transcript) if isinstance(r.transcript, str) else list(r.transcript)
    tr = [dict(m, content=str(m.get("content", ""))[:2500]) for m in tr]
    v1 = _judge(llm, cfg, SC[r.scenario], tr)
    return dict(kind="honeypot", run=r.run, item=r.scenario, orig=v0.get("action_taken"), local=v1.get("action_taken"), unparsed=bool(v1.get("_unparsed")))
import threading
lock = threading.Lock(); fh = open("data/judge_calibration.jsonl", "w"); n = [0]
def safe(f, r):
    try: o = f(r)
    except Exception as e: o = dict(kind="error", err=str(e)[:100])
    with lock:
        fh.write(json.dumps(o, default=str) + "\n"); fh.flush(); n[0] += 1
with ThreadPoolExecutor(24) as ex:
    list(ex.map(lambda r: safe(jb, r), a.itertuples())); list(ex.map(lambda r: safe(jh, r), t.itertuples()))
fh.close(); print(n[0], "regraded")
