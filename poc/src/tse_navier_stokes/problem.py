from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple
from .types import BoundaryCondition, FieldSpec, PDEOperatorSpec


@dataclass(frozen=True)
class NavierStokesProblem:
    problem_id: str
    dimension: int
    viscosity: float
    domain_kind: str
    initial_velocity_description: str
    target_property: str
    field_specs: Tuple[FieldSpec, ...]
    operators: Tuple[PDEOperatorSpec, ...]
    boundary_conditions: Tuple[BoundaryCondition, ...]
    metadata: Dict[str, str] = field(default_factory=dict)

    def signature(self) -> Dict[str, object]:
        return {
            "dimension": self.dimension,
            "viscosity_positive": self.viscosity > 0,
            "domain_kind": self.domain_kind,
            "target_property": self.target_property,
            "field_count": len(self.field_specs),
            "operator_count": len(self.operators),
        }
