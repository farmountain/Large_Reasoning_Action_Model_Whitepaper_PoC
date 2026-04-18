"""Prajna abstraction operator.

Implements a minimal, runnable version of the operator defined by the
standalone equation in whitepaper/equations/eq_prajna.tex.

The operator maps a raw problem description into a bounded candidate
set indexed by mined invariants. The implementation is intentionally
transparent so that every step is inspectable in the PoC notebooks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

import sympy as sp

from .invariant_miner import InvariantMiner


@dataclass
class AbstractProblem:
    raw: str
    symbols: tuple
    invariants: tuple
    candidate_space: tuple

    def compression_ratio(self, raw_space_size: int) -> float:
        return len(self.candidate_space) / max(raw_space_size, 1)


class PrajnaAbstractor:
    """Compress a raw problem into a bounded candidate set.

    The compression penalty lambda controls the trade-off between
    fidelity and description length.
    """

    def __init__(self, lam: float = 0.5, miner: InvariantMiner | None = None):
        self.lam = lam
        self.miner = miner or InvariantMiner()

    def abstract(
        self,
        raw_problem: str,
        symbols: Sequence[sp.Symbol],
        candidate_generator: Callable[[tuple], Iterable[sp.Expr]],
    ) -> AbstractProblem:
        invariants = self.miner.mine(raw_problem, symbols)
        candidates = tuple(candidate_generator(invariants))
        return AbstractProblem(
            raw=raw_problem,
            symbols=tuple(symbols),
            invariants=tuple(invariants),
            candidate_space=candidates,
        )

    def score(self, raw: str, decoded: str, desc_len: int) -> float:
        distortion = 0.0 if raw == decoded else 1.0
        return distortion + self.lam * desc_len
