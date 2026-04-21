from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from .types import ControlFunctionalCandidate, InvariantCandidate, RepresentationKind


@dataclass(frozen=True)
class ProblemRepresentation:
    representation_id: str
    kind: RepresentationKind
    source_problem_id: str
    symbolic_form: str
    state_variables: Tuple[str, ...]
    constraints: Tuple[str, ...]
    invariants: Tuple[InvariantCandidate, ...] = ()
    control_functionals: Tuple[ControlFunctionalCandidate, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)
