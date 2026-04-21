from __future__ import annotations
from ..problem import NavierStokesProblem
from ..representations import ProblemRepresentation
from ..types import (
    Assumption,
    ControlFunctionalCandidate,
    RepresentationKind,
    TransformationFamily,
)
from .base import Transformation, TransformationResult


class EnergyTransform(Transformation):
    transform_id = "t_energy"
    family = TransformationFamily.INVARIANT_DISCOVERY
    input_kind = RepresentationKind.PHYSICAL
    output_kind = RepresentationKind.ENERGY

    def applicable(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> bool:
        return representation.kind == RepresentationKind.PHYSICAL and problem.viscosity > 0

    def apply(self, problem: NavierStokesProblem, representation: ProblemRepresentation) -> TransformationResult:
        control_functional = ControlFunctionalCandidate(
            name="augmented_energy_barrier",
            formula=(
                "Q(t) = (1/2)||u(t)||_{L^2}^2 + lambda * ||P_{>K} u(t)||_{L^2}^2, "
                "dQ/dt <= -nu * ||grad u||_{L^2}^2 + C(K, nu) * Q(t)"
            ),
            target_property="global_regularity",
            confidence=0.58,
        )
        new_repr = ProblemRepresentation(
            representation_id=f"{representation.representation_id}_energy",
            kind=RepresentationKind.ENERGY,
            source_problem_id=problem.problem_id,
            symbolic_form=(
                "E(t) = (1/2) * int |u(x,t)|^2 dx, "
                "dE/dt = -nu * ||grad u||_{L^2}^2, "
                "Leray energy inequality: E(t) + 2*nu*int_0^t ||grad u||^2 ds <= E(0)"
            ),
            state_variables=("E(t)", "||grad_u(t)||_{L^2}"),
            constraints=(
                "E(t) <= E(0) for all t >= 0",
                "nu > 0",
            ),
            invariants=(),
            control_functionals=(control_functional,),
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
                    name="leray_hopf_weak_solution",
                    description="u is a Leray-Hopf weak solution satisfying the energy inequality",
                    severity="low",
                ),
                Assumption(
                    name="phase_information_lost",
                    description="Energy view integrates out spatial phase; not a lossless transformation",
                    severity="medium",
                ),
            ),
            equivalence_claim=(
                "Approximate: energy formulation discards phase information. "
                "The Leray energy inequality holds for all Leray-Hopf weak solutions but the "
                "converse (energy bound implies regularity) requires additional assumptions."
            ),
            audit_notes=(
                "Energy inequality is well-established for Leray-Hopf solutions.",
                "Augmented functional Q adds high-frequency penalty term for sharper control.",
            ),
        )
