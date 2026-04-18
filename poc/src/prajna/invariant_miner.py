"""Invariant miner used by the Prajna abstraction layer.

We mine three simple classes of invariants in this PoC: degree, parity,
and coefficient sign pattern. A production system would plug in richer
symbolic pipelines; the PoC keeps the logic short so that the test
cases can be followed by hand.
"""

from __future__ import annotations

from typing import Sequence

import sympy as sp


class InvariantMiner:
    def mine(self, raw_problem: str, symbols: Sequence[sp.Symbol]) -> list:
        expr = sp.sympify(raw_problem, locals={str(s): s for s in symbols})
        invariants = []
        for s in symbols:
            try:
                invariants.append(("degree", str(s), int(sp.degree(expr, s))))
            except sp.PolynomialError:
                invariants.append(("degree", str(s), -1))
        coeffs = expr.as_coefficients_dict()
        parity = sum(1 for v in coeffs.values() if int(v) % 2 == 0)
        invariants.append(("even_coeff_count", parity))
        sign_pattern = tuple(int(sp.sign(v)) for v in coeffs.values())
        invariants.append(("sign_pattern", sign_pattern))
        return invariants
