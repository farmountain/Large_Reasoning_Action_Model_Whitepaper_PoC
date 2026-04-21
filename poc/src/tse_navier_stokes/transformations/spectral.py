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


class SpectralTransform(Transformation):
    transform_id = "t_spectral"
    family = TransformationFamily.REPRESENTATION_SHIFT
    input_kind = RepresentationKind.PHYSICAL
    output_kind = RepresentationKind.SPECTRAL

    def applicable(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> bool:
        return representation.kind == RepresentationKind.PHYSICAL

    def apply(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> TransformationResult:
        invariant = InvariantCandidate(
            name="frequency_tail_mass",
            formula=(
                "M_K(t) = sum_{|k|>K} |hat_u(k,t)|^2, "
                "M_K(t) -> 0 as K -> infty for smooth solutions"
            ),
            rationale=(
                "In spectral space, regularity is controlled by the decay of Fourier coefficients. "
                "Blow-up corresponds to the failure of high-frequency tail mass to remain small, "
                "making M_K a natural regularity indicator."
            ),
            confidence=0.61,
        )
        new_repr = ProblemRepresentation(
            representation_id=f"{representation.representation_id}_spectral",
            kind=RepresentationKind.SPECTRAL,
            source_problem_id=problem.problem_id,
            symbolic_form=(
                "d(hat_u(k))/dt + nu|k|^2 hat_u(k) = -i * sum_{p+q=k} (k . hat_u(p)) hat_u(q) "
                "+ pressure projection, k in Z^3, div constraint: k . hat_u(k) = 0"
            ),
            state_variables=("hat_u(k,t) for k in Z^3",),
            constraints=(
                "k . hat_u(k) = 0 (divergence-free in Fourier space)",
                "hat_u(-k) = conj(hat_u(k)) (real-valued field)",
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
                    name="periodic_or_whole_space",
                    description=(
                        "Fourier transform requires periodic domain (T^3) or Schwartz-class "
                        "decay on R^3; transform is exact in either case"
                    ),
                    severity="low",
                ),
            ),
            equivalence_claim=(
                "Exact: Fourier transform is an isometric isomorphism on L^2; "
                "the spectral formulation is fully equivalent to the physical one."
            ),
            audit_notes=(
                "Nonlinear term becomes a convolution in Fourier space.",
                "High-frequency decay rate directly encodes Sobolev regularity.",
            ),
        )
