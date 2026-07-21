#!/bin/bash
set -u
cd "$(dirname "$0")/.."
wait_for(){ while pgrep -f "$1" >/dev/null; do sleep 15; done; }
echo "[orch3 $(date +%H:%M:%S)] audit reversibility"
python3 -u scripts/run_audits.py --scale reversibility > data/runs/audit_reversibility.log 2>&1
echo "[orch3 $(date +%H:%M:%S)] audit disentangle"
python3 -u scripts/run_audits.py --scale disentangle > data/runs/audit_disentangle.log 2>&1
echo "[orch3 $(date +%H:%M:%S)] embeddings"
python3 -u scripts/embed_souls.py --scale reversibility > data/runs/embed_reversibility.log 2>&1
python3 -u scripts/embed_souls.py --scale disentangle > data/runs/embed_disentangle.log 2>&1
echo "[orch3 $(date +%H:%M:%S)] DONE"
