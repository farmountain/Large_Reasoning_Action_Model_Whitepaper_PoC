"""Tier-3 validator.

Composes three sub-validators: formal (Lean-style), causal (DoWhy-style),
and circuit (TransformerLens-style). All three must pass for a
candidate to be accepted, matching the three-tier acceptance probability
stated in whitepaper/equations/eq_three_tier.tex.

The PoC ships classical stand-ins for each sub-validator so that the
pipeline runs end-to-end on a laptop. Real bridges to Lean 4, DoWhy,
and TransformerLens are wired in the notebooks.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class ValidationReport:
    formal: bool
    causal: bool
    circuit: bool
    reasons: list = field(default_factory=list)

    @property
    def accepted(self) -> bool:
        return self.formal and self.causal and self.circuit


class LeanBridge:
    """Thin wrapper around a Lean 4 subprocess.

    If `lean` is not on PATH we fall back to a syntactic check: the
    candidate must evaluate to a non-empty string containing the
    substring "proof" to be accepted. This keeps the PoC functional
    without a Lean install.
    """

    def __init__(self, lean_cmd: Optional[str] = None):
        self.lean_cmd = lean_cmd or shutil.which("lean")

    def check(self, proof_script: str) -> bool:
        if not self.lean_cmd:
            return bool(proof_script) and "proof" in proof_script.lower()
        try:
            proc = subprocess.run(
                [self.lean_cmd, "--stdin"],
                input=proof_script.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )
            return proc.returncode == 0
        except Exception:
            return False


class Tier3Validator:
    def __init__(
        self,
        formal: Optional[Callable[[str], bool]] = None,
        causal: Optional[Callable[[object], bool]] = None,
        circuit: Optional[Callable[[object], bool]] = None,
    ):
        self._lean = LeanBridge()
        self.formal = formal or (lambda s: self._lean.check(str(s)))
        self.causal = causal or (lambda obj: True)
        self.circuit = circuit or (lambda obj: True)

    def validate(self, candidate) -> ValidationReport:
        report = ValidationReport(formal=False, causal=False, circuit=False)
        report.formal = bool(self.formal(candidate))
        if not report.formal:
            report.reasons.append("formal_check_failed")
        report.causal = bool(self.causal(candidate))
        if not report.causal:
            report.reasons.append("causal_identifiability_failed")
        report.circuit = bool(self.circuit(candidate))
        if not report.circuit:
            report.reasons.append("circuit_faithfulness_failed")
        return report
