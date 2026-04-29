#!/usr/bin/env python3
"""
Identifiability audit for ripple_quantum_tests_v6_joint.

Goal:
- Stress test whether (mu, rho, eta) are uniquely anchored or pseudo-anchors.
- Produce evidence bundles: multi-restart convergence, profile scans, permutation control.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from ripple_quantum_tests_v6_joint import (
    F0_REL_TOL,
    build_rows,
    eval_joint_loss,
    joint_cfg_from_args,
    joint_curves,
    run_de_joint,
    state_after_de,
)


BOUNDS = [
    (0.85, 2.35),  # mu
    (1.85, 2.75),  # rho
    (0.04, 0.14),  # eta
    (1.8e-5, 8.5e-5),  # bw
]


def run_de_numpy(
    obj,
    bounds: list[tuple[float, float]],
    *,
    seed: int,
    maxiter: int,
    popsize: int = 14,
    f_scale: float = 0.82,
    crossover: float = 0.78,
) -> dict[str, Any]:
    rng = np.random.default_rng(int(seed))
    dim = len(bounds)
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    span = hi - lo
    pop = lo + rng.random((int(popsize), dim)) * span
    vals = np.array([obj(v) for v in pop], dtype=float)
    nit = 0
    for nit in range(1, int(maxiter) + 1):
        for i in range(pop.shape[0]):
            idxs = np.arange(pop.shape[0])
            idxs = idxs[idxs != i]
            a, b, c = rng.choice(idxs, size=3, replace=False)
            mutant = pop[a] + f_scale * (pop[b] - pop[c])
            mutant = np.clip(mutant, lo, hi)
            trial = pop[i].copy()
            j_rand = int(rng.integers(0, dim))
            for j in range(dim):
                if (rng.random() < crossover) or (j == j_rand):
                    trial[j] = mutant[j]
            tv = obj(trial)
            if tv <= vals[i]:
                pop[i] = trial
                vals[i] = tv
    bi = int(np.argmin(vals))
    return {
        "x": np.array(pop[bi], dtype=float),
        "fun": float(vals[bi]),
        "nit": int(nit),
        "success": True,
    }


def vec_to_named(vec: np.ndarray) -> dict[str, float]:
    return {"mu": float(vec[0]), "rho": float(vec[1]), "eta": float(vec[2]), "bw_ghz": float(vec[3])}


def get_bounds(args: argparse.Namespace) -> list[tuple[float, float]]:
    if bool(args.bounds_expand):
        return [
            (0.65, 2.85),  # mu expanded
            (1.45, 3.15),  # rho expanded
            (0.005, 0.22),  # eta expanded
            (1.0e-5, 1.1e-4),  # bw expanded
        ]
    return list(BOUNDS)


def restart_block(args: argparse.Namespace, jcfg: dict[str, Any], bounds: list[tuple[float, float]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for i in range(int(args.restarts)):
        seed = int(args.seed) + i * 9973
        res = run_de_joint(
            bounds,
            int(args.atomic_mode_n),
            float(args.atomic_rho_exponent),
            float(args.mri_quad),
            float(args.w_f0),
            float(args.w_gamma),
            seed,
            int(args.maxiter),
            jcfg,
        )
        st = state_after_de(
            res,
            int(args.atomic_mode_n),
            float(args.atomic_rho_exponent),
            float(args.mri_quad),
            float(args.shape_threshold_x),
            float(args.shape_threshold_y),
            float(args.r2_min) if args.r2_min >= 0 else None,
            jcfg,
        )
        rows.append(
            {
                "restart_id": i,
                "seed": seed,
                "loss": float(st["fun"]),
                "joint_pass": bool(st["joint_pass"]),
                "f0_rel_err": float(st["mphys"]["f0_rel_err"]),
                "gamma_rel_err": float(st["mphys"]["gamma_rel_err"]),
                "x": vec_to_named(np.array([st["mu"], st["rho"], st["eta"], st["bw"]], dtype=float)),
            }
        )
    losses = np.array([r["loss"] for r in rows], dtype=float)
    mu = np.array([r["x"]["mu"] for r in rows], dtype=float)
    rho = np.array([r["x"]["rho"] for r in rows], dtype=float)
    eta = np.array([r["x"]["eta"] for r in rows], dtype=float)
    return {
        "rows": rows,
        "summary": {
            "n_restarts": int(args.restarts),
            "joint_pass_rate": float(np.mean([1.0 if r["joint_pass"] else 0.0 for r in rows])),
            "loss_min": float(np.min(losses)),
            "loss_median": float(np.median(losses)),
            "loss_max": float(np.max(losses)),
            "mu_std": float(np.std(mu)),
            "rho_std": float(np.std(rho)),
            "eta_std": float(np.std(eta)),
        },
    }


def profile_scan(
    args: argparse.Namespace,
    jcfg: dict[str, Any],
    best_vec: np.ndarray,
    bounds: list[tuple[float, float]],
) -> dict[str, Any]:
    scans: dict[str, Any] = {}
    pmap = {"mu": 0, "rho": 1, "eta": 2}
    for pname, pidx in pmap.items():
        lo, hi = bounds[pidx]
        grid = np.linspace(lo, hi, int(args.profile_points))
        rows: list[dict[str, Any]] = []
        free_idx = [0, 1, 2, 3]
        free_idx.remove(pidx)
        free_bounds = [bounds[j] for j in free_idx]

        for gi, gval in enumerate(grid):
            def obj_free(vf: np.ndarray) -> float:
                full = np.array(best_vec, dtype=float)
                full[pidx] = float(gval)
                for k, j in enumerate(free_idx):
                    full[j] = float(vf[k])
                return float(
                    eval_joint_loss(
                        full,
                        int(args.atomic_mode_n),
                        float(args.atomic_rho_exponent),
                        float(args.mri_quad),
                        float(args.w_f0),
                        float(args.w_gamma),
                        jcfg,
                    )
                )

            res = run_de_numpy(
                obj_free,
                bounds=free_bounds,
                seed=int(args.seed) + 3701 * gi + 97 * (pidx + 1),
                maxiter=int(args.profile_maxiter),
            )
            rows.append(
                {
                    "fixed_value": float(gval),
                    "best_loss": float(res["fun"]),
                    "success": bool(res["success"]),
                    "nit": int(res["nit"]),
                }
            )
        lv = np.array([r["best_loss"] for r in rows], dtype=float)
        scans[pname] = {
            "rows": rows,
            "best_loss_min": float(np.min(lv)),
            "best_loss_p10": float(np.percentile(lv, 10)),
            "best_loss_p90": float(np.percentile(lv, 90)),
            "dynamic_range": float(np.max(lv) - np.min(lv)),
        }
    return scans


def _perm_objective(
    vec: np.ndarray,
    *,
    args: argparse.Namespace,
    jcfg: dict[str, Any],
    rng: np.random.Generator,
) -> float:
    mu, rho, eta, bw = float(vec[0]), float(vec[1]), float(vec[2]), float(vec[3])
    data = joint_curves(
        mu,
        rho,
        eta,
        max(float(bw), 1e-6),
        int(args.atomic_mode_n),
        float(args.atomic_rho_exponent),
        float(args.mri_quad),
        jcfg,
    )
    # Destroy shape correspondence but keep each marginal range.
    loss = 0.0
    for _name, (xv, qv, rv, _meta) in data["packs"].items():
        qv_perm = qv[rng.permutation(qv.size)]
        met = build_rows({"tmp": (xv, qv_perm, rv, {})}, float(args.shape_threshold_x), float(args.shape_threshold_y), None)[0]
        loss += met.nrmse_y
    loss += float(args.w_f0) * (data["meta_phys"]["f0_rel_err"] ** 2)
    loss += float(args.w_gamma) * (data["meta_phys"]["gamma_rel_err"] ** 2)
    return float(loss)


def permutation_block(args: argparse.Namespace, jcfg: dict[str, Any], bounds: list[tuple[float, float]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for i in range(int(args.permutation_runs)):
        rng = np.random.default_rng(int(args.seed) + 70000 + i * 123)

        def obj(v: np.ndarray) -> float:
            return _perm_objective(v, args=args, jcfg=jcfg, rng=rng)

        res = run_de_numpy(
            obj,
            bounds=bounds,
            seed=int(args.seed) + 80000 + i * 101,
            maxiter=max(20, int(args.maxiter) // 2),
        )
        rows.append(
            {
                "run_id": i,
                "loss_perm_best": float(res["fun"]),
                "x_perm_best": vec_to_named(np.array(res["x"], dtype=float)),
            }
        )
    lv = np.array([r["loss_perm_best"] for r in rows], dtype=float)
    return {
        "rows": rows,
        "summary": {
            "n_runs": int(args.permutation_runs),
            "perm_loss_min": float(np.min(lv)),
            "perm_loss_median": float(np.median(lv)),
            "perm_loss_max": float(np.max(lv)),
        },
    }


def bootstrap_block(
    args: argparse.Namespace,
    jcfg: dict[str, Any],
    best_vec: np.ndarray,
    bounds: list[tuple[float, float]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    base_loss = float(
        eval_joint_loss(
            best_vec,
            int(args.atomic_mode_n),
            float(args.atomic_rho_exponent),
            float(args.mri_quad),
            float(args.w_f0),
            float(args.w_gamma),
            jcfg,
        )
    )
    for i in range(int(args.bootstrap_runs)):
        rng = np.random.default_rng(int(args.seed) + 91000 + i * 131)
        sigma = float(args.bootstrap_noise_scale) * max(base_loss, 1e-6)

        def obj(v: np.ndarray) -> float:
            base = float(
                eval_joint_loss(
                    v,
                    int(args.atomic_mode_n),
                    float(args.atomic_rho_exponent),
                    float(args.mri_quad),
                    float(args.w_f0),
                    float(args.w_gamma),
                    jcfg,
                )
            )
            return base + float(rng.normal(0.0, sigma))

        res = run_de_numpy(
            obj,
            bounds=bounds,
            seed=int(args.seed) + 92000 + i * 173,
            maxiter=max(25, int(args.maxiter) // 2),
        )
        rows.append({"run_id": i, "x_boot_best": vec_to_named(np.array(res["x"], dtype=float)), "loss_boot_best": float(res["fun"])})

    mu = np.array([r["x_boot_best"]["mu"] for r in rows], dtype=float)
    rho = np.array([r["x_boot_best"]["rho"] for r in rows], dtype=float)
    eta = np.array([r["x_boot_best"]["eta"] for r in rows], dtype=float)
    return {
        "rows": rows,
        "summary": {
            "n_runs": int(args.bootstrap_runs),
            "noise_scale": float(args.bootstrap_noise_scale),
            "mu_mean": float(np.mean(mu)),
            "mu_std": float(np.std(mu)),
            "mu_p05": float(np.percentile(mu, 5)),
            "mu_p95": float(np.percentile(mu, 95)),
            "rho_mean": float(np.mean(rho)),
            "rho_std": float(np.std(rho)),
            "rho_p05": float(np.percentile(rho, 5)),
            "rho_p95": float(np.percentile(rho, 95)),
            "eta_mean": float(np.mean(eta)),
            "eta_std": float(np.std(eta)),
            "eta_p05": float(np.percentile(eta, 5)),
            "eta_p95": float(np.percentile(eta, 95)),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Identifiability audit for v6 joint medium triplet")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=90)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--profile-points", type=int, default=11)
    ap.add_argument("--profile-maxiter", type=int, default=55)
    ap.add_argument("--permutation-runs", type=int, default=4)
    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)
    ap.add_argument("--atomic-rho-exponent", type=float, default=0.35)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--atomic-mode-n", type=int, default=1)
    ap.add_argument("--w-f0", type=float, default=800.0)
    ap.add_argument("--w-gamma", type=float, default=400.0)
    ap.add_argument("--wave-speed", choices=["constant_c", "derived"], default="constant_c")
    ap.add_argument("--disp-expo-mu", type=float, default=0.25)
    ap.add_argument("--disp-expo-rho", type=float, default=0.25)
    ap.add_argument("--disp-k-eta", type=float, default=0.0)
    ap.add_argument("--c-ref-m-s", type=float, default=299792458.0)
    ap.add_argument("--bootstrap-runs", type=int, default=6)
    ap.add_argument("--bootstrap-noise-scale", type=float, default=0.03)
    ap.add_argument("--bounds-expand", action="store_true", help="Use wider parameter bounds to test boundary-lock artifacts.")
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_v6_identifiability_audit")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jcfg = joint_cfg_from_args(args)
    bounds = get_bounds(args)

    restarts = restart_block(args, jcfg, bounds)
    best_row = min(restarts["rows"], key=lambda r: r["loss"])
    best_vec = np.array(
        [
            best_row["x"]["mu"],
            best_row["x"]["rho"],
            best_row["x"]["eta"],
            best_row["x"]["bw_ghz"],
        ],
        dtype=float,
    )

    scans = profile_scan(args, jcfg, best_vec, bounds)
    perms = permutation_block(args, jcfg, bounds)
    boots = bootstrap_block(args, jcfg, best_vec, bounds)

    best_loss = float(best_row["loss"])
    perm_floor = float(perms["summary"]["perm_loss_min"])
    evidence = {
        "restart_tight": bool(
            restarts["summary"]["mu_std"] < 0.03
            and restarts["summary"]["rho_std"] < 0.04
            and restarts["summary"]["eta_std"] < 0.01
        ),
        "profile_nonflat": bool(
            scans["mu"]["dynamic_range"] > 0.01
            and scans["rho"]["dynamic_range"] > 0.01
            and scans["eta"]["dynamic_range"] > 0.01
        ),
        "perm_degrades": bool((perm_floor - best_loss) > 0.03),
        "bootstrap_tight": bool(
            boots["summary"]["mu_std"] < 0.03 and boots["summary"]["rho_std"] < 0.05 and boots["summary"]["eta_std"] < 0.015
        ),
    }
    evidence["overall_anchor_supported"] = bool(all(evidence.values()))

    payload = {
        "meta": {
            "suite": "ripple_v6_identifiability_audit",
            "f0_rel_tol": F0_REL_TOL,
            "settings": vars(args),
            "bounds": {
                "mu": bounds[0],
                "rho": bounds[1],
                "eta": bounds[2],
                "bw_ghz": bounds[3],
            },
        },
        "best_restart": best_row,
        "multi_restart": restarts,
        "profile_scans": scans,
        "permutation_control": perms,
        "bootstrap_recovery": boots,
        "evidence_checks": evidence,
    }
    p_json = out_dir / "RIPPLE_V6_IDENTIFIABILITY_AUDIT.json"
    p_md = out_dir / "RIPPLE_V6_IDENTIFIABILITY_AUDIT_SUMMARY.md"
    p_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# Ripple v6 Identifiability Audit",
        "",
        f"- best loss: `{best_loss:.8f}`",
        (
            "- best x: "
            f"mu={best_row['x']['mu']:.6f}, rho={best_row['x']['rho']:.6f}, "
            f"eta={best_row['x']['eta']:.6f}, bw={best_row['x']['bw_ghz']:.6e}"
        ),
        (
            "- restart std: "
            f"mu={restarts['summary']['mu_std']:.6f}, "
            f"rho={restarts['summary']['rho_std']:.6f}, "
            f"eta={restarts['summary']['eta_std']:.6f}"
        ),
        (
            "- profile dynamic range: "
            f"mu={scans['mu']['dynamic_range']:.6f}, "
            f"rho={scans['rho']['dynamic_range']:.6f}, "
            f"eta={scans['eta']['dynamic_range']:.6f}"
        ),
        (
            "- permutation floor(min): "
            f"{perms['summary']['perm_loss_min']:.6f} "
            f"(delta={perms['summary']['perm_loss_min'] - best_loss:.6f})"
        ),
        (
            "- bootstrap std: "
            f"mu={boots['summary']['mu_std']:.6f}, "
            f"rho={boots['summary']['rho_std']:.6f}, "
            f"eta={boots['summary']['eta_std']:.6f}"
        ),
        f"- checks: {json.dumps(evidence, ensure_ascii=False)}",
        "",
        "## Reading rule",
        "- If overall_anchor_supported=false, treat (mu,rho,eta) as potentially non-unique pseudo-anchors.",
    ]
    p_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("wrote", p_json.as_posix())
    print("wrote", p_md.as_posix())
    print("overall_anchor_supported:", evidence["overall_anchor_supported"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
