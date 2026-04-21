from __future__ import annotations
from ..types import RepresentationKind
from ..worlds import HypothesisWorld

# Per-kind oracle hardness estimates: lower = easier oracle (cheaper to verify)
_KIND_HARDNESS: dict[RepresentationKind, float] = {
    RepresentationKind.ENERGY:            0.37,
    RepresentationKind.VORTICITY:         0.46,
    RepresentationKind.SPECTRAL:          0.51,
    RepresentationKind.SCALE_SPLIT:       0.56,
    RepresentationKind.BLOWUP_RESCALING:  0.72,
    RepresentationKind.BOUNDED_SURROGATE: 0.33,
}

_DEFAULT_HARDNESS = 0.65


class OracleHardnessEstimator:
    """Estimates oracle hardness for a HypothesisWorld.

    Returns a float in [0, 1] where lower means an easier oracle
    (cheaper / more tractable verification cost).
    """

    def estimate(self, world: HypothesisWorld) -> float:
        """Return oracle hardness score in [0, 1] for the given world."""
        return _KIND_HARDNESS.get(world.representation.kind, _DEFAULT_HARDNESS)
