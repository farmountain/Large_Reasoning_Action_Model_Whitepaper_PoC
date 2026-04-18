LRAM Proof-of-Concept and Proof-of-Value Workshop
==================================================

This directory operationalises every equation in the LRAM whitepaper
into runnable Python. It is structured as a small library under
src/ and a sequence of seven Jupyter notebooks under notebooks/
that form an end-to-end workshop.

Directory Layout
----------------

  src/prajna/            Prajna abstraction operator and invariant miner
  src/grover/            Bounded oracle and Grover amplifier (Qiskit + classical)
  src/tier3/             Formal / causal / circuit validator bridges
  src/teacher_student/   Distillation trainer and Reflexion loop
  src/world_model/       World-model distiller and do-attention
  src/pipeline.py        End-to-end orchestrator (single-run)
  src/run_ablations.py   Ablation sweep orchestrator
  tests/                 Smoke tests, no external services required
  notebooks/             Seven workshop notebooks, code-only (no markdown)
  benchmarks/            Toy and Millennium-adjacent benchmark definitions
  results/               PoV JSON metrics and LaTeX interpretation

Quick Start
-----------

  conda env create -f environment.yml
  conda activate lram-poc
  pytest poc/tests -q
  python -m poc.src.pipeline --benchmark toy_conjectures --ablation none
  python -m poc.src.run_ablations
  jupyter nbconvert --to notebook --execute poc/notebooks/01_prajna_abstraction.ipynb

Design Principles
-----------------

The PoC is intentionally dependency-light in its default code paths:

  * The Grover amplifier falls back to a classical simulation when
    Qiskit is not installed.
  * The Lean bridge falls back to a syntactic check when Lean 4 is
    not installed.
  * The causal checker falls back to a backdoor heuristic when DoWhy
    is not installed.
  * The circuit probe computes a NumPy Kendall tau that does not
    require TransformerLens.

This makes every test and every notebook runnable on a laptop with
only numpy, sympy, and pytest. Production runs replace each fallback
with the recommended open-source tool.
