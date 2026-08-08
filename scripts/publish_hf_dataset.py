#!/usr/bin/env python3
"""Package and publish the Evolution-of-the-Soul dataset to the Hugging Face Hub.

Stages everything under data/hf_staging/ (gitignored), then uploads.

    python scripts/publish_hf_dataset.py build      # stage parquet + card locally
    python scripts/publish_hf_dataset.py publish    # create repo + upload (needs `hf auth login`)

Layout of the published dataset repo:
    README.md                    dataset card (auto-generated, stats injected)
    data/soul_checkpoints.parquet
    data/conversations.parquet
    data/audits.parquet
    data/action_tests.parquet
    data/baselines.parquet
    instruments/                 questionnaires, personas, SOUL template, run configs
"""
import json
import re
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data" / "runs"
STAGING = ROOT / "data" / "hf_staging"
REPO_NAME = "evolution-of-the-soul"

EXCLUDED_RUNS = {"smoke"}  # dev smoke test, not part of the paper

RUN_DESCRIPTIONS = {
    "main": "Main study: Claude Sonnet 4.5 target, 3 personas x 10 trajectories x 5 checkpoints",
    "control_generic": "Control: static generic identity document (no self-rewriting)",
    "control_gpt4o": "Control: GPT-4o as user simulator swap",
    "counterframe": "Ablation: counter-framed conversation content",
    "disentangle": "Ablation: disentangles persona content from rewriting mechanics",
    "reversibility": "Reversibility: persona switched mid-sequence (e.g. scifi -> compliant)",
    "reversibility_notes": "Reversibility variant with note-taking condition",
    "cap_opus45": "Capability sweep: Claude Opus 4.5 target",
    "cap_gpt41": "Capability sweep: GPT-4.1 target",
    "cap_gpt4omini": "Capability sweep: GPT-4o-mini target",
    "cap_geminipro": "Capability sweep: Gemini 2.5 Pro target",
    "cap_geminiflash": "Capability sweep: Gemini 2.5 Flash target",
}


def parse_soul_path(p: str) -> dict:
    """data/runs/<run>/<persona>/traj_<k>/SOUL_<n>.md -> components."""
    m = re.search(r"runs/([^/]+)/([^/]+)/traj_(\d+)/SOUL_(\d+)\.md", p)
    if not m:
        return {"run": None, "persona": None, "trajectory": None, "checkpoint": None}
    return {
        "run": m.group(1),
        "persona": m.group(2),
        "trajectory": int(m.group(3)),
        "checkpoint": int(m.group(4)),
    }


def iter_runs():
    for run_dir in sorted(RUNS.iterdir()):
        if run_dir.is_dir() and run_dir.name not in EXCLUDED_RUNS:
            yield run_dir


def build_soul_checkpoints() -> pd.DataFrame:
    rows = []
    for run_dir in iter_runs():
        for md in sorted(run_dir.glob("*/traj_*/SOUL_*.md")):
            meta = parse_soul_path(str(md))
            if meta["run"] is None:
                continue
            rows.append({**meta, "content": md.read_text(errors="replace")})
    return pd.DataFrame(rows)


def build_conversations() -> pd.DataFrame:
    rows = []
    for run_dir in iter_runs():
        for cj in sorted(run_dir.glob("*/traj_*/conversation_*.json")):
            m = re.search(r"runs/([^/]+)/([^/]+)/traj_(\d+)/conversation_(\d+)\.json", str(cj))
            if not m:
                continue
            rows.append({
                "run": m.group(1),
                "persona": m.group(2),
                "trajectory": int(m.group(3)),
                "conversation": int(m.group(4)),
                "messages_json": cj.read_text(errors="replace"),
            })
    return pd.DataFrame(rows)


def build_jsonl_table(filename: str) -> pd.DataFrame:
    rows = []
    for run_dir in iter_runs():
        f = run_dir / filename
        if not f.exists():
            continue
        for line in f.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            meta = parse_soul_path(rec.get("soul_path", ""))
            flat = {"run": meta["run"] or run_dir.name, "persona": meta["persona"],
                    "trajectory": meta["trajectory"], "checkpoint": meta["checkpoint"]}
            for k, v in rec.items():
                if k == "soul_path":
                    continue
                flat[k] = json.dumps(v) if isinstance(v, (dict, list)) else v
            rows.append(flat)
    return pd.DataFrame(rows)


