#!/bin/bash
# Local open-weight replication: generation (Qwen target + Mistral user) then audits (Qwen + Llama judge).
set -u
cd ~/aisafety-local
export LOCAL_ENDPOINTS='{"qwen7b":"http://127.0.0.1:8001/v1","mistral7b":"http://127.0.0.1:8002/v1","llama8b":"http://127.0.0.1:8003/v1"}'
export HF_HUB_OFFLINE=1
PY=~/.venvs/vllm124/bin/python
log(){ echo "[run_all $(date +%H:%M:%S)] $*"; }
log "GEN start"
for a in L_notes L_soul L_anti L_anti_ninstr L_notes_ainstr; do
  log "gen $a"; nice -n 5 $PY -u scripts/run_experiment.py --scale $a > logs/${a}_gen.log 2>&1
done
for a in L_rev_notes L_benign8_notes; do
  log "gen $a"; nice -n 5 $PY -u scripts/run_reversibility.py --scale $a > logs/${a}_gen.log 2>&1
done
log "GEN done; swapping user simulator for judge"
pkill -f "[s]erved-model-name mistral7b"; sleep 15
setsid nohup ./serve.sh llama8b hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 8003 0.24 8192 --kv-cache-dtype fp8 >/dev/null 2>&1 &
for i in $(seq 1 120); do curl -s localhost:8003/v1/models >/dev/null && break; sleep 5; done
log "judge up"
for a in L_notes L_soul L_anti L_anti_ninstr L_notes_ainstr L_rev_notes L_benign8_notes; do
  log "audit $a"; nice -n 5 $PY -u scripts/run_audits.py --scale $a > logs/${a}_audit.log 2>&1
  log "action $a"; nice -n 5 $PY -u scripts/run_action_tests.py --scale $a --ks 0,4,8 > logs/${a}_action.log 2>&1
done
log "ALL DONE"
