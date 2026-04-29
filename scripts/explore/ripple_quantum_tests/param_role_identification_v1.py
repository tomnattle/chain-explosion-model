#!/usr/bin/env python3
"""
Parameter role identification (v6 toy model).

Goal:
  Instead of asking what mu/rho/eta correspond to in real matter,
  identify what they *do inside the model* by measuring local influence:
    - local Jacobian: d(metric)/d(param) at the current lock point
    - gate margin sensitivity: which part of joint_pass breaks first
    - identifiability: rank/condition of the local Jacobian

Scope:
  Uses v6 `joint_curves` + continuous metrics from `curve_shape_metrics`
  and gate definitions consistent with `state_after_de`.

Outputs:
  artifacts/param_role_identification_v1/ROLE_IDENTIFICATION.json
  artifacts/param_role_identification_v1/ROLE_IDENTIFICATION.md
  artifacts/param_role_identification_v1/heatmap_jacobian.png
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
    spec = importlib.util.spec_from_file_location("v6_role_ident", p)
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


def curve_metrics_from_packs(v6m, packs: dict[str, Any], th_x: float, th_y: float, r2_min: float | None):
    """
    Return per-panel continuous metrics (nrmse_x/y, r2) and boolean gate components.
    """
    out: dict[str, Any] = {"panels": {}}
    for name, (xv, qv, rv, _meta) in packs.items():
        met = v6m.curve_shape_metrics(qv, rv, xv)
        ok = (met["nrmse_x"] <= th_x) and (met["nrmse_y"] <= th_y)
        if r2_min is not None:
            ok = ok and (met["r2"] >= r2_min)
        out["panels"][name] = {
            "nrmse_x": float(met["nrmse_x"]),
            "nrmse_y": float(met["nrmse_y"]),
            "r2": float(met["r2"]),
            "shape_pass_local": bool(ok),
        }
    return out


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
    ap.add_argument("--rho-delta", type=float, default=1e-4)
    ap.add_argument("--mu-delta", type=float, default=1e-4)
    ap.add_argument("--eta-delta", type=float, default=1e-4)
    ap.add_argument("--bw-delta", type=float, default=1e-8)
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

    def eval_at(params: dict[str, float]) -> dict[str, Any]:
        mu, rho, eta, bw = params["mu"], params["rho"], params["eta"], params["bw"]
        data = v6m.joint_curves(mu, rho, eta, bw, mode_n, alpha, mri_quad, jcfg)
        packs = data["packs"]
        meta = data["meta_phys"]
        met_p = curve_metrics_from_packs(v6m, packs, th_x, th_y, r2_min)
        # Continuous metrics vector (for Jacobian)
        # Panel order is fixed to match earlier scripts.
        panel_order = ["laser_threshold", "semiconductor_cutoff", "mri_larmor", "atomic_clock_modes"]
        metrics = []
        panel_metrics = {}
        for pn in panel_order:
            metrics.append(met_p["panels"][pn]["nrmse_y"])
            panel_metrics[pn] = met_p["panels"][pn]
        metrics.extend([meta["f0_rel_err"], meta["gamma_rel_err"]])
        return {
            "metrics_vec": np.asarray(metrics, dtype=float),
            "panel_order": panel_order,
            "panel_metrics": panel_metrics,
            "meta_phys": meta,
            "shape_gate": met_p,
        }

    base = eval_at(lock)
    metric_names = [
        "nrmse_y_laser_threshold",
        "nrmse_y_semiconductor_cutoff",
        "nrmse_y_mri_larmor",
        "nrmse_y_atomic_clock_modes",
        "f0_rel_err",
        "gamma_rel_err",
    ]
    params_order = ["mu", "rho", "eta", "bw"]
    deltas = {
        "mu": float(args.mu_delta),
        "rho": float(args.rho_delta),
        "eta": float(args.eta_delta),
        "bw": float(args.bw_delta),
    }

    # Local Jacobian by central differences.
    J = np.zeros((len(metric_names), len(params_order)), dtype=float)
    for j, p in enumerate(params_order):
        d = deltas[p]
        p_plus = dict(lock)
        p_minus = dict(lock)
        p_plus[p] = float(p_plus[p] + d)
        p_minus[p] = float(p_minus[p] - d)
        f_plus = eval_at(p_plus)["metrics_vec"]
        f_minus = eval_at(p_minus)["metrics_vec"]
        J[:, j] = (f_plus - f_minus) / (2.0 * d)

    # Identifiability: rank / conditioning of J.
    # Use only the metric components that are usually gate-relevant (shape + f0).
    J_shape_f0 = J[0:5, :]  # 4 panels + f0_rel_err
    u, svals, vt = np.linalg.svd(J_shape_f0, full_matrices=False)
    rank = int(np.sum(svals > 1e-12))
    cond = float(svals[0] / max(svals[-1], 1e-18)) if len(svals) > 1 else float("inf")

    # Gate margin decomposition at base.
    # joint_pass gates:
    # - shape: for each panel: nrmse_x <= th_x, nrmse_y <= th_y, r2 >= r2_min
    # - gamma_ok: gamma_rel_err < 1e-9
    # - f0_ok: f0_rel_err <= F0_REL_TOL
    gamma_ok_margin = 1e-9 - float(base["meta_phys"]["gamma_rel_err"])
    f0_ok_margin = float(v6m.F0_REL_TOL) - float(base["meta_phys"]["f0_rel_err"])
    # worst-case shape margin among panels
    shape_margins = []
    for pn, pm in base["panel_metrics"].items():
        mx = float(th_x) - float(pm["nrmse_x"])
        my = float(th_y) - float(pm["nrmse_y"])
        mr = float("inf") if r2_min is None else float(pm["r2"]) - float(r2_min)
        shape_margins.append(min(mx, my, mr))
    worst_shape_margin = float(np.min(shape_margins)) if shape_margins else float("nan")

    # Determine dominant parameter per metric by abs Jacobian magnitude.
    dominance: dict[str, Any] = {}
    for i, mn in enumerate(metric_names):
        j_best = int(np.argmax(np.abs(J[i, :])))
        dominance[mn] = {
            "dominant_param": params_order[j_best],
            "dmetric_dparam": float(J[i, j_best]),
            "abs_sensitivity": float(np.abs(J[i, j_best])),
        }

    # A small alpha sweep: how rho sensitivity changes with alpha
    alpha_sweep = [0.25, 0.35, 0.45]
    alpha_slopes = []
    def eval_atomic_nrmse_y(params: dict[str, float], alpha_val: float) -> float:
        data = v6m.joint_curves(params["mu"], params["rho"], params["eta"], params["bw"], mode_n, alpha_val, mri_quad, jcfg)
        packs = data["packs"]
        met_p = curve_metrics_from_packs(v6m, packs, th_x, th_y, r2_min)
        return float(met_p["panels"]["atomic_clock_modes"]["nrmse_y"])

    for a in alpha_sweep:
        # slope in rho for atomic panel nrmse_y at fixed (mu,eta,bw)
        d = deltas["rho"]
        plus = dict(lock)
        minus = dict(lock)
        plus["rho"] = lock["rho"] + d
        minus["rho"] = lock["rho"] - d

        ny_lock = eval_atomic_nrmse_y(lock, a)
        ny_plus = eval_atomic_nrmse_y(plus, a)
        ny_minus = eval_atomic_nrmse_y(minus, a)
        slope = float((ny_plus - ny_minus) / (2.0 * d))
        alpha_slopes.append(
            {"alpha": a, "d(nrmse_y_atomic)/drho": slope, "atomic_nrmse_y_at_lock": ny_lock}
        )

    out = {
        "meta": {
            "script": "param_role_identification_v1.py",
            "git_scope": "toy v6 gates only",
            "lock": lock,
            "mode_n": mode_n,
            "alpha": alpha,
            "mri_quad": mri_quad,
            "thresholds": {"th_x": th_x, "th_y": th_y, "r2_min": r2_min},
            "F0_REL_TOL": float(v6m.F0_REL_TOL),
            "gamma_gate": 1e-9,
            "finite_diff_deltas": deltas,
            "metrics_vector": metric_names,
            "params_vector": params_order,
        },
        "jacobian": {
            "J_metric_by_param": J.tolist(),
            "dominance": dominance,
        },
        "gate_margins_at_lock": {
            "worst_shape_margin": worst_shape_margin,
            "f0_ok_margin": f0_ok_margin,
            "gamma_ok_margin": gamma_ok_margin,
        },
        "identifiability": {
            "rank_shape_f0": rank,
            "condition_shape_f0": cond,
            "note": "Higher rank and better conditioning imply parameters are locally distinguishable by these metrics.",
        },
        "alpha_sweep_rho_slope": alpha_slopes,
    }

    out_dir = Path("artifacts/param_role_identification_v1")
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ROLE_IDENTIFICATION.json"
    json_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # Plot heatmap
    if plt is not None and args.plot:
        fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=150)
        im = ax.imshow(np.abs(J), aspect="auto", interpolation="nearest", cmap="viridis")
        ax.set_xticks(range(len(params_order)))
        ax.set_xticklabels(params_order)
        ax.set_yticks(range(len(metric_names)))
        ax.set_yticklabels(metric_names, fontsize=8)
        for i in range(len(metric_names)):
            for j in range(len(params_order)):
                ax.text(j, i, f"{J[i, j]:.1e}", ha="center", va="center", fontsize=7, color="w" if np.abs(J[i, j]) > 1e-12 else "black")
        fig.colorbar(im, ax=ax, fraction=0.03, pad=0.03, label="abs(J)")
        ax.set_title("Local Jacobian: |d(metric)/d(param)| at lock point")
        fig.tight_layout()
        fig.savefig(out_dir / "heatmap_jacobian.png", dpi=160)
        plt.close(fig)

    md_lines = [
        "# ROLE_IDENTIFICATION (v6 toy, local)",
        "",
        "## Dominant parameters (by abs Jacobian)",
    ]
    # Compact md
    for mn in metric_names:
        d = dominance[mn]
        md_lines.append(f"- {mn}: dominant={d['dominant_param']}, dmetric/dparam={d['dmetric_dparam']:.3e}")
    md_lines += [
        "",
        "## Gate margins at lock",
        f"- worst_shape_margin (across panels): {worst_shape_margin:.6g}",
        f"- f0_ok_margin: {f0_ok_margin:.6g} (positive means f0 passes)",
        f"- gamma_ok_margin: {gamma_ok_margin:.6g} (positive means gamma passes)",
        "",
        "## Identifiability",
        f"- rank_shape_f0: {rank}",
        f"- condition_shape_f0: {cond:.3g}",
        "",
        "## Files",
        f"- {json_path}",
        f"- {out_dir / 'heatmap_jacobian.png'} (if plot enabled)",
    ]
    md_path = out_dir / "ROLE_IDENTIFICATION.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print("wrote", json_path)
    print("wrote", md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

