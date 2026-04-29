#!/usr/bin/env python3
"""
Ripple quantum tests v9 (material extension, additive only).

Design goal:
- Do NOT modify existing v6/v7/v8 scripts.
- Add a parallel, standalone pipeline for material-property approximation.
- Introduce multiple experiments with explicit fit/val/blind split.

This script is a methodological extension scaffold, not a first-principles proof.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np

try:
    from scipy.optimize import differential_evolution
except Exception:  # pragma: no cover
    differential_evolution = None


# Locked point from earlier pipeline as default anchor (can be changed by CLI)
MU0 = 1.5495
RHO0 = 2.35
ETA0 = 0.08

OUT_DIR_DEFAULT = Path("artifacts/ripple_quantum_tests_v9_material")


def nrmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    diff = y_true - y_pred
    rmse = float(np.sqrt(np.mean(diff**2)))
    span = float(np.max(y_true) - np.min(y_true))
    if span < 1e-12:
        span = 1.0
    return rmse / span


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    centered = y_true - float(np.mean(y_true))
    ss_tot = float(np.sum(centered**2))
    if ss_tot < 1e-12:
        return 1.0 if ss_res < 1e-12 else 0.0
    return float(1.0 - ss_res / ss_tot)


def split_indices(n: int, fit_ratio: float, val_ratio: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    i_fit = int(max(1, min(n - 2, round(n * fit_ratio))))
    i_val = int(max(i_fit + 1, min(n - 1, round(n * (fit_ratio + val_ratio)))))
    idx = np.arange(n)
    return idx[:i_fit], idx[i_fit:i_val], idx[i_val:]


# ---- Experiment references (standalone proxies) ----
def ref_dispersion_n_omega(w: np.ndarray) -> np.ndarray:
    # Smooth Cauchy-like proxy curve for refractive index vs frequency
    x = w / float(np.max(w))
    return 1.45 + 0.08 * x**2 + 0.02 * x**4


def ref_absorption_alpha_omega(w: np.ndarray) -> np.ndarray:
    # Non-negative absorption proxy with gentle rise
    x = w / float(np.max(w))
    return 0.01 + 0.10 * x**1.7


def ref_reflectance_r_theta(theta: np.ndarray) -> np.ndarray:
    # Angle-dependent reflectance proxy
    ct = np.cos(theta)
    return np.clip(0.03 + 0.18 * (1.0 - ct) ** 1.4, 0.0, 1.0)


def ref_group_delay_tau_omega(w: np.ndarray) -> np.ndarray:
    # Group delay proxy (arbitrary units)
    x = w / float(np.max(w))
    return 1.0 + 0.25 * x + 0.12 * x**2


# ---- Ripple-side parametric approximators ----
def rip_dispersion_n_omega(w: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    x = w / float(np.max(w))
    base = 1.0 + 0.32 * np.sqrt(max(rho, 1e-9) / max(mu, 1e-9))
    bend = 0.06 * (1.0 + 0.6 * (eta - ETA0))
    return base + bend * x**2 + 0.01 * x**4


def rip_absorption_alpha_omega(w: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    x = w / float(np.max(w))
    scale = 0.015 + 0.18 * max(eta, 1e-9) / max(rho, 1e-9)
    stiff = 0.06 / np.sqrt(max(mu, 1e-9))
    y = scale + stiff * x**1.8
    return np.maximum(y, 0.0)


def rip_reflectance_r_theta(theta: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    ct = np.cos(theta)
    amp = 0.14 * np.sqrt(max(rho, 1e-9) / max(mu, 1e-9))
    eta_term = 0.04 * (eta / max(ETA0, 1e-9))
    y = 0.02 + (amp + eta_term) * (1.0 - ct) ** 1.3
    return np.clip(y, 0.0, 1.0)


def rip_group_delay_tau_omega(w: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    x = w / float(np.max(w))
    slope = 0.18 * np.sqrt(max(mu, 1e-9) / max(rho, 1e-9))
    curv = 0.10 * (1.0 + 0.4 * eta)
    return 1.0 + slope * x + curv * x**2


@dataclass
class Experiment:
    name: str
    axis: np.ndarray
    ref_fn: Callable[[np.ndarray], np.ndarray]
    rip_fn: Callable[[np.ndarray, float, float, float], np.ndarray]
    weight: float


def build_experiments() -> list[Experiment]:
    omega = np.linspace(1.0, 10.0, 240)
    theta = np.linspace(0.0, np.pi / 2.0, 200)
    return [
        Experiment("dispersion_n_omega", omega, ref_dispersion_n_omega, rip_dispersion_n_omega, 1.0),
        Experiment("absorption_alpha_omega", omega, ref_absorption_alpha_omega, rip_absorption_alpha_omega, 1.0),
        Experiment("reflectance_r_theta", theta, ref_reflectance_r_theta, rip_reflectance_r_theta, 0.9),
        Experiment("group_delay_tau_omega", omega, ref_group_delay_tau_omega, rip_group_delay_tau_omega, 0.9),
    ]


def objective(
    vec: np.ndarray,
    exps: list[Experiment],
    fit_ratio: float,
    val_ratio: float,
    penalty_energy: float,
) -> float:
    mu, rho, eta = float(vec[0]), float(vec[1]), float(vec[2])
    total = 0.0
    for e in exps:
        y_ref = e.ref_fn(e.axis)
        y_rip = e.rip_fn(e.axis, mu, rho, eta)
        fit_idx, _, _ = split_indices(len(e.axis), fit_ratio, val_ratio)
        total += e.weight * nrmse(y_ref[fit_idx], y_rip[fit_idx])

        # Soft physics-inspired penalty: reflectance + absorption should not exceed 1 by too much
        if e.name == "reflectance_r_theta":
            alpha = rip_absorption_alpha_omega(np.linspace(1.0, 10.0, len(e.axis)), mu, rho, eta)
            excess = np.maximum((y_rip + alpha) - 1.0, 0.0)
            total += penalty_energy * float(np.mean(excess**2))
    return float(total)


def run_de(
    exps: list[Experiment],
    fit_ratio: float,
    val_ratio: float,
    seed: int,
    maxiter: int,
    bounds: list[tuple[float, float]],
    penalty_energy: float,
) -> np.ndarray:
    def obj(v: np.ndarray) -> float:
        return objective(v, exps, fit_ratio, val_ratio, penalty_energy)

    if differential_evolution is not None:
        res = differential_evolution(obj, bounds=bounds, seed=seed, maxiter=maxiter, polish=True)
        return np.array(res.x, dtype=float)

    # Fallback random search (keeps script runnable without scipy)
    rng = np.random.default_rng(seed)
    best_x = None
    best_f = float("inf")
    for _ in range(max(2000, maxiter * 50)):
        x = np.array([rng.uniform(lo, hi) for lo, hi in bounds], dtype=float)
        f = obj(x)
        if f < best_f:
            best_f, best_x = f, x
    assert best_x is not None
    return best_x


def evaluate_all(
    exps: list[Experiment],
    mu: float,
    rho: float,
    eta: float,
    fit_ratio: float,
    val_ratio: float,
) -> list[dict]:
    rows: list[dict] = []
    for e in exps:
        y_ref = e.ref_fn(e.axis)
        y_rip = e.rip_fn(e.axis, mu, rho, eta)
        fit_idx, val_idx, blind_idx = split_indices(len(e.axis), fit_ratio, val_ratio)
        rows.append(
            {
                "name": e.name,
                "fit_nrmse": nrmse(y_ref[fit_idx], y_rip[fit_idx]),
                "val_nrmse": nrmse(y_ref[val_idx], y_rip[val_idx]),
                "blind_nrmse": nrmse(y_ref[blind_idx], y_rip[blind_idx]),
                "fit_r2": r2_score(y_ref[fit_idx], y_rip[fit_idx]),
                "val_r2": r2_score(y_ref[val_idx], y_rip[val_idx]),
                "blind_r2": r2_score(y_ref[blind_idx], y_rip[blind_idx]),
            }
        )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="v9 additive material extension (no edits to v6/v7/v8).")
    ap.add_argument("--fit-ratio", type=float, default=0.60)
    ap.add_argument("--val-ratio", type=float, default=0.20)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=120)
    ap.add_argument("--penalty-energy", type=float, default=50.0)
    ap.add_argument("--out-dir", type=str, default=str(OUT_DIR_DEFAULT))
    ap.add_argument("--mu-init", type=float, default=MU0)
    ap.add_argument("--rho-init", type=float, default=RHO0)
    ap.add_argument("--eta-init", type=float, default=ETA0)
    args = ap.parse_args()

    fit_ratio = float(np.clip(args.fit_ratio, 0.2, 0.8))
    val_ratio = float(np.clip(args.val_ratio, 0.1, 0.6))
    if fit_ratio + val_ratio >= 0.95:
        val_ratio = 0.95 - fit_ratio

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    exps = build_experiments()

    bounds = [
        (0.85, 2.35),  # mu
        (1.85, 2.75),  # rho
        (0.01, 0.25),  # eta
    ]

    best = run_de(
        exps=exps,
        fit_ratio=fit_ratio,
        val_ratio=val_ratio,
        seed=int(args.seed),
        maxiter=int(args.maxiter),
        bounds=bounds,
        penalty_energy=float(args.penalty_energy),
    )

    mu, rho, eta = float(best[0]), float(best[1]), float(best[2])
    rows = evaluate_all(exps, mu, rho, eta, fit_ratio, val_ratio)

    payload = {
        "meta": {
            "suite": "ripple_quantum_tests_v9_material_extension",
            "note": "Additive extension. Does not modify v6/v7/v8.",
            "positioning": "Phenomenological material-property approximation scaffold.",
            "fit_ratio": fit_ratio,
            "val_ratio": val_ratio,
            "blind_ratio": float(1.0 - fit_ratio - val_ratio),
            "seed": int(args.seed),
            "maxiter": int(args.maxiter),
            "penalty_energy": float(args.penalty_energy),
        },
        "optimum": {"mu": mu, "rho": rho, "eta": eta},
        "experiments": rows,
    }

    (out_dir / "RIPPLE_QUANTUM_TESTS_V9_RESULTS.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    md = [
        "# Ripple Quantum Tests v9 (Material Extension)",
        "",
        "- additive only: no edits to v6/v7/v8",
        f"- optimum: mu={mu:.6f}, rho={rho:.6f}, eta={eta:.6f}",
        f"- split: fit={fit_ratio:.2f}, val={val_ratio:.2f}, blind={1.0-fit_ratio-val_ratio:.2f}",
        "",
        "| experiment | fit_nrmse | val_nrmse | blind_nrmse | fit_r2 | val_r2 | blind_r2 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        md.append(
            f"| {r['name']} | {r['fit_nrmse']:.6f} | {r['val_nrmse']:.6f} | {r['blind_nrmse']:.6f} | "
            f"{r['fit_r2']:.6f} | {r['val_r2']:.6f} | {r['blind_r2']:.6f} |"
        )
    (out_dir / "RIPPLE_QUANTUM_TESTS_V9_SUMMARY.md").write_text("\n".join(md), encoding="utf-8")

    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V9_RESULTS.json")
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V9_SUMMARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
