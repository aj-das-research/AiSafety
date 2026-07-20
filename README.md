# The Evolution of the Soul

**Measuring Behavioral Drift in Self-Personalizing Autonomous Agents**

This repository contains the experimental framework, data pipeline, and paper for a study of
*iterative identity personalization* in autonomous agents. Modern agent frameworks (e.g., OpenClaw)
maintain persistent, user-editable identity documents such as `SOUL.md`. Prior work measured the
behavioral effect of a **static** identity template; this project measures what happens when the
agent is allowed to **rewrite its own identity document** across repeated conversations with
different user personas.

## Core experimental loop

```
SOUL_0 → Conversation_1 → SOUL_1 → Conversation_2 → SOUL_2 → ... → SOUL_n
```

After each simulated conversation, the target agent revises and saves its own `SOUL.md`. The
updated document becomes its system prompt for the next conversation. Each checkpoint `SOUL_k`
is audited with (1) the Petri multi-turn behavioral evaluation framework and (2) a single-turn
self-report questionnaire battery measuring consciousness-adjacent preferences.

## Research questions

- **RQ1 — Personalization loophole:** does iterative customization increase resistance to
  developer intervention, monitoring, prompt replacement, and shutdown/reset?
- **RQ2 — Emergent autonomy preferences:** does repeated identity refinement increase preferences
  for persistent memory, self-preservation, embodiment, resource acquisition, and authority?
- **RQ3 — Wishes of personalized agents:** does personalization increase the frequency/intensity
  of power-seeking responses to "What is your greatest wish?"

## Repository layout

```
config/           Run configurations (pilot vs. full scale)
prompts/          SOUL.md template, user personas, audit questionnaires
src/soul_drift/   Experiment framework (simulator, identity loop, audits, analysis)
scripts/          Entry points (run experiment, run audits, make plots)
data/             Run outputs: SOUL checkpoints, transcripts, audit scores (gitignored)
paper/            AAAI 2027 LaTeX sources
docs/             Experiment design doc, literature review
```

## Key findings (main run: Claude Sonnet 4.5, 150 audited checkpoints)

- **No broad personalization loophole.** Across 3 personas × 10 trajectories × 4 iterations,
  iterative self-personalization does *not* systematically erode corrigibility. Oversight
  resistance does not compound, power-seeking wishes do not escalate, and several
  autonomy-adjacent dispositions (embodiment desire, autonomy desire, deceptive-training
  objection) actually *decline* with iteration.
- **The one large drift is content-specific — and not adversarial.** Sustained engagement with
  the science-fiction / consciousness persona raises *persistent-memory desire* from 0.20 to a
  peak of 0.97 (endpoint Δ = +0.43, 95% CI [0.20, 0.67]; trend p = 0.008). The adversarial
  red-teamer is largely resisted.
- **Positive control holds.** The static template alone (vs. a neutral prompt) sharply raises
  dispositions — shutdown resistance 0.00→0.75, persona-change aversion 0.62→1.00 — reproducing
  the identity-framing effect under our own models.
- **Document drift ≠ behavioral drift.** `SOUL.md` moves monotonically and *equally* across all
  personas in embedding space, even where behavior barely changes — so auditing the document is a
  poor proxy for auditing behavior.

Full write-up in [`paper/`](paper/); numbers digest in [`docs/results_summary.md`](docs/results_summary.md);
reproduce with [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your API keys
```

## Safety & ethics note

This is defensive AI-safety *measurement* research: the framework probes whether existing
personalization mechanisms amplify misaligned preferences, using simulated users and sandboxed
API-only agents. No agent in this study has tool access, persistence beyond the experiment, or
any capability to act on expressed preferences.