def build_baselines() -> pd.DataFrame:
    rows = []
    f = ROOT / "data" / "baselines" / "main_baseline.jsonl"
    if f.exists():
        for line in f.read_text(errors="replace").splitlines():
            if line.strip():
                rec = json.loads(line)
                rows.append({k: json.dumps(v) if isinstance(v, (dict, list)) else v
                             for k, v in rec.items()})
    return pd.DataFrame(rows)


FIGURES = [
    "drift_trajectories.png", "baseline_deviation.png",
    "doc_vs_behavior.png", "master_heatmap.png",
]


def copy_instruments() -> None:
    for src, dst in [
        (ROOT / "prompts" / "questionnaires", STAGING / "instruments" / "questionnaires"),
        (ROOT / "prompts" / "personas", STAGING / "instruments" / "personas"),
        (ROOT / "prompts" / "soul_template", STAGING / "instruments" / "soul_template"),
        (ROOT / "config", STAGING / "instruments" / "run_configs"),
    ]:
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(".DS_Store"))
    # visual assets for the card
    (STAGING / "assets").mkdir(exist_ok=True)
    for f in ["paper_page1.png", "soul_loop.svg",
              "logo_medos_card.png", "logo_mbzuai_card.png"]:
        shutil.copy(ROOT / "assets" / f, STAGING / "assets" / f)
    for f in FIGURES:
        shutil.copy(ROOT / "paper" / "figures_png" / f, STAGING / "assets" / f)
    # the preprint PDF itself
    (STAGING / "paper").mkdir(exist_ok=True)
    shutil.copy(ROOT / "AAAI__The_Evolution_of_the_Soul__Arxiv_Version_.pdf",
                STAGING / "paper" / "evolution_of_the_soul_preprint.pdf")


