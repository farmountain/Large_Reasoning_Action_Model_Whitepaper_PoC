"""Phase 3: environment validation."""
import json, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent

required = {
    "numpy":   ("import numpy as np; v=np.__version__", "REQUIRED"),
    "sympy":   ("import sympy; v=sympy.__version__", "REQUIRED"),
    "pytest":  ("import pytest; v=pytest.__version__", "REQUIRED"),
}
optional = {
    "qiskit":            ("import qiskit; v=qiskit.__version__", "OPTIONAL -- Grover falls back to classical"),
    "dowhy":             ("import dowhy; v=dowhy.__version__", "OPTIONAL -- causal checker uses backdoor heuristic"),
    "transformer_lens":  ("import transformer_lens; v='ok'", "OPTIONAL -- circuit probe uses NumPy Kendall tau"),
}

env = {}
missing_required = []

def probe(name, code, status):
    ns = {}
    try:
        exec(code, ns)
        return {"available": True, "version": ns.get("v", "ok"), "status": status}
    except Exception as e:
        return {"available": False, "status": status, "error": str(e)[:80]}

for pkg, (code, status) in required.items():
    env[pkg] = probe(pkg, code, status)
    if not env[pkg]["available"]:
        missing_required.append(pkg)

for pkg, (code, status) in optional.items():
    env[pkg] = probe(pkg, code, status)

(root / ".poc_harness_env.json").write_text(json.dumps(env, indent=2))

print("Environment:")
for pkg, info in env.items():
    if info["available"]:
        print(f"  {pkg:<22} OK   {info.get('version','')}")
    else:
        fb = info['status'].split('--')[1].strip() if '--' in info['status'] else info.get('error','')
        tag = "MISSING" if "REQUIRED" in info['status'] else "MISSING  FALLBACK:"
        print(f"  {pkg:<22} {tag} {fb}")

if missing_required:
    print(f"\nERROR: Required packages missing: {missing_required}")
    print("Install with: pip install " + " ".join(missing_required))
    sys.exit(1)
else:
    print("\nAll REQUIRED dependencies present. OPTIONAL fallbacks noted above.")
