"""Smoke tests for the LRAM PoC.

These tests run in a few seconds without any external services
(no Lean, no Qiskit required, no GPU). They guarantee the pipeline
executes end-to-end and that every module imports cleanly.
"""

from __future__ import annotations

import math

import numpy as np
import sympy as sp

from poc.src.grover.amplifier import GroverAmplifier
from poc.src.grover.oracle import BoundedOracle
from poc.src.prajna.abstraction import PrajnaAbstractor
from poc.src.teacher_student.distill import DistillationTrainer, Teacher
from poc.src.teacher_student.reflexion import ReflexionLoop, ReflexionMemory
from poc.src.tier3.causal_checker import CausalChecker, CausalQuery
from poc.src.tier3.circuit_probe import CircuitProbe
from poc.src.tier3.validator import Tier3Validator
from poc.src.world_model.distill_world import Transition, WorldModelDistiller
from poc.src.world_model.do_attention import DoAttention


def test_prajna_compresses():
    x, y = sp.symbols("x y")
    ab = PrajnaAbstractor()
    out = ab.abstract("x**2 + 2*x*y + y**2", [x, y], lambda inv: (("sq", inv),))
    assert len(out.candidate_space) == 1
    assert out.invariants


def test_oracle_counts_queries():
    o = BoundedOracle(lambda c: c == "good")
    r = o.evaluate(["good", "bad", "good"])
    assert r.accepted == ["good", "good"]
    assert r.query_count == 3


def test_grover_theoretical_matches_pi_over_4_sqrt():
    assert GroverAmplifier.theoretical_iterations(64, 1) == math.floor((math.pi / 4) * 8)


def test_grover_classical_finds_winner():
    amp = GroverAmplifier(oracle=lambda c: c == "win", backend="classical")
    g = amp.amplify(["a", "win", "b", "c"])
    assert g.winner == "win"
    assert g.backend == "classical"


def test_tier3_all_pass():
    v = Tier3Validator(
        formal=lambda c: True,
        causal=lambda c: True,
        circuit=lambda c: True,
    )
    r = v.validate("anything")
    assert r.accepted


def test_tier3_failure_records_reason():
    v = Tier3Validator(
        formal=lambda c: False,
        causal=lambda c: True,
        circuit=lambda c: True,
    )
    r = v.validate("anything")
    assert not r.accepted
    assert "formal_check_failed" in r.reasons


def test_causal_backdoor_default():
    assert CausalChecker(use_dowhy=False).is_identifiable(
        CausalQuery(treatment="t", outcome="y", confounders=("z",))
    )


def test_circuit_probe_perfect_correlation():
    s = CircuitProbe().score([1, 2, 3], [1, 2, 3])
    assert s.faithful
    assert abs(s.kendall_tau - 1.0) < 1e-9


def test_distillation_step_reduces_loss():
    teachers = [
        Teacher("a", lambda s: np.array([0.6, 0.2, 0.2])),
        Teacher("b", lambda s: np.array([0.2, 0.6, 0.2])),
    ]
    t = DistillationTrainer(teachers=teachers, n_actions=3, lr=0.1)
    losses = [t.step(np.array([0.0, 0.0, 0.0]), np.array([0.33, 0.33, 0.34]))["total"] for _ in range(20)]
    assert losses[-1] <= losses[0]


def test_reflexion_adds_memory_on_failure():
    m = ReflexionMemory()
    loop = ReflexionLoop(
        validator=lambda c: False,
        reflect_fn=lambda t, c: "bad candidate",
        memory=m,
    )
    loop.step({}, "x")
    assert len(m) == 1


def test_do_attention_runs():
    Q = np.eye(2)
    K = np.eye(2)
    V = np.array([[1.0, 0.0], [0.0, 1.0]])
    out = DoAttention(d_k=2)(Q, K, V, do_x=np.array([1.0, 0.0]))
    assert out.shape == (2, 2)


def test_world_model_fits():
    rng = np.random.default_rng(0)
    data = []
    for _ in range(50):
        s = rng.standard_normal(3)
        a = rng.standard_normal(2)
        s2 = s + 0.1 * a[:3] if len(a) >= 3 else s
        data.append(Transition(state=s, action=a, reward=float(np.sum(s)), next_state=s2))
    wm = WorldModelDistiller(state_dim=3, action_dim=2)
    losses = wm.fit(data, epochs=30, lr=0.01)
    assert losses[-1] <= losses[0]


def test_pipeline_runs():
    from poc.src.pipeline import run

    m = run("toy_conjectures", "none")
    assert m["candidate_space_size"] > 0
    assert m["accepted_in_oracle"] >= 0