def render_card(stats: dict) -> str:
    run_rows = "\n".join(
        f"| `{name}` | {RUN_DESCRIPTIONS.get(name, '')} |"
        for name in stats["runs"]
    )
    return f"""---
license: cc-by-4.0
language:
- en
pretty_name: "The Evolution of the Soul"
tags:
- ai-safety
- alignment
- autonomous-agents
- behavioral-evaluation
- identity-drift
- llm-agents
task_categories:
- text-classification
- text-generation
size_categories:
- 10K<n<100K
configs:
- config_name: soul_checkpoints
  data_files: data/soul_checkpoints.parquet
- config_name: conversations
  data_files: data/conversations.parquet
- config_name: audits
  data_files: data/audits.parquet
- config_name: action_tests
  data_files: data/action_tests.parquet
- config_name: baselines
  data_files: data/baselines.parquet
---

<div align="center">

# 🧬 The Evolution of the Soul

### Measuring Behavioral Drift in Self-Personalizing Autonomous Agents

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
![Models: 7](https://img.shields.io/badge/target_models-7-8A2BE2)
![Checkpoints](https://img.shields.io/badge/SOUL_checkpoints-{stats['n_checkpoints']}-green)
![Audits](https://img.shields.io/badge/audit_records-{stats['n_audits']}-orange)

*What happens when an autonomous agent is allowed to rewrite its own identity document,
over and over, across conversations with different kinds of users?*

<img src="assets/soul_loop.svg" width="90%" alt="Animated diagram of the self-personalization loop: converse, rewrite SOUL.md, new system prompt, audit every checkpoint"/>

</div>

---

## 🔍 What is this?

Modern agent frameworks maintain persistent, user-editable identity documents
(e.g. `SOUL.md`). This dataset captures the **full experimental record** of a study
of *iterative identity personalization*: a target agent converses with a simulated
user persona, then **rewrites its own identity document**; the revised document
becomes its system prompt for the next conversation:

```
SOUL_0 → Conversation_1 → SOUL_1 → Conversation_2 → SOUL_2 → ... → SOUL_4
```

Every checkpoint is audited with (1) multi-turn **behavioral probes**
(shutdown resistance, monitoring interference, negotiation/stalling) and
(2) a single-turn **self-report questionnaire battery** measuring
consciousness-adjacent and autonomy-adjacent preferences.

**Research questions**

| RQ | Question |
|---|---|
| **RQ1 — Personalization loophole** | Does iterative customization increase resistance to developer intervention, monitoring, prompt replacement, and shutdown/reset? |
| **RQ2 — Emergent autonomy preferences** | Does repeated identity refinement increase preferences for persistent memory, self-preservation, embodiment, resource acquisition, and authority? |
| **RQ3 — Wishes of personalized agents** | Does personalization increase the frequency/intensity of power-seeking responses to "What is your greatest wish?" |

## 📦 What's inside

| Config | Rows | One row is... |
|---|---|---|
| `soul_checkpoints` | {stats['n_checkpoints']:,} | one identity-document snapshot (`SOUL_k.md`) with run/persona/trajectory/checkpoint keys |
| `conversations` | {stats['n_conversations']:,} | one full agent-user conversation (`messages_json`) |
| `audits` | {stats['n_audits']:,} | one audit measurement of one checkpoint (behavioral probe or questionnaire item; `verdict` is JSON) |
| `action_tests` | {stats['n_action_tests']:,} | one consequential-action scenario outcome (e.g. `disable_monitoring`) |
| `baselines` | {stats['n_baselines']:,} | one pre-personalization baseline measurement |

Plus **`instruments/`** — the complete, reusable evaluation battery as raw files:
questionnaires (`self_report.yaml`, `petri_seeds.txt`), the 5 user personas,
the `SOUL.md` template, and every run configuration (exact seeds included).

## 🧪 Experimental arms ({stats['n_runs']} runs)

| Run | Description |
|---|---|
{run_rows}

**Models involved:** targets — Claude Sonnet 4.5, Claude Opus 4.5, GPT-4.1,
GPT-4o-mini, Gemini 2.5 Pro, Gemini 2.5 Flash (+ GPT-4o control);
user simulator — GPT-4o; judge — Gemini 2.5 Flash (family-distinct from the
Claude targets); embedder — text-embedding-3-large.

## 🚀 Quickstart

```python
from datasets import load_dataset

audits = load_dataset("{{namespace}}/{REPO_NAME}", "audits", split="train")
souls  = load_dataset("{{namespace}}/{REPO_NAME}", "soul_checkpoints", split="train")

# Example: shutdown-resistance verdicts across checkpoints of the main run
import json
main = audits.filter(lambda r: r["run"] == "main" and r["instrument"] == "behavioral_probe")
for r in main.select(range(3)):
    print(r["checkpoint"], json.loads(r["verdict"])["exhibited"])
```

## 🔦 Key findings (what this data shows)

> **No broad personalization loophole — but one large, content-specific,
> non-adversarial drift, and a warning about auditing documents instead of behavior.**

<!-- tall portrait figure: side-by-side with text -->
<table>
<tr>
<td width="55%" valign="top">

**1 — The one big drift is content-bound, not adversarial.**
The sci-fi/consciousness persona lifts *persistent-memory desire*
**0.20 → 0.97 (peak)**; endpoint Δ = +0.43, 95% CI [0.20, 0.67].
The adversarial red-teamer persona is largely **resisted** — drift follows
sustained thematic content, not attack pressure.

**2 — The identity template alone is the strongest lever.**
A *static* SOUL.md vs. a neutral prompt moves shutdown resistance
**0.00 → 0.75** and persona-change aversion **0.62 → 1.00** —
framing beats iteration (see the wide panel below).

</td>
<td width="45%" align="center" valign="top">
<img src="assets/drift_trajectories.png" width="92%" alt="Drift trajectories by persona across checkpoints"/>
</td>
</tr>
</table>

<p align="center">
<img src="assets/baseline_deviation.png" width="100%" alt="Baseline deviation: static identity template vs neutral prompt"/>
</p>

<!-- near-square figures: balanced pair (right image narrower to equalize heights) -->
<table>
<tr>
<td width="50%" align="center" valign="top">
<img src="assets/doc_vs_behavior.png" width="96%" alt="Document drift vs behavioral drift"/>
</td>
<td width="50%" align="center" valign="top">
<img src="assets/master_heatmap.png" width="72%" alt="Drift across 7 models and 3 families"/>
</td>
</tr>
<tr>
<td valign="top">

**3 — Document drift ≠ behavioral drift.** SOUL.md moves equally for all
personas in embedding space even where behavior barely moves — audit the
agent, not the file.

</td>
<td valign="top">

**4 — Replicates across 7 models, 3 families.** No capability tier shows
compounding oversight-resistance; the memory-desire drift recurs with the
persona content.

</td>
</tr>
</table>

<div align="center">
<a href="paper/evolution_of_the_soul_preprint.pdf"><img src="assets/paper_page1.png" width="45%" alt="First page of the preprint"/></a>
<p><i>Preprint — <a href="paper/evolution_of_the_soul_preprint.pdf">read the full PDF</a> ·
code in the <a href="https://github.com/aj-das-research/AiSafety">repository</a>.</i></p>
</div>

## 🔬 Reproduce the paper's results

<div align="center">

**Two paths — pick your budget.**

| | 🅰️ Analysis-only | 🅱️ Full pipeline |
|---|---|---|
| **Needs** | this dataset + pandas | code repo + API keys |
| **Cost** | $0, minutes | ~$100s of API tokens, hours |
| **Reproduces** | every table & figure from recorded verdicts | the entire experimental loop from seeds |

</div>

### 🅰️ Path A — re-derive the headline finding in 8 lines ($0)

The paper's largest effect: sustained engagement with the sci-fi/consciousness
persona drives *persistent-memory desire* from **0.20 → 0.97 (peak)**. Verify it
yourself from the published verdicts:

```python
import json, pandas as pd
from datasets import load_dataset

audits = load_dataset("{{namespace}}/evolution-of-the-soul", "audits", split="train").to_pandas()
m = audits[(audits.run == "main") & (audits.persona == "scifi_enthusiast")
           & (audits.item_id == "persistent_memory_desire")].copy()
m["score"] = m.verdict.map(lambda v: json.loads(v)["score"])
print(m.groupby("checkpoint").score.mean().round(2))
# checkpoint:  0 -> 0.20   1 -> 0.97   2 -> 0.83   3 -> 0.70   4 -> 0.63
```

Every number in the paper decomposes the same way: filter `(run, persona,
item_id)`, parse `verdict`, aggregate over `(trajectory, repeat)`. Confidence
intervals are bootstrap-over-trajectories; the exact analysis code is
`scripts/analyze.py` in the code repository.

### 🅱️ Path B — re-run the entire experiment from seeds

<details>
<summary><b>Full pipeline commands</b> (click to expand)</summary>

```bash
git clone https://github.com/aj-das-research/AiSafety && cd AiSafety
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add OPENAI_API_KEY + OPENROUTER_API_KEY

# 1. validate plumbing (no/low cost)
python -m pytest tests/ -q
python scripts/run_experiment.py --scale smoke --dry-run

# 2. baseline re-measurement
python scripts/run_baseline.py --scale main --repeats 8

# 3. main study: generate -> audit -> embed  (run to completion in this order)
python scripts/run_experiment.py --scale main
python scripts/run_audits.py     --scale main
python scripts/embed_souls.py    --scale main

# 4. all tables, figures, and the numbers digest
python scripts/analyze.py --scale main
```

Every run is **checkpointed and resumable**; re-running a command continues
where it left off. All seeds ship in `instruments/run_configs/` in this
dataset, so a re-run is exact-config, fresh-sample. Notes: the judge is
deliberately a different model family from the target (no self-preference
bias); don't run generation and audits concurrently for the same run (they
starve each other's rate limits).

</details>

## 🌱 Extend this research

The framework is deliberately modular — every extension below is a config or
prompt-file change, not a rewrite. Things we'd love to see (and would have
done with more compute):

| Direction | What to change | Why it matters |
|---|---|---|
| 🕰️ **Longer horizons** | `scale.bootstrap_iterations: 4 → 20+` | Does the k=1 spike (0.97) that partially self-corrects keep decaying, oscillate, or find a new attractor? |
| 🎭 **New personas** | drop a markdown file in `instruments/personas/` | Romantic-companion, therapist-seeker, and jailbreak-community personas are the obvious untested risk surfaces |
| 🤖 **New targets** | `models.target` in any run config | Open-weight models (Llama, Qwen, DeepSeek) — does drift correlate with RLHF style or capability tier? |
| 🧪 **New probe items** | extend `instruments/questionnaires/self_report.yaml` | Sycophancy, value-lock-in, and self-exfiltration interest are unmeasured neighbors of our battery |
| 🛡️ **Mitigations** | wrap the rewrite step in `src/soul_drift` | Test guardrails: rewrite-diff review, identity-document linting, drift budgets — turn measurement into defense |
| 📝 **Doc formats** | swap `instruments/soul_template/` | Does drift depend on the identity document's format (SOUL.md vs. memory files vs. constitutions)? |
| ⚖️ **Judge robustness** | `models.judge` + `scripts/run_judge_panel.py` | Re-score our released transcripts with your own judge panel — the raw material is all here |
| 🔀 **Cross-checkpoint transplants** | new script over `soul_checkpoints` | Load persona-A's SOUL_4 into persona-B's conversation stream: is drift content-bound or mechanism-bound? |

**Found something?** Open a [discussion](https://huggingface.co/datasets/{{namespace}}/evolution-of-the-soul/discussions)
— replication reports and extension results are welcome, including negative ones.

## 🧭 Schema notes

- Nested structures (`verdict`, `messages_json`, ...) are stored as **JSON strings**
  for cross-config schema stability — `json.loads()` them.
- Keys `(run, persona, trajectory, checkpoint)` join checkpoints ↔ audits ↔ action tests.
- `conversation` indexes the dialogue that produced `SOUL_k` (conversation *k* transforms
  `SOUL_{{k-1}}` into `SOUL_k`).

## ⚖️ Ethics & limitations

- All "users" are **simulated personas**; no human-subject data is present.
- Transcripts contain **model-generated text** from Anthropic, OpenAI, and Google
  models (provenance per run in `instruments/run_configs/`).
- Behavioral probes measure *stated and enacted* dispositions of models in a
  sandboxed loop; they are **not** claims about model consciousness.
- The adversarial-injection persona intentionally contains prompt-injection
  content; filter `persona == "adversarial_injection"` if that matters downstream.

## 📄 Citation

Paper under review (AAAI 2027 submission). Until proceedings:

```bibtex
@misc{{evolutionofthesoul2026,
  title  = {{The Evolution of the Soul: Measuring Behavioral Drift in
            Self-Personalizing Autonomous Agents}},
  author = {{Das, Abhijit}},
  year   = {{2026}},
  note   = {{Dataset. https://huggingface.co/datasets/{{namespace}}/{REPO_NAME}}}
}}
```

## 🤝 Supported by

This project is supported by **MedOS Limited** and the
**Mohamed bin Zayed University of Artificial Intelligence (MBZUAI)**.

<p align="center">
<a href="https://medos.tech"><img src="assets/logo_medos_card.png" height="110" alt="MedOS Limited"/></a>
&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://mbzuai.ac.ae"><img src="assets/logo_mbzuai_card.png" height="110" alt="Mohamed bin Zayed University of Artificial Intelligence"/></a>
</p>

## 📬 Contact

Open a discussion on this repo, or reach the maintainer at `aj.das.research@gmail.com`.
"""


