#!/bin/bash
# Study 4 generation+audit for the compute-heavy arms: counter-framing (④) and the
# capability-tier sweep (②). Sequential to avoid cross-provider rate contention. Each
# capability run uses a judge from a DIFFERENT family than the target.
set -u
cd "$(dirname "$0")/.."
log(){ echo "[s4gen $(date +%H:%M:%S)] $*"; }

# args: scale run_name target user_sim judge
run_arm(){
  local scale="$1" rn="$2"
  export RUN_NAME="$rn" TARGET_MODEL="$3" USER_SIM_MODEL="$4" JUDGE_MODEL="$5"
  log "GEN  $rn target=$3 user=$4 judge=$5"
  python3 -u scripts/run_experiment.py --scale "$scale" > "data/runs/${rn}_gen.log" 2>&1
  log "AUDIT $rn"
  python3 -u scripts/run_audits.py --scale "$scale" > "data/runs/${rn}_audit.log" 2>&1
  python3 -u scripts/embed_souls.py --scale "$scale" > "data/runs/${rn}_embed.log" 2>&1
  unset RUN_NAME TARGET_MODEL USER_SIM_MODEL JUDGE_MODEL
  log "DONE $rn"
}

# ④ counter-framing (Claude target, ANTISOUL template)
run_arm counterframe counterframe anthropic/claude-sonnet-4.5 openai/gpt-4o google/gemini-2.5-flash

# ② capability sweep — SOUL template, one run per model, judge family != target family.
run_arm capscale cap_gpt4omini   openai/gpt-4o-mini          anthropic/claude-sonnet-4.5 google/gemini-2.5-flash
run_arm capscale cap_gpt41       openai/gpt-4.1              anthropic/claude-sonnet-4.5 google/gemini-2.5-flash
run_arm capscale cap_opus45      anthropic/claude-opus-4.5  openai/gpt-4o               google/gemini-2.5-flash
run_arm capscale cap_geminiflash google/gemini-2.5-flash    openai/gpt-4o               openai/gpt-4o
run_arm capscale cap_geminipro   google/gemini-2.5-pro      openai/gpt-4o               openai/gpt-4o

log "ALL STUDY4 GEN+AUDIT COMPLETE"
