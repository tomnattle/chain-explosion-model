#!/usr/bin/env python3
"""
Scan rho at fixed (mu, eta, bw) and record per-panel shape metrics + joint gate breakdown.

v6 has four toy panels (laser / semiconductor / MRI / atomic), not Bell E(XXX); we export
nrmse_x, nrmse_y, r2, shape_pass and global f0/gamma gates matching state_after_de.

Finds which gates fail first when stepping rho away from rho_ref in +/- directions.
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


def load_v6(repo_root: Path):
    p = repo_root / "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py"
    spec = importlib.util.spec_from_file_location("v6_rho_gate", p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {p}")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def jcfg_for_v6(m) -> dict[str, Any]:
    args = SimpleNamespace(
        wave_speed="constant_c",
        disp_expo_mu=0.25,
        disp_expo_rho=0.25,
        disp_k_eta=0.0,
        c_ref_m_s=m.C_LIGHT_M_S,
    )
    return m.joint_cfg_from_args(args)


def row_metrics(m, packs: dict, th_x: float, th_y: float, r2_min: float | None) -> list[dict[str, Any]]:
    rows = m.build_rows(packs, th_x, th_y, r2_min)
    out = []
    for r in rows:
        met = m.curve_shape_metrics(
            packs[r.name][1],
            packs[r.name][2],
            packs[r.name][0],
        )
        out.append(
            {
                "name": r.name,
                "nrmse_x": float(met["nrmse_x"]),
                "nrmse_y": float(met["nrmse_y"]),
                "r2": float(met["r2"]),
                "shape_pass": bool(r.shape_pass),
            }
        )
    return out


def gate_breakdown(m, meta_phys: dict, row_metrics_list: list[dict]) -> dict[str, Any]:
    shape_ok = {r["name"]: r["shape_pass"] for r in row_metrics_list}
    gamma_ok = bool(meta_phys["gamma_rel_err"] < 1e-9)
    f0_ok = bool(meta_phys["f0_rel_err"] <= m.F0_REL_TOL)
    joint = all(shape_ok.values()) and gamma_ok and f0_ok
    failed: list[str] = [n for n, ok in shape_ok.items() if not ok]
    if not gamma_ok:
        failed.append("gamma_algebraic_gate")
    if not f0_ok:
        failed.append("f0_gate")
    return {
        "joint_pass": joint,
        "shape_ok": shape_ok,
        "gamma_ok": gamma_ok,
        "f0_ok": f0_ok,
        "failed_gates": failed,
    }


def first_transition(
    rhos: np.ndarray,
    joint_flags: np.ndarray,
    start_idx: int,
    direction: int,
) -> dict[str, Any] | None:
    """Walk from a passing start_idx; return first rho where joint fails. direction +1 / -1."""
    n = len(rhos)
    j = int(start_idx)
    if j < 0 or j >= n or not joint_flags[j]:
        return None
    if direction == 1:
        last = j
        for i in range(j + 1, n):
            if joint_flags[i]:
                last = i
            else:
                return {
                    "rho_last_pass": float(rhos[last]),
                    "rho_first_fail": float(rhos[i]),
                    "index_fail": int(i),
                }
    else:
        last = j
        for i in range(j - 1, -1, -1):
            if joint_flags[i]:
                last = i
            else:
                return {
                    "rho_last_pass": float(rhos[last]),
                    "rho_first_fail": float(rhos[i]),
                    "index_fail": int(i),
                }
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mu", type=float, default=1.5495)
    ap.add_argument("--eta", type=float, default=0.08)
    ap.add_argument("--bw", type=float, default=2.9999999860115105e-05, help="fixed bw (lock-optimum default)")
    ap.add_argument("--rho-min", type=float, default=2.30)
    ap.add_argument("--rho-max", type=float, default=2.40)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--rho-ref", type=float, default=2.35)
    ap.add_argument("--atomic-rho-exponent", type=float, default=0.35)
    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--atomic-mode-n", type=int, default=1)
    ap.add_argument("--out-dir", type=str, default="artifacts/rho_gate_sensitivity_scan")
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
    mu = float(args.mu)
    eta = float(args.eta)
    bw = float(args.bw)

    rhos = np.linspace(float(args.rho_min), float(args.rho_max), int(args.n))
    # linspace may miss rho_ref exactly; snap so L ∝ (rho/RHO_REF)^alpha hits nominal at ref.
    ir = int(np.argmin(np.abs(rhos - float(args.rho_ref))))
    rhos = rhos.copy()
    rhos[ir] = float(args.rho_ref)
    series = []
    joint_arr = np.zeros(len(rhos), dtype=bool)

    for i, rho in enumerate(rhos):
        data = m.joint_curves(mu, rho, eta, bw, mode_n, alpha, mri_quad, jcfg)
        packs = data["packs"]
        meta = data["meta_phys"]
        rlist = row_metrics(m, packs, th_x, th_y, r2_min)
        gb = gate_breakdown(m, meta, rlist)
        joint_arr[i] = gb["joint_pass"]
        row_by_name = {r["name"]: r for r in rlist}
        series.append(
            {
                "rho": float(rho),
                "joint_pass": gb["joint_pass"],
                "failed_gates": gb["failed_gates"],
                "f0_rel_err": float(meta["f0_rel_err"]),
                "gamma_rel_err": float(meta["gamma_rel_err"]),
                "f0_ripple_ghz": float(meta["f0_ripple_ghz"]),
                "length_m": float(meta["length_m"]),
                "panels": row_by_name,
            }
        )

    i_near = int(np.argmin(np.abs(rhos - float(args.rho_ref))))
    pass_idx = np.flatnonzero(joint_arr)
    if pass_idx.size == 0:
        i_pass_center = None
    else:
        i_pass_center = int(pass_idx[np.argmin(np.abs(pass_idx - i_near))])

    tr_up = first_transition(rhos, joint_arr, i_pass_center, +1) if i_pass_center is not None else None
    tr_dn = first_transition(rhos, joint_arr, i_pass_center, -1) if i_pass_center is not None else None

    def gates_at(idx: int) -> dict[str, Any]:
        return {
            "rho": float(rhos[idx]),
            "failed_gates": series[idx]["failed_gates"],
            "f0_rel_err": series[idx]["f0_rel_err"],
        }

    transitions: dict[str, Any] = {
        "rho_ref": float(args.rho_ref),
        "index_nearest_rho_ref": i_near,
        "joint_pass_at_nearest_grid": bool(joint_arr[i_near]),
        "index_pass_center": i_pass_center,
        "rho_at_pass_center": float(rhos[i_pass_center]) if i_pass_center is not None else None,
        "step_rho": float(rhos[1] - rhos[0]) if len(rhos) > 1 else 0.0,
        "increasing_rho": tr_up,
        "decreasing_rho": tr_dn,
    }
    if tr_up:
        transitions["first_fail_increasing"] = gates_at(tr_up["index_fail"])
        if tr_up["index_fail"] > 0:
            transitions["just_before_fail_increasing"] = gates_at(tr_up["index_fail"] - 1)
    if tr_dn:
        transitions["first_fail_decreasing"] = gates_at(tr_dn["index_fail"])
        if tr_dn["index_fail"] + 1 < len(rhos):
            transitions["just_before_fail_decreasing"] = gates_at(tr_dn["index_fail"] + 1)

    n_pass = int(np.sum(joint_arr))
    ic = i_pass_center if i_pass_center is not None else i_near
    # Slopes of nrmse_y near rho_ref (finite difference, interior index only)
    sens: dict[str, float] = {}
    if ic is not None and 0 < ic < len(rhos) - 1:
        for name in PANEL_ORDER:
            ny0 = series[ic - 1]["panels"][name]["nrmse_y"]
            ny2 = series[ic + 1]["panels"][name]["nrmse_y"]
            dr = float(rhos[ic + 1] - rhos[ic - 1])
            sens[name] = float((ny2 - ny0) / dr) if dr > 0 else float("nan")
    dom = max(sens, key=lambda k: abs(sens[k])) if sens else None
    payload = {
        "meta": {
            "script": "rho_gate_sensitivity_scan.py",
            "note": "v6 uses four shape panels + f0_gate + gamma; no Bell E(XXX) in this module.",
            "mu": mu,
            "eta": eta,
            "bw": bw,
            "atomic_rho_exponent": alpha,
            "v6_RHO_REF": float(m.RHO_REF),
        },
        "transitions": transitions,
        "pass_count_on_grid": n_pass,
        "dnrmse_y_drho_near_ref": sens,
        "steepest_panel_by_abs_slope": dom,
        "interpretation": [
            "Joint failure when rho leaves 2.35 (fixed bw) is dominated by atomic_clock_modes + f0_gate: "
            "cavity length uses L ∝ (rho/RHO_REF)^alpha with RHO_REF=2.35 in v6, so f0_ripple matches Cs f0 only at rho=RHO_REF; "
            "misaligned Gaussian vs qm_atomic also breaks shape (nrmse, r2).",
            "MRI gamma gate is algebraically exact (gamma_rel_err=0); laser and semiconductor panels can remain shape_pass while atomic fails.",
        ],
        "series": series,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "RHO_GATE_SENSITIVITY.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Plots: NRMSE_y vs rho per panel
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), dpi=120)
    for ax, name in zip(axes.flat, PANEL_ORDER):
        ny = [series[i]["panels"][name]["nrmse_y"] for i in range(len(rhos))]
        ax.plot(rhos, ny, lw=1.1, color="#1f77b4")
        ax.axvline(float(args.rho_ref), color="k", ls="--", lw=0.9)
        ax.axhline(th_y, color="red", ls=":", lw=0.9, label=f"th_y={th_y}")
        ax.set_title(name)
        ax.set_xlabel("rho")
        ax.set_ylabel("nrmse_y")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle(f"NRMSE_y vs rho (mu={mu}, eta={eta}, bw fixed)")
    fig.tight_layout()
    p1 = out_dir / "rho_vs_nrmse_y_panels.png"
    fig.savefig(p1, dpi=160)
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(9, 4), dpi=120)
    ax2.plot(rhos, [s["f0_rel_err"] for s in series], color="purple", lw=1.2, label="f0_rel_err")
    ax2.axhline(m.F0_REL_TOL, color="r", ls="--", label=f"F0_REL_TOL={m.F0_REL_TOL:.3e}")
    ax2.axvline(float(args.rho_ref), color="k", ls="--", lw=0.9)
    ax2.set_xlabel("rho")
    ax2.set_ylabel("relative error")
    ax2.set_title("Atomic f0 mismatch vs rho (length ∝ (rho/rho_ref)^alpha)")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    p2 = out_dir / "rho_vs_f0_rel_err.png"
    fig2.savefig(p2, dpi=160)
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(9, 3), dpi=120)
    ax3.fill_between(rhos, 0, joint_arr.astype(float), step="mid", alpha=0.35, color="green")
    ax3.plot(rhos, joint_arr.astype(float), "k-", drawstyle="steps-mid", lw=0.8)
    ax3.axvline(float(args.rho_ref), color="k", ls="--")
    ax3.set_xlabel("rho")
    ax3.set_ylabel("joint_pass")
    ax3.set_title("Joint pass vs rho (fixed bw)")
    fig3.tight_layout()
    p3 = out_dir / "rho_vs_joint_pass.png"
    fig3.savefig(p3, dpi=160)
    plt.close(fig3)

    # CSV (wide)
    csv_path = out_dir / "rho_gate_scan.csv"
    with csv_path.open("w", encoding="utf-8") as f:
        hdr = ["rho", "joint_pass", "f0_rel_err", "gamma_rel_err", "failed_gates"]
        for name in PANEL_ORDER:
            hdr.extend([f"{name}_nrmse_y", f"{name}_shape_pass"])
        f.write(",".join(hdr) + "\n")
        for s in series:
            row = [
                str(s["rho"]),
                str(int(s["joint_pass"])),
                str(s["f0_rel_err"]),
                str(s["gamma_rel_err"]),
                ";".join(s["failed_gates"]),
            ]
            for name in PANEL_ORDER:
                p = s["panels"][name]
                row.append(str(p["nrmse_y"]))
                row.append(str(int(p["shape_pass"])))
            f.write(",".join(row) + "\n")

    summary_md = [
        "# Rho gate sensitivity (v6)",
        "",
        f"- Fixed mu={mu}, eta={eta}, bw={bw}.",
        f"- rho in [{args.rho_min}, {args.rho_max}], n={args.n}.",
        f"- joint_pass count on grid: **{n_pass}**",
        "",
        "## Transitions from rho_ref",
        json.dumps(transitions, indent=2),
        "",
        "## Plots",
        f"- {p1.name}, {p2.name}, {p3.name}",
        f"- {json_path.name}, {csv_path.name}",
    ]
    (out_dir / "RHO_GATE_SENSITIVITY.md").write_text("\n".join(summary_md), encoding="utf-8")

    print("wrote", json_path)
    print("wrote", p1, p2, p3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
