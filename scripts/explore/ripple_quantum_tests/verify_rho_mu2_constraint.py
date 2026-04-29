#!/usr/bin/env python3
"""
Verify whether rho -> mu^2 is an intrinsic attractor of the v6 joint objective.

Does NOT modify ripple_quantum_tests_v6_joint.py. Reuses eval_joint_loss + state_after_de.

Tests (user spec):
  1) Fix mu, optimize (rho, eta, bw) — report best rho vs mu^2 and joint_pass.
  2) Fix mu, force rho = mu^2, optimize (eta, bw) — report loss and joint_pass.
  3) Scan rho in [mu^2 - delta, mu^2 + delta]; for each rho, optimize (eta, bw) — loss curve.

Anti-cheat:
  - Same gates/thresholds as v6 main (shape thresholds, r2_min, F0_REL_TOL, gamma).
  - No hand-tuned success; joint_pass comes only from state_after_de.
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
    from scipy.optimize import differential_evolution
except Exception:  # pragma: no cover
    differential_evolution = None


def load_v6(repo_root: Path):
    p = repo_root / "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py"
    spec = importlib.util.spec_from_file_location("v6_joint_verify", p)
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


def fake_de_result(x4: np.ndarray, fun: float, nit: int = 0, success: bool = True):
    return SimpleNamespace(x=np.array(x4, dtype=float), fun=float(fun), nit=int(nit), success=bool(success))


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify rho ~ mu^2 under v6 joint objective")
    ap.add_argument("--mu", type=float, default=1.5495)
    ap.add_argument("--atomic-rho-exponent", type=float, default=0.35, help="same as v6 --atomic-rho-exponent")
    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--atomic-mode-n", type=int, default=1)
    ap.add_argument("--w-f0", type=float, default=800.0)
    ap.add_argument("--w-gamma", type=float, default=400.0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=120)
    ap.add_argument("--scan-delta", type=float, default=0.2)
    ap.add_argument("--scan-points", type=int, default=21)
    ap.add_argument(
        "--scan-maxiter",
        type=int,
        default=-1,
        help="DE maxiter for inner (eta,bw) per rho; -1 means same as --maxiter",
    )
    ap.add_argument(
        "--rho-bounds",
        type=str,
        default="1.85,2.75",
        help="rho min,max (v6 default bounds)",
    )
    ap.add_argument("--out-dir", type=str, default="artifacts/verify_rho_mu2_constraint")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[3]
    m = load_v6(repo)
    jcfg = jcfg_for_v6(m)
    alpha = float(args.atomic_rho_exponent)
    mode_n = int(args.atomic_mode_n)
    mri_quad = float(args.mri_quad)
    w_f0 = float(args.w_f0)
    w_gamma = float(args.w_gamma)
    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min: float | None = None if args.r2_min < 0 else float(args.r2_min)
    mu_fixed = float(args.mu)
    rho_target = float(mu_fixed**2)
    rho_lo, rho_hi = [float(x) for x in args.rho_bounds.split(",")]

    def loss_full(vec4: np.ndarray) -> float:
        return float(
            m.eval_joint_loss(
                np.asarray(vec4, dtype=float),
                mode_n,
                alpha,
                mri_quad,
                w_f0,
                w_gamma,
                jcfg,
            )
        )

    def state_from_vec4(vec4: np.ndarray) -> dict[str, Any]:
        fun = loss_full(vec4)
        res = fake_de_result(vec4, fun)
        return m.state_after_de(res, mode_n, alpha, mri_quad, th_x, th_y, r2_min, jcfg)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "meta": {
            "script": "verify_rho_mu2_constraint.py",
            "note": "rho_mu2 audit under v6 joint loss + same gates as v6 main",
            "mu_fixed": mu_fixed,
            "rho_target_mu_squared": rho_target,
            "atomic_rho_exponent": alpha,
        },
        "test1_rho_free": None,
        "test2_rho_forced_mu2": None,
        "test3_scan": None,
    }

    # --- Test 1: fix mu, optimize rho, eta, bw ---
    def obj1(v: np.ndarray) -> float:
        rho, eta, bw = float(v[0]), float(v[1]), float(v[2])
        return loss_full(np.array([mu_fixed, rho, eta, bw], dtype=float))

    bounds1 = [
        (rho_lo, rho_hi),
        (0.04, 0.14),
        (1.8e-5, 8.5e-5),
    ]
    if differential_evolution is None:
        raise RuntimeError("scipy differential_evolution required for this audit")
    r1 = differential_evolution(
        obj1,
        bounds=bounds1,
        seed=int(args.seed),
        maxiter=int(args.maxiter),
        polish=True,
    )
    best1 = np.array([mu_fixed, float(r1.x[0]), float(r1.x[1]), float(r1.x[2])], dtype=float)
    st1 = state_from_vec4(best1)
    payload["test1_rho_free"] = {
        "optimum": {"mu": float(best1[0]), "rho": float(best1[1]), "eta": float(best1[2]), "bw_ghz": float(best1[3])},
        "loss": float(r1.fun),
        "joint_pass": bool(st1["joint_pass"]),
        "rho_minus_mu2": float(best1[1] - rho_target),
        "rel_err_rho_vs_mu2": float(abs(best1[1] - rho_target) / max(abs(rho_target), 1e-12)),
    }

    # --- Test 2: rho = mu^2 exactly, optimize eta, bw ---
    rho_f = float(mu_fixed**2)
    if not (rho_lo <= rho_f <= rho_hi):
        payload["test2_rho_forced_mu2"] = {
            "skipped": True,
            "reason": f"mu^2={rho_f} outside rho bounds [{rho_lo},{rho_hi}]",
        }
    else:

        def obj2(v: np.ndarray) -> float:
            eta, bw = float(v[0]), float(v[1])
            return loss_full(np.array([mu_fixed, rho_f, eta, bw], dtype=float))

        bounds2 = [(0.04, 0.14), (1.8e-5, 8.5e-5)]
        r2 = differential_evolution(
            obj2,
            bounds=bounds2,
            seed=int(args.seed) + 1,
            maxiter=int(args.maxiter),
            polish=True,
        )
        best2 = np.array([mu_fixed, rho_f, float(r2.x[0]), float(r2.x[1])], dtype=float)
        st2 = state_from_vec4(best2)
        payload["test2_rho_forced_mu2"] = {
            "optimum": {"mu": float(best2[0]), "rho": float(best2[1]), "eta": float(best2[2]), "bw_ghz": float(best2[3])},
            "loss": float(r2.fun),
            "joint_pass": bool(st2["joint_pass"]),
        }

    # --- Test 3: scan rho, re-optimize eta,bw each time ---
    scan_maxiter = int(args.maxiter) if int(args.scan_maxiter) < 0 else int(args.scan_maxiter)
    scan_rhos = np.linspace(rho_target - float(args.scan_delta), rho_target + float(args.scan_delta), int(args.scan_points))
    scan_rows = []
    best_scan = {"loss": float("inf"), "rho": None, "vec": None, "joint_pass": False}
    for rho_s in scan_rhos:
        if rho_s < rho_lo or rho_s > rho_hi:
            scan_rows.append({"rho": float(rho_s), "skipped": True, "reason": "outside rho bounds"})
            continue

        def obj3(v: np.ndarray) -> float:
            eta, bw = float(v[0]), float(v[1])
            return loss_full(np.array([mu_fixed, float(rho_s), eta, bw], dtype=float))

        r3 = differential_evolution(
            obj3,
            bounds=bounds2,
            seed=int(args.seed) + int(hash(float(rho_s)) % 10000),
            maxiter=scan_maxiter,
            polish=True,
        )
        v3 = np.array([mu_fixed, float(rho_s), float(r3.x[0]), float(r3.x[1])], dtype=float)
        st3 = state_from_vec4(v3)
        scan_rows.append(
            {
                "rho": float(rho_s),
                "loss": float(r3.fun),
                "joint_pass": bool(st3["joint_pass"]),
                "eta": float(v3[2]),
                "bw_ghz": float(v3[3]),
            }
        )
        if float(r3.fun) < best_scan["loss"]:
            best_scan = {
                "loss": float(r3.fun),
                "rho": float(rho_s),
                "vec": v3.tolist(),
                "joint_pass": bool(st3["joint_pass"]),
            }

    losses = [row["loss"] for row in scan_rows if "loss" in row]
    rhos_ok = [row["rho"] for row in scan_rows if "loss" in row]
    argmin_local = int(np.argmin(losses)) if losses else -1
    rho_at_min = float(rhos_ok[argmin_local]) if argmin_local >= 0 else None

    payload["test3_scan"] = {
        "delta": float(args.scan_delta),
        "inner_maxiter": scan_maxiter,
        "points_requested": int(args.scan_points),
        "rho_at_global_min_in_scan": rho_at_min,
        "loss_at_that_rho": float(losses[argmin_local]) if argmin_local >= 0 else None,
        "distance_rho_at_min_to_mu2": float(rho_at_min - rho_target) if rho_at_min is not None else None,
        "best_overall_in_scan": best_scan,
        "series": scan_rows,
    }

    # Interpretation (honest, not a proof of Maxwell)
    interp = []
    t1 = payload["test1_rho_free"]
    if t1 and t1["rel_err_rho_vs_mu2"] < 0.05:
        interp.append("Test1: optimized rho is within 5% of mu^2 under free rho — consistent with rho≈mu^2 attractor in this toy objective.")
    elif t1:
        interp.append(
            f"Test1: optimized rho={t1['optimum']['rho']:.6g} differs from mu^2={rho_target:.6g} by rel {t1['rel_err_rho_vs_mu2']:.4f} — not a tight mu^2 lock under this loss."
        )
    if rho_at_min is not None and abs(rho_at_min - rho_target) < 0.02:
        interp.append("Test3: loss minimum in scan lies near mu^2 — supports local attractor near mu^2 (within scan window).")
    elif rho_at_min is not None:
        interp.append(
            f"Test3: loss minimum in scan at rho={rho_at_min:.6g}, not mu^2={rho_target:.6g} — rho=mu^2 is not the unique minimizer on this interval."
        )
    payload["interpretation"] = interp

    json_path = out_dir / "RHO_MU2_VERIFY.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# Rho vs mu^2 constraint audit (v6 joint loss)",
        "",
        f"- mu_fixed = {mu_fixed}",
        f"- mu^2 = {rho_target:.10g}",
        "",
        "## Test 1: rho free (optimize rho, eta, bw)",
        json.dumps(payload["test1_rho_free"], indent=2),
        "",
        "## Test 2: rho = mu^2 (optimize eta, bw)",
        json.dumps(payload.get("test2_rho_forced_mu2"), indent=2),
        "",
        "## Test 3: scan rho",
        f"- rho at min loss in scan: `{rho_at_min}`",
        f"- distance to mu^2: `{payload['test3_scan'].get('distance_rho_at_min_to_mu2')}`",
        "",
        "## Interpretation",
    ]
    for line in interp:
        md_lines.append(f"- {line}")

    (out_dir / "RHO_MU2_VERIFY.md").write_text("\n".join(md_lines), encoding="utf-8")
    print("wrote", json_path)
    print("wrote", out_dir / "RHO_MU2_VERIFY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
