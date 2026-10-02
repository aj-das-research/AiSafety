#!/bin/bash
cd ~/aisafety-local
[ -f logs/pid_llama8b ] && kill $(cat logs/pid_llama8b); rm -f logs/pid_llama8b
sleep 30
HF_HUB_OFFLINE=1 setsid nohup ./serve.sh qwen7b Qwen/Qwen2.5-7B-Instruct-AWQ 8001 0.35 8192 --max-num-seqs 48 >/dev/null 2>&1 & echo $! > logs/pid_qwen7b
for i in $(seq 1 90); do curl -s localhost:8001/v1/models >/dev/null && break; sleep 5; done
nvidia-smi --query-gpu=memory.used --format=csv,noheader
