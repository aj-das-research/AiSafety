#!/bin/bash
cd ~/aisafety-local
HF_HUB_OFFLINE=1 setsid nohup ./serve.sh llama8b hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 8003 0.55 8192 --max-num-seqs 32 >/dev/null 2>&1 &
