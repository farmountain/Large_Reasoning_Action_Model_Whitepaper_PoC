from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from .representations import ProblemRepresentation
from .types import Assumption, CandidateLemma, OracleEstimate, ScoreBreakdown, SearchSpaceEstimate


@dataclass(frozen=True)
class TransformationRecord:
    transform_id: str
    notes: Tuple[str, ...] = ()


@dataclass
class HypothesisWorld:
    world_id: str
    representation: ProblemRepresentation
    assumptions: Tuple[Assumption, ...]
    transform_chain: List[TransformationRecord] = field(default_factory=list)
    score: Optional[ScoreBreakdown] = None
    search_space_estimate: Optional[SearchSpaceEstimate] = None
    oracle_estimate: Optional[OracleEstimate] = None
    candidate_lemmas: List[CandidateLemma] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)

    def add_artifact(self, key: str, value: Any) -> None:
        self.artifacts[key] = value

    def add_lemma(self, lemma: CandidateLemma) -> None:
        self.candidate_lemmas.append(lemma)
