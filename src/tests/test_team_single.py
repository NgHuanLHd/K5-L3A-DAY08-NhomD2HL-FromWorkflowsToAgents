from __future__ import annotations

import pytest

import lab8.shapes.single as single_mod
from lab8.db import init_store
from lab8.handoff import WRITE_TOOLS
from lab8.runtime import run_react as real_run_react
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

CASES = ["C-001", "C-002", "C-011", "C-013", "C-014"]


def _spy(monkeypatch):
    """Wrap run_react to record every action decide() returns."""
    log = {"actions": [], "max_steps": None}

    def spy_run_react(conn, budget, *, observation, decide, max_steps=8, worker=False):
        log["max_steps"] = max_steps

        def recording_decide(obs):
            action = decide(obs)
            log["actions"].append(action)
            return action

        return real_run_react(
            conn, budget, observation=observation, decide=recording_decide,
            max_steps=max_steps, worker=worker,
        )

    monkeypatch.setattr(single_mod, "run_react", spy_run_react)
    return log


@pytest.mark.parametrize("claim_id", CASES)
def test_single_decide_never_returns_write_tool(tmp_path, monkeypatch, claim_id):
    log = _spy(monkeypatch)
    store = tmp_path / f"{claim_id}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    SHAPES["single"](claim_id, seed=11, store_path=str(store))
    tools = [a.get("tool") for a in log["actions"] if "tool" in a]
    assert tools, "decide should call at least one read tool"
    assert not set(tools) & set(WRITE_TOOLS)
    assert "issue_refund" not in tools


@pytest.mark.parametrize("claim_id", CASES)
def test_single_stops_within_8_steps(tmp_path, monkeypatch, claim_id):
    log = _spy(monkeypatch)
    store = tmp_path / f"{claim_id}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = SHAPES["single"](claim_id, seed=11, store_path=str(store))
    assert log["max_steps"] == 8
    assert len(log["actions"]) <= 8
    assert "final" in log["actions"][-1]
    assert result.error_reason != "step_cap"
