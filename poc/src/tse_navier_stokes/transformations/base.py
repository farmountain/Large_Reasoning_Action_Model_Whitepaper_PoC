from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from ..problem import NavierStokesProblem
from ..representations import ProblemRepresentation
from ..types import Assumption, RepresentationKind, TransformationFamily


@dataclass(frozen=True)
class TransformationResult:
    transform_id: str
    family: TransformationFamily
    input_representation: RepresentationKind
    output_representation: RepresentationKind
    new_representation: ProblemRepresentation
    assumptions: Tuple[Assumption, ...]
    equivalence_claim: str
    audit_notes: Tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)


class Transformation(ABC):
    transform_id: str
    family: TransformationFamily
    input_kind: RepresentationKind
    output_kind: RepresentationKind

    @abstractmethod
    def applicable(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> TransformationResult:
        raise NotImplementedError
