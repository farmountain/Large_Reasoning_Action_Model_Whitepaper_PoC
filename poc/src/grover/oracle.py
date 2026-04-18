"""Bounded oracle for candidate predicates.

Corresponds to the standalone equation in whitepaper/equations/eq_oracle.tex.
The oracle is a Python callable over the bounded candidate set. In
production this can be compiled to a reversible quantum circuit; the
PoC uses a classical callable so that every notebook runs on a laptop
without a simulator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, TypeVar

Candidate = TypeVar("Candidate")


@dataclass
class OracleResult:
    accepted: list
    query_count: int


class BoundedOracle:
    def __init__(self, predicate: Callable[[Candidate], bool]):
        self.predicate = predicate
        self._query_count = 0

    def query(self, c: Candidate) -> bool:
        self._query_count += 1
        return bool(self.predicate(c))

    def evaluate(self, candidates: Sequence[Candidate]) -> OracleResult:
        self._query_count = 0
        accepted = [c for c in candidates if self.query(c)]
        return OracleResult(accepted=accepted, query_count=self._query_count)
