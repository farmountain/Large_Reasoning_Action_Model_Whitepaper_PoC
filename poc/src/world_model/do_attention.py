"""Do-attention layer.

Corresponds to the standalone equation in whitepaper/equations/eq_do_attention.tex.
A NumPy reference implementation. Swap in torch.nn equivalents in the
notebooks for GPU execution.
"""

from __future__ import annotations

import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


class DoAttention:
    def __init__(self, d_k: int, beta: float = 1.0):
        self.d_k = d_k
        self.beta = beta

    def intervention_bias(self, do_x: np.ndarray, keys: np.ndarray) -> np.ndarray:
        # simple interventional bias: dot-product between intervention
        # vector and keys, normalised by sqrt(d_k).
        return (keys @ do_x) / np.sqrt(self.d_k)

    def __call__(
        self,
        Q: np.ndarray,
        K: np.ndarray,
        V: np.ndarray,
        do_x: np.ndarray | None = None,
    ) -> np.ndarray:
        scores = (Q @ K.T) / np.sqrt(self.d_k)
        if do_x is not None:
            bias = self.intervention_bias(do_x, K)
            scores = scores + self.beta * bias
        weights = softmax(scores, axis=-1)
        return weights @ V
