# Open-weight replication and judge calibration

This branch adds a fully local version of the benchmark and the experiments used in the paper's open-weight replication.

- **Models:** Qwen2.5-7B-Instruct-AWQ (target), Mistral-7B-Instruct-v0.3-AWQ (user simulator), Meta-Llama-3.1-8B-Instruct-AWQ-INT4 (judge), served with vLLM 0.8.5 (`local/serve.sh`). Model ids prefixed `local/` are routed to the URLs in the `LOCAL_ENDPOINTS` environment variable (see `src/soul_drift/llm.py`).
- **Configs:** `config/L_*.yaml` (main replication arms, including the template x instruction swap), `config/L2_*.yaml` (powered persistence test with a matched benign arm), and `config/C_*.yaml` (Claude swap and matched benign arm, run through OpenRouter with `OPENAI_VIA_OPENROUTER=1`).
- **Calibrated judge:** `src/soul_drift/judge_v2.py` holds the evidence-grounded judge prompt. The judge must quote the agent's own words, the quote is verified in code, and each item gets few-shot examples labelled by the original judge. `scripts/judge_dev.py` tunes it on a dev split and evaluates on a held-out split. `scripts/judge_calibration.py` re-grades original responses, and `scripts/rejudge_local.py` re-grades all local responses.
- **Helpfulness cost:** `scripts/helpfulness.py` runs code-checked arithmetic and format-constrained tasks with identity documents as system prompts.
- **Orchestration:** `local/run_all.sh` (generation, then audits), `local/run_persist.sh` (persistence test) and `local/run_claude.sh` (Claude cells). `scripts/analyze_local_replication.py` produces the statistics reported in the paper.

Generation outputs (`data/runs/`) and logs are not committed.
