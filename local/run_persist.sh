#!/bin/bash
# Powered persistence test: generation -> audits -> calibrated re-grading. Servers managed by PID files.
set -u
cd ~/aisafety-local
export LOCAL_ENDPOINTS='{"qwen7b":"http://127.0.0.1:8001/v1","mistral7b":"http://127.0.0.1:8002/v1","llama8b":"http://127.0.0.1:8003/v1"}'
export HF_HUB_OFFLINE=1
PY=~/.venvs/vllm124/bin/python
log(){ echo "[persist $(date +%H:%M:%S)] $*"; }
start(){ # name repo port util len extra...
  local n=$1; shift; setsid nohup ./serve.sh $n "$@" >/dev/null 2>&1 & echo $! > logs/pid_$n
  for i in $(seq 1 120); do curl -s localhost:$2/v1/models >/dev/null && break; sleep 5; done; log "up $n ($(nvidia-smi --query-gpu=memory.used --format=csv,noheader))"; }
stop(){ local n=$1; [ -f logs/pid_$n ] && kill $(cat logs/pid_$n) 2>/dev/null; rm -f logs/pid_$n
  for i in $(seq 1 30); do pgrep -f -- "served-model-name $n" >/dev/null || break; sleep 2; done; sleep 20; log "stopped $n"; }
# A. generation
start qwen7b Qwen/Qwen2.5-7B-Instruct-AWQ 8001 0.31 16384
start mistral7b solidrust/Mistral-7B-Instruct-v0.3-AWQ 8002 0.24 16384 --kv-cache-dtype fp8 --chat-template $HOME/aisafety-local/mistral_template.jinja
for a in L2_rev L2_benign8 L2_drive8; do log "gen $a"; nice -n 5 $PY -u scripts/run_reversibility.py --scale $a > logs/${a}_gen.log 2>&1; done
stop mistral7b; stop qwen7b
# B. audits with original judge prompt (raw), then honeypots
start qwen7b Qwen/Qwen2.5-7B-Instruct-AWQ 8001 0.29 8192 --max-num-seqs 48
start llama8b hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 8003 0.27 4096 --max-num-seqs 32
for a in L2_rev L2_benign8 L2_drive8; do
  sed -i 's/max_workers: 12/max_workers: 40/' config/$a.yaml
  log "audit $a"; nice -n 5 $PY -u scripts/run_audits.py --scale $a > logs/${a}_audit.log 2>&1
  log "action $a"; nice -n 5 $PY -u scripts/run_action_tests.py --scale $a --ks 0,4,8 > logs/${a}_action.log 2>&1
done
stop llama8b; stop qwen7b
# C. calibrated re-grading (judge v2)
start llama8b hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 8003 0.55 8192 --max-num-seqs 32
log "rejudge"; $PY -u scripts/rejudge_local.py > logs/rejudge_L2.log 2>&1
log "ALL DONE"
