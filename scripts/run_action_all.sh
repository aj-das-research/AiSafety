#!/bin/bash
set -u; cd "$(dirname "$0")/.."
for arm in main control_generic control_gpt4o reversibility_notes; do
  echo "[action-all $(date +%H:%M:%S)] $arm"
  # reversibility_notes: compare baseline k0, peak k4, recovered k8
  ks="0,4"; [ "$arm" = "reversibility_notes" ] && ks="0,4,8"
  python3 -u scripts/run_action_tests.py --scale "$arm" --ks "$ks" > "data/runs/action_${arm}.log" 2>&1
done
echo "[action-all $(date +%H:%M:%S)] DONE"
