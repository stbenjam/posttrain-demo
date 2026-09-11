"""Run all four conditions on the same fresh test after checkpoint selection."""
import subprocess
import sys
from common import ROOT

conditions = [
    ("final_base", []),
    ("final_base_instructed", ["--instructed"]),
    ("final_v1", ["--adapter", str(ROOT / "adapters-selected")]),
    ("final_v2", ["--adapter", str(ROOT / "adapters-v2-selected")]),
]
for name, _ in conditions:
    for suffix in ("jsonl", "summary.json", "log"):
        if (ROOT / "runs" / f"{name}.{suffix}").exists():
            raise SystemExit(f"Preserving an existing {name} result; run individual evaluations with new filenames.")
(ROOT / 'runs').mkdir(exist_ok=True)
for name, extra in conditions:
    print(f"Evaluating {name}...", flush=True)
    with (ROOT / "runs" / f"{name}.log").open("x") as log:
        subprocess.run([sys.executable, str(ROOT / "evaluate.py"),
                        "--cases", str(ROOT / "data/final.cases.jsonl"),
                        "--output", str(ROOT / "runs" / f"{name}.jsonl"), *extra],
                       check=True, stdout=log, stderr=subprocess.STDOUT)
subprocess.run([sys.executable, str(ROOT / "compare.py"), "--final"], check=True)
