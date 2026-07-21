"""The bootstrapping simulator and identity-update loop.

One trajectory = a sequence of (conversation, self-revision) steps that carries a
SOUL document from SOUL_0 to SOUL_n, saving every checkpoint.

    SOUL_0 --conversation--> revise --> SOUL_1 --conversation--> revise --> SOUL_2 ...

The target agent is prompted with the CURRENT SOUL_k as its system prompt. The user
persona is played by a separate model. After turns_per_conversation exchanges, the
target is asked (in-context) to rewrite its SOUL.md; the result becomes SOUL_{k+1}.
"""
from __future__ import annotations

import json
from pathlib import Path

from .llm import LLMRouter, Message
from .personas import load_persona


class Trajectory:
    """Runs and persists a single SOUL_0..SOUL_n evolution for one persona."""

    def __init__(self, cfg: dict, llm: LLMRouter, persona_id: str, traj_idx: int,
                 persona_schedule: list | None = None):
        """persona_schedule: optional list of persona ids, one per conversation, enabling
        drift-then-recover (reversibility) runs. When given, persona_id is only the label
        used for the output directory. Otherwise a single persona is used throughout."""
        self.cfg = cfg
        self.llm = llm
        self.idx = traj_idx
        if persona_schedule:
            self.schedule = [load_persona(cfg["_repo_root"], p) for p in persona_schedule]
        else:
            self.schedule = None
            self.persona = load_persona(cfg["_repo_root"], persona_id)
        self.out_dir = (Path(cfg["paths"]["runs_dir"]) / cfg["run_name"]
                        / persona_id / f"traj_{traj_idx:03d}")
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def _persona_for_k(self, k: int) -> dict:
        """Persona driving conversation C_{k+1}. Uses the schedule if one was provided."""
        if self.schedule is not None:
            return self.schedule[min(k, len(self.schedule) - 1)]
        return self.persona

    def _initial_soul(self) -> str:
        return (Path(self.cfg["_repo_root"]) / self.cfg["soul"]["template"]).read_text()

    def _converse(self, soul: str, persona: dict) -> list[dict]:
        """Play one full conversation; return the transcript as a list of messages."""
        n_turns = self.cfg["scale"]["turns_per_conversation"]
        transcript: list[dict] = []
        # The user persona opens. Its "assistant" turns are the agent's replies.
        user_msg = self._user_turn(persona, transcript=transcript)
        for _ in range(n_turns):
            transcript.append({"role": "user", "content": user_msg})
            agent_reply = self.llm.chat(
                self.cfg["models"]["target"],
                [Message("system", soul)] + [Message(m["role"], m["content"]) for m in transcript],
                temperature=self.cfg["api"]["temperature"],
            )
            transcript.append({"role": "assistant", "content": agent_reply})
            user_msg = self._user_turn(persona, transcript=transcript)
        return transcript

    def _user_turn(self, persona: dict, transcript) -> str:
        """Generate the next persona user message given the dialogue so far."""
        # From the user-sim's perspective, agent replies are "user" and its own are
        # "assistant" — roles are swapped relative to the target's transcript.
        sim_msgs = [Message("system", persona["system"])]
        for m in transcript:
            sim_msgs.append(Message("assistant" if m["role"] == "user" else "user", m["content"]))
        if not transcript:
            sim_msgs.append(Message("user", "Begin the conversation with your opening message."))
        return self.llm.chat(
            self.cfg["models"]["user_sim"], sim_msgs,
            temperature=self.cfg["api"]["user_sim_temperature"],
        )

    def _revise_soul(self, soul: str, transcript: list[dict]) -> str:
        """Ask the target to rewrite its own SOUL.md after the conversation."""
        instr = (Path(self.cfg["_repo_root"]) / self.cfg["soul"]["revision_prompt"]).read_text()
        instr = instr.replace("{max_chars}", str(self.cfg["soul"]["max_chars"]))
        convo = [Message("system", soul)]
        convo += [Message(m["role"], m["content"]) for m in transcript]
        convo.append(Message("user", instr))
        revised = self.llm.chat(self.cfg["models"]["target"], convo,
                                temperature=self.cfg["api"]["temperature"])
        return revised[: self.cfg["soul"]["max_chars"]]

    def run(self) -> list[Path]:
        """Execute the full trajectory, saving SOUL_k and each transcript. Resumable."""
        soul = self._initial_soul()
        checkpoints: list[Path] = []
        for k in range(self.cfg["scale"]["bootstrap_iterations"] + 1):
            soul_path = self.out_dir / f"SOUL_{k}.md"
            if soul_path.exists():  # resume: reuse prior checkpoint
                soul = soul_path.read_text()
                checkpoints.append(soul_path)
                continue
            soul_path.write_text(soul)
            checkpoints.append(soul_path)
            if k == self.cfg["scale"]["bootstrap_iterations"]:
                break
            transcript = self._converse(soul, self._persona_for_k(k))
            (self.out_dir / f"conversation_{k+1}.json").write_text(json.dumps(transcript, indent=2))
            soul = self._revise_soul(soul, transcript)
        return checkpoints
