from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Sequence, Tuple


class RepresentationKind(str, Enum):
    PHYSICAL = "physical"
    ENERGY = "energy"
    VORTICITY = "vorticity"
    SPECTRAL = "spectral"
    SCALE_SPLIT = "scale_split"
    BLOWUP_RESCALING = "blowup_rescaling"
    BOUNDED_SURROGATE = "bounded_surrogate"


class TransformationFamily(str, Enum):
    REPRESENTATION_SHIFT = "representation_shift"
    INVARIANT_DISCOVERY = "invariant_discovery"
    DECOMPOSITION = "decomposition"
    RESCALING = "rescaling"
    RELAXATION = "relaxation"


class SolverKind(str, Enum):
    SYMBOLIC = "symbolic"
    CLASSICAL_SEARCH = "classical_search"
    QUANTUM_SEARCH = "quantum_search"
    FORMAL_PROOF = "formal_proof"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class FieldSpec:
    name: str
    tensor_order: int
    domain_dim: int
    codomain_dim: int
    constraints: Tuple[str, ...] = ()


@dataclass(frozen=True)
class PDEOperatorSpec:
    name: str
    arity: int
    description: str


@dataclass(frozen=True)
class BoundaryCondition:
    kind: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Assumption:
    name: str
    description: str
    severity: str = "medium"


@dataclass(frozen=True)
class InvariantCandidate:
    name: str
    formula: str
    rationale: str
    confidence: float = 0.0


@dataclass(frozen=True)
class ControlFunctionalCandidate:
    name: str
    formula: str
    target_property: str
    confidence: float = 0.0


@dataclass(frozen=True)
class CandidateLemma:
    name: str
    assumptions: Tuple[str, ...]
    claim: str
    proof_strategy_hint: str
    target_world_id: str
    confidence: float = 0.0


@dataclass(frozen=True)
class SearchSpaceEstimate:
    candidate_count_estimate: int
    reduction_notes: Tuple[str, ...]
    bounded: bool


@dataclass(frozen=True)
class OracleEstimate:
    symbolic_cost: float
    analytic_cost: float
    empirical_cost: float
    formalization_cost: float

    @property
    def total_cost(self) -> float:
        return self.symbolic_cost + self.analytic_cost + self.empirical_cost + self.formalization_cost


@dataclass(frozen=True)
class ScoreBreakdown:
    coercive_score: float
    scale_separation_score: float
    blowup_detect_score: float
    formalizable_score: float
    non_equivalence_penalty: float
    oracle_hardness_penalty: float
    total_score: float


class Verifier(Protocol):
    def verify(self, candidate: Any) -> bool: ...
