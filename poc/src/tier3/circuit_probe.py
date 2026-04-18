"""Circuit probe for mechanistic interpretability.

The PoC ships a minimal faithfulness test: given an attribution vector
a and a logit-change vector l, we report Kendall tau. Real usage wires
TransformerLens patching in the notebooks. We keep the function
dependency-free so unit tests run without torch.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class CircuitScore:
    kendall_tau: float

    @property
    def faithful(self) -> bool:
        return self.kendall_tau >= 0.5


class CircuitProbe:
    def score(
        self,
        attribution: Sequence[float],
        logit_change: Sequence[float],
    ) -> CircuitScore:
        if len(attribution) != len(logit_change) or len(attribution) < 2:
            return CircuitScore(kendall_tau=0.0)
        concordant = 0
        discordant = 0
        n = len(attribution)
        for i in range(n):
            for j in range(i + 1, n):
                da = attribution[i] - attribution[j]
                dl = logit_change[i] - logit_change[j]
                if da * dl > 0:
                    concordant += 1
                elif da * dl < 0:
                    discordant += 1
        denom = concordant + discordant
        if denom == 0:
            return CircuitScore(kendall_tau=0.0)
        return CircuitScore(kendall_tau=(concordant - discordant) / denom)
