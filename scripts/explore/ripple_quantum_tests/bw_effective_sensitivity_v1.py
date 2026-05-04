#!/usr/bin/env python3
"""
Effective bw sensitivity under fixed (mu, eta).

For each rho in [rho_min, rho_max]:
  - scan bw densely in bounds
  - record: min atomic nrmse_y achievable, and whether any bw yields joint_pass

Answer:
  - how much of the "needle" is due to f0_gate (rho-only, bw-independent)
  - how much is due to atomic_clock_modes shape gate (bw-dependent)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


def load_v6(repo_root: Path):
    p = repo_root / "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py"
    spec = importlib.util.spec_from_file_location("v6_bw_eff", p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {p}")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def jcfg_for_v6(v6m) -> dict[str, Any]:
    args = SimpleNamespace(
        wave_speed="constant_c",
        disp_expo_mu=0.25,
        disp_expo_rho=0.25,
        disp_k_eta=0.0,
        c_ref_m_s=v6m.C_LIGHT_M_S,
    )
    return v6m.joint_cfg_from_args(args)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mu", type=float, default=1.5495)
    ap.add_argument("--eta", type=float, default=0.08)
    ap.add_argument("--rho-min", type=float, default=2.34)
    ap.add_argument("--rho-max", type=float, default=2.36)
    ap.add_argument("--rho-points", type=int, default=41)

    ap.add_argument("--bw-lo", type=float, default=1.8e-5)
    ap.add_argument("--bw-hi", type=float, default=8.5e-5)
    ap.add_argument("--bw-scan-points", type=int, default=120)

    ap.add_argument("--bw-lock", type=float, default=3e-5, help="for reference value in plots")

    ap.add_argument("--mode-n", type=int, default=1)
    ap.add_argument("--alpha", type=float, default=0.35)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--w-f0", type=float, default=800.0)
    ap.add_argument("--w-gamma", type=float, default=400.0)

    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)

    ap.add_argument("--out-dir", type=str, default="artifacts/param_role_identification_v1/bw_effective_sensitivity")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[3]
    v6m = load_v6(repo)
    jcfg = jcfg_for_v6(v6m)

    mu = float(args.mu)
    eta = float(args.eta)
    mode_n = int(args.mode_n)
    alpha = float(args.alpha)
    mri_quad = float(args.mri_quad)
    w_f0 = float(args.w_f0)
    w_gamma = float(args.w_gamma)

    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min: float | None = None if args.r2_min < 0 else float(args.r2_min)

    rho_grid = np.linspace(float(args.rho_min), float(args.rho_max), int(args.rho_points))
    bw_grid = np.linspace(float(args.bw_lo), float(args.bw_hi), int(args.bw_scan_points))

    # For existential: any bw that yields joint_pass.
    rows: list[dict[str, Any]] = []

    panel_name = "atomic_clock_modes"

    def joint_state(mu_v: float, rho_v: float, eta_v: float, bw_v: float) -> dict[str, Any]:
        # state_after_de only needs packs + gates; give a lightweight fake result.
        data = v6m.joint_curves(mu_v, rho_v, eta_v, bw_v, mode_n, alpha, mri_quad, jcfg)
        packs = data["packs"]
        meta = data["meta_phys"]
        # Build gate rows consistent with state_after_de.
        rows_local = v6m.build_rows(packs, th_x, th_y, r2_min)
        all_shape = all(r.shape_pass for r in rows_local)
        gamma_ok = meta["gamma_rel_err"] < 1e-9
        f0_ok = meta["f0_rel_err"] <= v6m.F0_REL_TOL
        joint_pass = bool(all_shape and gamma_ok and f0_ok)
        # atomic nrmse_y for that bw
        atomic_row = next((r for r in rows_local if r.name == panel_name), None)
        atomic_met = v6m.curve_shape_metrics(packs[panel_name][1], packs[panel_name][2], packs[panel_name][0])
        return {
            "joint_pass": joint_pass,
            "f0_rel_err": float(meta["f0_rel_err"]),
            "gamma_rel_err": float(meta["gamma_rel_err"]),
            "atomic_nrmse_y": float(atomic_met["nrmse_y"]),
            "atomic_shape_pass": bool(atomic_row.shape_pass) if atomic_row is not None else bool(False),
            "atomic_r2": float(atomic_met["r2"]),
        }

    for rho in rho_grid:
        best_atomic_ny = float("inf")
        best_bw = None
        atomic_shape_pass_exists = False
        any_joint_pass = False
        best_joint_loss = float("inf")
        best_joint_bw = None
        best_joint_atomic_ny = None
        # bw scan
        for bw in bw_grid:
            st = joint_state(mu, float(rho), eta, float(bw))
            if st["atomic_nrmse_y"] < best_atomic_ny:
                best_atomic_ny = st["atomic_nrmse_y"]
                best_bw = float(bw)
            if st["atomic_shape_pass"]:
                atomic_shape_pass_exists = True
            if st["joint_pass"]:
                any_joint_pass = True
                best_joint_atomic_ny = float(st["atomic_nrmse_y"])
                vec = np.array([mu, float(rho), eta, float(bw)], dtype=float)
                fun = float(v6m.eval_joint_loss(vec, mode_n, alpha, mri_quad, w_f0, w_gamma, jcfg))
                if fun < best_joint_loss:
                    best_joint_loss = fun
                    best_joint_bw = float(bw)

        rows.append(
            {
                "rho": float(rho),
                "any_joint_pass": bool(any_joint_pass),
                "best_atomic_nrmse_y": float(best_atomic_ny),
                "best_atomic_bw": best_bw,
                "atomic_shape_pass_exists": bool(atomic_shape_pass_exists),
                "best_joint_bw": best_joint_bw,
                "best_joint_loss": best_joint_loss if best_joint_bw is not None else None,
                "notes": "Existential bw scan for joint_pass; f0 depends on rho only, atomic shape depends on bw.",
            }
        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "BW_EFFECTIVE_SENSITIVITY.json"
    payload = {
        "meta": {
            "script": "bw_effective_sensitivity_v1.py",
            "mu": mu,
            "eta": eta,
            "mode_n": mode_n,
            "alpha": alpha,
            "mri_quad": mri_quad,
            "thresholds": {"th_x": th_x, "th_y": th_y, "r2_min": r2_min},
            "bw_bounds": [float(args.bw_lo), float(args.bw_hi)],
            "bw_scan_points": int(args.bw_scan_points),
            "rho_bounds": [float(args.rho_min), float(args.rho_max)],
            "rho_points": int(args.rho_points),
            "F0_REL_TOL": float(v6m.F0_REL_TOL),
        },
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Plot
    if plt is not None:
        rhos = [r["rho"] for r in rows]
        best_ny = [r["best_atomic_nrmse_y"] for r in rows]
        pass_mask = [1.0 if r["any_joint_pass"] else 0.0 for r in rows]
        f0_curve = []
        # f0_rel_err independent of bw: compute at bw-lock
        for rho in rhos:
            st0 = joint_state(mu, float(rho), eta, float(args.bw_lock))
            f0_curve.append(st0["f0_rel_err"])

        fig, ax = plt.subplots(figsize=(10, 5.2), dpi=130)
        ax.plot(rhos, best_ny, lw=1.4, color="#1f77b4", label="best atomic nrmse_y (over bw)")
        ax.axhline(th_y, color="red", ls="--", lw=1.1, label=f"th_y={th_y}")
        ax2 = ax.twinx()
        ax2.plot(rhos, f0_curve, lw=1.2, color="#7f3c8d", alpha=0.85, label="f0_rel_err (bw-lock)")
        ax2.axhline(v6m.F0_REL_TOL, color="#7f3c8d", ls=":", lw=1.1, alpha=0.8, label="F0_REL_TOL")
        ax.set_xlabel("rho")
        ax.set_ylabel("best atomic nrmse_y")
        ax2.set_ylabel("f0_rel_err")
        ax.grid(alpha=0.3)
        # third axis: pass mask as markers
        for x, pm in zip(rhos, pass_mask):
            if pm > 0:
                ax.scatter([x], [th_y * 0.8], s=22, c="green", zorder=5)
        fig.suptitle("BW effective sensitivity: atomic shape vs rho-only f0 gate")
        fig.tight_layout()
        fig.savefig(out_dir / "bw_effective_sensitivity.png", dpi=170)
        plt.close(fig)

    print("wrote", json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

