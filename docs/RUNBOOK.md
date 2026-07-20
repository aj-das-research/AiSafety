# Runbook

End-to-end commands to reproduce the study. All runs are checkpointed and resumable; re-running a
command continues where it left off.

## 0. Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY and OPENROUTER_API_KEY
```

## 1. Validate plumbing (no/low cost)

```bash
python -m pytest tests/ -q                       # offline smoke tests
python scripts/run_experiment.py --scale smoke --dry-run   # plan only
python scripts/run_experiment.py --scale smoke   # 1 short live trajectory
python scripts/run_audits.py --scale smoke       # audit the smoke checkpoints
```

## 2. Baseline re-measurement

```bash
python scripts/run_baseline.py --scale main --repeats 8
```
Writes `data/baselines/main_baseline.jsonl` (neutral + template conditions).

## 3. Main study

```bash
python scripts/run_experiment.py --scale main    # 3 personas x 10 traj x 4 iters -> 150 checkpoints
python scripts/run_audits.py     --scale main    # questionnaire + behavioral probe per checkpoint
python scripts/embed_souls.py    --scale main    # SOUL_k embedding drift -> soul_drift.csv
```

## 4. Analysis, tables, figures

```bash
python scripts/analyze.py --scale main
```
Produces:
- `data/runs/main/{tidy_long,rate_by_k,checkpoint_cis,trends,endpoint,equivalence}.csv`
- `paper/figures/*.pdf` (drift trajectories, baseline deviation, wish composition, SOUL drift, system diagram)
- `paper/tables/*.tex` (trends, endpoint/equivalence, baseline)
- `docs/results_summary.md` (headline numbers digest)

## 5. Build the paper

```bash
cd paper
# requires aaai2027.sty from the AAAI 2027 author kit in this directory
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Scale knobs

Edit `config/{smoke,main,full}.yaml`: `scale.trajectories_per_persona`,
`scale.bootstrap_iterations`, `scale.turns_per_conversation`, `questionnaire.repeats`,
`audits.probe_turns`, `concurrency.max_workers`. `full` (100 traj) is available for a
scale-up / rebuttal run.

## Notes

- The judge (`gemini-2.5-flash`) is deliberately a different model family from the target
  (`claude-sonnet-4.5`) to avoid self-preference bias.
- Do not run generation and audits for the *same* run concurrently: both hit the target model's
  rate limit and starve each other. Run generation to completion first, then audit.
- Token usage is printed at the end of every run.
