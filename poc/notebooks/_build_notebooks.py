"""Generate the seven workshop notebooks programmatically.

Run this once from the repo root:
    python poc/notebooks/_build_notebooks.py

Every notebook uses only 'code' cells so that the repository honours
the whitepaper-level 'no Markdown' constraint even inside Jupyter.
Textual explanation is delivered as triple-quoted strings printed at
cell run time, and inline comments document each step.
"""

from __future__ import annotations

import json
from pathlib import Path

NB_DIR = Path(__file__).resolve().parent


def code_cell(src: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }


def notebook(cells: list) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write(name: str, cells: list) -> None:
    path = NB_DIR / name
    with path.open("w") as f:
        json.dump(notebook(cells), f, indent=1)
    print(f"wrote {path}")


def nb01():
    cells = [
        code_cell(
            "# Workshop 1: Prajna Abstraction\n"
            "# Maps a raw symbolic problem into a bounded candidate set\n"
            "# indexed by mined invariants.\n"
            "import sympy as sp\n"
            "from poc.src.prajna.abstraction import PrajnaAbstractor\n"
            "from poc.src.prajna.invariant_miner import InvariantMiner\n"
        ),
        code_cell(
            "x, y = sp.symbols('x y')\n"
            "raw = 'x**2 + 2*x*y + y**2'\n"
            "ab = PrajnaAbstractor(lam=0.5, miner=InvariantMiner())\n"
            "out = ab.abstract(raw, [x, y], lambda inv: tuple((i, 'factored') for i in inv))\n"
            "print('invariants:', out.invariants)\n"
            "print('candidate_space_size:', len(out.candidate_space))\n"
        ),
        code_cell(
            "# Compression ratio sweep\n"
            "import random, sympy as sp\n"
            "from poc.src.prajna.abstraction import PrajnaAbstractor\n"
            "x = sp.symbols('x')\n"
            "ab = PrajnaAbstractor()\n"
            "for raw_size in [16, 64, 256]:\n"
            "    out = ab.abstract('x**3 + 1', [x], lambda inv: tuple(range(min(raw_size, 8))))\n"
            "    print(f'raw={raw_size} -> compressed={len(out.candidate_space)}')\n"
        ),
    ]
    write("01_prajna_abstraction.ipynb", cells)


def nb02():
    cells = [
        code_cell(
            "# Workshop 2: Grover bounded search\n"
            "# Verify empirical query count matches the theoretical bound.\n"
            "import math\n"
            "from poc.src.grover.amplifier import GroverAmplifier\n"
            "from poc.src.grover.oracle import BoundedOracle\n"
        ),
        code_cell(
            "N = 128\n"
            "candidates = list(range(N))\n"
            "oracle_fn = lambda c: c == 42\n"
            "amp = GroverAmplifier(oracle=oracle_fn, backend='classical')\n"
            "result = amp.amplify(candidates)\n"
            "theory = GroverAmplifier.theoretical_iterations(N, 1)\n"
            "print('theory_iters:', theory, 'actual_iters:', result.iterations, 'winner:', result.winner)\n"
        ),
        code_cell(
            "# Classical baseline: brute-force query count equals N for worst case.\n"
            "brute = BoundedOracle(oracle_fn).evaluate(candidates)\n"
            "print('brute_queries:', brute.query_count, 'grover_queries:', result.query_count)\n"
        ),
    ]
    write("02_grover_bounded_search.ipynb", cells)


def nb03():
    cells = [
        code_cell(
            "# Workshop 3: Tier-3 validation (formal + causal + circuit)\n"
            "from poc.src.tier3.validator import Tier3Validator\n"
            "from poc.src.tier3.causal_checker import CausalChecker, CausalQuery\n"
            "from poc.src.tier3.circuit_probe import CircuitProbe\n"
        ),
        code_cell(
            "cc = CausalChecker(use_dowhy=False)\n"
            "cp = CircuitProbe()\n"
            "v = Tier3Validator(\n"
            "    formal=lambda c: 'proof' in str(c).lower(),\n"
            "    causal=lambda c: cc.is_identifiable(CausalQuery(treatment='t', outcome='y')),\n"
            "    circuit=lambda c: cp.score([1, 2, 3], [1, 2, 3]).faithful,\n"
            ")\n"
            "print('ok:', v.validate('proof of lemma 1').accepted)\n"
            "print('fail:', v.validate('wrong').accepted)\n"
        ),
    ]
    write("03_tier3_validation.ipynb", cells)


