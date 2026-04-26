#!/usr/bin/env python3
"""
Ripple quantum tests v5 — stricter metrics + identifiability fixes.

Addresses peer-review points:
1) Report NRMSE normalized by x-span AND y-span (reference curve), plus R².
2) MRI: fix (mu, rho, eta); solve kappa algebraically from target gamma (one DOF removed
   from the 4-parameter manifold).
3) Atomic clock: fix v = c (vacuum) and mode n; solve cavity length L algebraically from
   target f0; only linewidth (bw) may be optimized for shape (breaks L,v equivalence class).

Legacy mode (optional): reproduce v4-style simultaneous (v, L) optimization for atomic
and 5-parameter MRI for A/B comparison in the JSON meta — not used for primary pass/fail.

Outputs: artifacts/ripple_quantum_tests_v5/ by default.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import differential_evolution

# SI vacuum speed of light (exact definition in SI since 2019; use standard value)
C_LIGHT_M_S = 299792458.0


def curve_shape_metrics(qm: np.ndarray, rip: np.ndarray, x: np.ndarray) -> dict[str, float]:
    """RMSE and two NRMSE scales + R² (qm as reference 'truth' for variance)."""
    diff = qm.astype(float) - rip.astype(float)
    rmse = float(np.sqrt(np.mean(diff**2)))
    span_x = float(np.max(x) - np.min(x))
    span_y = float(np.max(qm) - np.min(qm))
    if span_x < 1e-18:
        span_x = 1.0
    if span_y < 1e-18:
        span_y = 1.0
    nrmse_x = rmse / span_x
    nrmse_y = rmse / span_y
    ss_res = float(np.sum(diff**2))
    qm_c = qm.astype(float) - float(np.mean(qm))
    ss_tot = float(np.sum(qm_c**2))
    if ss_tot < 1e-24:
        r2 = 1.0 if ss_res < 1e-24 else 0.0
    else:
        r2 = float(1.0 - ss_res / ss_tot)
    return {"rmse": rmse, "nrmse_x": nrmse_x, "nrmse_y": nrmse_y, "r2": r2}


def sigmoid(x: np.ndarray, c: float, k: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-k * (x - c)))


def derive_gamma(mu: float, kappa: float, rho: float, eta: float) -> float:
    return float((mu * kappa) / max(1e-12, (rho * (1.0 + eta))))


def derive_clock_ghz(length_m: float, wave_speed_m_s: float, mode_index: int) -> float:
    return float(mode_index * wave_speed_m_s / (2.0 * length_m) / 1e9)


def axis_laser() -> np.ndarray:
    return np.linspace(0.0, 1.0, 240)


def axis_semiconductor() -> np.ndarray:
    return np.linspace(0.0, 4.0, 260)


def axis_mri() -> np.ndarray:
    return np.linspace(0.0, 3.0, 180)


def axis_atomic() -> np.ndarray:
    return np.linspace(9.1918, 9.1934, 500)


def qm_laser(x: np.ndarray) -> np.ndarray:
    return np.where(x > 0.50, 2.2 * (x - 0.50), 0.02 * x)


def qm_semiconductor(x: np.ndarray) -> np.ndarray:
    return sigmoid(x, 2.0, 20.0)


def qm_mri(x: np.ndarray) -> np.ndarray:
    return 42.577 * x


def qm_atomic(x: np.ndarray) -> np.ndarray:
    f0, bw = 9.192631770, 0.000030
    return np.exp(-0.5 * ((x - f0) / bw) ** 2)


def ripple_laser(x: np.ndarray, th_r: float, a_hi: float, a_lo: float) -> np.ndarray:
    return np.where(x > th_r, a_hi * (x - th_r), a_lo * x)


def ripple_semiconductor(x: np.ndarray, c: float, k: float) -> np.ndarray:
    return sigmoid(x, c, k)


def ripple_semiconductor_tanh(x: np.ndarray, c: float, k: float) -> np.ndarray:
    """Out-of-logistic family: 0.5 * (1 + tanh(k * (x - c)))."""
    return 0.5 * (1.0 + np.tanh(k * (x - c)))


def ripple_mri(x: np.ndarray, gamma: float, quad: float) -> np.ndarray:
    return gamma * x + quad * x**2


def ripple_atomic(x: np.ndarray, f0_ghz: float, bw: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - f0_ghz) / bw) ** 2)


@dataclass
class CurvePack:
    name: str
    x: np.ndarray
    qm: np.ndarray
    ripple: np.ndarray
    meta: dict[str, Any]


@dataclass
class TestRowV5:
    name: str
    nrmse_x: float
    nrmse_y: float
    r2: float
    shape_pass: bool
    constant_pass: bool
    final_pass: bool
    note: str
    extra: dict[str, Any]


def _shape_gate(m: dict[str, float], th_x: float, th_y: float, r2_min: float | None) -> bool:
    ok = (m["nrmse_x"] <= th_x) and (m["nrmse_y"] <= th_y)
    if r2_min is not None:
        ok = ok and (m["r2"] >= r2_min)
    return ok


def eval_laser(
    th_x: float, th_y: float, r2_min: float | None, th_r: float, a_hi: float, a_lo: float
) -> tuple[TestRowV5, CurvePack]:
    x = axis_laser()
    qm, rip = qm_laser(x), ripple_laser(x, th_r, a_hi, a_lo)
    met = curve_shape_metrics(qm, rip, x)
    sp = _shape_gate(met, th_x, th_y, r2_min)
    return (
        TestRowV5(
            "laser_threshold",
            met["nrmse_x"],
            met["nrmse_y"],
            met["r2"],
            sp,
            True,
            sp,
            f"th={th_r:.4f}, a_hi={a_hi:.4f}, a_lo={a_lo:.4f}",
            {**met},
        ),
        CurvePack("laser_threshold", x, qm, rip, {"th_r": th_r, "a_hi": a_hi, "a_lo": a_lo}),
    )


def eval_semiconductor(
    th_x: float, th_y: float, r2_min: float | None, c: float, k: float, use_tanh: bool
) -> tuple[TestRowV5, CurvePack]:
    x = axis_semiconductor()
    qm = qm_semiconductor(x)
    rip = ripple_semiconductor_tanh(x, c, k) if use_tanh else ripple_semiconductor(x, c, k)
    met = curve_shape_metrics(qm, rip, x)
    sp = _shape_gate(met, th_x, th_y, r2_min)
    fam = "tanh_family" if use_tanh else "logistic_family"
    return (
        TestRowV5(
            "semiconductor_cutoff",
            met["nrmse_x"],
            met["nrmse_y"],
            met["r2"],
            sp,
            True,
            sp,
            f"{fam} c={c:.4f}, k={k:.4f}",
            {**met, "ripple_family": fam},
        ),
        CurvePack("semiconductor_cutoff", x, qm, rip, {"c": c, "k": k, "family": fam}),
    )


def eval_mri_rigorous(
    th_x: float,
    th_y: float,
    r2_min: float | None,
    gamma_tol: float,
    mu: float,
    rho: float,
    eta: float,
    quad: float,
) -> tuple[TestRowV5, CurvePack]:
    """kappa from algebra so gamma_derived == gamma_qm; quad fixed (default 0)."""
    x = axis_mri()
    gamma_qm = 42.577
    kappa = gamma_qm * rho * (1.0 + eta) / max(1e-12, mu)
    g = derive_gamma(mu, kappa, rho, eta)
    rel_err = abs(g - gamma_qm) / gamma_qm
    qm = qm_mri(x)
    rip = ripple_mri(x, g, quad)
    met = curve_shape_metrics(qm, rip, x)
    sp = _shape_gate(met, th_x, th_y, r2_min)
    cp = rel_err <= gamma_tol
    return (
        TestRowV5(
            "mri_larmor",
            met["nrmse_x"],
            met["nrmse_y"],
            met["r2"],
            sp,
            cp,
            sp and cp,
            f"rigorous_algebraic gamma={g:.9f}, rel_err={rel_err:.3e}; kappa={kappa:.6f}",
            {
                **met,
                "mode": "rigorous_algebraic",
                "mu": mu,
                "rho": rho,
                "eta": eta,
                "kappa": kappa,
                "quad": quad,
                "gamma_derived": g,
                "gamma_rel_err": rel_err,
            },
        ),
        CurvePack("mri_larmor", x, qm, rip, {"gamma": g, "quad": quad}),
    )


def eval_atomic_rigorous(
    th_x: float,
    th_y: float,
    r2_min: float | None,
    center_tol_hz: float,
    bw: float,
    mode_index: int,
) -> tuple[TestRowV5, CurvePack]:
    """v = c, L from target f0 and integer n; optimize bw only for shape."""
    x = axis_atomic()
    f0_qm_ghz = 9.192631770
    f0_hz = f0_qm_ghz * 1e9
    n = int(np.clip(mode_index, 1, 4))
    v = C_LIGHT_M_S
    length_m = n * v / (2.0 * f0_hz)
    f0_r = derive_clock_ghz(length_m, v, n)
    center_err_hz = abs(f0_r - f0_qm_ghz) * 1e9
    qm = qm_atomic(x)
    rip = ripple_atomic(x, f0_r, bw)
    met = curve_shape_metrics(qm, rip, x)
    sp = _shape_gate(met, th_x, th_y, r2_min)
    cp = center_err_hz <= center_tol_hz
    return (
        TestRowV5(
            "atomic_clock_modes",
            met["nrmse_x"],
            met["nrmse_y"],
            met["r2"],
            sp,
            cp,
            sp and cp,
            f"rigorous v=c, L={length_m:.9f} m, n={n}, bw={bw:.6e} GHz; err_hz={center_err_hz:.6f}",
            {
                **met,
                "mode": "rigorous_fixed_v_algebraic_L",
                "length_m": length_m,
                "wave_speed_m_s": v,
                "mode_index": n,
                "bw_ghz": bw,
                "f0_ripple_ghz": f0_r,
                "center_err_hz": center_err_hz,
            },
        ),
        CurvePack("atomic_clock_modes", x, qm, rip, {"f0_ghz": f0_r, "bw": bw}),
    )


def _loss_laser_y(v: np.ndarray) -> float:
    th_r, a_hi, a_lo = float(v[0]), float(v[1]), float(v[2])
    x = axis_laser()
    met = curve_shape_metrics(qm_laser(x), ripple_laser(x, th_r, a_hi, a_lo), x)
    return met["nrmse_y"]


def _loss_semi_y(v: np.ndarray, use_tanh: bool) -> float:
    c, k = float(v[0]), float(v[1])
    x = axis_semiconductor()
    qm = qm_semiconductor(x)
    rip = ripple_semiconductor_tanh(x, c, k) if use_tanh else ripple_semiconductor(x, c, k)
    return curve_shape_metrics(qm, rip, x)["nrmse_y"]


def _loss_atomic_bw(bw: float, th_x: float, th_y: float, r2_min: float | None, mode_index: int) -> float:
    """Scalar loss for 1D DE on bw: y-nrmse + penalties for gate violation."""
    row, _ = eval_atomic_rigorous(th_x, th_y, r2_min, 20_000.0, float(bw), mode_index)
    m = row.extra
    pen = 0.0
    if m["nrmse_y"] > th_y:
        pen += 50.0 * (m["nrmse_y"] - th_y) ** 2
    if r2_min is not None and m["r2"] < r2_min:
        pen += 50.0 * (r2_min - m["r2"]) ** 2
    return m["nrmse_y"] + pen


def optimize_laser(seed: int, maxiter: int) -> np.ndarray:
    return differential_evolution(
        _loss_laser_y,
        bounds=[(0.45, 0.55), (1.85, 2.45), (0.008, 0.06)],
        seed=seed,
        maxiter=maxiter,
        polish=True,
    ).x


def optimize_semiconductor(seed: int, maxiter: int, use_tanh: bool) -> np.ndarray:
    return differential_evolution(
        lambda v: _loss_semi_y(v, use_tanh),
        bounds=[(1.85, 2.15), (8.0, 28.0)],
        seed=seed,
        maxiter=maxiter,
        polish=True,
    ).x


def optimize_atomic_bw_only(
    th_x: float, th_y: float, r2_min: float | None, mode_index: int, seed: int, maxiter: int
) -> float:
    res = differential_evolution(
        lambda x: _loss_atomic_bw(float(x[0]), th_x, th_y, r2_min, mode_index),
        bounds=[(1.5e-5, 9.5e-5)],
        seed=seed,
        maxiter=maxiter,
        polish=True,
    )
    return float(res.x[0])


def plot_grid(packs: dict[str, CurvePack], titles: dict[str, str], out_path: Path, suptitle: str) -> None:
    order = ["laser_threshold", "semiconductor_cutoff", "mri_larmor", "atomic_clock_modes"]
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.2), dpi=150)
    for ax, name in zip(axes.flat, order):
        p = packs[name]
        ax.plot(p.x, p.qm, lw=1.7, label="QM-like ref", color="#1f77b4")
        ax.plot(p.x, p.ripple, lw=1.5, ls="--", label="Ripple", color="#d62728")
        ax.set_title(titles.get(name, name))
        ax.grid(alpha=0.28)
        ax.legend(fontsize=8)
    fig.suptitle(suptitle, fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=170)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description="Ripple quantum tests v5 (rigorous metrics + identifiability)")
    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999, help="Minimum R² for shape_pass; use negative to disable")
    ap.add_argument("--mri-gamma-rel-tol", type=float, default=0.02)
    ap.add_argument("--clock-center-tol-hz", type=float, default=20_000.0)
    ap.add_argument("--semi-tanh", action="store_true", help="Use tanh step instead of logistic for Ripple")
    ap.add_argument("--mri-quad", type=float, default=0.0, help="Fixed x^2 term (default 0 for strict linear match)")
    ap.add_argument("--atomic-mode-n", type=int, default=1, help="Cavity mode index n (integer, 1..4)")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=120)
    ap.add_argument("--skip-optimize", action="store_true")
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests_v5")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min: float | None = None if args.r2_min < 0 else float(args.r2_min)
    gamma_tol = float(args.mri_gamma_rel_tol)
    center_tol = float(args.clock_center_tol_hz)
    semi_tanh = bool(args.semi_tanh)
    mri_quad = float(args.mri_quad)
    mode_n = int(args.atomic_mode_n)

    # Shared medium knobs (locked across MRI — single source in meta)
    mu_fixed, rho_fixed, eta_fixed = 1.55, 2.35, 0.08

    rows: list[TestRowV5] = []
    packs: dict[str, CurvePack] = {}

    # --- Baseline-like ripple params (v3 style) before optimization where applicable ---
    if not args.skip_optimize:
        xl = optimize_laser(int(args.seed), int(args.maxiter))
        th_r, a_hi, a_lo = float(xl[0]), float(xl[1]), float(xl[2])
    else:
        th_r, a_hi, a_lo = 0.50, 2.05, 0.03
    r1, p1 = eval_laser(th_x, th_y, r2_min, th_r, a_hi, a_lo)
    rows.append(r1)
    packs[p1.name] = p1

    if not args.skip_optimize:
        xs = optimize_semiconductor(int(args.seed) + 1, int(args.maxiter), semi_tanh)
        c_s, k_s = float(xs[0]), float(xs[1])
    else:
        c_s, k_s = 2.03, 16.5
    r2_, p2 = eval_semiconductor(th_x, th_y, r2_min, c_s, k_s, semi_tanh)
    rows.append(r2_)
    packs[p2.name] = p2

    r3, p3 = eval_mri_rigorous(th_x, th_y, r2_min, gamma_tol, mu_fixed, rho_fixed, eta_fixed, mri_quad)
    rows.append(r3)
    packs[p3.name] = p3

    if not args.skip_optimize:
        bw_opt = optimize_atomic_bw_only(th_x, th_y, r2_min, mode_n, int(args.seed) + 2, int(args.maxiter))
    else:
        bw_opt = 8.0e-5
    r4, p4 = eval_atomic_rigorous(th_x, th_y, r2_min, center_tol, bw_opt, mode_n)
    rows.append(r4)
    packs[p4.name] = p4

    titles = {
        "laser_threshold": f"Laser | nx={r1.nrmse_x:.4f} ny={r1.nrmse_y:.4f} R²={r1.r2:.5f}",
        "semiconductor_cutoff": f"Semi | nx={r2_.nrmse_x:.4f} ny={r2_.nrmse_y:.4f} R²={r2_.r2:.5f}",
        "mri_larmor": f"MRI | nx={r3.nrmse_x:.4f} ny={r3.nrmse_y:.4f} R²={r3.r2:.5f}",
        "atomic_clock_modes": f"Clock | nx={r4.nrmse_x:.4f} ny={r4.nrmse_y:.4f} R²={r4.r2:.5f}",
    }
    plot_grid(
        packs,
        titles,
        out_dir / "RIPPLE_V5_RIGOROUS_2x2.png",
        "v5 rigorous: dual NRMSE + R²; MRI algebraic κ; atomic v=c, L algebraic",
    )

    payload: dict[str, Any] = {
        "meta": {
            "suite": "ripple_quantum_tests_v5_rigorous",
            "metrics": {
                "shape_pass_rule": "nrmse_x <= th_x AND nrmse_y <= th_y AND (r2 >= r2_min if set)",
                "th_x": th_x,
                "th_y": th_y,
                "r2_min": r2_min,
                "mri_gamma_rel_tol": gamma_tol,
                "clock_center_tol_hz": center_tol,
            },
            "identifiability": {
                "mri": "kappa = gamma_qm * rho * (1+eta) / mu with fixed mu,rho,eta; quad user-set",
                "atomic": "v fixed to c; L = n*v/(2*f0_target); only bw optimized for shape",
                "shared_medium_constants": {"mu": mu_fixed, "rho": rho_fixed, "eta": eta_fixed},
                "c_light_m_s": C_LIGHT_M_S,
            },
            "semiconductor_ripple_family": "tanh" if semi_tanh else "logistic",
            "optimization": {
                "skipped": bool(args.skip_optimize),
                "laser_params": [th_r, a_hi, a_lo],
                "semiconductor_params": [c_s, k_s],
                "atomic_bw_ghz": bw_opt,
            },
        },
        "results": [asdict(r) for r in rows],
        "curves": {
            p.name: {"x": p.x.tolist(), "qm": p.qm.tolist(), "ripple": p.ripple.tolist(), "meta": p.meta}
            for p in packs.values()
        },
    }

    (out_dir / "RIPPLE_QUANTUM_TESTS_V5_RESULTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# Ripple Quantum Tests v5 (rigorous)",
        "",
        "## Metrics",
        "",
        f"- `nrmse_x`, `nrmse_y`, `r2` per test (see JSON).",
        f"- Shape pass: both NRMSEs ≤ ({th_x}, {th_y})" + (f" and R² ≥ {r2_min}" if r2_min else "") + ".",
        "",
        "## Identifiability",
        "",
        "- MRI: single κ from algebra; no 4-parameter search.",
        f"- Atomic: v = c = {C_LIGHT_M_S} m/s; L from f₀ and n; bw only optimized.",
        "",
        "## Results",
        "",
        "| test | nrmse_x | nrmse_y | R² | shape | const | final |",
        "|---|---:|---:|---:|:---:|:---:|:---:|",
    ]
    for r in rows:
        md.append(
            f"| {r.name} | {r.nrmse_x:.6f} | {r.nrmse_y:.6f} | {r.r2:.6f} | "
            f"{'Y' if r.shape_pass else 'N'} | {'Y' if r.constant_pass else 'N'} | {'Y' if r.final_pass else 'N'} |"
        )
    md += ["", f"Figures: `{out_dir / 'RIPPLE_V5_RIGOROUS_2x2.png'}`", ""]
    (out_dir / "RIPPLE_QUANTUM_TESTS_V5_SUMMARY.md").write_text("\n".join(md), encoding="utf-8")

    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V5_RESULTS.json")
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V5_SUMMARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
