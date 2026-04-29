#!/usr/bin/env python3
"""
Executioner analysis: dense rho scan, per-panel NRMSE breakdown, slopes at rho_ref, first gate to fail.

Maps v6 panel names to report keys:
  laser_threshold -> nrmse_laser_threshold
  semiconductor_cutoff -> nrmse_semiconductor_edge (alias)
  mri_larmor -> nrmse_mri_larmor
  atomic_clock_modes -> nrmse_atomic_clock_modes
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PANEL_ORDER = ["laser_threshold", "semiconductor_cutoff", "mri_larmor", "atomic_clock_modes"]

REPORT_KEYS = {
    "laser_threshold": "nrmse_laser_threshold",
    "semiconductor_cutoff": "nrmse_semiconductor_edge",
    "mri_larmor": "nrmse_mri_larmor",
    "atomic_clock_modes": "nrmse_atomic_clock_modes",
}


def load_v6(repo_root: Path):
    p = repo_root / "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py"
    spec = importlib.util.spec_from_file_location("v6_exec", p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {p}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def jcfg_for_v6(m) -> dict[str, Any]:
    args = SimpleNamespace(
        wave_speed="constant_c",
        disp_expo_mu=0.25,
        disp_expo_rho=0.25,
        disp_k_eta=0.0,
        c_ref_m_s=m.C_LIGHT_M_S,
    )
    return m.joint_cfg_from_args(args)


def panel_row_metrics(m, packs: dict, th_x: float, th_y: float, r2_min: float | None) -> dict[str, dict[str, Any]]:
    rows = m.build_rows(packs, th_x, th_y, r2_min)
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        name = r.name
        met = m.curve_shape_metrics(packs[name][1], packs[name][2], packs[name][0])
        out[name] = {
            "nrmse_x": float(met["nrmse_x"]),
            "nrmse_y": float(met["nrmse_y"]),
            "r2": float(met["r2"]),
            "shape_pass": bool(r.shape_pass),
        }
    return out


def gate_breakdown(m, meta: dict, panels: dict[str, dict]) -> dict[str, Any]:
    shape_ok = {k: panels[k]["shape_pass"] for k in PANEL_ORDER}
    gamma_ok = bool(meta["gamma_rel_err"] < 1e-9)
    f0_ok = bool(meta["f0_rel_err"] <= m.F0_REL_TOL)
    joint = all(shape_ok.values()) and gamma_ok and f0_ok
    failed = [n for n, ok in shape_ok.items() if not ok]
    if not gamma_ok:
        failed.append("gamma_algebraic_gate")
    if not f0_ok:
        failed.append("f0_gate")
    return {"joint_pass": joint, "shape_ok": shape_ok, "gamma_ok": gamma_ok, "f0_ok": f0_ok, "failed_gates": failed}


def newly_failed_gates(prev: dict[str, Any], curr: dict[str, Any]) -> list[str]:
    """Which gate keys flipped from ok to fail between two breakdown dicts."""
    out: list[str] = []
    for k in PANEL_ORDER:
        if prev["shape_ok"].get(k) and not curr["shape_ok"].get(k):
            out.append(f"shape:{k}")
    if prev["gamma_ok"] and not curr["gamma_ok"]:
        out.append("gamma_algebraic_gate")
    if prev["f0_ok"] and not curr["f0_ok"]:
        out.append("f0_gate")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Executioner: rho sensitivity breakdown (v6 joint gates)")
    ap.add_argument("--mu", type=float, default=1.5495)
    ap.add_argument("--eta", type=float, default=0.08)
    ap.add_argument("--bw", type=float, default=2.9999999860115105e-05)
    ap.add_argument("--rho-min", type=float, default=2.34)
    ap.add_argument("--rho-max", type=float, default=2.36)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--rho-ref", type=float, default=2.35)
    ap.add_argument("--atomic-rho-exponent", type=float, default=0.35)
    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--atomic-mode-n", type=int, default=1)
    ap.add_argument("--out-dir", type=str, default="artifacts/rho_sensitivity_breakdown")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[3]
    m = load_v6(repo)
    jcfg = jcfg_for_v6(m)
    alpha = float(args.atomic_rho_exponent)
    mode_n = int(args.atomic_mode_n)
    mri_quad = float(args.mri_quad)
    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min: float | None = None if args.r2_min < 0 else float(args.r2_min)
    mu, eta, bw = float(args.mu), float(args.eta), float(args.bw)

    rhos = np.linspace(float(args.rho_min), float(args.rho_max), int(args.n))
    ir = int(np.argmin(np.abs(rhos - float(args.rho_ref))))
    rhos = rhos.copy()
    rhos[ir] = float(args.rho_ref)

    series: list[dict[str, Any]] = []
    joint_arr = np.zeros(len(rhos), dtype=bool)

    for i, rho in enumerate(rhos):
        data = m.joint_curves(mu, rho, eta, bw, mode_n, alpha, mri_quad, jcfg)
        packs = data["packs"]
        meta = data["meta_phys"]
        panels = panel_row_metrics(m, packs, th_x, th_y, r2_min)
        gb = gate_breakdown(m, meta, panels)
        joint_arr[i] = gb["joint_pass"]

        nrmse_report = {REPORT_KEYS[name]: panels[name]["nrmse_y"] for name in PANEL_ORDER}
        series.append(
            {
                "rho": float(rho),
                "joint_pass": gb["joint_pass"],
                "nrmse_by_report_key": nrmse_report,
                "panels_v6": panels,
                "gate": {
                    "shape_ok": gb["shape_ok"],
                    "gamma_ok": gb["gamma_ok"],
                    "f0_ok": gb["f0_ok"],
                    "failed_gates": gb["failed_gates"],
                },
                "f0_rel_err": float(meta["f0_rel_err"]),
                "gamma_rel_err": float(meta["gamma_rel_err"]),
            }
        )

    # Central derivative d(nrmse_y)/drho at rho_ref
    slopes: dict[str, float] = {}
    if 0 < ir < len(rhos) - 1:
        dr = float(rhos[ir + 1] - rhos[ir - 1])
        for name in PANEL_ORDER:
            k = REPORT_KEYS[name]
            y0 = series[ir - 1]["nrmse_by_report_key"][k]
            y2 = series[ir + 1]["nrmse_by_report_key"][k]
            slopes[k] = float((y2 - y0) / dr) if dr > 0 else float("nan")
    exec_key = max(slopes, key=lambda x: abs(slopes[x])) if slopes else None

    # First joint fail: newly violated gates vs previous index (+/- rho)
    def first_fail_scan(direction: int) -> dict[str, Any] | None:
        step = 1 if direction > 0 else -1
        i0 = ir
        if not joint_arr[i0]:
            return None
        i = i0 + step
        while 0 <= i < len(rhos):
            if joint_arr[i]:
                i += step
                continue
            prev_b = {
                "shape_ok": {k: series[i - step]["panels_v6"][k]["shape_pass"] for k in PANEL_ORDER},
                "gamma_ok": series[i - step]["gate"]["gamma_ok"],
                "f0_ok": series[i - step]["gate"]["f0_ok"],
            }
            curr_b = {
                "shape_ok": {k: series[i]["panels_v6"][k]["shape_pass"] for k in PANEL_ORDER},
                "gamma_ok": series[i]["gate"]["gamma_ok"],
                "f0_ok": series[i]["gate"]["f0_ok"],
            }
            new_f = newly_failed_gates(prev_b, curr_b)
            return {
                "direction": "increasing_rho" if step > 0 else "decreasing_rho",
                "rho_last_pass": float(rhos[i - step]),
                "rho_first_fail": float(rhos[i]),
                "newly_failed": new_f,
                "failed_gates_full": series[i]["gate"]["failed_gates"],
            }
        return None

    fail_up = first_fail_scan(+1)
    fail_dn = first_fail_scan(-1)

    pass_count = int(np.sum(joint_arr))
    payload: dict[str, Any] = {
        "meta": {
            "script": "rho_sensitivity_breakdown.py",
            "mu": mu,
            "eta": eta,
            "bw": bw,
            "rho_scan": [float(rhos[0]), float(rhos[-1]), int(args.n)],
            "rho_ref_snapped": float(args.rho_ref),
            "v6_RHO_REF": float(m.RHO_REF),
            "shape_threshold_y": th_y,
            "F0_REL_TOL": float(m.F0_REL_TOL),
        },
        "executioner": {
            "largest_abs_dnrmse_drho": exec_key,
            "dnrmse_y_drho_at_ref": slopes,
            "first_joint_fail": {"increasing_rho": fail_up, "decreasing_rho": fail_dn},
        },
        "pass_count_on_grid": pass_count,
        "series": series,
        "note": (
            "Atomic panel + f0_gate typically flip together: L ∝ (rho/RHO_REF)^alpha ties f0 to rho; "
            "shape uses same Gaussian vs qm_atomic."
        ),
    }
    (Path(args.out_dir)).mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.out_dir)
    jpath = out_dir / "RHO_SENSITIVITY_BREAKDOWN.json"
    jpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Single figure: four nrmse_y vs rho + threshold line
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    for name, c in zip(PANEL_ORDER, colors):
        k = REPORT_KEYS[name]
        ys = [s["nrmse_by_report_key"][k] for s in series]
        ax.plot(rhos, ys, lw=1.3, label=k, color=c)
    ax.axhline(th_y, color="k", ls="--", lw=1, alpha=0.7, label=f"th_y={th_y}")
    ax.axvline(float(args.rho_ref), color="purple", ls=":", lw=1.2, label=f"rho_ref={args.rho_ref}")
    ax.set_xlabel("rho")
    ax.set_ylabel("nrmse_y (per panel)")
    ax.set_title(f"Executioner breakdown: mu={mu}, eta={eta}, bw fixed | steepest: {exec_key}")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    pfig = out_dir / "rho_executioner_nrmse_y.png"
    fig.savefig(pfig, dpi=170)
    plt.close(fig)

    csv_path = out_dir / "rho_executioner_series.csv"
    with csv_path.open("w", encoding="utf-8") as f:
        hdr = ["rho", "joint_pass", "f0_rel_err"] + [REPORT_KEYS[n] for n in PANEL_ORDER]
        f.write(",".join(hdr) + "\n")
        for s in series:
            row = [str(s["rho"]), str(int(s["joint_pass"])), str(s["f0_rel_err"])]
            for n in PANEL_ORDER:
                row.append(str(s["nrmse_by_report_key"][REPORT_KEYS[n]]))
            f.write(",".join(row) + "\n")

    md = [
        "# Rho executioner breakdown",
        "",
        f"- Largest |d(nrmse_y)/dρ| at ref: **{exec_key}**",
        f"- Slopes: `{json.dumps(slopes)}`",
        "",
        "## First joint fail (newly violated vs previous)",
        json.dumps({"increasing_rho": fail_up, "decreasing_rho": fail_dn}, indent=2),
        "",
        f"- Files: `{jpath.name}`, `{pfig.name}`, `{csv_path.name}`",
    ]
    (out_dir / "RHO_SENSITIVITY_BREAKDOWN.md").write_text("\n".join(md), encoding="utf-8")

    print("wrote", jpath)
    print("wrote", pfig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
