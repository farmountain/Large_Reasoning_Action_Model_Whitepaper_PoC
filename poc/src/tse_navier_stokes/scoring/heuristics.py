from __future__ import annotations
from ..types import RepresentationKind, ScoreBreakdown
from ..worlds import HypothesisWorld
from .base import WorldScorer

# Per-representation base scores: (coercive, scale_sep, blowup, formalizable)
_BASE_SCORES: dict[RepresentationKind, tuple[float, float, float, float]] = {
    RepresentationKind.PHYSICAL:          (0.30, 0.20, 0.20, 0.40),
    RepresentationKind.ENERGY:            (0.80, 0.45, 0.50, 0.65),
    RepresentationKind.VORTICITY:         (0.55, 0.50, 0.85, 0.60),
    RepresentationKind.SPECTRAL:          (0.45, 0.75, 0.55, 0.55),
    RepresentationKind.SCALE_SPLIT:       (0.60, 0.90, 0.65, 0.58),
    RepresentationKind.BLOWUP_RESCALING:  (0.48, 0.35, 0.90, 0.55),
    RepresentationKind.BOUNDED_SURROGATE: (0.72, 0.60, 0.50, 0.80),
}

# Weights for the weighted sum
_W_COERCIVE     = 0.28
_W_SCALE_SEP    = 0.22
_W_BLOWUP       = 0.24
_W_FORMALIZABLE = 0.16
_W_NON_EQ       = 0.05
_W_ORACLE       = 0.05

# Non-equivalence penalties per equivalence risk level
_NON_EQ_PENALTY: dict[str, float] = {"low": 0.0, "medium": 0.10, "high": 0.25}

# Oracle hardness fallback per kind
_KIND_ORACLE: dict[RepresentationKind, float] = {
    RepresentationKind.ENERGY:            0.37,
    RepresentationKind.VORTICITY:         0.46,
    RepresentationKind.SPECTRAL:          0.51,
    RepresentationKind.SCALE_SPLIT:       0.56,
    RepresentationKind.BLOWUP_RESCALING:  0.72,
    RepresentationKind.BOUNDED_SURROGATE: 0.33,
}


class NavierStokesHeuristicScorer(WorldScorer):
    """Heuristic scorer for Navier-Stokes hypothesis worlds.

    Computes a ScoreBreakdown using per-representation base scores and a
    weighted linear combination with penalties for non-equivalence risk and
    oracle hardness.
    """

    def score(self, world: HypothesisWorld) -> ScoreBreakdown:
        kind = world.representation.kind
        coercive, scale_sep, blowup, formalizable = _BASE_SCORES.get(
            kind, (0.30, 0.30, 0.30, 0.30)
        )

        non_eq_penalty = self._non_equivalence_penalty(world)
        oracle_penalty = self._oracle_hardness_penalty(world)

        total = (
            _W_COERCIVE * coercive
            + _W_SCALE_SEP * scale_sep
            + _W_BLOWUP * blowup
            + _W_FORMALIZABLE * formalizable
            - _W_NON_EQ * non_eq_penalty
            - _W_ORACLE * oracle_penalty
        )
        total = max(0.0, min(1.0, total))

        return ScoreBreakdown(
            coercive_score=coercive,
            scale_separation_score=scale_sep,
            blowup_detect_score=blowup,
            formalizable_score=formalizable,
            non_equivalence_penalty=non_eq_penalty,
            oracle_hardness_penalty=oracle_penalty,
            total_score=total,
        )

    def _non_equivalence_penalty(self, world: HypothesisWorld) -> float:
        """Derive non-equivalence penalty from equivalence audit artifact if present,
        otherwise fall back to transform-chain heuristic."""
        audit = world.artifacts.get("equivalence_audit")
        if audit is not None:
            risk = getattr(audit, "risk_level", "low")
            return _NON_EQ_PENALTY.get(risk, 0.0)
        if not world.transform_chain:
            return 0.0
        last_id = world.transform_chain[-1].transform_id
        high_risk = {"t_blowup_rescale", "t_bounded_surrogate"}
        medium_risk = {"t_energy"}
        if last_id in high_risk:
            return _NON_EQ_PENALTY["high"]
        if last_id in medium_risk:
            return _NON_EQ_PENALTY["medium"]
        return _NON_EQ_PENALTY["low"]

    def _oracle_hardness_penalty(self, world: HypothesisWorld) -> float:
        """Return oracle hardness as a [0,1] penalty value."""
        if world.oracle_estimate is not None:
            raw = world.oracle_estimate.total_cost / 4.0
            return max(0.0, min(1.0, raw))
        return _KIND_ORACLE.get(world.representation.kind, 0.65)
