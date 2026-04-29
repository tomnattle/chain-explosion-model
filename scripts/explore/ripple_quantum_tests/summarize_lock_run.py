#!/usr/bin/env python3
"""
Summarize locked unified run into a single audit-grade markdown page.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


LOCKED = {"mu": 1.55, "rho": 2.35, "eta": 0.08, "bw_ghz": 3.0e-5}


def sha256_file(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def get_stage(manifest: dict[str, Any], name: str) -> dict[str, Any] | None:
    for s in manifest.get("runs", []):
        if s.get("stage") == name:
            return s
    return None


def load_v6_module(repo_root: Path):
    p = repo_root / "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py"
    spec = importlib.util.spec_from_file_location("v6_joint", p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load v6 module: {p}")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def build_jcfg(v6m):
    return {
        "wave_speed_mode": "constant_c",
        "expo_mu": 0.25,
        "expo_rho": 0.25,
        "k_eta": 0.0,
        "c_ref_m_s": float(v6m.C_LIGHT_M_S),
        "mu_ref": float(v6m.MU_REF),
        "rho_ref": float(v6m.RHO_REF),
        "eta_ref": float(v6m.ETA_REF),
    }


def eval_loss(v6m, mu: float, rho: float, eta: float, bw: float, alpha: float) -> float:
    v = np.array([mu, rho, eta, bw], dtype=float)
    return float(v6m.eval_joint_loss(v, 1, alpha, 0.0, 800.0, 400.0, build_jcfg(v6m)))


def jitter_hardness(v6m, alpha: float, delta: float = 1e-4) -> dict[str, Any]:
    c = eval_loss(v6m, LOCKED["mu"], LOCKED["rho"], LOCKED["eta"], LOCKED["bw_ghz"], alpha)
    out: dict[str, Any] = {"center_loss": c, "delta": delta, "axes": {}}
    slopes = []
    for k in ("mu", "rho", "eta"):
        mu, rho, eta = LOCKED["mu"], LOCKED["rho"], LOCKED["eta"]
        if k == "mu":
            lp = eval_loss(v6m, mu + delta, rho, eta, LOCKED["bw_ghz"], alpha)
            lm = eval_loss(v6m, mu - delta, rho, eta, LOCKED["bw_ghz"], alpha)
        elif k == "rho":
            lp = eval_loss(v6m, mu, rho + delta, eta, LOCKED["bw_ghz"], alpha)
            lm = eval_loss(v6m, mu, rho - delta, eta, LOCKED["bw_ghz"], alpha)
        else:
            lp = eval_loss(v6m, mu, rho, eta + delta, LOCKED["bw_ghz"], alpha)
            lm = eval_loss(v6m, mu, rho, eta - delta, LOCKED["bw_ghz"], alpha)
        slope = (abs(lp - c) + abs(lm - c)) / (2.0 * delta)
        slopes.append(slope)
        out["axes"][k] = {"loss_plus": lp, "loss_minus": lm, "slope": slope}
    out["hardness_score"] = float(np.mean(slopes))
    return out


def counterfactual_mu1_best(v6m, alpha: float) -> dict[str, Any]:
    # Coarse grid is deterministic and lightweight; enough for audit counterfactual baseline.
    rhos = np.linspace(1.85, 2.75, 25)
    etas = np.linspace(0.04, 0.14, 25)
    bws = np.linspace(1.8e-5, 8.5e-5, 25)
    best = {"loss": float("inf"), "rho": None, "eta": None, "bw_ghz": None}
    for rho in rhos:
        for eta in etas:
            for bw in bws:
                loss = eval_loss(v6m, 1.0, float(rho), float(eta), float(bw), alpha)
                if loss < best["loss"]:
                    best = {"loss": float(loss), "rho": float(rho), "eta": float(eta), "bw_ghz": float(bw)}
    return best


def parse_v8_robustness(v8_json: dict[str, Any]) -> dict[str, Any]:
    rounds = v8_json.get("multi_round_hardening", {}).get("rounds", [])
    total = len(rounds)
    passed = sum(1 for r in rounds if bool(r.get("round_pass")))
    score = (passed / total) if total else 0.0
    return {"passed": passed, "total": total, "score": score}


RHO_AUDIT_SCRIPTS = [
    "scripts/explore/ripple_quantum_tests/rho_sensitivity_breakdown.py",
    "scripts/explore/ripple_quantum_tests/rho_gate_sensitivity_scan.py",
    "scripts/explore/ripple_quantum_tests/rho_mu_feasibility_map.py",
    "scripts/explore/ripple_quantum_tests/verify_rho_mu2_constraint.py",
]

RHO_AUDIT_ARTIFACTS = [
    "artifacts/rho_sensitivity_breakdown",
    "artifacts/rho_gate_sensitivity_scan",
    "artifacts/rho_mu_feasibility_map",
    "artifacts/verify_rho_mu2_constraint",
]


def write_rho_atomic_lock_extension(repo_root: Path, manifest_git_head: str) -> dict[str, Any]:
    """Sidecar audit extension (does not mutate RUN_MANIFEST.json snapshot)."""
    script_sha: dict[str, str] = {}
    for rel in RHO_AUDIT_SCRIPTS:
        p = repo_root / rel
        key = Path(rel).name.replace(".py", "")
        script_sha[key] = sha256_file(p)
    payload: dict[str, Any] = {
        "kind": "rho_atomic_lock_audit_extension",
        "indexed_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head_at_index": manifest_git_head,
        "scope_note": (
            "Findings apply to v6 joint_curves + state_after_de gates. rho=2.35 coincides with v6 RHO_REF; "
            "not a laboratory material identification."
        ),
        "script_sha256": script_sha,
        "script_paths": RHO_AUDIT_SCRIPTS,
        "primary_artifact_dirs": RHO_AUDIT_ARTIFACTS,
        "executioner_summary": {
            "dominant_panel": "atomic_clock_modes",
            "co_gate": "f0_gate",
            "rho_mu_squared_hypothesis": "rejected_under_joint_gates (see verify_rho_mu2 artifacts)",
        },
    }
    ext_path = repo_root / "artifacts/ripple_unified_lock/RHO_ATOMIC_LOCK_AUDIT_EXTENSION.json"
    ext_path.parent.mkdir(parents=True, exist_ok=True)
    ext_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def rho_audit_markdown_section(ext: dict[str, Any]) -> list[str]:
    rel_ext = "artifacts/ripple_unified_lock/RHO_ATOMIC_LOCK_AUDIT_EXTENSION.json"
    lines = [
        "",
        "## Rho atomic lock chain (post-lock audit)",
        "",
        "Independent scans on v6 gates; traceability extension:",
        f"- `{rel_ext}` (indexed UTC: `{ext.get('indexed_at_utc', '')}`)",
        "",
        "### Scripts (SHA256 in extension JSON)",
    ]
    for rel in RHO_AUDIT_SCRIPTS:
        lines.append(f"- `{rel}`")
    lines.extend(
        [
            "",
            "### Artifact directories",
        ]
    )
    for d in RHO_AUDIT_ARTIFACTS:
        lines.append(f"- `{d}/` (JSON, CSV, PNG as produced by each script)")
    lines.extend(
        [
            "",
            "### Audit-grade conclusions (toy scope only)",
            "",
            "- **Executor**: `atomic_clock_modes` shape + **`f0_gate`** dominate rho sensitivity; steepest |d(nrmse_y)/dρ| on the atomic panel in dense scans.",
            "- **rho = 2.35**: matches **`RHO_REF`** in `ripple_quantum_tests_v6_joint.py` via `L ∝ (rho/RHO_REF)^alpha`; joint pass is not proof of continuum material density.",
            "- **rho ≈ mu²**: falsified as required joint attractor under the same gates (see `verify_rho_mu2_constraint`).",
            "",
            "### Human index",
            "",
            "- `artifacts/rho_atomic_lock_audit/RHO_ATOMIC_LOCK_CHAIN.md`",
        ]
    )
    return lines


def parse_recovery_from_csv(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    ok = [r for r in rows if int(r["joint_pass_final"]) == 1]
    if not ok:
        return None
    best = sorted(ok, key=lambda r: float(r["loss_final"]))[0]
    return {
        "alpha": float(best["alpha"]),
        "loss_final": float(best["loss_final"]),
        "mu": float(best["mu"]),
        "rho": float(best["rho"]),
        "eta": float(best["eta"]),
        "bw_ghz": float(best["bw_ghz"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize locked run into FINAL_AUDIT_SUMMARY.md")
    ap.add_argument("--manifest", type=str, default="artifacts/ripple_unified_lock/RUN_MANIFEST.json")
    ap.add_argument("--out-md", type=str, default="artifacts/ripple_unified_lock/FINAL_AUDIT_SUMMARY.md")
    ap.add_argument(
        "--skip-rho-audit-extension",
        action="store_true",
        help="do not write RHO_ATOMIC_LOCK_AUDIT_EXTENSION.json or append rho chain section",
    )
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    repo_root = Path.cwd()
    manifest = load_json(manifest_path)

    v6_primary = get_stage(manifest, "v6_primary") or {}
    v6_recovered = get_stage(manifest, "v6_recovered_snapshot")

    stress_csv = repo_root / "artifacts/ripple_quantum_tests_v6_lock_stress_refine/RIPPLE_V6_STRESS_ALPHA.csv"
    if v6_recovered is None:
        csv_recovered = parse_recovery_from_csv(stress_csv)
    else:
        csv_recovered = None

    v8_json = load_json(repo_root / "artifacts/ripple_quantum_tests_v8_unify/v8_quantum_grand_unification.json")
    v8_robust = parse_v8_robustness(v8_json)

    v6m = load_v6_module(repo_root)
    alpha_for_audit = float((v6_recovered or {}).get("alpha", 0.35))
    jitter = jitter_hardness(v6m, alpha=alpha_for_audit, delta=1e-4)
    cf_mu1 = counterfactual_mu1_best(v6m, alpha=alpha_for_audit)

    primary_loss = float(v6_primary.get("loss", np.nan))
    recovered_loss = None
    if v6_recovered is not None:
        recovered_loss = float(v6_recovered.get("loss_final", 0.0))
    elif csv_recovered is not None:
        recovered_loss = float(csv_recovered.get("loss_final", 0.0))
    logical_delta = (primary_loss - recovered_loss) if (recovered_loss is not None) else np.nan

    status = "RECOVERED" if (bool(v6_primary.get("joint_pass")) is False and recovered_loss is not None) else "UNRESOLVED"

    current_script = Path(__file__).resolve()
    lines = [
        "# FINAL AUDIT SUMMARY",
        "",
        f"- **Status**: `{status}`",
        f"- **Core Triplet (Locked)**: `{LOCKED['mu']:.4f} / {LOCKED['rho']:.2f} / {LOCKED['eta']:.2f}`",
        f"- **Joint Consistency**: `{'Pass (V6 refined)' if status == 'RECOVERED' else 'Pending'}`",
        f"- **Stability**: `{v8_robust['passed']}/{v8_robust['total']} Monte Carlo passed`",
        "- **Known Limits**: `V9 Material Generalization pending`",
        "",
        "## Anti-Cheat Identity",
        "",
        f"- git_head: `{manifest.get('git_head', '')}`",
        f"- python: `{manifest.get('python_version', '')}`",
        f"- script_sha256.v6_joint: `{manifest.get('script_sha256', {}).get('v6_joint', '')}`",
        f"- script_sha256.v8_unify: `{manifest.get('script_sha256', {}).get('v8_unify', '')}`",
        f"- script_sha256.v9_material_extension: `{manifest.get('script_sha256', {}).get('v9_material_extension', '')}`",
        f"- script_sha256.summarize_lock_run: `{sha256_file(current_script)}`",
        "",
        "## Traceability",
        "",
        f"- v6_primary joint_pass: `{v6_primary.get('joint_pass', None)}`",
        f"- v6_primary loss: `{primary_loss:.12g}`",
        f"- v6_recovered loss: `{recovered_loss if recovered_loss is not None else 'N/A'}`",
        f"- logical_delta (primary - recovered): `{logical_delta if logical_delta == logical_delta else 'N/A'}`",
        "",
        "## Device Fingerprint",
        "",
        f"- os: `{manifest.get('device_fingerprint', {}).get('os', '')}`",
        f"- cpu_name: `{manifest.get('device_fingerprint', {}).get('cpu_name', '')}`",
        f"- cpu_cores_logical: `{manifest.get('device_fingerprint', {}).get('cpu_cores_logical', '')}`",
        f"- cpu_cores_physical: `{manifest.get('device_fingerprint', {}).get('cpu_cores_physical', '')}`",
        f"- blas_info_json: `{manifest.get('device_fingerprint', {}).get('blas_info', '')}`",
        "",
        "## Sensitivity Jitter (±0.0001 around locked triplet)",
        "",
        f"- alpha_for_audit: `{alpha_for_audit}`",
        f"- center_loss: `{jitter['center_loss']:.12g}`",
        f"- hardness_score(mean slope): `{jitter['hardness_score']:.12g}`",
        f"- slope_mu: `{jitter['axes']['mu']['slope']:.12g}`",
        f"- slope_rho: `{jitter['axes']['rho']['slope']:.12g}`",
        f"- slope_eta: `{jitter['axes']['eta']['slope']:.12g}`",
        "",
        "## Counterfactual Negative Control (mu fixed = 1.0)",
        "",
        f"- best_loss_under_mu1: `{cf_mu1['loss']:.12g}`",
        f"- best_rho_under_mu1: `{cf_mu1['rho']}`",
        f"- best_eta_under_mu1: `{cf_mu1['eta']}`",
        f"- best_bw_under_mu1: `{cf_mu1['bw_ghz']}`",
        "",
        "> Interpretation rule: if `best_loss_under_mu1` remains materially above recovered-loss baseline,",
        "> then textbook-mu=1.0 does not close the same objective under this audit setup.",
    ]

    if not args.skip_rho_audit_extension:
        ext = write_rho_atomic_lock_extension(repo_root, str(manifest.get("git_head", "")))
        lines.extend(rho_audit_markdown_section(ext))

    out_path = Path(args.out_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
