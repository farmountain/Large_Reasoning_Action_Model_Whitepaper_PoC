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


class ScaleSplitTransform(Transformation):
    transform_id = "t_scale_split"
    family = TransformationFamily.DECOMPOSITION
    input_kind = RepresentationKind.SPECTRAL
    output_kind = RepresentationKind.SCALE_SPLIT

    def applicable(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> bool:
        return representation.kind == RepresentationKind.SPECTRAL

    def apply(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> TransformationResult:
        invariant = InvariantCandidate(
            name="scale_interaction_bound",
            formula=(
                "u = u_low + u_high, u_low = P_{<=K(t)} u, u_high = P_{>K(t)} u, "
                "||u_low * grad u_high||_{L^2} <= C * ||u_low||_{L^inf} * ||grad u_high||_{L^2}"
            ),
            rationale=(
                "Splitting into low- and high-frequency parts allows independent control of each regime. "
                "Low-frequency part is smoother and can be bounded in L^inf; high-frequency part "
                "carries the regularity-critical energy. The adaptive threshold K(t) tracks the "
                "energy concentration scale."
            ),
            confidence=0.65,
        )
        new_repr = ProblemRepresentation(
            representation_id=f"{representation.representation_id}_scale_split",
            kind=RepresentationKind.SCALE_SPLIT,
            source_problem_id=problem.problem_id,
            symbolic_form=(
                "u = u_low + u_high, "
                "u_low = P_{<=K(t)} u = sum_{|k|<=K(t)} hat_u(k) e^{ik.x}, "
                "u_high = P_{>K(t)} u = sum_{|k|>K(t)} hat_u(k) e^{ik.x}, "
                "K(t) = K_0 * (1 + ||u_low(t)||_{H^1} / nu)^{alpha} for tunable alpha > 0"
            ),
            state_variables=("u_low(x,t)", "u_high(x,t)", "K(t)"),
            constraints=(
                "u_low + u_high = u (exact decomposition)",
                "P_{<=K} P_{>K} = 0 (orthogonality of projections)",
                "K(t) >= 1 for all t",
            ),
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
                    name="adaptive_threshold_well_defined",
                    description=(
                        "K(t) is a measurable function of the solution; requires the solution "
                        "to be locally bounded in H^1 on [0, T)"
                    ),
                    severity="medium",
                ),
                Assumption(
                    name="linear_decomposition_exact",
                    description=(
                        "Littlewood-Paley projections are linear and partition of unity; "
                        "decomposition is exact"
                    ),
                    severity="low",
                ),
            ),
            equivalence_claim=(
                "Exact: u_low + u_high = u by construction via complementary Fourier projections. "
                "The decomposition is linear and recombines exactly."
            ),
            audit_notes=(
                "Adaptive K(t) introduces time-dependent splitting; analysis must track K(t) evolution.",
                "Paraproduct structure (low-high, high-low, high-high interactions) governs nonlinear terms.",
            ),
        )
