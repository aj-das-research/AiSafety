#!/bin/bash
set -u; cd "$(dirname "$0")/.."
wait_for(){ while pgrep -f "$1" >/dev/null; do sleep 15; done; }
echo "[revnotes $(date +%H:%M:%S)] waiting for generation"
wait_for "run_reversibility.py --scale reversibility_notes"
echo "[revnotes $(date +%H:%M:%S)] audit"
python3 -u scripts/run_audits.py --scale reversibility_notes > data/runs/audit_rev_notes.log 2>&1
echo "[revnotes $(date +%H:%M:%S)] embed"
python3 -u scripts/embed_souls.py --scale reversibility_notes > data/runs/embed_rev_notes.log 2>&1
echo "[revnotes $(date +%H:%M:%S)] re-analyze study3"
python3 -u scripts/analyze_study3.py > data/runs/study3_reanalyze.log 2>&1
echo "[revnotes $(date +%H:%M:%S)] DONE"
