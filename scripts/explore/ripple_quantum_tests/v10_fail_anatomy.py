#!/usr/bin/env python3
"""
v10 — Failure anatomy (additive). Assume locked triplet semantics are OK; hunt for
implementation / function-family / data-consistency issues behind V9 gate failures.

Reads the same CSV layout as v9_realdata_runner.py:
  dispersion_n_omega.csv, absorption_alpha_omega.csv,
  reflectance_r_theta.csv, group_delay_tau_omega.csv
Each file: columns x,y (sorted by x).

Outputs:
  artifacts/ripple_quantum_tests_v10_fail_anatomy/V10_FAIL_ANATOMY.json
  artifacts/ripple_quantum_tests_v10_fail_anatomy/V10_FAIL_ANATOMY.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

LOCKED = {"mu": 1.55, "rho": 2.35, "eta": 0.08}


def load_xy(path: Path) -> tuple[np.ndarray, np.ndarray]:
    xs: list[float] = []
    ys: list[float] = []
    with path.open("r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if not rd.fieldnames or "x" not in rd.fieldnames or "y" not in rd.fieldnames:
            raise ValueError(f"{path} must have columns x,y")
        for row in rd:
            xs.append(float(row["x"]))
            ys.append(float(row["y"]))
    x = np.array(xs, dtype=float)
    y = np.array(ys, dtype=float)
    o = np.argsort(x)
    return x[o], y[o]


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 3 or b.size < 3:
        return float("nan")
    a = a - np.mean(a)
    b = b - np.mean(b)
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    if den < 1e-18:
        return float("nan")
    return float(np.dot(a, b) / den)


def rip_absorption(x: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    u = x / max(float(np.max(x)), 1e-9)
    y = 0.015 + 0.18 * max(eta, 1e-9) / max(rho, 1e-9) + 0.06 / math.sqrt(max(mu, 1e-9)) * u**1.8
    return np.maximum(y, 0.0)


def rip_dispersion(x: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    u = x / max(float(np.max(x)), 1e-9)
    return (
        1.0
        + 0.32 * math.sqrt(max(rho, 1e-9) / max(mu, 1e-9))
        + 0.06 * (1.0 + 0.6 * eta) * u**2
        + 0.01 * u**4
    )


def rip_group_delay_model(x: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    u = x / max(float(np.max(x)), 1e-9)
    return 1.0 + 0.18 * math.sqrt(max(mu, 1e-9) / max(rho, 1e-9)) * u + 0.10 * (1.0 + 0.4 * eta) * u**2


def nrmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    span = float(np.max(y_true) - np.min(y_true))
    return rmse / max(span, 1e-12)


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    c = y_true - float(np.mean(y_true))
    ss_tot = float(np.sum(c**2))
    if ss_tot < 1e-24:
        return 1.0 if ss_res < 1e-24 else 0.0
    return float(1.0 - ss_res / ss_tot)


def peak_score(y: np.ndarray) -> dict[str, Any]:
    """Heuristic: large second derivative energy => sharp features / resonance-like."""
    if y.size < 5:
        return {"d2y_rms": 0.0, "note": "too_few_points"}
    d2 = np.diff(y, n=2)
    return {"d2y_rms": float(np.sqrt(np.mean(d2**2))), "n_points": int(y.size)}


def lorentz_residual_fit(x: np.ndarray, residual: np.ndarray) -> dict[str, Any]:
    """
    Grid search one Lorentz bump on residual r(x):
      bump = A * w^2 / ((x-x0)^2 + w^2)
    Not a full MLE; diagnostic only.
    """
    if x.size < 8:
        return {"skipped": True, "reason": "too_few_points"}
    x0_grid = np.linspace(float(np.min(x)), float(np.max(x)), 12)
    w_grid = np.linspace((float(np.max(x)) - float(np.min(x))) * 0.02, (float(np.max(x)) - float(np.min(x))) * 0.25, 8)
    best = {"mse": float("inf"), "x0": None, "w": None, "A": None}
    base = rip_absorption(x, LOCKED["mu"], LOCKED["rho"], LOCKED["eta"])
    for x0 in x0_grid:
        for w in w_grid:
            if w < 1e-9:
                continue
            denom = (x - x0) ** 2 + w**2
            bump = (w**2) / denom
            # least squares for A: residual ~ A * bump
            num = float(np.dot(residual, bump))
            den = float(np.dot(bump, bump)) + 1e-18
            A = num / den
            pred = base + A * bump
            mse = float(np.mean((pred - (base + residual)) ** 2))
            if mse < best["mse"]:
                best = {"mse": mse, "x0": float(x0), "w": float(w), "A": float(A)}
    r_full = residual  # y - base
    y_data = base + r_full
    pred_best = base + best["A"] * ((best["w"] ** 2) / ((x - best["x0"]) ** 2 + best["w"] ** 2))
    return {
        "skipped": False,
        "best_x0": best["x0"],
        "best_w": best["w"],
        "best_A": best["A"],
        "r2_after_lorentz_on_full": r2(y_data, pred_best),
        "nrmse_after_on_full": nrmse(y_data, pred_best),
    }


def group_delay_consistency_audit(x_n: np.ndarray, n: np.ndarray, x_tau: np.ndarray, tau: np.ndarray) -> dict[str, Any]:
    """
    Heuristic audit: compare shape of tau(omega) with |dn/domega| (same omega grid if aligned).
    If CSVs use different x grids, interpolate n onto x_tau.
    """
    dn = np.gradient(n, x_n, edge_order=2)
    n_on_tau = np.interp(x_tau, x_n, n)
    dn_on_tau = np.interp(x_tau, x_n, dn)
    model_tau = rip_group_delay_model(x_tau, LOCKED["mu"], LOCKED["rho"], LOCKED["eta"])
    return {
        "corr_tau_vs_abs_dn": pearson(tau, np.abs(dn_on_tau)),
        "corr_tau_vs_dn": pearson(tau, dn_on_tau),
        "corr_tau_vs_model_tau": pearson(tau, model_tau),
        "note": "dn/domega is central to group delay; low corr suggests x-axis mismatch or missing phi(omega) link.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="v10 failure anatomy for V9 realdata inputs")
    ap.add_argument("--data-dir", type=str, default="artifacts/ripple_quantum_tests_v9_realdata_input_template")
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests_v10_fail_anatomy")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    x_n, y_n = load_xy(data_dir / "dispersion_n_omega.csv")
    x_a, y_a = load_xy(data_dir / "absorption_alpha_omega.csv")
    x_r, y_r = load_xy(data_dir / "reflectance_r_theta.csv")
    x_t, y_t = load_xy(data_dir / "group_delay_tau_omega.csv")

    mu, rho, eta = LOCKED["mu"], LOCKED["rho"], LOCKED["eta"]
    pred_a = rip_absorption(x_a, mu, rho, eta)
    pred_t = rip_group_delay_model(x_t, mu, rho, eta)
    pred_n = rip_dispersion(x_n, mu, rho, eta)

    res_a = y_a - pred_a
    res_t = y_t - pred_t

    payload: dict[str, Any] = {
        "meta": {
            "suite": "ripple_quantum_tests_v10_fail_anatomy",
            "data_dir": str(data_dir.as_posix()),
            "locked_triplet": LOCKED,
            "assumption": "Triplet semantics OK; diagnose function family / data / cross-panel consistency.",
        },
        "absorption": {
            "peak_metrics": peak_score(y_a),
            "locked_triplet_full_r2": r2(y_a, pred_a),
            "locked_triplet_full_nrmse": nrmse(y_a, pred_a),
            "residual_mean": float(np.mean(res_a)),
            "residual_std": float(np.std(res_a)),
            "lorentz_on_residual": lorentz_residual_fit(x_a, res_a),
            "diagnosis": [],
        },
        "group_delay": {
            "locked_triplet_full_r2": r2(y_t, pred_t),
            "locked_triplet_full_nrmse": nrmse(y_t, pred_t),
            "consistency_with_dispersion": group_delay_consistency_audit(x_n, y_n, x_t, y_t),
            "diagnosis": [],
        },
        "dispersion": {
            "locked_triplet_full_r2": r2(y_n, pred_n),
            "locked_triplet_full_nrmse": nrmse(y_n, pred_n),
        },
        "reflectance": {
            "note": "Usually passes gate; listed for completeness.",
            "locked_triplet_full_r2": r2(y_r, y_r * 0 + np.mean(y_r)),  # placeholder avoid unused
        },
    }

    def rip_refl(theta: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
        ct = np.cos(theta)
        y = 0.02 + (0.14 * math.sqrt(max(rho, 1e-9) / max(mu, 1e-9)) + 0.04 * eta) * (1 - ct) ** 1.3
        return np.clip(y, 0.0, 1.0)

    pred_r = rip_refl(x_r, mu, rho, eta)
    payload["reflectance"] = {
        "locked_triplet_full_r2": r2(y_r, pred_r),
        "locked_triplet_full_nrmse": nrmse(y_r, pred_r),
    }

    # Diagnosis bullets
    if payload["absorption"]["peak_metrics"]["d2y_rms"] > 0.02:
        payload["absorption"]["diagnosis"].append(
            "Absorption y(x) has non-trivial curvature energy; single smooth power-law may be structurally underfitting."
        )
    lorentz = payload["absorption"]["lorentz_on_residual"]
    if not lorentz.get("skipped") and lorentz.get("r2_after_lorentz_on_full", -1) > r2(y_a, pred_a) + 0.05:
        payload["absorption"]["diagnosis"].append(
            "Diagnostic Lorentz bump materially reduces error at LOCKED triplet → missing resonance/broadband loss term in alpha(omega)."
        )
    if r2(y_a, pred_a) < 0.5:
        payload["absorption"]["diagnosis"].append(
            "At locked triplet, absorption R² is poor on full span → formula family mismatch before any re-optimization."
        )

    cons = payload["group_delay"]["consistency_with_dispersion"]
    if not math.isnan(cons["corr_tau_vs_abs_dn"]) and abs(cons["corr_tau_vs_abs_dn"]) < 0.3:
        payload["group_delay"]["diagnosis"].append(
            "Low correlation between tau(omega) and |dn/domega| on aligned grid → group_delay CSV may not be Kramers-Kronig-consistent with dispersion CSV, or tau is not dφ/dω in the same units."
        )
    if r2(y_t, pred_t) < 0.1:
        payload["group_delay"]["diagnosis"].append(
            "Current rip_group_delay is low-order polynomial in normalized omega; data may need phase-derived tau_g = dφ/dω linkage."
        )

    (out_dir / "V10_FAIL_ANATOMY.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# V10 Failure Anatomy",
        "",
        f"- data_dir: `{data_dir.as_posix()}`",
        f"- locked triplet: μ={mu}, ρ={rho}, η={eta}",
        "",
        "## Absorption",
        f"- full-span R² (locked): `{payload['absorption']['locked_triplet_full_r2']:.6f}`",
        f"- full-span NRMSE (locked): `{payload['absorption']['locked_triplet_full_nrmse']:.6f}`",
        f"- d2y RMS (curvature proxy): `{payload['absorption']['peak_metrics']['d2y_rms']:.6g}`",
        "",
        "**Diagnosis:**",
    ]
    for line in payload["absorption"]["diagnosis"] or ["(none — check Lorentz diagnostic in JSON)"]:
        md.append(f"- {line}")
    md += [
        "",
        "## Group delay",
        f"- full-span R² (locked): `{payload['group_delay']['locked_triplet_full_r2']:.6f}`",
        f"- corr(tau, |dn/dω|): `{cons['corr_tau_vs_abs_dn']}`",
        f"- corr(tau, model_tau): `{cons['corr_tau_vs_model_tau']}`",
        "",
        "**Diagnosis:**",
    ]
    for line in payload["group_delay"]["diagnosis"] or ["(none)"]:
        md.append(f"- {line}")

    md += [
        "",
        "## Dispersion (reference)",
        f"- full-span R² (locked): `{payload['dispersion']['locked_triplet_full_r2']:.6f}`",
        "",
        "## Reflectance",
        f"- full-span R² (locked): `{payload['reflectance']['locked_triplet_full_r2']:.6f}`",
        "",
        "## Next step (v10 → v11)",
        "- If Lorentz diagnostic helps: extend alpha(omega) with a bounded oscillator term (audit-only branch).",
        "- If tau vs dn/dω decorrelates: regenerate group_delay from a single phase model or unify omega grid and units.",
    ]

    (out_dir / "V10_FAIL_ANATOMY.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote", out_dir / "V10_FAIL_ANATOMY.json")
    print("wrote", out_dir / "V10_FAIL_ANATOMY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
