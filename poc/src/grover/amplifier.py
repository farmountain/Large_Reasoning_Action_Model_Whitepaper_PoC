"""Grover-style amplitude amplification.

Corresponds to the standalone equation in whitepaper/equations/eq_grover.tex.

We provide two implementations:

1. `amplify_classical` simulates the expected query count of an ideal
   Grover run on a classical machine. It is used for ablation studies
   and for laptops without Qiskit.

2. `amplify_qiskit` builds and runs an actual Grover circuit on the
   Qiskit Aer simulator when Qiskit is installed. It falls back to the
   classical path if Qiskit is not available.

Both return the same `GroverResult` dataclass so downstream code does
not branch on the backend.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Sequence, TypeVar

Candidate = TypeVar("Candidate")


@dataclass
class GroverResult:
    winner: Candidate | None
    iterations: int
    query_count: int
    backend: str


class GroverAmplifier:
    def __init__(self, oracle: Callable[[Candidate], bool], backend: str = "auto"):
        self.oracle = oracle
        self.backend = backend

    @staticmethod
    def theoretical_iterations(N: int, M: int) -> int:
        if M <= 0 or N <= 0:
            return 0
        return max(1, math.floor((math.pi / 4) * math.sqrt(N / M)))

    def amplify_classical(self, candidates: Sequence[Candidate]) -> GroverResult:
        if not candidates:
            return GroverResult(None, 0, 0, "classical")
        accepted = [c for c in candidates if self.oracle(c)]
        N, M = len(candidates), len(accepted)
        iters = self.theoretical_iterations(N, M)
        winner = random.choice(accepted) if accepted else None
        return GroverResult(
            winner=winner,
            iterations=iters,
            query_count=iters,
            backend="classical",
        )

    def amplify_qiskit(self, candidates: Sequence[Candidate]) -> GroverResult:
        try:
            from qiskit import QuantumCircuit
            from qiskit_aer import AerSimulator
            from qiskit.circuit.library import GroverOperator, PhaseOracle  # noqa: F401
        except Exception:
            return self.amplify_classical(candidates)

        N = len(candidates)
        if N == 0:
            return GroverResult(None, 0, 0, "qiskit")
        n_qubits = max(1, math.ceil(math.log2(N)))
        accepted_indices = [i for i, c in enumerate(candidates) if self.oracle(c)]
        if not accepted_indices:
            return GroverResult(None, 0, 0, "qiskit")
        iters = self.theoretical_iterations(2 ** n_qubits, len(accepted_indices))

        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.h(range(n_qubits))
        for _ in range(iters):
            self._apply_marking(qc, accepted_indices, n_qubits)
            self._apply_diffuser(qc, n_qubits)
        qc.measure(range(n_qubits), range(n_qubits))

        sim = AerSimulator()
        result = sim.run(qc, shots=1024).result()
        counts = result.get_counts()
        best = max(counts, key=counts.get)
        idx = int(best, 2)
        winner = candidates[idx] if idx < N else None
        return GroverResult(
            winner=winner,
            iterations=iters,
            query_count=iters,
            backend="qiskit",
        )

    @staticmethod
    def _apply_marking(qc, accepted_indices, n_qubits) -> None:
        for idx in accepted_indices:
            bits = format(idx, f"0{n_qubits}b")
            for q, b in enumerate(bits):
                if b == "0":
                    qc.x(q)
            qc.h(n_qubits - 1)
            qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            qc.h(n_qubits - 1)
            for q, b in enumerate(bits):
                if b == "0":
                    qc.x(q)

    @staticmethod
    def _apply_diffuser(qc, n_qubits) -> None:
        qc.h(range(n_qubits))
        qc.x(range(n_qubits))
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        qc.x(range(n_qubits))
        qc.h(range(n_qubits))

    def amplify(self, candidates: Sequence[Candidate]) -> GroverResult:
        if self.backend in ("classical", "auto"):
            if self.backend == "classical":
                return self.amplify_classical(candidates)
            try:
                return self.amplify_qiskit(candidates)
            except Exception:
                return self.amplify_classical(candidates)
        return self.amplify_qiskit(candidates)
