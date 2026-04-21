"""Phase 4: build experiment matrix, run ablation sweep, collect results."""
import json, subprocess, sys, hashlib, datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent

# 4A: matrix
benchmarks = ["toy_conjectures"]
ablations = ["none", "no_prajna", "no_grover", "no_tier3", "no_reflexion"]
matrix = [{"benchmark": b, "ablation": a} for b in benchmarks for a in ablations]
(root / ".poc_harness_matrix.json").write_text(json.dumps(matrix, indent=2))

print(f"Experiment matrix: {len(matrix)} cells ({len(benchmarks)} benchmarks x {len(ablations)} ablations)")
print("")

# 4B: reproducibility metadata
reqs = root / "poc" / "requirements.txt"
env_hash = hashlib.sha256(reqs.read_bytes()).hexdigest()[:12] if reqs.exists() else "no-requirements-txt"
try:
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()[:10]
except Exception:
    git_sha = "unavailable"

meta = {
    "python_version": sys.version.split()[0],
    "seed": 42,
    "env_hash": env_hash,
    "git_sha": git_sha,
    "timestamp_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
}
(root / ".poc_harness_meta.json").write_text(json.dumps(meta, indent=2))
print(f"Reproducibility: git={git_sha}, seed=42, env={env_hash}, ts={meta['timestamp_utc']}")
print("")

# 4C/4D: run full ablation sweep via run_ablations
print("Running ablation sweep (5 variants)...")
result = subprocess.run(
    [sys.executable, "-m", "poc.src.run_ablations"],
    capture_output=True, text=True, cwd=root
)
print(result.stdout.strip())
if result.returncode != 0:
    print(f"STDERR: {result.stderr.strip()[:500]}", file=sys.stderr)
    sys.exit(result.returncode)

# Load results
results_file = root / "poc" / "results" / "pov_metrics.json"
if not results_file.exists():
    print("ERROR: pov_metrics.json not written by run_ablations", file=sys.stderr)
    sys.exit(1)

raw = json.loads(results_file.read_text())
# Normalise: run_ablations writes an ablation-keyed dict directly
results = raw if isinstance(raw, dict) and "none" in raw else {raw.get("ablation", "none"): raw}

(root / ".poc_harness_results.json").write_text(json.dumps(results, indent=2))
print(f"\nResults collected for ablations: {list(results.keys())}")
