#!/usr/bin/env python3
"""
Atomic lock keyframes visual (v6 toy).

Fix (mu, eta, bw) near the recovered lock and vary rho over a few key points.
For each rho:
  - plot atomic_clock_modes panel: QM reference vs Ripple curve
  - annotate f0_rel_err, and whether state_after_de => joint_pass

Outputs:
  artifacts/atomic_lock_keyframes_visual_v1/atomic_rho_keyframes.png
  artifacts/atomic_lock_keyframes_visual_v1/atomic_rho_{rho}.png
  artifacts/atomic_lock_keyframes_visual_v1/KEYFRAMES.json
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

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_v6(repo_root: Path):
    p = repo_root / "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py"
    spec = importlib.util.spec_from_file_location("v6_atomic_viz", p)
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
    ap.add_argument("--bw-ghz", type=float, default=3.0e-5)

    ap.add_argument("--alpha", type=float, default=0.35)
    ap.add_argument("--mode-n", type=int, default=1)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--w-f0", type=float, default=800.0)
    ap.add_argument("--w-gamma", type=float, default=400.0)

    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)

    ap.add_argument("--rho-ref", type=float, default=2.35)
    ap.add_argument("--rho-deltas", type=str, default="0,1e-4,-1e-4,5e-5,-5e-5,1.507507536e-4,-1.002512e-4")
    ap.add_argument("--out-dir", type=str, default="artifacts/atomic_lock_keyframes_visual_v1")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[3]
    v6m = load_v6(repo)
    jcfg = jcfg_for_v6(v6m)

    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min: float | None = None if args.r2_min < 0 else float(args.r2_min)

    mode_n = int(args.mode_n)
    alpha = float(args.alpha)
    mri_quad = float(args.mri_quad)
    w_f0 = float(args.w_f0)
    w_gamma = float(args.w_gamma)

    mu = float(args.mu)
    eta = float(args.eta)
    bw = float(args.bw_ghz)
    rho_ref = float(args.rho_ref)

    deltas = [float(x.strip()) for x in str(args.rho_deltas).split(",") if x.strip() != ""]
    rhos = []
    for d in deltas:
        r = rho_ref + d
        # keep uniqueness while preserving order
        if not any(abs(r - rr) < 1e-12 for rr in rhos):
            rhos.append(r)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    keyframes: list[dict[str, Any]] = []

    # Make a grid of subplots.
    n = len(rhos)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5.2, nrows * 3.6), dpi=150)
    axes = np.asarray(axes).reshape(-1)

    for idx, rho in enumerate(rhos):
        data = v6m.joint_curves(mu, rho, eta, bw, mode_n, alpha, mri_quad, jcfg)
        packs = data["packs"]
        meta = data["meta_phys"]

        # Build gate verdict at this fixed point.
        vec = np.array([mu, rho, eta, bw], dtype=float)
        fun = float(v6m.eval_joint_loss(vec, mode_n, alpha, mri_quad, w_f0, w_gamma, jcfg))
        res = SimpleNamespace(x=vec, fun=fun)
        st = v6m.state_after_de(res, mode_n, alpha, mri_quad, th_x, th_y, r2_min, jcfg)

        xa, atom_qm, atom_r = packs["atomic_clock_modes"][0], packs["atomic_clock_modes"][1], packs["atomic_clock_modes"][2]

        ax = axes[idx]
        ax.plot(xa, atom_qm, lw=2.0, label="QM", color="#1f77b4")
        ax.plot(xa, atom_r, lw=1.8, ls="--", label="Ripple", color="#d62728")
        ax.axvline(meta["f0_ripple_ghz"], color="k", ls=":", lw=1.0, alpha=0.75, label="f0_ripple")

        ax.set_title(
            f"rho={rho:.6g}\n"
            f"joint_pass={st['joint_pass']}\n"
            f"f0_rel_err={meta['f0_rel_err']:.2e}",
            fontsize=10,
        )
        ax.grid(alpha=0.25)
        ax.set_xlabel("frequency (GHz)")
        ax.set_ylabel("amplitude")
        ax.legend(fontsize=7, loc="upper right")

        keyframes.append(
            {
                "rho": float(rho),
                "mu": mu,
                "eta": eta,
                "bw_ghz": bw,
                "joint_pass": bool(st["joint_pass"]),
                "f0_rel_err": float(meta["f0_rel_err"]),
                "gamma_rel_err": float(meta["gamma_rel_err"]),
                "f0_ripple_ghz": float(meta["f0_ripple_ghz"]),
                "atom_nrmse_y": float(
                    st["rows"][3].nrmse_y if len(st.get("rows", [])) >= 4 else float("nan")
                ),
                "failed_gates": st["rows"][3].shape_pass if len(st.get("rows", [])) >= 4 else None,
            }
        )

    # Hide unused axes
    for j in range(n, len(axes)):
        axes[j].axis("off")

    fig.tight_layout()
    montage_path = out_dir / "atomic_rho_keyframes.png"
    fig.savefig(montage_path, dpi=170)
    plt.close(fig)

    # Also write per-rho single frame images for convenience.
    for rho in rhos:
        data = v6m.joint_curves(mu, rho, eta, bw, mode_n, alpha, mri_quad, jcfg)
        packs = data["packs"]
        meta = data["meta_phys"]
        vec = np.array([mu, rho, eta, bw], dtype=float)
        fun = float(v6m.eval_joint_loss(vec, mode_n, alpha, mri_quad, w_f0, w_gamma, jcfg))
        res = SimpleNamespace(x=vec, fun=fun)
        st = v6m.state_after_de(res, mode_n, alpha, mri_quad, th_x, th_y, r2_min, jcfg)

        xa, atom_qm, atom_r = packs["atomic_clock_modes"][0], packs["atomic_clock_modes"][1], packs["atomic_clock_modes"][2]

        plt.figure(figsize=(7.8, 4.8), dpi=150)
        plt.plot(xa, atom_qm, lw=2.0, label="QM", color="#1f77b4")
        plt.plot(xa, atom_r, lw=1.8, ls="--", label="Ripple", color="#d62728")
        plt.axvline(meta["f0_ripple_ghz"], color="k", ls=":", lw=1.0, alpha=0.75, label="f0_ripple")
        plt.title(
            f"rho={rho:.6g}\n"
            f"joint_pass={st['joint_pass']}\n"
            f"f0_rel_err={meta['f0_rel_err']:.2e}",
            fontsize=11,
        )
        plt.grid(alpha=0.25)
        plt.xlabel("frequency (GHz)")
        plt.ylabel("amplitude")
        plt.legend(fontsize=8, loc="upper right")

        fpath = out_dir / f"atomic_rho_{rho:.6g}.png"
        plt.tight_layout()
        plt.savefig(fpath, dpi=170)
        plt.close()

    (out_dir / "KEYFRAMES.json").write_text(json.dumps(keyframes, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", montage_path)
    print("wrote per-rho keyframes and KEYFRAMES.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

