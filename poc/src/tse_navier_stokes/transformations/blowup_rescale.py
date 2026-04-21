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


class BlowupRescalingTransform(Transformation):
    transform_id = "t_blowup_rescale"
    family = TransformationFamily.RESCALING
    input_kind = RepresentationKind.PHYSICAL
    output_kind = RepresentationKind.BLOWUP_RESCALING

    def applicable(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> bool:
        return problem.dimension == 3 and representation.kind == RepresentationKind.PHYSICAL

    def apply(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> TransformationResult:
        invariant = InvariantCandidate(
            name="blow_up_profile_exclusion",
            formula=(
                "U(xi, tau) = (T-t)^{1/2} u(x, t), xi = x / (T-t)^{1/2}, tau = -log(T-t); "
                "Type-I assumption: |u(x,t)| <= C / sqrt(T-t). "
                "No non-trivial self-similar profile U satisfying rescaled NS exists."
            ),
            rationale=(
                "Under Type-I blow-up scaling, the rescaled profile U satisfies a stationary "
                "or slowly-varying PDE. Ruling out all admissible self-similar profiles U "
                "would exclude Type-I singularities. Tsai and Hou-Li approaches work in this regime."
            ),
            confidence=0.55,
        )
        new_repr = ProblemRepresentation(
            representation_id=f"{representation.representation_id}_blowup_rescale",
            kind=RepresentationKind.BLOWUP_RESCALING,
            source_problem_id=problem.problem_id,
            symbolic_form=(
                "U(xi, tau) = lambda(t) * u(lambda(t)*xi, t), lambda(t) = (T-t)^{1/2}, "
                "tau = -log(T-t), "
                "dU/dtau + (1/2)(xi . grad_xi)U + (1/2)U + (U . grad_xi)U "
                "= -grad_xi P + nu * Delta_xi U, div_xi U = 0"
            ),
            state_variables=("U(xi, tau)", "P(xi, tau)"),
            constraints=(
                "Type-I scaling: |u(x,t)| <= C*(T-t)^{-1/2}",
                "div_xi U = 0",
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
                    name="type_i_blowup_hypothesis",
                    description=(
                        "Assumes potential blow-up is of Type-I: |u(x,t)| <= C*(T-t)^{-1/2}. "
                        "Type-II blow-up (faster growth) is not covered by this rescaling."
                    ),
                    severity="high",
                ),
                Assumption(
                    name="finite_blowup_time_T",
                    description="Assumes a finite potential blow-up time T exists; analysis is near T.",
                    severity="medium",
                ),
            ),
            equivalence_claim=(
                "Assumption-dependent: the rescaled system is equivalent to the original NS "
                "only under the Type-I scaling hypothesis. Excludes Type-II and borderline scenarios."
            ),
            audit_notes=(
                "Self-similar rescaling eliminates the explicit time parameter near blow-up.",
                "Stationary solutions of the rescaled system correspond to Type-I blow-up profiles.",
                "Ruling out such profiles (Tsai 1998, Hou-Li) gives partial regularity results.",
            ),
        )
