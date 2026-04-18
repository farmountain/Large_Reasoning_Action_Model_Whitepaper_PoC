"""World-model distillation.

Corresponds to the standalone equation in whitepaper/equations/eq_world_model.tex.
Minimal NumPy implementation with a linear next-state predictor and a
linear reward predictor. Suitable for the PoC and for unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

import numpy as np


@dataclass
class Transition:
    state: np.ndarray
    action: np.ndarray
    reward: float
    next_state: np.ndarray


class WorldModelDistiller:
    def __init__(self, state_dim: int, action_dim: int, alpha: float = 1.0, gamma: float = 0.1):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.alpha = alpha
        self.gamma = gamma
        self.W_s = np.zeros((state_dim, state_dim + action_dim))
        self.W_r = np.zeros(state_dim + action_dim)

    def predict_next(self, s: np.ndarray, a: np.ndarray) -> np.ndarray:
        return self.W_s @ np.concatenate([s, a])

    def predict_reward(self, s: np.ndarray, a: np.ndarray) -> float:
        return float(self.W_r @ np.concatenate([s, a]))

    def fit(self, dataset: Sequence[Transition], epochs: int = 50, lr: float = 0.01) -> list:
        losses = []
        for _ in range(epochs):
            total = 0.0
            for tr in dataset:
                sa = np.concatenate([tr.state, tr.action])
                pred_s = self.W_s @ sa
                pred_r = float(self.W_r @ sa)
                err_s = pred_s - tr.next_state
                err_r = pred_r - tr.reward
                self.W_s -= lr * np.outer(err_s, sa)
                self.W_r -= lr * self.alpha * err_r * sa
                total += float(np.sum(err_s ** 2) + self.alpha * err_r ** 2)
            losses.append(total / max(len(dataset), 1))
        return losses
