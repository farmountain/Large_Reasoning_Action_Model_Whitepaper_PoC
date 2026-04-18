Millennium-Adjacent Benchmarks
===============================

Placeholder for bounded Millennium-adjacent fragments. These are NOT
attacks on the Millennium Prize Problems themselves. They are
restricted numerical or combinatorial surrogates chosen to exercise
the LRAM architecture on harder-than-toy instances.

Planned entries (Stage 2 of the roadmap in
whitepaper/sections/14_roadmap_millennium.tex):

    bounded_zeta_zeros/
        Numerical verification of the first N non-trivial zeta zeros
        lying on the critical line. Oracle: compare against a trusted
        numerical table. Prajna: exploit functional-equation symmetry.

    bounded_sat/
        Random 3-SAT instances at the phase transition. Oracle:
        linear-time DPLL. Prajna: community detection on the variable
        graph.

    restricted_navier_stokes/
        Short-time numerical solutions on a small grid under benign
        initial data. Oracle: comparison with a pseudo-spectral
        reference. Prajna: spectral-basis compression.

Each entry will ship with a deterministic seed, a reference dataset,
and an expected metrics file. These are not included in the initial
PoC; they are scoped for follow-up work.
