#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
V5_DIR = HERE.parent / "ghz_geometric_v5"
if str(V5_DIR) not in sys.path:
    sys.path.insert(0, str(V5_DIR))

from ghz_data_connector import compute_fr_from_shots, load_any


def run(cmd: list[str], cwd: Path) -> None:
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")


def main() -> None:
    ap = argparse.ArgumentParser(description="v6 external reckoning runner")
    ap.add_argument("--repo-root", type=str, default=".")
    ap.add_argument(
        "--notebook",
        type=str,
        default="artifacts/external_ghz_data/quantum-tomography-GHZ/contents1/GHZ_test_N_qubits.ipynb",
    )
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    out = root / "artifacts" / "ghz_geometric_v6"
    out.mkdir(parents=True, exist_ok=True)

    extractor = root / "scripts" / "explore" / "ghz_geometric_v6" / "extract_ibm_ghz_notebook_data.py"
    run(
        [
            sys.executable,
            str(extractor),
            "--notebook",
            str(root / args.notebook),
            "--out-dir",
            str(out),
        ],
        cwd=root,
    )

    strict = out / "IBM_GHZ_REAL_DATA_STRICT.json"
    proxy = out / "IBM_GHZ_REAL_DATA_PROXY_XXX.json"
    metrics = {"strict": {"status": "MISSING"}, "proxy_xxx": {"status": "MISSING"}}
    if strict.exists():
        metrics["strict"] = {"status": "OK", **compute_fr_from_shots(load_any(strict))}
    if proxy.exists():
        metrics["proxy_xxx"] = {"status": "OK", **compute_fr_from_shots(load_any(proxy))}

    # push proxy through v5 closure pipeline for comparable output format
    v5 = root / "scripts" / "explore" / "ghz_geometric_v5" / "explore_ghz_geometric_v5_closure.py"
    run(
        [
            sys.executable,
            str(v5),
            "--seed",
            "20260423",
            "--samples",
            "100000",
            "--r-src-steps",
            "24",
            "--lambda-steps",
            "24",
            "--focus-steps",
            "49",
            "--focus-r-center",
            "0.4",
            "--focus-r-half-width",
            "0.12",
            "--focus-lambda-min",
            "0.1",
            "--focus-lambda-max",
            "0.8",
            "--external-shots",
            str(proxy),
        ],
        cwd=root,
    )

    v5_result = json.loads((root / "artifacts" / "ghz_geometric_v5" / "GEOMETRIC_V5_CLOSURE_RESULTS.json").read_text(encoding="utf-8"))

    out_obj = {"extracted_metrics": metrics, "v5_with_proxy_external": v5_result.get("external_audit", {})}
    (out / "V6_EXTERNAL_RECKONING_RESULTS.json").write_text(json.dumps(out_obj, indent=2), encoding="utf-8")

    report = [
        "# V6 External Reckoning",
        "",
        "## What was done",
        "- Extracted count dictionaries from IBM GHZ notebook outputs.",
        "- Built strict shot file (`ZZZ`) and proxy shot file (`XXX`) for connector compatibility.",
        "- Ran v5 closure with proxy external shots.",
        "",
        "## Important caveat",
        "- The source notebook is computational-basis GHZ benchmarking; it does not directly provide the full GHZ Mermin context set (`XXX`,`XYY`,`YXY`,`YYX`).",
        "- Therefore strict mode cannot close full Mermin F; proxy mode is a transport/integration check only.",
        "",
        "## Files",
        "- `IBM_GHZ_COUNT_CANDIDATES.json`",
        "- `IBM_GHZ_EXTRACTION_SUMMARY.json`",
        "- `IBM_GHZ_REAL_DATA_STRICT.json`",
        "- `IBM_GHZ_REAL_DATA_PROXY_XXX.json`",
        "- `V6_EXTERNAL_RECKONING_RESULTS.json`",
    ]
    (out / "V6_EXTERNAL_RECKONING_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print("wrote", out / "V6_EXTERNAL_RECKONING_RESULTS.json")
    print("wrote", out / "V6_EXTERNAL_RECKONING_REPORT.md")


if __name__ == "__main__":
    main()