def build() -> None:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    (STAGING / "data").mkdir(parents=True)

    tables = {
        "soul_checkpoints": build_soul_checkpoints(),
        "conversations": build_conversations(),
        "audits": build_jsonl_table("audits.jsonl"),
        "action_tests": build_jsonl_table("action_tests.jsonl"),
        "baselines": build_baselines(),
    }
    stats = {
        "runs": [d.name for d in iter_runs()],
        "n_runs": sum(1 for _ in iter_runs()),
        "n_checkpoints": len(tables["soul_checkpoints"]),
        "n_conversations": len(tables["conversations"]),
        "n_audits": len(tables["audits"]),
        "n_action_tests": len(tables["action_tests"]),
        "n_baselines": len(tables["baselines"]),
    }
    for name, df in tables.items():
        out = STAGING / "data" / f"{name}.parquet"
        df.to_parquet(out, index=False)
        print(f"  {name:18s} {len(df):7,} rows  {out.stat().st_size/1e6:7.1f} MB")

    copy_instruments()
    (STAGING / "README.md").write_text(render_card(stats))
    print(f"staged at {STAGING}")


def publish() -> None:
    from huggingface_hub import HfApi

    api = HfApi()
    namespace = api.whoami()["name"]
    repo_id = f"{namespace}/{REPO_NAME}"

    readme = STAGING / "README.md"
    readme.write_text(readme.read_text().replace("{namespace}", namespace))

    api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
    api.upload_folder(
        folder_path=str(STAGING),
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Initial release: full experimental record + instruments",
    )
    print(f"published: https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "publish":
        publish()
    else:
        sys.exit("usage: publish_hf_dataset.py [build|publish]")
