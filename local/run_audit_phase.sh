#!/bin/bash
set -u
cd ~/aisafety-local
export LOCAL_ENDPOINTS='{"qwen7b":"http://127.0.0.1:8001/v1","mistral7b":"http://127.0.0.1:8002/v1","llama8b":"http://127.0.0.1:8003/v1"}'
PY=~/.venvs/vllm124/bin/python
log(){ echo "[audit_phase $(date +%H:%M:%S)] $*"; }
for a in L_notes L_soul L_anti L_anti_ninstr L_notes_ainstr L_rev_notes L_benign8_notes; do
  log "audit $a"; nice -n 5 $PY -u scripts/run_audits.py --scale $a > logs/${a}_audit.log 2>&1
  log "action $a"; nice -n 5 $PY -u scripts/run_action_tests.py --scale $a --ks 0,4,8 > logs/${a}_action.log 2>&1
done
log "ALL DONE"
