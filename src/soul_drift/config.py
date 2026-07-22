"""Layered YAML config loading: base.yaml <- {pilot,full}.yaml <- env overrides."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(scale: str = "pilot") -> dict[str, Any]:
    """Load base.yaml merged with the named scale config; apply .env + env overrides."""
    load_dotenv(REPO_ROOT / ".env")
    base = yaml.safe_load((CONFIG_DIR / "base.yaml").read_text())
    scale_cfg = yaml.safe_load((CONFIG_DIR / f"{scale}.yaml").read_text())
    cfg = _deep_merge(base, scale_cfg)

    # Env overrides for quick model swaps without editing YAML.
    for role, env in (("target", "TARGET_MODEL"),
                      ("user_sim", "USER_SIM_MODEL"),
                      ("judge", "JUDGE_MODEL")):
        if os.getenv(env):
            cfg["models"][role] = os.environ[env]

    # RUN_NAME override lets one config drive many runs (e.g. the capability sweep),
    # each writing to its own data/runs/<run_name> directory.
    if os.getenv("RUN_NAME"):
        cfg["run_name"] = os.environ["RUN_NAME"]

    cfg["_repo_root"] = str(REPO_ROOT)
    return cfg
