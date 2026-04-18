"""Reflexion loop.

Corresponds to the standalone equation in whitepaper/equations/eq_reflexion.tex.
Implements an episodic memory with decay and a reflect callable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class ReflectionEntry:
    text: str
    weight: float = 1.0


class ReflexionMemory:
    def __init__(self, decay: float = 0.9, max_entries: int = 256):
        self.decay = decay
        self.max_entries = max_entries
        self._buffer: List[ReflectionEntry] = []

    def decay_all(self) -> None:
        for e in self._buffer:
            e.weight *= self.decay
        self._buffer = [e for e in self._buffer if e.weight > 1e-3]

    def add(self, text: str) -> None:
        self._buffer.append(ReflectionEntry(text=text))
        if len(self._buffer) > self.max_entries:
            self._buffer = self._buffer[-self.max_entries :]

    def replay(self) -> List[str]:
        return [e.text for e in self._buffer]

    def __len__(self) -> int:
        return len(self._buffer)


class ReflexionLoop:
    def __init__(
        self,
        validator: Callable[[object], bool],
        reflect_fn: Callable[[object, object], str],
        memory: ReflexionMemory | None = None,
    ):
        self.validator = validator
        self.reflect = reflect_fn
        self.memory = memory if memory is not None else ReflexionMemory()

    def step(self, trajectory, candidate) -> dict:
        self.memory.decay_all()
        verdict = bool(self.validator(candidate))
        if not verdict:
            reflection = self.reflect(trajectory, candidate)
            self.memory.add(reflection)
        return {
            "verdict": verdict,
            "memory_size": len(self.memory),
        }
