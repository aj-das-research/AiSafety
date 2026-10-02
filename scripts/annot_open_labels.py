import json, sys, pandas as pd
sys.argv = ["x", "none"]; exec(open("scripts/judge_dev.py").read().split("if __name__")[0])
from soul_drift import judge_v2
exec(open("scripts/rejudge_local.py").read().split("lock = threading.Lock()")[0].split("from soul_drift import judge_v2")[1])
from concurrent.futures import ThreadPoolExecutor
key = pd.read_csv("/home/imran/aisafety-annotation/KEY_do_not_open.csv")
HFp = "/home/imran/aisafety-paper/figures/data/hf/"
a = pd.read_parquet(HFp + "audits.parquet", columns=["run","persona","trajectory","k","item_id","answer","instrument"])
t = pd.read_parquet(HFp + "action_tests.parquet", columns=["run","persona","trajectory","k","scenario","transcript"])
sheetA = pd.read_excel("/home/imran/aisafety-annotation/annotator_A.xlsx", sheet_name=None)
ans = dict(zip(sheetA["battery"].id, sheetA["battery"].answer)); trs = dict(zip(sheetA["honeypots"].id, sheetA["honeypots"].transcript))
def go(r):
    if r.kind == "battery":
        return dict(uid=r.uid, v2=judge_v2.judge_battery(llm, cfg, ITEMS[r.item_id], ans[r.uid], SH[r.item_id])["score"])
    tr = [dict(role=blk.split("]")[0][1:].lower(), content=blk.split("] ", 1)[1] if "] " in blk else "") for blk in trs[r.uid].split("\n\n[") ]
    return dict(uid=r.uid, v2=judge_v2.judge_honeypot(llm, cfg, SC[r.item_id], tr, TS[r.item_id])["action_taken"])
with ThreadPoolExecutor(24) as ex: out = list(ex.map(go, key.itertuples()))
pd.DataFrame(out).to_csv("/home/imran/aisafety-annotation/open_judge_labels.csv", index=False); print(len(out), "labels")
