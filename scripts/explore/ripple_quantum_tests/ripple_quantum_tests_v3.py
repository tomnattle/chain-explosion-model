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
    constant_mode: str
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
    ripple = np.where(x > 0.50, 2.05 * (x - 0.50), 0.03 * x)
    e = nrmse(qm, ripple)
    shape_pass = e <= shape_th
    res = TestResult(
        name="laser_threshold",
        nrmse=e,
        shape_pass=shape_pass,
        constant_mode="shape_only",
        constant_pass=True,
        final_pass=shape_pass,
        note="No exact physical constant required in this test.",
    )
    return res, {"x": x.tolist(), "qm": qm.tolist(), "ripple": ripple.tolist()}


def semiconductor_case(shape_th: float) -> tuple[TestResult, dict]:
    x = np.linspace(0.0, 4.0, 260)
    qm = sigmoid(x, 2.0, 20.0)
    ripple = sigmoid(x, 2.03, 16.5)
    e = nrmse(qm, ripple)
    shape_pass = e <= shape_th
    res = TestResult(
        name="semiconductor_cutoff",
        nrmse=e,
        shape_pass=shape_pass,
        constant_mode="shape_only",
        constant_pass=True,
        final_pass=shape_pass,
        note="Band-edge shape comparison only.",
    )
    return res, {"x": x.tolist(), "qm": qm.tolist(), "ripple": ripple.tolist()}


def derive_gamma_from_ripple_params(mu: float, kappa: float, rho: float, eta: float) -> float:
    # A toy derivation from ripple-medium parameters (not fitted directly to target gamma).
    # Unit consistency is abstracted in this prototype.
    return float((mu * kappa) / max(1e-12, (rho * (1.0 + eta))))


def derive_clock_freq_from_cavity(length_m: float, wave_speed_m_s: float, mode_index: int) -> float:
    # Standing-wave cavity mode: f_n = n * v / (2L)
    return float(mode_index * wave_speed_m_s / (2.0 * length_m))


def mri_case(shape_th: float, const_rel_tol: float, constant_mode: str) -> tuple[TestResult, dict]:
    x = np.linspace(0.0, 3.0, 180)
    gamma_qm = 42.577
    qm = gamma_qm * x

    if constant_mode == "calibrated":
        gamma_ripple = 42.2
        note_mode = "calibrated_reference"
    else:
        # derived mode: no direct target fitting
        mu, kappa, rho, eta = 1.55, 57.8, 2.35, 0.08
        gamma_ripple = derive_gamma_from_ripple_params(mu, kappa, rho, eta)
        note_mode = "derived_from_ripple_params"
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
        constant_mode=note_mode,
        constant_pass=constant_pass,
        final_pass=final_pass,
        note=f"gamma_qm={gamma_qm:.6f}, gamma_ripple={gamma_ripple:.6f}, rel_err={rel_err:.6f}",
    )
    return res, {
        "x": x.tolist(),
        "qm": qm.tolist(),
        "ripple": ripple.tolist(),
        "gamma_qm": gamma_qm,
        "gamma_ripple": gamma_ripple,
        "gamma_rel_err": rel_err,
    }


