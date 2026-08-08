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