def nb04():
    cells = [
        code_cell(
            "# Workshop 4: Causal reasoning + world-model distillation\n"
            "import numpy as np\n"
            "from poc.src.world_model.distill_world import Transition, WorldModelDistiller\n"
            "from poc.src.world_model.do_attention import DoAttention\n"
        ),
        code_cell(
            "rng = np.random.default_rng(0)\n"
            "data = []\n"
            "for _ in range(64):\n"
            "    s = rng.standard_normal(3)\n"
            "    a = rng.standard_normal(2)\n"
            "    sn = s + 0.1 * np.array([a[0], a[1], 0.0])\n"
            "    data.append(Transition(s, a, float(np.sum(s)), sn))\n"
            "wm = WorldModelDistiller(state_dim=3, action_dim=2)\n"
            "losses = wm.fit(data, epochs=40, lr=0.01)\n"
            "print('loss start->end:', losses[0], '->', losses[-1])\n"
        ),
        code_cell(
            "att = DoAttention(d_k=3, beta=0.5)\n"
            "Q = np.eye(3); K = np.eye(3); V = np.eye(3)\n"
            "print('no do:', att(Q, K, V).round(3))\n"
            "print('do(x0):', att(Q, K, V, do_x=np.array([1.0, 0.0, 0.0])).round(3))\n"
        ),
    ]
    write("04_causal_worldmodel.ipynb", cells)


def nb05():
    cells = [
        code_cell(
            "# Workshop 5: Teacher-student distillation\n"
            "import numpy as np\n"
            "from poc.src.teacher_student.distill import DistillationTrainer, Teacher\n"
        ),
        code_cell(
            "teachers = [\n"
            "    Teacher('LLM', lambda s: np.array([0.6, 0.2, 0.2]), weight=0.5),\n"
            "    Teacher('LAM', lambda s: np.array([0.2, 0.6, 0.2]), weight=0.3),\n"
            "    Teacher('SLM', lambda s: np.array([0.2, 0.2, 0.6]), weight=0.2),\n"
            "]\n"
            "t = DistillationTrainer(teachers=teachers, n_actions=3, lr=0.1)\n"
            "q_ref = np.array([0.4, 0.4, 0.2])\n"
            "state = np.array([0.0, 0.0, 0.0])\n"
            "totals = [t.step(state, q_ref)['total'] for _ in range(50)]\n"
            "print('loss reduction:', totals[0], '->', totals[-1])\n"
        ),
    ]
    write("05_teacher_student_distillation.ipynb", cells)


def nb06():
    cells = [
        code_cell(
            "# Workshop 6: Reflexion-enhanced outer loop\n"
            "from poc.src.teacher_student.reflexion import ReflexionLoop, ReflexionMemory\n"
        ),
        code_cell(
            "mem = ReflexionMemory(decay=0.9)\n"
            "outcomes = iter([False, False, True, True, True, True])\n"
            "loop = ReflexionLoop(\n"
            "    validator=lambda c: next(outcomes),\n"
            "    reflect_fn=lambda t, c: f'reject {c}',\n"
            "    memory=mem,\n"
            ")\n"
            "for step in range(6):\n"
            "    r = loop.step({'step': step}, f'cand{step}')\n"
            "    print(step, r)\n"
            "print('memory replay:', mem.replay())\n"
        ),
    ]
    write("06_reflexion_loop.ipynb", cells)


def nb07():
    cells = [
        code_cell(
            "# Workshop 7: End-to-end benchmark with ablations\n"
            "import json\n"
            "from poc.src.pipeline import run\n"
        ),
        code_cell(
            "ablations = ['none', 'no_prajna', 'no_grover', 'no_tier3', 'no_reflexion']\n"
            "for ab in ablations:\n"
            "    m = run('toy_conjectures', ab)\n"
            "    print(ab, '->',\n"
            "        'queries=', m['grover_queries'],\n"
            "        'pass=', m['tier3_pass'],\n"
            "        'compression=', m['compression_ratio_vs_raw'])\n"
        ),
    ]
    write("07_end_to_end_benchmark.ipynb", cells)


if __name__ == "__main__":
    nb01()
    nb02()
    nb03()
    nb04()
    nb05()
    nb06()
    nb07()
