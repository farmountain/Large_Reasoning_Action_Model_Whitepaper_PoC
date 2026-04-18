"""Teacher-student distillation.

Corresponds to the standalone equation in whitepaper/equations/eq_distillation.tex.
The PoC uses a NumPy-based categorical student so the notebooks run
without a GPU. The structure of the training loop is identical to a
PyTorch version: the only substitution is the parameter update rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)


def _kl(p: np.ndarray, q: np.ndarray, eps: float = 1e-9) -> float:
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    return float(np.sum(p * np.log(p / q)))


@dataclass
class Teacher:
    name: str
    policy: Callable[[np.ndarray], np.ndarray]  # state -> prob vector
    weight: float = 1.0


class DistillationTrainer:
    def __init__(
        self,
        teachers: Sequence[Teacher],
        n_actions: int,
        lr: float = 0.05,
        eta: float = 0.1,
        mu: float = 1e-4,
    ):
        self.teachers = list(teachers)
        self.n_actions = n_actions
        self.lr = lr
        self.eta = eta
        self.mu = mu
        self.logits = np.zeros(n_actions)

    def student_policy(self, state: np.ndarray) -> np.ndarray:
        return _softmax(self.logits + state[: self.n_actions])

    def step(self, state: np.ndarray, q_ref: np.ndarray) -> dict:
        pi = self.student_policy(state)
        kl_sum = 0.0
        grad = np.zeros_like(self.logits)
        total_w = sum(t.weight for t in self.teachers) or 1.0
        for t in self.teachers:
            p_t = t.policy(state)
            kl_sum += (t.weight / total_w) * _kl(pi, p_t)
            grad += (t.weight / total_w) * (pi - p_t)
        q_loss = float(np.mean((pi - q_ref) ** 2))
        grad += self.eta * (pi - q_ref)
        grad += self.mu * self.logits
        self.logits -= self.lr * grad
        return {
            "kl": kl_sum,
            "q_loss": q_loss,
            "total": kl_sum + self.eta * q_loss + self.mu * float(np.sum(self.logits ** 2)),
        }
