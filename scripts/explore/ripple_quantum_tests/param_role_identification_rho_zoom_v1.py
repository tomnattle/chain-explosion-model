#!/usr/bin/env python3
"""
Local rho zoom: how the Jacobian (metric sensitivities) changes
when shrinking the finite-difference step in rho.

This answers: the "needle" scale is governed by which metric
and on what rho scale that metric's sensitivity blows up.
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
    spec = importlib.util.spec_from_file_location("v6_role_zoom", p)
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
    ap.add_argument("--rho", type=float, default=2.35)
    ap.add_argument("--eta", type=float, default=0.08)
    ap.add_argument("--bw-ghz", type=float, default=3e-5)

    ap.add_argument("--mode-n", type=int, default=1)
    ap.add_argument("--alpha", type=float, default=0.35)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--w-f0", type=float, default=800.0)
    ap.add_argument("--w-gamma", type=float, default=400.0)

    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)

    ap.add_argument(
        "--rho-deltas",
        type=str,
        default="1e-4,3e-5,1e-5",
        help="comma-separated rho finite-difference steps",
    )
    ap.add_argument("--plot", action="store_true", default=True)
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[3]
    v6m = load_v6(repo)
    jcfg = jcfg_for_v6(v6m)

    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min = None if args.r2_min < 0 else float(args.r2_min)

    mode_n = int(args.mode_n)
    alpha = float(args.alpha)
    mri_quad = float(args.mri_quad)
    w_f0 = float(args.w_f0)
    w_gamma = float(args.w_gamma)

    lock = {"mu": float(args.mu), "rho": float(args.rho), "eta": float(args.eta), "bw": float(args.bw_ghz)}
    params_order = ["mu", "rho", "eta", "bw"]
    # metrics: 4 panel nrmse_y + f0_rel_err + gamma_rel_err
    metric_names = [
        "nrmse_y_laser_threshold",
        "nrmse_y_semiconductor_cutoff",
        "nrmse_y_mri_larmor",
        "nrmse_y_atomic_clock_modes",
        "f0_rel_err",
        "gamma_rel_err",
    ]
    panel_order = ["laser_threshold", "semiconductor_cutoff", "mri_larmor", "atomic_clock_modes"]

    def metrics_vec(mu: float, rho: float, eta: float, bw: float) -> np.ndarray:
        data = v6m.joint_curves(mu, rho, eta, bw, mode_n, alpha, mri_quad, jcfg)
        packs = data["packs"]
        meta = data["meta_phys"]
        met_p = {}
        # Use continuous metrics; r2 gate not needed for derivatives.
        for pn in panel_order:
            xv, qv, rv, _ = packs[pn]
            met = v6m.curve_shape_metrics(qv, rv, xv)
            met_p[pn] = met
        return np.asarray(
            [
                met_p["laser_threshold"]["nrmse_y"],
                met_p["semiconductor_cutoff"]["nrmse_y"],
                met_p["mri_larmor"]["nrmse_y"],
                met_p["atomic_clock_modes"]["nrmse_y"],
                meta["f0_rel_err"],
                meta["gamma_rel_err"],
            ],
            dtype=float,
        )

    rho_deltas = [float(x.strip()) for x in str(args.rho_deltas).split(",") if x.strip()]
    # For other params use fixed finite-diff steps.
    del_mu = 1e-4
    del_eta = 1e-4
    del_bw = 1e-8

    results = {
        "meta": {
            "script": "param_role_identification_rho_zoom_v1.py",
            "lock": lock,
            "mode_n": mode_n,
            "alpha": alpha,
            "mri_quad": mri_quad,
            "thresholds": {"th_x": th_x, "th_y": th_y, "r2_min": r2_min},
            "w_f0": w_f0,
            "w_gamma": w_gamma,
            "panel_order": panel_order,
        },
        "rho_delta_scan": [],
    }

    for rd in rho_deltas:
        # central differences for rho only: compute d(metrics)/d(rho) at lock.
        mu0, rho0, eta0, bw0 = lock["mu"], lock["rho"], lock["eta"], lock["bw"]
        mp = metrics_vec(mu0, rho0 + rd, eta0, bw0)
        mm = metrics_vec(mu0, rho0 - rd, eta0, bw0)
        d_rho = (mp - mm) / (2.0 * rd)

        row = {
            "rho_delta": rd,
            "dmetric_d_rho": dict(zip(metric_names, d_rho.tolist())),
            "abs_dmetric_d_rho_ranked": sorted(
                [{ "metric": mn, "abs_sens": float(abs(v)) } for mn, v in zip(metric_names, d_rho)],
                key=lambda x: x["abs_sens"],
                reverse=True,
            )[:3],
        }
        results["rho_delta_scan"].append(row)

    out_dir = Path("artifacts/param_role_identification_v1/rho_zoom")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ROLE_IDENTIFICATION_RHO_ZOOM.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Optional plot: abs sensitivities vs rho_delta for top-3 metrics across all deltas.
    if plt is not None and args.plot and results["rho_delta_scan"]:
        # gather candidates by abs
        acc: dict[str, float] = {}
        for row in results["rho_delta_scan"]:
            for mn in metric_names:
                acc[mn] = max(acc.get(mn, 0.0), abs(row["dmetric_d_rho"][mn]))
        top = sorted(acc.keys(), key=lambda k: acc[k], reverse=True)[:4]

        fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
        for mn in top:
            ys = [abs(r["dmetric_d_rho"][mn]) for r in results["rho_delta_scan"]]
            ax.plot([r["rho_delta"] for r in results["rho_delta_scan"]], ys, marker="o", label=mn)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("|rho_delta|")
        ax.set_ylabel("|d(metric)/d(rho)| at lock")
        ax.set_title("rho finite-difference zoom")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out_dir / "rho_zoom_abs_sensitivity.png", dpi=160)
        plt.close(fig)

    print("wrote", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

