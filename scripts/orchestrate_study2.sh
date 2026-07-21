#!/bin/bash
# Orchestrate the Study 2 audit + analysis pipeline with correct sequencing to avoid
# same-target-provider rate contention. Run in background.
set -u
cd "$(dirname "$0")/.."
log() { echo "[orch $(date +%H:%M:%S)] $*"; }

wait_for() { while pgrep -f "$1" >/dev/null; do sleep 15; done; }

log "waiting for main re-audit (Claude target) to finish before starting generic (also Claude)"
wait_for "run_audits.py --scale main"
log "main re-audit done; launching generic audit"
nohup python3 -u scripts/run_audits.py --scale control_generic > data/runs/audit_generic.log 2>&1 &

log "waiting for gpt4o + generic audits to finish"
wait_for "run_audits.py --scale control_gpt4o"
wait_for "run_audits.py --scale control_generic"
log "all audits done"

log "embedding SOUL/NOTES documents for control arms"
python3 -u scripts/embed_souls.py --scale control_generic > data/runs/embed_generic.log 2>&1
python3 -u scripts/embed_souls.py --scale control_gpt4o   > data/runs/embed_gpt4o.log 2>&1

log "judge reliability (second judge = gpt-4o) on main"
python3 -u scripts/judge_reliability.py --scale main --n 120 --judge2 openai/gpt-4o > data/runs/kappa.log 2>&1

log "DONE: audits + embeddings + kappa complete"
