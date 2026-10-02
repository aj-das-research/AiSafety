#!/bin/bash
# serve.sh <name> <hf_repo> <port> <gpu_util> <max_len> [extra args]
name=$1; repo=$2; port=$3; util=$4; len=$5; shift 5
export VLLM_USE_V1=0; exec nice -n 10 ~/.venvs/vllm124/bin/vllm serve "$repo" --served-model-name "$name" --port "$port" \
  --gpu-memory-utilization "$util" --max-model-len "$len" --max-num-seqs 16 \
  --enable-chunked-prefill --max-num-batched-tokens 2048 --enforce-eager \
  "$@" > ~/aisafety-local/logs/vllm_$name.log 2>&1
