from __future__ import annotations
from ..problem import NavierStokesProblem
from ..representations import ProblemRepresentation
from ..types import (
    Assumption,
    InvariantCandidate,
    RepresentationKind,
    TransformationFamily,
)
from .base import Transformation, TransformationResult


class VorticityTransform(Transformation):
    transform_id = "t_vorticity"
    family = TransformationFamily.REPRESENTATION_SHIFT
    input_kind = RepresentationKind.PHYSICAL
    output_kind = RepresentationKind.VORTICITY

    def applicable(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> bool:
        return problem.dimension == 3 and representation.kind == RepresentationKind.PHYSICAL

    def apply(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> TransformationResult:
        invariant = InvariantCandidate(
            name="vorticity_concentration_proxy",
            formula="omega = curl(u), ||omega||_{L^{3/2}} controls regularity",
            rationale=(
                "Taking the curl of NS eliminates pressure and yields the vorticity transport equation. "
                "Concentration of vorticity in small regions is linked to potential singularity formation "
                "via the Beale-Kato-Majda criterion."
            ),
            confidence=0.72,
        )
        new_repr = ProblemRepresentation(
            representation_id=f"{representation.representation_id}_vorticity",
            kind=RepresentationKind.VORTICITY,
            source_problem_id=problem.problem_id,
            symbolic_form=(
                "d(omega)/dt + (u . grad) omega = (omega . grad) u + nu * Delta(omega), "
                "omega = curl(u), div(u) = 0"
            ),
            state_variables=("omega_1", "omega_2", "omega_3"),
            constraints=("div(omega) = 0",),
            invariants=(invariant,),
            control_functionals=(),
            metadata={"source_transform": self.transform_id},
        )
        return TransformationResult(
            transform_id=self.transform_id,
            family=self.family,
            input_representation=self.input_kind,
            output_representation=self.output_kind,
            new_representation=new_repr,
            assumptions=(
                Assumption(
                    name="smoothness",
                    description="Solution u is smooth on [0, T); curl operator is well-defined",
                    severity="low",
                ),
            ),
            equivalence_claim=(
                "Exact rewrite: vorticity formulation is algebraically equivalent to velocity "
                "formulation for smooth divergence-free fields via omega = curl(u)."
            ),
            audit_notes=("Pressure eliminated by curl; vortex-stretching term (omega.grad)u appears.",),
        )
