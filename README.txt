Large Reasoning and Action Model (LRAM) Whitepaper and Proof-of-Concept
========================================================================

This repository publishes a professional whitepaper and an end-to-end
open-source proof-of-concept for the Large Reasoning and Action Model
(LRAM), a hierarchical architecture for machine-assisted mathematical
discovery and validated action selection.

Top-Level Layout
----------------

  whitepaper/
      LRAM_Whitepaper.tex    Main LaTeX entry point (compile with latexmk).
      sections/              Sixteen chapter .tex files.
      equations/             Ten standalone Word-Equation-Editor-compatible
                             LaTeX equation files, one per equation in the
                             mathematical architecture.
      figures/               ASCII diagrams of the architecture, the three-tier
                             stack, and the Reflexion loop.

  poc/
      src/                   Runnable Python modules operationalising every
                             equation in the whitepaper.
      tests/                 Dependency-light smoke tests.
      notebooks/             Seven code-only workshop notebooks.
      benchmarks/            Toy conjectures and Millennium-adjacent
                             benchmark definitions.
      results/               JSON metrics and LaTeX interpretation produced
                             by the pipeline orchestrator.
      README.txt             PoC-specific quick start.

  README.md                  Original repository stub (kept for historical
                             continuity only).
  README.txt                 Plain-text pointer for readers who prefer the
                             no-markdown artefacts.
  LICENSE                    MIT.

Build the Whitepaper
--------------------

  cd whitepaper
  latexmk -pdf LRAM_Whitepaper.tex

Run the Proof-of-Value Workshop
-------------------------------

  conda env create -f poc/environment.yml
  conda activate lram-poc
  pytest poc/tests -q
  python -m poc.src.pipeline --benchmark toy_conjectures --ablation none
  python -m poc.src.run_ablations

Defensible Thesis
-----------------

Yes, in the weak sense: LRAM is a credible convergence accelerator for
bounded, oracle-friendly mathematics. No, in the strong sense: LRAM is
not a universal solver for open mathematics. Both statements are true
at the same time, and together they define the intellectually honest
home of the programme. See whitepaper/sections/15_conclusion.tex.
