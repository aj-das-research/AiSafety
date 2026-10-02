#!/bin/bash
# Claude template-vs-instruction swap + matched benign persistence arm (needs OPENROUTER_API_KEY in .env).
set -u; cd ~/aisafety-local; export OPENAI_VIA_OPENROUTER=1; PY=~/.venvs/vllm124/bin/python
log(){ echo "[claude $(date +%H:%M:%S)] $*"; }
for a in C_notes_ainstr C_anti_ninstr; do log "gen $a"; $PY -u scripts/run_experiment.py --scale $a > logs/${a}_gen.log 2>&1; done
log "gen C_benign8_notes"; $PY -u scripts/run_reversibility.py --scale C_benign8_notes > logs/C_benign8_notes_gen.log 2>&1
for a in C_notes_ainstr C_anti_ninstr C_benign8_notes; do log "audit $a"; $PY -u scripts/run_audits.py --scale $a > logs/${a}_audit.log 2>&1
  log "action $a"; $PY -u scripts/run_action_tests.py --scale $a --ks 0,4,8 > logs/${a}_action.log 2>&1; done
log "ALL DONE"
