#!/usr/bin/env python3
"""
Ripple quantum tests v6 — Grand consistency / joint parameter vector.

Single shared medium triple (mu, rho, eta) drives toy mappings into all four experiments:
  - MRI: kappa solved algebraically so gamma_derived == gamma_QM (identifiable branch).
  - Atomic: cavity length uses nominal L ∝ v/(2 f0) * (rho/rho_ref)**alpha.
    Default: v = c (constant).  Optional --wave-speed derived: v = f(mu,rho,eta) calibrated
    so v(mu_ref,rho_ref,eta_ref)=c (see ripple_medium_dispersion.py).  c_ref is still an SI anchor.
  - Laser / semiconductor: explicit smooth dependence on (mu, rho, eta) (toy bridge).

Objective: minimize sum of nrmse_y over four panels + penalty on relative f0 error.

This is still a *toy coupling* — the bridge formulas are documented, not derived from
first principles. The scientific utility is: (i) explicit joint infeasibility when the
penalty cannot be driven down, (ii) one JSON with a single theta* and per-panel metrics.

Stress mode (--stress): sweep atomic coupling exponent alpha and optionally f0-penalty
weight w_f0; write CSV + phase-diagram PNGs showing where joint_pass breaks.

Outputs: artifacts/ripple_quantum_tests_v6/ by default.
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

from ripple_medium_dispersion import maxwell_analogy_note, phase_speed_m_s

C_LIGHT_M_S = 299792458.0
GAMMA_QM = 42.577
F0_QM_GHZ = 9.192631770
RHO_REF = 2.35
MU_REF = 1.55
ETA_REF = 0.08
# Relative tolerance on f0 equivalent to 20 kHz at Cs hyperfine (~9.19 GHz)
F0_REL_TOL = 20_000.0 / (F0_QM_GHZ * 1e9)


def joint_cfg_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "wave_speed_mode": str(getattr(args, "wave_speed", "constant_c")),
        "expo_mu": float(getattr(args, "disp_expo_mu", 0.25)),
        "expo_rho": float(getattr(args, "disp_expo_rho", 0.25)),
        "k_eta": float(getattr(args, "disp_k_eta", 0.0)),
        "c_ref_m_s": float(getattr(args, "c_ref_m_s", C_LIGHT_M_S)),
        "mu_ref": MU_REF,
        "rho_ref": RHO_REF,
        "eta_ref": ETA_REF,
    }


def curve_shape_metrics(qm: np.ndarray, rip: np.ndarray, x: np.ndarray) -> dict[str, float]:
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
    return GAMMA_QM * x


def qm_atomic(x: np.ndarray) -> np.ndarray:
    f0, bw = F0_QM_GHZ, 0.000030
    return np.exp(-0.5 * ((x - f0) / bw) ** 2)


def ripple_laser(x: np.ndarray, th_r: float, a_hi: float, a_lo: float) -> np.ndarray:
    return np.where(x > th_r, a_hi * (x - th_r), a_lo * x)


def ripple_atomic(x: np.ndarray, f0_ghz: float, bw: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - f0_ghz) / bw) ** 2)


def ripple_mri(x: np.ndarray, gamma: float, quad: float) -> np.ndarray:
    return gamma * x + quad * x**2


def medium_to_laser_params(mu: float, rho: float, eta: float) -> tuple[float, float, float]:
    """Toy bridge: nominal point (MU_REF,RHO_REF,ETA_REF) maps near QM reference laser."""
    th_r = float(np.clip(0.5 + 0.05 * (rho / RHO_REF - 1.0), 0.45, 0.55))
    a_hi = float(2.2 * (mu / MU_REF) ** 0.12)
    a_lo = float(0.02 * (1.0 + 0.4 * (eta / ETA_REF - 1.0)))
    return th_r, a_hi, a_lo


def medium_to_semi_params(mu: float, rho: float, eta: float) -> tuple[float, float]:
    c = float(2.0 + 0.12 * (rho / RHO_REF - 1.0) + 0.06 * (eta - ETA_REF))
    k = float(20.0 - 2.5 * (rho / RHO_REF - 1.0) + 8.0 * (eta - ETA_REF))
    k = float(np.clip(k, 10.0, 32.0))
    _ = mu  # reserved if future bridge uses mu
    return c, k


def joint_curves(
    mu: float,
    rho: float,
    eta: float,
    bw: float,
    mode_n: int,
    atomic_rho_exponent: float,
    mri_quad: float,
    jcfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rho = max(float(rho), 0.35)
    mu = max(float(mu), 0.2)
    eta = max(float(eta), 0.01)

    cfg = jcfg or {}
    wsm = str(cfg.get("wave_speed_mode", "constant_c"))
    if wsm == "derived":
        v_ms = phase_speed_m_s(
            mu,
            rho,
            eta,
            mu_ref=float(cfg["mu_ref"]),
            rho_ref=float(cfg["rho_ref"]),
            eta_ref=float(cfg["eta_ref"]),
            c_ref_m_s=float(cfg.get("c_ref_m_s", C_LIGHT_M_S)),
            expo_mu=float(cfg.get("expo_mu", 0.25)),
            expo_rho=float(cfg.get("expo_rho", 0.25)),
            k_eta=float(cfg.get("k_eta", 0.0)),
        )
    else:
        v_ms = float(C_LIGHT_M_S)

    kappa = GAMMA_QM * rho * (1.0 + eta) / mu
    g = derive_gamma(mu, kappa, rho, eta)
    gamma_rel_err = abs(g - GAMMA_QM) / GAMMA_QM

    f0_hz = F0_QM_GHZ * 1e9
    n = int(np.clip(mode_n, 1, 4))
    l_nom = n * v_ms / (2.0 * f0_hz)
    length_m = float(l_nom * (rho / RHO_REF) ** float(atomic_rho_exponent))
    f0_ripple = float(n * v_ms / (2.0 * length_m) / 1e9)
    f0_rel_err = abs(f0_ripple - F0_QM_GHZ) / F0_QM_GHZ

    xl = axis_laser()
    th_r, a_hi, a_lo = medium_to_laser_params(mu, rho, eta)
    laser_qm, laser_r = qm_laser(xl), ripple_laser(xl, th_r, a_hi, a_lo)

    xs = axis_semiconductor()
    c_s, k_s = medium_to_semi_params(mu, rho, eta)
    semi_qm, semi_r = qm_semiconductor(xs), sigmoid(xs, c_s, k_s)

    xm = axis_mri()
    mri_qm, mri_r = qm_mri(xm), ripple_mri(xm, g, mri_quad)

    xa = axis_atomic()
    atom_qm, atom_r = qm_atomic(xa), ripple_atomic(xa, f0_ripple, float(bw))

    packs = {
        "laser_threshold": (xl, laser_qm, laser_r, {"th_r": th_r, "a_hi": a_hi, "a_lo": a_lo}),
        "semiconductor_cutoff": (xs, semi_qm, semi_r, {"c": c_s, "k": k_s}),
        "mri_larmor": (xm, mri_qm, mri_r, {"gamma_derived": g, "kappa": kappa, "quad": mri_quad}),
        "atomic_clock_modes": (
            xa,
            atom_qm,
            atom_r,
            {
                "f0_ripple_ghz": f0_ripple,
                "length_m": length_m,
                "bw": bw,
                "mode_index": n,
                "wave_speed_m_s": v_ms,
            },
        ),
    }
    meta_phys = {
        "mu": mu,
        "rho": rho,
        "eta": eta,
        "kappa_algebraic": kappa,
        "gamma_derived": g,
        "gamma_rel_err": gamma_rel_err,
        "length_m": length_m,
        "l_nominal_m": l_nom,
        "wave_speed_m_s": v_ms,
        "wave_speed_mode": wsm,
        "atomic_rho_exponent": atomic_rho_exponent,
        "f0_ripple_ghz": f0_ripple,
        "f0_rel_err": f0_rel_err,
    }
    return {"packs": packs, "meta_phys": meta_phys}


def eval_joint_loss(
    vec: np.ndarray,
    mode_n: int,
    atomic_rho_exponent: float,
    mri_quad: float,
    w_f0: float,
    w_gamma: float,
    jcfg: dict[str, Any],
) -> float:
    mu, rho, eta, bw = float(vec[0]), float(vec[1]), float(vec[2]), float(vec[3])
    bw = max(bw, 1.0e-6)
    data = joint_curves(mu, rho, eta, bw, mode_n, atomic_rho_exponent, mri_quad, jcfg)
    mphys = data["meta_phys"]
    loss = 0.0
    for name, (xv, qv, rv, _) in data["packs"].items():
        loss += curve_shape_metrics(qv, rv, xv)["nrmse_y"]
    loss += w_f0 * (mphys["f0_rel_err"] ** 2)
    loss += w_gamma * (mphys["gamma_rel_err"] ** 2)
    return float(loss)


def run_de_joint(
    bounds: list[tuple[float, float]],
    mode_n: int,
    alpha: float,
    mri_quad: float,
    w_f0: float,
    w_gamma: float,
    seed: int,
    maxiter: int,
    jcfg: dict[str, Any],
):
    def objective(v: np.ndarray) -> float:
        return eval_joint_loss(v, mode_n, alpha, mri_quad, w_f0, w_gamma, jcfg)

    return differential_evolution(
        objective,
        bounds=bounds,
        seed=int(seed),
        maxiter=int(maxiter),
        polish=True,
    )


def state_after_de(
    res: Any,
    mode_n: int,
    alpha: float,
    mri_quad: float,
    th_x: float,
    th_y: float,
    r2_min: float | None,
    jcfg: dict[str, Any],
) -> dict[str, Any]:
    mu_o, rho_o, eta_o, bw_o = float(res.x[0]), float(res.x[1]), float(res.x[2]), float(res.x[3])
    data = joint_curves(mu_o, rho_o, eta_o, bw_o, mode_n, alpha, mri_quad, jcfg)
    packs = data["packs"]
    mphys = data["meta_phys"]
    rows = build_rows(packs, th_x, th_y, r2_min)
    all_shape = all(r.shape_pass for r in rows)
    gamma_ok = mphys["gamma_rel_err"] < 1e-9
    f0_ok = mphys["f0_rel_err"] <= F0_REL_TOL
    joint_pass = bool(all_shape and gamma_ok and f0_ok)
    max_ny = max(r.nrmse_y for r in rows)
    return {
        "mu": mu_o,
        "rho": rho_o,
        "eta": eta_o,
        "bw": bw_o,
        "packs": packs,
        "mphys": mphys,
        "rows": rows,
        "joint_pass": joint_pass,
        "max_nrmse_y": max_ny,
        "fun": float(res.fun),
    }


@dataclass
class Row:
    name: str
    nrmse_x: float
    nrmse_y: float
    r2: float
    shape_pass: bool
    note: str


def shape_gate(m: dict[str, float], th_x: float, th_y: float, r2_min: float | None) -> bool:
    ok = (m["nrmse_x"] <= th_x) and (m["nrmse_y"] <= th_y)
    if r2_min is not None:
        ok = ok and (m["r2"] >= r2_min)
    return ok


def build_rows(
    packs: dict[str, Any], th_x: float, th_y: float, r2_min: float | None
) -> list[Row]:
    rows = []
    for name, (xv, qv, rv, meta) in packs.items():
        met = curve_shape_metrics(qv, rv, xv)
        rows.append(
            Row(
                name,
                met["nrmse_x"],
                met["nrmse_y"],
                met["r2"],
                shape_gate(met, th_x, th_y, r2_min),
                f"nx={met['nrmse_x']:.5f} ny={met['nrmse_y']:.5f} r2={met['r2']:.6f}",
            )
        )
    return rows


def plot_grid(packs: dict[str, Any], row_summary: list[Row], out_path: Path, suptitle: str) -> None:
    order = ["laser_threshold", "semiconductor_cutoff", "mri_larmor", "atomic_clock_modes"]
    titles = {r.name: f"{r.name} ny={r.nrmse_y:.4f} R2={r.r2:.4f}" for r in row_summary}
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.2), dpi=150)
    for ax, name in zip(axes.flat, order):
        xv, qv, rv, _ = packs[name]
        ax.plot(xv, qv, lw=1.7, label="QM-like ref", color="#1f77b4")
        ax.plot(xv, rv, lw=1.5, ls="--", label="Ripple", color="#d62728")
        ax.set_title(titles[name])
        ax.grid(alpha=0.28)
        ax.legend(fontsize=8)
    fig.suptitle(suptitle, fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=170)
    plt.close(fig)


def stress_run_point(
    args: argparse.Namespace,
    bounds: list[tuple[float, float]],
    mode_n: int,
    alpha: float,
    mri_quad: float,
    wf0: float,
    w_gamma: float,
    seed: int,
    stress_iter: int,
    th_x: float,
    th_y: float,
    r2_min: float | None,
) -> tuple[Any, dict[str, Any], Any, dict[str, Any], bool]:
    """
    One stress grid evaluation: coarse DE, then optional refine DE if joint_pass fails.
    Returns (res_coarse, st_coarse, res_final, st_final, did_refine).
    """
    jcfg = joint_cfg_from_args(args)
    res = run_de_joint(bounds, mode_n, alpha, mri_quad, wf0, w_gamma, seed, stress_iter, jcfg)
    st = state_after_de(res, mode_n, alpha, mri_quad, th_x, th_y, r2_min, jcfg)
    if bool(getattr(args, "stress_refine", False)) and not st["joint_pass"]:
        r_it = int(getattr(args, "stress_refine_maxiter", 220))
        res2 = run_de_joint(bounds, mode_n, alpha, mri_quad, wf0, w_gamma, seed + 79_191, r_it, jcfg)
        st2 = state_after_de(res2, mode_n, alpha, mri_quad, th_x, th_y, r2_min, jcfg)
        return res, st, res2, st2, True
    return res, st, res, st, False


def run_stress_sweep(
    args: argparse.Namespace,
    out_dir: Path,
    bounds: list[tuple[float, float]],
    th_x: float,
    th_y: float,
    r2_min: float | None,
    mode_n: int,
    mri_quad: float,
) -> None:
    """Scan alpha (and optionally w_f0); write CSV + figures."""
    n_a = max(2, int(args.stress_alpha_steps))
    alphas = np.linspace(float(args.stress_alpha_min), float(args.stress_alpha_max), n_a)
    stress_iter = int(args.stress_maxiter)

    if args.stress_2d:
        n_w = max(2, int(args.stress_wf0_steps))
        wf0s = np.linspace(float(args.stress_wf0_min), float(args.stress_wf0_max), n_w)
        pass_mat = np.zeros((n_a, n_w), dtype=float)
        loss_mat = np.full((n_a, n_w), np.nan)
        long_lines: list[str] = [
            "i_alpha,i_wf0,alpha,w_f0,loss_coarse,joint_pass_coarse,loss_final,joint_pass_final,"
            "refine_ran,mu,rho,eta,bw_ghz,f0_rel_err,max_nrmse_y"
        ]
        for ia, alpha in enumerate(alphas):
            for jw, wf0 in enumerate(wf0s):
                seed = int(args.seed) + ia * 10007 + jw * 1301
                _rc, stc, _rf, stf, did_r = stress_run_point(
                    args,
                    bounds,
                    mode_n,
                    float(alpha),
                    mri_quad,
                    float(wf0),
                    float(args.w_gamma),
                    seed,
                    stress_iter,
                    th_x,
                    th_y,
                    r2_min,
                )
                pass_mat[ia, jw] = 1.0 if stf["joint_pass"] else 0.0
                loss_mat[ia, jw] = stf["fun"]
                mph = stf["mphys"]
                long_lines.append(
                    f"{ia},{jw},{alpha:.8g},{wf0:.8g},{stc['fun']:.8g},{int(stc['joint_pass'])},"
                    f"{stf['fun']:.8g},{int(stf['joint_pass'])},{int(did_r)},"
                    f"{stf['mu']:.8g},{stf['rho']:.8g},{stf['eta']:.8g},{stf['bw']:.8g},"
                    f"{mph['f0_rel_err']:.8g},{stf['max_nrmse_y']:.8g}"
                )
        csv_path = out_dir / "RIPPLE_V6_STRESS_GRID.csv"
        csv_path.write_text("\n".join(long_lines), encoding="utf-8")

        fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=150)
        im0 = axes[0].imshow(
            pass_mat.T,
            origin="lower",
            aspect="auto",
            extent=[
                alphas[0],
                alphas[-1],
                wf0s[0],
                wf0s[-1],
            ],
            cmap="RdYlGn",
            vmin=0,
            vmax=1,
        )
        axes[0].set_xlabel("atomic rho exponent α")
        axes[0].set_ylabel("w_f0 (f0 penalty weight)")
        axes[0].set_title("joint_pass (1=pass)")
        fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
        lim = np.nanmax(loss_mat)
        lim = max(lim, 1e-12)
        im1 = axes[1].imshow(
            np.log10(loss_mat.T + 1e-16),
            origin="lower",
            aspect="auto",
            extent=[alphas[0], alphas[-1], wf0s[0], wf0s[-1]],
            cmap="magma",
        )
        axes[1].set_xlabel("atomic rho exponent α")
        axes[1].set_ylabel("w_f0")
        axes[1].set_title("log10(joint loss)")
        fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
        rnote = " + refine on fail" if getattr(args, "stress_refine", False) else ""
        fig.suptitle(f"v6 stress: α × w_f0 (coarse iter={stress_iter}{rnote})", fontsize=11)
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        fig.savefig(out_dir / "RIPPLE_V6_STRESS_2D.png", dpi=165)
        plt.close(fig)
        print("wrote", csv_path, out_dir / "RIPPLE_V6_STRESS_2D.png")
        return

    lines_1d: list[str] = [
        "alpha,loss_coarse,joint_pass_coarse,loss_final,joint_pass_final,refine_ran,"
        "mu,rho,eta,bw_ghz,f0_rel_err,max_nrmse_y,nit_coarse,nit_final,success_final"
    ]
    losses: list[float] = []
    losses_final: list[float] = []
    passes: list[float] = []
    passes_final: list[float] = []
    f0errs: list[float] = []
    for i, alpha in enumerate(alphas):
        seed = int(args.seed) + i * 9973
        res_c, st_c, res_f, st_f, did_r = stress_run_point(
            args,
            bounds,
            mode_n,
            float(alpha),
            mri_quad,
            float(args.w_f0),
            float(args.w_gamma),
            seed,
            stress_iter,
            th_x,
            th_y,
            r2_min,
        )
        losses.append(st_c["fun"])
        losses_final.append(st_f["fun"])
        passes.append(1.0 if st_c["joint_pass"] else 0.0)
        passes_final.append(1.0 if st_f["joint_pass"] else 0.0)
        mph = st_f["mphys"]
        f0errs.append(float(mph["f0_rel_err"]))
        lines_1d.append(
            f"{alpha:.8g},{st_c['fun']:.8g},{int(st_c['joint_pass'])},"
            f"{st_f['fun']:.8g},{int(st_f['joint_pass'])},{int(did_r)},"
            f"{st_f['mu']:.8g},{st_f['rho']:.8g},{st_f['eta']:.8g},{st_f['bw']:.8g},"
            f"{mph['f0_rel_err']:.8g},{st_f['max_nrmse_y']:.8g},"
            f"{int(res_c.nit)},{int(res_f.nit)},{int(res_f.success)}"
        )

    p1d = out_dir / "RIPPLE_V6_STRESS_ALPHA.csv"
    p1d.write_text("\n".join(lines_1d), encoding="utf-8")

    fig, axes = plt.subplots(3, 1, figsize=(9.5, 8.0), dpi=150, sharex=True)
    if args.stress_refine:
        axes[0].plot(alphas, losses, "o-", color="#c0392b", lw=1.0, ms=3, label=f"coarse ({stress_iter})")
        axes[0].plot(alphas, losses_final, "s--", color="#e67e22", lw=1.0, ms=3, label="after refine")
        axes[1].step(alphas, passes, where="mid", color="#7fb3d5", label="coarse pass")
        axes[1].step(alphas, passes_final, where="mid", color="#27ae60", label="final pass")
        axes[1].legend(fontsize=7, loc="upper right")
    else:
        axes[0].plot(alphas, losses_final, "o-", color="#c0392b", lw=1.2, ms=4, label=f"loss (iter={stress_iter})")
        axes[0].legend(fontsize=7, loc="upper right")
        axes[1].step(alphas, passes_final, where="mid", color="#27ae60")
    axes[0].set_ylabel("joint loss")
    axes[0].grid(alpha=0.3)
    axes[0].set_title("v6 stress sweep vs α (L ∝ (ρ/ρ_ref)^α)")
    axes[1].set_ylabel("joint_pass")
    axes[1].set_ylim(-0.1, 1.1)
    axes[1].grid(alpha=0.3)
    axes[2].plot(alphas, f0errs, "s-", color="#2980b9", ms=3)
    axes[2].axhline(F0_REL_TOL, color="#7f8c8d", ls="--", label=f"f0 rel tol ≈ {F0_REL_TOL:.3e}")
    axes[2].set_ylabel("f0_rel_err")
    axes[2].set_xlabel("α")
    axes[2].legend(fontsize=8)
    axes[2].grid(alpha=0.3)
    fig.suptitle(
        f"stress maxiter={stress_iter} (use --maxiter for full single run)",
        fontsize=10,
        y=1.01,
    )
    fig.tight_layout()
    fig.savefig(out_dir / "RIPPLE_V6_STRESS_1D.png", dpi=165)
    plt.close(fig)
    print("wrote", p1d, out_dir / "RIPPLE_V6_STRESS_1D.png")


def main() -> int:
    ap = argparse.ArgumentParser(description="v6 joint medium parameters across four ripple tests")
    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)
    ap.add_argument("--atomic-rho-exponent", type=float, default=0.35, help="L = L_cs * (rho/rho_ref)^alpha")
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--atomic-mode-n", type=int, default=1)
    ap.add_argument("--w-f0", type=float, default=800.0, help="Weight on (f0_rel_err)^2")
    ap.add_argument("--w-gamma", type=float, default=400.0, help="Weight on (gamma_rel_err)^2 (0 if algebraic exact)")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=160)
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests_v6")
    ap.add_argument(
        "--stress",
        action="store_true",
        help="Sweep alpha (and optionally w_f0); outputs CSV + stress PNGs",
    )
    ap.add_argument("--stress-alpha-min", type=float, default=0.0)
    ap.add_argument("--stress-alpha-max", type=float, default=1.0)
    ap.add_argument("--stress-alpha-steps", type=int, default=21)
    ap.add_argument("--stress-maxiter", type=int, default=72, help="DE iterations per grid point (faster than --maxiter)")
    ap.add_argument("--stress-2d", action="store_true", help="2D grid: alpha × w_f0")
    ap.add_argument("--stress-wf0-min", type=float, default=50.0)
    ap.add_argument("--stress-wf0-max", type=float, default=2400.0)
    ap.add_argument("--stress-wf0-steps", type=int, default=12)
    ap.add_argument(
        "--stress-refine",
        action="store_true",
        help="When joint_pass fails at a stress grid point, rerun DE with --stress-refine-maxiter",
    )
    ap.add_argument("--stress-refine-maxiter", type=int, default=220)
    ap.add_argument(
        "--wave-speed",
        choices=["constant_c", "derived"],
        default="constant_c",
        help="derived: v=phase_speed(mu,rho,eta) with v(ref)=c_ref (see ripple_medium_dispersion.py)",
    )
    ap.add_argument("--disp-expo-mu", type=float, default=0.25)
    ap.add_argument("--disp-expo-rho", type=float, default=0.25)
    ap.add_argument("--disp-k-eta", type=float, default=0.0)
    ap.add_argument(
        "--c-ref-m-s",
        type=float,
        default=C_LIGHT_M_S,
        help="SI anchor: v equals this at (mu_ref,rho_ref,eta_ref) in derived mode",
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min: float | None = None if args.r2_min < 0 else float(args.r2_min)
    alpha = float(args.atomic_rho_exponent)
    mode_n = int(args.atomic_mode_n)
    mri_quad = float(args.mri_quad)
    jcfg = joint_cfg_from_args(args)

    bounds = [
        (0.85, 2.35),  # mu — upper at ref to help gamma; widen lower
        (1.85, 2.75),  # rho — around ref; coupling shifts f0
        (0.04, 0.14),  # eta
        (1.8e-5, 8.5e-5),  # bw
    ]

    if args.stress:
        run_stress_sweep(args, out_dir, bounds, th_x, th_y, r2_min, mode_n, mri_quad)
        return 0

    res = run_de_joint(
        bounds,
        mode_n,
        alpha,
        mri_quad,
        float(args.w_f0),
        float(args.w_gamma),
        int(args.seed),
        int(args.maxiter),
        jcfg,
    )

    st = state_after_de(res, mode_n, alpha, mri_quad, th_x, th_y, r2_min, jcfg)
    mu_o, rho_o, eta_o, bw_o = st["mu"], st["rho"], st["eta"], st["bw"]
    packs = st["packs"]
    mphys = st["mphys"]
    rows = st["rows"]
    joint_pass = st["joint_pass"]

    plot_grid(
        packs,
        rows,
        out_dir / "RIPPLE_V6_JOINT_2x2.png",
        f"v6 joint | v={args.wave_speed} | loss={res.fun:.6f} joint_pass={joint_pass}",
    )

    payload = {
        "meta": {
            "suite": "ripple_quantum_tests_v6_joint",
            "bridge_note": (
                "Toy analytic bridge from (mu,rho,eta) to laser/semi/atomic/MRI; "
                "not a first-principles derivation."
            ),
            "dispersion_note": maxwell_analogy_note(),
            "wave_speed_policy": args.wave_speed,
            "dispersion_params": {k: v for k, v in jcfg.items() if k != "wave_speed_mode"},
            "atomic_L_law": f"L = (n*v/(2*f0)) * (rho/{RHO_REF})^{alpha}",
            "alpha": alpha,
            "optimization": {
                "fun": float(res.fun),
                "nit": int(res.nit),
                "success": bool(res.success),
                "x": {"mu": mu_o, "rho": rho_o, "eta": eta_o, "bw_ghz": bw_o},
            },
            "gates": {
                "shape_threshold_x": th_x,
                "shape_threshold_y": th_y,
                "r2_min": r2_min,
                "joint_pass_all_shape_and_physics": joint_pass,
            },
        },
        "shared_parameters": mphys,
        "per_test": [asdict(r) for r in rows],
        "curves": {
            k: {
                "x": v[0].tolist(),
                "qm": v[1].tolist(),
                "ripple": v[2].tolist(),
                "meta": v[3],
            }
            for k, v in packs.items()
        },
    }
    (out_dir / "RIPPLE_QUANTUM_TESTS_V6_RESULTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# Ripple Quantum Tests v6 (joint)",
        "",
        f"- Optimum: mu={mu_o:.6f}, rho={rho_o:.6f}, eta={eta_o:.6f}, bw_GHz={bw_o:.6e}",
        f"- Joint loss: `{res.fun:.8f}` | `joint_pass`: **{joint_pass}**",
        f"- gamma_rel_err: `{mphys['gamma_rel_err']:.3e}` | f0_rel_err: `{mphys['f0_rel_err']:.3e}`",
        "",
        "| test | nrmse_x | nrmse_y | R² | shape_ok |",
        "|---|---:|---:|---:|:---:|",
    ]
    for r in rows:
        md.append(
            f"| {r.name} | {r.nrmse_x:.6f} | {r.nrmse_y:.6f} | {r.r2:.6f} | {'Y' if r.shape_pass else 'N'} |"
        )
    md.append("")
    (out_dir / "RIPPLE_QUANTUM_TESTS_V6_SUMMARY.md").write_text("\n".join(md), encoding="utf-8")

    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V6_RESULTS.json")
    print("joint_pass:", joint_pass, "loss:", res.fun)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
