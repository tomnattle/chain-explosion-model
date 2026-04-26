#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class TestResult:
    name: str
    nrmse: float
    shape_pass: bool
    constant_claim_level: str
    constant_pass: bool
    final_pass: bool
    note: str


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def nrmse(a: np.ndarray, b: np.ndarray) -> float:
    s = float(np.max(a) - np.min(a))
    if s < 1e-12:
        s = 1.0
    return rmse(a, b) / s


def sigmoid(x: np.ndarray, c: float, k: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-k * (x - c)))


def laser_case(shape_th: float) -> tuple[TestResult, dict]:
    x = np.linspace(0.0, 1.0, 240)
    qm = np.where(x > 0.50, 2.2 * (x - 0.50), 0.02 * x)
    ripple = np.where(x > 0.50, 2.10 * (x - 0.50), 0.03 * x)
    e = nrmse(qm, ripple)
    shape_pass = e <= shape_th
    res = TestResult(
        name="laser_threshold",
        nrmse=e,
        shape_pass=shape_pass,
        constant_claim_level="shape_only",
        constant_pass=True,
        final_pass=shape_pass,
        note="Threshold shape comparison only.",
    )
    return res, {"x": x.tolist(), "qm": qm.tolist(), "ripple": ripple.tolist()}


def semiconductor_case(shape_th: float) -> tuple[TestResult, dict]:
    x = np.linspace(0.0, 4.0, 260)
    qm = sigmoid(x, 2.0, 20.0)
    ripple = sigmoid(x, 2.02, 17.5)
    e = nrmse(qm, ripple)
    shape_pass = e <= shape_th
    res = TestResult(
        name="semiconductor_cutoff",
        nrmse=e,
        shape_pass=shape_pass,
        constant_claim_level="shape_only",
        constant_pass=True,
        final_pass=shape_pass,
        note="Cutoff-shape comparison only.",
    )
    return res, {"x": x.tolist(), "qm": qm.tolist(), "ripple": ripple.tolist()}


def mri_case(shape_th: float, const_rel_tol: float) -> tuple[TestResult, dict]:
    x = np.linspace(0.0, 3.0, 180)
    gamma_qm = 42.577
    qm = gamma_qm * x

    # Ripple v2: explicit "derived constant" placeholder from model block.
    # Currently still treated as assumed model constant (not first-principles proved).
    gamma_ripple = 42.2
    ripple = gamma_ripple * x + 0.02 * x**2

    e = nrmse(qm, ripple)
    shape_pass = e <= shape_th
    rel_err = abs(gamma_ripple - gamma_qm) / gamma_qm
    constant_pass = rel_err <= const_rel_tol
    final_pass = shape_pass and constant_pass
    res = TestResult(
        name="mri_larmor",
        nrmse=e,
        shape_pass=shape_pass,
        constant_claim_level="approx_constant_match",
        constant_pass=constant_pass,
        final_pass=final_pass,
        note=f"gamma relative error={rel_err:.6f}",
    )
    extra = {
        "x": x.tolist(),
        "qm": qm.tolist(),
        "ripple": ripple.tolist(),
        "gamma_qm": gamma_qm,
        "gamma_ripple": gamma_ripple,
        "gamma_rel_err": rel_err,
    }
    return res, extra


def atomic_clock_case(shape_th: float, center_tol_hz: float) -> tuple[TestResult, dict]:
    x = np.linspace(9.1918, 9.1934, 500)  # GHz
    f0_qm = 9.192631770
    bw_qm = 0.000030
    qm = np.exp(-0.5 * ((x - f0_qm) / bw_qm) ** 2)

    # Ripple v2: cavity-mode surrogate center/fwhm from assumed parameters.
    f0_r = 9.192620000
    bw_r = 0.000042
    ripple = np.exp(-0.5 * ((x - f0_r) / bw_r) ** 2)

    e = nrmse(qm, ripple)
    shape_pass = e <= shape_th
    center_err_hz = abs(f0_r - f0_qm) * 1e9
    constant_pass = center_err_hz <= center_tol_hz
    final_pass = shape_pass and constant_pass
    res = TestResult(
        name="atomic_clock_modes",
        nrmse=e,
        shape_pass=shape_pass,
        constant_claim_level="approx_center_match",
        constant_pass=constant_pass,
        final_pass=final_pass,
        note=f"center frequency error={center_err_hz:.3f} Hz",
    )
    extra = {
        "x": x.tolist(),
        "qm": qm.tolist(),
        "ripple": ripple.tolist(),
        "f0_qm_ghz": f0_qm,
        "f0_ripple_ghz": f0_r,
        "center_err_hz": center_err_hz,
    }
    return res, extra


def main() -> None:
    ap = argparse.ArgumentParser(description="Ripple quantum tests v2 (shape + constant checks)")
    ap.add_argument("--shape-threshold", type=float, default=0.18)
    ap.add_argument("--mri-const-rel-tol", type=float, default=0.02)
    ap.add_argument("--clock-center-tol-hz", type=float, default=20_000.0)
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests_v2")
    args = ap.parse_args()

    results = []
    curves = {}

    r1, c1 = laser_case(args.shape_threshold)
    r2, c2 = semiconductor_case(args.shape_threshold)
    r3, c3 = mri_case(args.shape_threshold, args.mri_const_rel_tol)
    r4, c4 = atomic_clock_case(args.shape_threshold, args.clock_center_tol_hz)
    results.extend([r1, r2, r3, r4])
    curves.update({r1.name: c1, r2.name: c2, r3.name: c3, r4.name: c4})

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    js = {
        "meta": {
            "suite": "ripple_quantum_tests_v2",
            "shape_threshold": args.shape_threshold,
            "mri_constant_relative_tolerance": args.mri_const_rel_tol,
            "clock_center_tolerance_hz": args.clock_center_tol_hz,
            "rule": "final_pass = shape_pass AND constant_pass",
        },
        "results": [r.__dict__ for r in results],
        "curves": curves,
    }
    (out_dir / "RIPPLE_QUANTUM_TESTS_V2_RESULTS.json").write_text(json.dumps(js, indent=2), encoding="utf-8")

    lines = [
        "# Ripple Quantum Tests v2 Summary",
        "",
        "This version separates shape similarity from constant-level checks.",
        "",
        f"- shape threshold: `{args.shape_threshold}`",
        f"- MRI constant tolerance (relative): `{args.mri_const_rel_tol}`",
        f"- Atomic clock center tolerance (Hz): `{args.clock_center_tol_hz}`",
        "",
        "| test | nrmse | shape_pass | constant_pass | final_pass | note |",
        "|---|---:|:---:|:---:|:---:|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.name} | {r.nrmse:.6f} | {'yes' if r.shape_pass else 'no'} | "
            f"{'yes' if r.constant_pass else 'no'} | {'yes' if r.final_pass else 'no'} | {r.note} |"
        )
    lines += [
        "",
        "## Reading Guide",
        "",
        "- `shape_pass` only means curve-shape compatibility.",
        "- `constant_pass` checks whether key constants are also close enough.",
        "- This still does not claim first-principles derivation unless a dedicated derivation module is added.",
    ]
    (out_dir / "RIPPLE_QUANTUM_TESTS_V2_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V2_RESULTS.json")
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V2_SUMMARY.md")


if __name__ == "__main__":
    main()
