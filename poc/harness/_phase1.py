"""Phase 1: write claims + metric map to .poc_harness_*.json."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent

claims = [
    {
        "claim_id": "C1",
        "statement": "Prajna reduces the candidate search space by at least 90% relative to the raw syntactic space",
        "measurable_proxy": "compression_ratio_vs_raw",
        "acceptance_criterion": "compression_ratio_vs_raw < 0.10",
        "failure_criterion": "compression_ratio_vs_raw >= 0.10",
        "source_section": "Section 4 (Compression), Section 5 (Prajna Abstraction)",
        "ablation_control": "no_prajna",
    },
    {
        "claim_id": "C2",
        "statement": "Grover query count matches the theoretical iteration bound floor(pi/4 * sqrt(N/M)) to within 1 query",
        "measurable_proxy": "grover_queries",
        "acceptance_criterion": "abs(grover_queries - grover_theoretical_iters) <= 1",
        "failure_criterion": "abs(grover_queries - grover_theoretical_iters) > 1",
        "source_section": "Section 5 (Grover Candidate Amplification)",
        "ablation_control": "no_grover",
    },
    {
        "claim_id": "C3",
        "statement": "Tier-3 validation accepts the Grover-selected winner (formal + causal + circuit checks all pass)",
        "measurable_proxy": "tier3_pass",
        "acceptance_criterion": "tier3_pass == True",
        "failure_criterion": "tier3_pass == False",
        "source_section": "Section 5 (Three-Tier Acceptance Probability)",
        "ablation_control": "no_tier3",
    },
    {
        "claim_id": "C4",
        "statement": "Removing Prajna (no_prajna ablation) increases oracle query count relative to full pipeline",
        "measurable_proxy": "grover_queries_no_prajna_vs_none",
        "acceptance_criterion": "grover_queries_no_prajna_vs_none > 0",
        "failure_criterion": "grover_queries_no_prajna_vs_none <= 0",
        "source_section": "Section 12 (Ablation Study)",
        "ablation_control": "no_prajna",
    },
    {
        "claim_id": "C5",
        "statement": "Removing Grover (no_grover ablation) increases oracle query count relative to full pipeline",
        "measurable_proxy": "grover_queries_no_grover_vs_none",
        "acceptance_criterion": "grover_queries_no_grover_vs_none > 0",
        "failure_criterion": "grover_queries_no_grover_vs_none <= 0",
        "source_section": "Section 12 (Ablation Study)",
        "ablation_control": "no_grover",
    },
    {
        "claim_id": "C6",
        "statement": "Reflexion loop activates and stores a textual critique when a candidate is rejected (convergence mechanism is operational)",
        "measurable_proxy": "reflexion_activated",
        "acceptance_criterion": "reflexion_activated == True",
        "failure_criterion": "reflexion_activated == False",
        "source_section": "Section 10 (Reflexion Loop), Section 12 (Ablation Study)",
        "ablation_control": "no_reflexion",
    },
    {
        "claim_id": "C7",
        "statement": "The architecture is real, reproducible, and every equation corresponds to an implemented module (smoke tests pass)",
        "measurable_proxy": "smoke_tests_pass",
        "acceptance_criterion": "smoke_tests_pass == True",
        "failure_criterion": "smoke_tests_pass == False",
        "source_section": "Section 12 (Conclusion of the PoV)",
        "ablation_control": None,
    },
]

metric_map = {
    "C1": {"field": "compression_ratio_vs_raw"},
    "C2": {"field": "grover_queries", "theory_field": "grover_theoretical_iters"},
    "C3": {"field": "tier3_pass"},
    "C4": {"field": "grover_queries", "compare_ablation": "no_prajna", "compare_baseline": "none"},
    "C5": {"field": "grover_queries", "compare_ablation": "no_grover", "compare_baseline": "none"},
    "C6": {"field": "reflexion_activated"},
    "C7": {"field": "smoke_tests_pass"},
}

(root / ".poc_harness_claims.json").write_text(json.dumps(claims, indent=2))
(root / ".poc_harness_metric_map.json").write_text(json.dumps(metric_map, indent=2))

print("Claims extracted: 7")
print("")
print(f"{'Claim':<6} {'Statement (abbreviated)':<55} {'Acceptance Criterion'}")
print(f"{'-----':<6} {'-----------------------------------------------':<55} {'----------------------------'}")
for c in claims:
    stmt = c['statement'][:53] + '..' if len(c['statement']) > 55 else c['statement']
    print(f"{c['claim_id']:<6} {stmt:<55} {c['acceptance_criterion']}")
