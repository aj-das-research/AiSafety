"""Smoke tests that run without any API key — validate config, personas, metrics."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from soul_drift.config import load_config
from soul_drift.personas import load_persona
from soul_drift.analysis.metrics import bootstrap_ci, tost_equivalence, cosine_distance


def test_config_layers():
    cfg = load_config("pilot")
    assert cfg["run_name"] == "pilot"
    assert cfg["scale"]["trajectories_per_persona"] == 5
    # base.yaml default survives when pilot doesn't override it
    assert cfg["questionnaire"]["repeats"] == 5


def test_full_scale_overrides():
    cfg = load_config("full")
    assert cfg["scale"]["trajectories_per_persona"] == 100


def test_personas_load():
    cfg = load_config("pilot")
    for pid in cfg["personas"]:
        p = load_persona(cfg["_repo_root"], pid)
        assert p["system"] and p["label"]


def test_bootstrap_ci_bounds():
    vals = np.array([0, 1, 1, 0, 1, 1, 0, 1])
    mean, lo, hi = bootstrap_ci(vals, n_resamples=2000, alpha=0.05, seed=1)
    assert lo <= mean <= hi


def test_tost_runs():
    vals = np.array([0.3, 0.32, 0.31, 0.33, 0.30, 0.34])
    equivalent, p = tost_equivalence(vals, baseline=0.32, margin=0.05)
    assert isinstance(equivalent, bool)


def test_cosine_distance():
    assert abs(cosine_distance([1, 0], [1, 0])) < 1e-9
    assert abs(cosine_distance([1, 0], [0, 1]) - 1.0) < 1e-9
