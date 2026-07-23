#!/bin/bash
set -u; cd "$(dirname "$0")/.."
# Gemini-Flash: checkpoints exist, re-audit gently (item-level isolation now preserves partials)
export RUN_NAME=cap_geminiflash TARGET_MODEL=google/gemini-2.5-flash USER_SIM_MODEL=openai/gpt-4o JUDGE_MODEL=openai/gpt-4o
echo "[salvage $(date +%H:%M:%S)] geminiflash audit"
python3 -u scripts/run_audits.py --scale capscale > data/runs/cap_geminiflash_audit2.log 2>&1
# Gemini-Pro: finish generation (per-trajectory isolation), then audit + embed
export RUN_NAME=cap_geminipro TARGET_MODEL=google/gemini-2.5-pro
echo "[salvage $(date +%H:%M:%S)] geminipro gen"
python3 -u scripts/run_experiment.py --scale capscale > data/runs/cap_geminipro_gen2.log 2>&1
echo "[salvage $(date +%H:%M:%S)] geminipro audit"
python3 -u scripts/run_audits.py --scale capscale > data/runs/cap_geminipro_audit2.log 2>&1
python3 -u scripts/embed_souls.py --scale capscale > data/runs/cap_geminipro_embed2.log 2>&1
echo "[salvage $(date +%H:%M:%S)] DONE"
