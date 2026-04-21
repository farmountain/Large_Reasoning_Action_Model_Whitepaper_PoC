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


class BoundedSurrogateTransform(Transformation):
    transform_id = "t_bounded_surrogate"
    family = TransformationFamily.RELAXATION
    input_kind = RepresentationKind.PHYSICAL
    output_kind = RepresentationKind.BOUNDED_SURROGATE

    def applicable(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> bool:
        return representation.kind == RepresentationKind.PHYSICAL

    def apply(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> TransformationResult:
        invariant = InvariantCandidate(
            name="periodic_regularity_proxy",
            formula=(
                "u_T3 solves NS on T^3 = (R/Z)^3 with same initial data class; "
                "||u_T3(t)||_{H^s(T^3)} < infty for all t > 0 implies conditional regularity on R^3 "
                "under spatial decay: |u_0(x)| <= C*(1+|x|)^{-alpha}, alpha > 3/2"
            ),
            rationale=(
                "The periodic (torus) setting is technically simpler: compact domain eliminates "
                "behaviour at spatial infinity. Regularity results on T^3 can transfer to R^3 "
                "via localization arguments when the R^3 solution has sufficient spatial decay. "
                "This is a standard surrogate used in numerical and theoretical analysis."
            ),
            confidence=0.45,
        )
        new_repr = ProblemRepresentation(
            representation_id=f"{representation.representation_id}_bounded_surrogate",
            kind=RepresentationKind.BOUNDED_SURROGATE,
            source_problem_id=problem.problem_id,
            symbolic_form=(
                "NS on T^3: du/dt + (u.grad)u = -grad p + nu*Delta u, div u = 0, "
                "x in T^3 = (R / (2*pi*Z))^3, t > 0, "
                "u(x+2*pi*e_i, t) = u(x, t) for i=1,2,3 (periodicity)"
            ),
            state_variables=("u(x,t) on T^3", "p(x,t) on T^3"),
            constraints=(
                "u periodic on T^3",
                "int_{T^3} u dx = 0 (zero mean, WLOG)",
                "div u = 0",
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
                    name="r3_to_t3_relaxation",
                    description=(
                        "R^3 problem is replaced by T^3 problem; large-scale behaviour differs. "
                        "Transfer of results requires spatial decay of initial data on R^3."
                    ),
                    severity="high",
                ),
                Assumption(
                    name="decay_at_infinity",
                    description=(
                        "Initial data u_0 on R^3 must satisfy |u_0(x)| <= C*(1+|x|)^{-alpha} "
                        "for alpha > 3/2 for periodic-to-whole-space transfer."
                    ),
                    severity="medium",
                ),
            ),
            equivalence_claim=(
                "Approximate: T^3 and R^3 differ at large scales; the periodic surrogate is a "
                "relaxation of the original problem. Transfer of regularity results is conditional "
                "on decay assumptions and localization arguments."
            ),
            audit_notes=(
                "Periodic domain simplifies functional analysis: no boundary terms, compact Sobolev embeddings.",
                "Solutions on T^3 may give insight into R^3 behaviour under spatial decay assumptions.",
                "This is a standard research surrogate, not an exact equivalence.",
            ),
        )
