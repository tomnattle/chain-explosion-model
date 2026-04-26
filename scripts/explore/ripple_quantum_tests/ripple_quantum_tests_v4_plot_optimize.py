#!/usr/bin/env python3
"""
Ripple quantum tests v4 — baseline plots, bounded optimization, optimized plots.

- Reuses v3 semantics: derived constants for MRI (gamma from mu,kappa,rho,eta) and
  atomic clock (f0 from cavity, linewidth bw free for shape matching).
- Outputs JSON + Markdown + a 2x2 baseline figure, a 2x2 optimized figure,
  and per-test PNGs under artifacts/ripple_quantum_tests_v4/.
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


def nrmse(a: np.ndarray, b: np.ndarray) -> float:
    s = float(np.max(a) - np.min(a))
    if s < 1e-12:
        s = 1.0
    return float(np.sqrt(np.mean((a - b) ** 2)) / s)


def sigmoid(x: np.ndarray, c: float, k: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-k * (x - c)))


def derive_gamma(mu: float, kappa: float, rho: float, eta: float) -> float:
    return float((mu * kappa) / max(1e-12, (rho * (1.0 + eta))))


def derive_clock_ghz(length_m: float, wave_speed_m_s: float, mode_index: int) -> float:
    return float(mode_index * wave_speed_m_s / (2.0 * length_m) / 1e9)


# --- Fixed QM reference axes (match v3) ---
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
class TestRow:
    name: str
    nrmse: float
    shape_pass: bool
    constant_pass: bool
    final_pass: bool
    note: str
    extra: dict[str, Any]


def eval_laser(shape_th: float, th_r: float, a_hi: float, a_lo: float) -> tuple[TestRow, CurvePack]:
    x = axis_laser()
    qm, rip = qm_laser(x), ripple_laser(x, th_r, a_hi, a_lo)
    e = nrmse(qm, rip)
    return (
        TestRow(
            "laser_threshold",
            e,
            e <= shape_th,
            True,
            e <= shape_th,
            f"ripple th={th_r:.4f}, a_hi={a_hi:.4f}, a_lo={a_lo:.4f}",
            {},
        ),
        CurvePack("laser_threshold", x, qm, rip, {"th_r": th_r, "a_hi": a_hi, "a_lo": a_lo}),
    )


def eval_semiconductor(shape_th: float, c: float, k: float) -> tuple[TestRow, CurvePack]:
    x = axis_semiconductor()
    qm, rip = qm_semiconductor(x), ripple_semiconductor(x, c, k)
    e = nrmse(qm, rip)
    return (
        TestRow(
            "semiconductor_cutoff",
            e,
            e <= shape_th,
            True,
            e <= shape_th,
            f"ripple sigmoid c={c:.4f}, k={k:.4f}",
            {},
        ),
        CurvePack("semiconductor_cutoff", x, qm, rip, {"c": c, "k": k}),
    )


def eval_mri(
    shape_th: float, gamma_tol: float, mu: float, kappa: float, rho: float, eta: float, quad: float
) -> tuple[TestRow, CurvePack]:
    x = axis_mri()
    gamma_qm = 42.577
    qm = qm_mri(x)
    g = derive_gamma(mu, kappa, rho, eta)
    rip = ripple_mri(x, g, quad)
    e = nrmse(qm, rip)
    rel_err = abs(g - gamma_qm) / gamma_qm
    c_pass = rel_err <= gamma_tol
    s_pass = e <= shape_th
    return (
        TestRow(
            "mri_larmor",
            e,
            s_pass,
            c_pass,
            s_pass and c_pass,
            f"gamma_qm={gamma_qm:.6f}, gamma_derived={g:.6f}, rel_err={rel_err:.6f}",
            {"gamma_derived": g, "gamma_rel_err": rel_err, "mu": mu, "kappa": kappa, "rho": rho, "eta": eta, "quad": quad},
        ),
        CurvePack("mri_larmor", x, qm, rip, {"gamma_derived": g, "quad": quad}),
    )


def eval_atomic(
    shape_th: float, center_tol_hz: float, length_m: float, wave_speed: float, mode: int, bw: float
) -> tuple[TestRow, CurvePack]:
    x = axis_atomic()
    f0_qm = 9.192631770
    qm = qm_atomic(x)
    mode_i = int(np.clip(round(mode), 1, 4))
    f0_r = derive_clock_ghz(length_m, wave_speed, mode_i)
    rip = ripple_atomic(x, f0_r, bw)
    e = nrmse(qm, rip)
    center_err_hz = abs(f0_r - f0_qm) * 1e9
    c_pass = center_err_hz <= center_tol_hz
    s_pass = e <= shape_th
    return (
        TestRow(
            "atomic_clock_modes",
            e,
            s_pass,
            c_pass,
            s_pass and c_pass,
            f"f0_qm={f0_qm:.9f} GHz, f0_ripple={f0_r:.9f} GHz, err_hz={center_err_hz:.3f}",
            {
                "f0_ripple_ghz": f0_r,
                "center_err_hz": center_err_hz,
                "length_m": length_m,
                "wave_speed_m_s": wave_speed,
                "mode_index": mode_i,
                "bw_ghz": bw,
            },
        ),
        CurvePack("atomic_clock_modes", x, qm, rip, {"f0_ripple_ghz": f0_r, "bw": bw, "mode_index": mode_i}),
    )


def _loss_laser(v: np.ndarray) -> float:
    th_r, a_hi, a_lo = float(v[0]), float(v[1]), float(v[2])
    x = axis_laser()
    return nrmse(qm_laser(x), ripple_laser(x, th_r, a_hi, a_lo))


def _loss_semi(v: np.ndarray) -> float:
    c, k = float(v[0]), float(v[1])
    x = axis_semiconductor()
    return nrmse(qm_semiconductor(x), ripple_semiconductor(x, c, k))


def _loss_mri(v: np.ndarray, gamma_tol: float, shape_th: float) -> float:
    mu, kappa, rho, eta, quad = float(v[0]), float(v[1]), float(v[2]), float(v[3]), float(v[4])
    x = axis_mri()
    g = derive_gamma(mu, kappa, rho, eta)
    gamma_qm = 42.577
    rel_err = abs(g - gamma_qm) / gamma_qm
    rip = ripple_mri(x, g, quad)
    e = nrmse(qm_mri(x), rip)
    pen_shape = max(0.0, e - shape_th) ** 2 * 25.0
    pen_gamma = max(0.0, rel_err - gamma_tol) ** 2 * 10.0
    return rel_err + 0.35 * e + pen_shape + pen_gamma


def _loss_atomic(v: np.ndarray, shape_th: float, center_tol_hz: float) -> float:
    length_m, wave_speed, mode_f, bw = float(v[0]), float(v[1]), float(v[2]), float(v[3])
    mode_i = int(np.clip(round(mode_f), 1, 4))
    x = axis_atomic()
    f0_qm = 9.192631770
    f0_r = derive_clock_ghz(length_m, wave_speed, mode_i)
    center_err_hz = abs(f0_r - f0_qm) * 1e9
    rip = ripple_atomic(x, f0_r, bw)
    e = nrmse(qm_atomic(x), rip)
    pen_shape = max(0.0, e - shape_th) ** 2 * 30.0
    pen_center = max(0.0, center_err_hz - center_tol_hz) ** 2 / (center_tol_hz**2)
    return e + center_err_hz / 2.5e6 + pen_shape + pen_center


def optimize_all(
    shape_th: float, gamma_tol: float, center_tol_hz: float, seed: int, maxiter: int
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    kwargs = {"maxiter": maxiter, "polish": True, "seed": int(rng.integers(0, 2**31 - 1))}

    res_laser = differential_evolution(
        _loss_laser,
        bounds=[(0.45, 0.55), (1.85, 2.45), (0.008, 0.06)],
        **kwargs,
    )
    res_semi = differential_evolution(
        _loss_semi,
        bounds=[(1.90, 2.10), (10.0, 28.0)],
        **kwargs,
    )
    res_mri = differential_evolution(
        lambda v: _loss_mri(v, gamma_tol, shape_th),
        bounds=[(0.4, 4.0), (15.0, 140.0), (0.4, 8.0), (0.01, 0.35), (0.005, 0.08)],
        **kwargs,
    )
    res_atomic = differential_evolution(
        lambda v: _loss_atomic(v, shape_th, center_tol_hz),
        bounds=[
            (0.012, 0.022),
            (299_500_000.0, 301_200_000.0),
            (0.8, 2.2),
            (0.000018, 0.000095),
        ],
        **kwargs,
    )

    return {
        "laser": res_laser.x,
        "semiconductor": res_semi.x,
        "mri": res_mri.x,
        "atomic": res_atomic.x,
        "laser_fun": res_laser.fun,
        "semi_fun": res_semi.fun,
        "mri_fun": res_mri.fun,
        "atomic_fun": res_atomic.fun,
    }


def baseline_params_v3() -> dict[str, Any]:
    return {
        "laser": (0.50, 2.05, 0.03),
        "semiconductor": (2.03, 16.5),
        "mri": (1.55, 57.8, 2.35, 0.08, 0.02),
        "atomic": (0.01635, 300_652_011.0, 1, 0.000080),
    }


def run_baseline(shape_th: float, gamma_tol: float, center_tol_hz: float) -> tuple[list[TestRow], dict[str, CurvePack]]:
    b = baseline_params_v3()
    rows, packs = [], {}
    r, p = eval_laser(shape_th, *b["laser"])
    rows.append(r)
    packs[r.name] = p
    r, p = eval_semiconductor(shape_th, *b["semiconductor"])
    rows.append(r)
    packs[r.name] = p
    r, p = eval_mri(shape_th, gamma_tol, *b["mri"])
    rows.append(r)
    packs[r.name] = p
    L, v, mode, bw = b["atomic"]
    r, p = eval_atomic(shape_th, center_tol_hz, L, v, mode, bw)
    rows.append(r)
    packs[r.name] = p
    return rows, packs


def run_optimized(
    shape_th: float, gamma_tol: float, center_tol_hz: float, opt: dict[str, np.ndarray]
) -> tuple[list[TestRow], dict[str, CurvePack]]:
    rows, packs = [], {}
    th_r, a_hi, a_lo = opt["laser"]
    r, p = eval_laser(shape_th, float(th_r), float(a_hi), float(a_lo))
    rows.append(r)
    packs[r.name] = p
    c, k = opt["semiconductor"]
    r, p = eval_semiconductor(shape_th, float(c), float(k))
    rows.append(r)
    packs[r.name] = p
    mu, ka, rho, eta, quad = opt["mri"]
    r, p = eval_mri(shape_th, gamma_tol, float(mu), float(ka), float(rho), float(eta), float(quad))
    rows.append(r)
    packs[r.name] = p
    L, v, mode_f, bw = opt["atomic"]
    r, p = eval_atomic(shape_th, center_tol_hz, float(L), float(v), float(mode_f), float(bw))
    rows.append(r)
    packs[r.name] = p
    return rows, packs


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


def plot_single(p: CurvePack, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.4, 3.6), dpi=140)
    ax.plot(p.x, p.qm, lw=1.6, label="QM-like ref")
    ax.plot(p.x, p.ripple, lw=1.4, ls="--", label="Ripple")
    ax.set_title(title)
    ax.grid(alpha=0.28)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_metrics_compare(before: list[TestRow], after: list[TestRow], shape_th: float, out_path: Path) -> None:
    names = [r.name for r in before]
    labels = ["Laser", "Semi", "MRI", "Clock"]
    x = np.arange(len(names))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9.2, 4.6), dpi=150)
    nb = [r.nrmse for r in before]
    na = [r.nrmse for r in after]
    ax.bar(x - w / 2, nb, w, label="baseline (v3-style)", color="#7f8c8d")
    ax.bar(x + w / 2, na, w, label="after optimize", color="#2ecc71")
    ax.axhline(shape_th, color="#c0392b", ls="--", lw=1.0, label=f"shape threshold={shape_th}")
    ax.set_xticks(x, labels)
    ax.set_ylabel("NRMSE")
    ax.set_title("NRMSE: baseline vs optimized (v4)")
    ax.grid(alpha=0.25, axis="y")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=165)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description="v4: plot + optimize ripple quantum tests")
    ap.add_argument("--shape-threshold", type=float, default=0.18)
    ap.add_argument("--mri-gamma-rel-tol", type=float, default=0.02)
    ap.add_argument("--clock-center-tol-hz", type=float, default=20_000.0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=80, help="DE maxiter per test (raise for deeper search)")
    ap.add_argument("--skip-optimize", action="store_true", help="Only baseline plots + JSON")
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests_v4")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    shape_th = float(args.shape_threshold)
    gamma_tol = float(args.mri_gamma_rel_tol)
    center_tol = float(args.clock_center_tol_hz)

    base_rows, base_packs = run_baseline(shape_th, gamma_tol, center_tol)
    titles = {
        "laser_threshold": f"Laser threshold | nrmse={base_rows[0].nrmse:.4f}",
        "semiconductor_cutoff": f"Semiconductor cutoff | nrmse={base_rows[1].nrmse:.4f}",
        "mri_larmor": f"MRI Larmor | nrmse={base_rows[2].nrmse:.4f}",
        "atomic_clock_modes": f"Atomic clock | nrmse={base_rows[3].nrmse:.4f}",
    }
    plot_grid(base_packs, titles, out_dir / "RIPPLE_V4_BASELINE_2x2.png", "Ripple quantum tests v4 — baseline (v3-style params)")
    for r in base_rows:
        plot_single(base_packs[r.name], f"{r.name} baseline | nrmse={r.nrmse:.4f}", out_dir / f"{r.name}_baseline.png")

    opt_meta: dict[str, Any] = {"skipped": bool(args.skip_optimize)}
    opt_rows: list[TestRow] = []
    opt_packs: dict[str, CurvePack] = {}

    if not args.skip_optimize:
        opt = optimize_all(shape_th, gamma_tol, center_tol, int(args.seed), int(args.maxiter))
        opt_meta.update(
            {
                "differential_evolution": {
                    "laser_x": opt["laser"].tolist(),
                    "semiconductor_x": opt["semiconductor"].tolist(),
                    "mri_x": opt["mri"].tolist(),
                    "atomic_x": opt["atomic"].tolist(),
                    "raw_loss_laser": float(opt["laser_fun"]),
                    "raw_loss_semi": float(opt["semi_fun"]),
                    "raw_loss_mri": float(opt["mri_fun"]),
                    "raw_loss_atomic": float(opt["atomic_fun"]),
                }
            }
        )
        opt_rows, opt_packs = run_optimized(shape_th, gamma_tol, center_tol, opt)
        titles_o = {
            "laser_threshold": f"Laser | nrmse={opt_rows[0].nrmse:.4f} final={opt_rows[0].final_pass}",
            "semiconductor_cutoff": f"Semi | nrmse={opt_rows[1].nrmse:.4f} final={opt_rows[1].final_pass}",
            "mri_larmor": f"MRI | nrmse={opt_rows[2].nrmse:.4f} final={opt_rows[2].final_pass}",
            "atomic_clock_modes": f"Clock | nrmse={opt_rows[3].nrmse:.4f} final={opt_rows[3].final_pass}",
        }
        plot_grid(opt_packs, titles_o, out_dir / "RIPPLE_V4_OPTIMIZED_2x2.png", "Ripple quantum tests v4 — after bounded optimization")
        for r in opt_rows:
            plot_single(
                opt_packs[r.name],
                f"{r.name} optimized | nrmse={r.nrmse:.4f} pass={r.final_pass}",
                out_dir / f"{r.name}_optimized.png",
            )
        plot_metrics_compare(base_rows, opt_rows, shape_th, out_dir / "RIPPLE_V4_NRMSE_BEFORE_AFTER.png")

    payload = {
        "meta": {
            "suite": "ripple_quantum_tests_v4",
            "shape_threshold": shape_th,
            "mri_gamma_relative_tolerance": gamma_tol,
            "clock_center_tolerance_hz": center_tol,
            "rule": "final_pass = shape_pass AND constant_pass (MRI/atomic derived)",
            "optimization": opt_meta,
        },
        "baseline": {
            "results": [asdict(r) for r in base_rows],
            "curves": {p.name: {"x": p.x.tolist(), "qm": p.qm.tolist(), "ripple": p.ripple.tolist(), "meta": p.meta} for p in base_packs.values()},
        },
    }
    if opt_rows:
        payload["optimized"] = {
            "results": [asdict(r) for r in opt_rows],
            "curves": {p.name: {"x": p.x.tolist(), "qm": p.qm.tolist(), "ripple": p.ripple.tolist(), "meta": p.meta} for p in opt_packs.values()},
        }

    (out_dir / "RIPPLE_QUANTUM_TESTS_V4_RESULTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Ripple Quantum Tests v4",
        "",
        "Baseline uses v3-style ripple parameters; optimized uses `scipy.optimize.differential_evolution` on bounded domains.",
        "",
        f"- shape threshold: `{shape_th}`",
        f"- MRI γ relative tolerance: `{gamma_tol}`",
        f"- clock center tolerance (Hz): `{center_tol}`",
        "",
        "## Baseline",
        "",
        "| test | nrmse | shape | const | final | note |",
        "|---|---:|:---:|:---:|:---:|---|",
    ]
    for r in base_rows:
        md_lines.append(
            f"| {r.name} | {r.nrmse:.6f} | {'Y' if r.shape_pass else 'N'} | {'Y' if r.constant_pass else 'N'} | "
            f"{'Y' if r.final_pass else 'N'} | {r.note} |"
        )
    if opt_rows:
        md_lines += [
            "",
            "## Optimized",
            "",
            "| test | nrmse | shape | const | final | note |",
            "|---|---:|:---:|:---:|:---:|---|",
        ]
        for r in opt_rows:
            md_lines.append(
                f"| {r.name} | {r.nrmse:.6f} | {'Y' if r.shape_pass else 'N'} | {'Y' if r.constant_pass else 'N'} | "
                f"{'Y' if r.final_pass else 'N'} | {r.note} |"
            )
    md_lines += [
        "",
        "## Interpretation",
        "",
        "- **Laser / semiconductor (shape-only constants):** the optimizer can drive NRMSE to ~0 when ripple parameters are free, "
        "because the reference curves live in the same function family. That is a *curve-matching* success, not a physics identification.",
        "- **MRI / atomic (derived constants):** passing `final_pass` means the search found medium/cavity parameters inside the stated "
        "bounds such that derived γ (or cavity f₀) and the ripple curve both meet tolerances.",
        "",
        "## Figures",
        "",
        "- `RIPPLE_V4_BASELINE_2x2.png`",
        "- `RIPPLE_V4_OPTIMIZED_2x2.png` (if optimization ran)",
        "- `RIPPLE_V4_NRMSE_BEFORE_AFTER.png`",
        "- Per-test `*_baseline.png` / `*_optimized.png`",
    ]
    (out_dir / "RIPPLE_QUANTUM_TESTS_V4_SUMMARY.md").write_text("\n".join(md_lines), encoding="utf-8")

    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V4_RESULTS.json")
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V4_SUMMARY.md")
    print("figures in", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
