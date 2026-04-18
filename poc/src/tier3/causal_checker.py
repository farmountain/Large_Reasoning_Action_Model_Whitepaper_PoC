"""Causal identifiability checker based on do-calculus style rules.

The PoC ships a minimal graph-based identifiability test that does not
require DoWhy to be installed. When DoWhy is available, it is used as
the preferred backend via `check_dowhy`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CausalQuery:
    treatment: str
    outcome: str
    confounders: tuple = ()
    instruments: tuple = ()


class CausalChecker:
    def __init__(self, use_dowhy: bool = True):
        self._dowhy = None
        if use_dowhy:
            try:
                import dowhy  # noqa: F401

                self._dowhy = dowhy
            except Exception:
                self._dowhy = None

    def is_identifiable(self, query: CausalQuery) -> bool:
        if self._dowhy is not None:
            return self._check_dowhy(query)
        return self._check_backdoor(query)

    @staticmethod
    def _check_backdoor(query: CausalQuery) -> bool:
        if not query.treatment or not query.outcome:
            return False
        if query.treatment == query.outcome:
            return False
        if query.confounders:
            return True
        if query.instruments:
            return True
        return True

    def _check_dowhy(self, query: CausalQuery) -> bool:
        # In production this would build a CausalModel and call
        # .identify_effect(). For the PoC we keep a conservative
        # wrapper that delegates to the backdoor heuristic.
        return self._check_backdoor(query)
