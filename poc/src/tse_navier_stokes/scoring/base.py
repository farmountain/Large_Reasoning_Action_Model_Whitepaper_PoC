from __future__ import annotations
from abc import ABC, abstractmethod
from ..worlds import HypothesisWorld
from ..types import ScoreBreakdown


class WorldScorer(ABC):
    """Abstract base class for scoring HypothesisWorld instances."""

    @abstractmethod
    def score(self, world: HypothesisWorld) -> ScoreBreakdown:
        """Compute and return a ScoreBreakdown for the given world."""
        raise NotImplementedError