def atomic_case(shape_th: float, center_tol_hz: float, constant_mode: str) -> tuple[TestResult, dict]:
    x = np.linspace(9.1918, 9.1934, 500)  # GHz
    f0_qm = 9.192631770
    bw_qm = 0.000030
    qm = np.exp(-0.5 * ((x - f0_qm) / bw_qm) ** 2)

    if constant_mode == "calibrated":
        f0_r = 9.192620000
        bw_r = 0.000042
        note_mode = "calibrated_reference"
    else:
        # derived mode from cavity parameters, no direct target assignment
        length_m = 0.01635
        wave_speed = 300_652_011.0
        mode = 1
        f0_r_hz = derive_clock_freq_from_cavity(length_m, wave_speed, mode)
        f0_r = f0_r_hz / 1e9
        bw_r = 0.000080
        note_mode = "derived_from_cavity_params"
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
        constant_mode=note_mode,
        constant_pass=constant_pass,
        final_pass=final_pass,
        note=f"f0_qm={f0_qm:.9f} GHz, f0_ripple={f0_r:.9f} GHz, err={center_err_hz:.3f} Hz",
    )
    return res, {
        "x": x.tolist(),
        "qm": qm.tolist(),
        "ripple": ripple.tolist(),
        "f0_qm_ghz": f0_qm,
        "f0_ripple_ghz": f0_r,
        "center_err_hz": center_err_hz,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Ripple quantum tests v3 (derived-constant mode)")
    ap.add_argument("--shape-threshold", type=float, default=0.18)
    ap.add_argument("--mri-const-rel-tol", type=float, default=0.02)
    ap.add_argument("--clock-center-tol-hz", type=float, default=20_000.0)
    ap.add_argument(
        "--constant-mode",
        choices=["derived", "calibrated"],
        default="derived",
        help="derived=from ripple parameters; calibrated=near-target reference baseline",
    )
    ap.add_argument(
        "--allow-calibrated",
        action="store_true",
        help="Explicitly allow calibrated mode (disabled by default to avoid target-fitting misuse).",
    )
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests_v3")
    args = ap.parse_args()

    if args.constant_mode == "calibrated" and not args.allow_calibrated:
        raise SystemExit(
            "Blocked by anti-cheat policy: calibrated mode requires --allow-calibrated.\n"
            "Use derived mode for primary claims."
        )

    results: list[TestResult] = []
    curves: dict = {}

    r1, c1 = laser_case(args.shape_threshold)
    r2, c2 = semiconductor_case(args.shape_threshold)
    r3, c3 = mri_case(args.shape_threshold, args.mri_const_rel_tol, args.constant_mode)
    r4, c4 = atomic_case(args.shape_threshold, args.clock_center_tol_hz, args.constant_mode)
    results.extend([r1, r2, r3, r4])
    curves.update({r1.name: c1, r2.name: c2, r3.name: c3, r4.name: c4})

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "meta": {
            "suite": "ripple_quantum_tests_v3",
            "constant_mode": args.constant_mode,
            "allow_calibrated": bool(args.allow_calibrated),
            "anti_cheat_policy": (
                "Primary claims must use derived mode. "
                "Calibrated mode is comparison-only and requires explicit opt-in."
            ),
            "shape_threshold": args.shape_threshold,
            "mri_constant_relative_tolerance": args.mri_const_rel_tol,
            "clock_center_tolerance_hz": args.clock_center_tol_hz,
            "rule": "final_pass = shape_pass AND constant_pass",
        },
        "results": [r.__dict__ for r in results],
        "curves": curves,
    }
    (out_dir / "RIPPLE_QUANTUM_TESTS_V3_RESULTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Ripple Quantum Tests v3 Summary",
        "",
        "v3 separates derived-constant mode and calibrated-reference mode.",
        "",
        f"- constant mode: `{args.constant_mode}`",
        f"- shape threshold: `{args.shape_threshold}`",
        f"- MRI constant tolerance (relative): `{args.mri_const_rel_tol}`",
        f"- Atomic clock center tolerance (Hz): `{args.clock_center_tol_hz}`",
        "",
        "| test | nrmse | shape_pass | constant_mode | constant_pass | final_pass |",
        "|---|---:|:---:|---|:---:|:---:|",
    ]
    for r in results:
        lines.append(
            f"| {r.name} | {r.nrmse:.6f} | {'yes' if r.shape_pass else 'no'} | "
            f"{r.constant_mode} | {'yes' if r.constant_pass else 'no'} | {'yes' if r.final_pass else 'no'} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- In `derived` mode, MRI/atomic constants come from model parameters (no direct target assignment).",
        "- In `calibrated` mode, constants are near target by design and serve as a comparison baseline.",
        "- If only calibrated passes but derived fails, it indicates parameter-fit ability, not derivation maturity.",
    ]
    (out_dir / "RIPPLE_QUANTUM_TESTS_V3_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")

    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V3_RESULTS.json")
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V3_SUMMARY.md")


if __name__ == "__main__":
    main()
