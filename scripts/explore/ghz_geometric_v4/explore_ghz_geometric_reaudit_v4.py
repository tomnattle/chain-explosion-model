#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


PI = math.pi
TWO_PI = 2.0 * PI


def compute_distances(r_src: float, r_obs: float = 1.0) -> np.ndarray:
    obs_angles = np.array([0.0, 2.0 * PI / 3.0, 4.0 * PI / 3.0], dtype=np.float64)
    src_angles = np.array([0.0, 2.0 * PI / 3.0, 4.0 * PI / 3.0], dtype=np.float64)
    obs_pos = np.stack([r_obs * np.cos(obs_angles), r_obs * np.sin(obs_angles)], axis=1)
    src_pos = np.stack([r_src * np.cos(src_angles), r_src * np.sin(src_angles)], axis=1)
    d = np.zeros((3, 3), dtype=np.float64)
    for i in range(3):
        for j in range(3):
            u = src_pos[i] - obs_pos[j]
            d[i, j] = np.sqrt(np.sum(u * u))
    return d


def observer_signal(lams: np.ndarray, obs_idx: int, meas_angle: float, d: np.ndarray, lambda_w: float) -> np.ndarray:
    out = np.zeros(lams.shape[1], dtype=np.float64)
    for i in range(3):
        dij = float(d[i, obs_idx])
        ph = TWO_PI * dij / lambda_w
        out += (1.0 / dij) * np.cos(lams[i] - meas_angle - ph)
    return out


def soft_detector(x: np.ndarray, t: float) -> np.ndarray:
    y = np.zeros_like(x)
    y[x > t] = 1.0
    y[x < -t] = -1.0
    return y


def e3_gated(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray, gate_k: float) -> tuple[float, float]:
    ta = gate_k * float(np.sqrt(np.mean(sa * sa)))
    tb = gate_k * float(np.sqrt(np.mean(sb * sb)))
    tc = gate_k * float(np.sqrt(np.mean(sc * sc)))
    a = soft_detector(sa, ta)
    b = soft_detector(sb, tb)
    c = soft_detector(sc, tc)
    m = (np.abs(a) > 0.0) & (np.abs(b) > 0.0) & (np.abs(c) > 0.0)
    if not np.any(m):
        return 0.0, 0.0
    return float(np.mean(a[m] * b[m] * c[m])), float(np.mean(m))


def ghz_f_r_from_contexts(
    c_xxx: tuple[np.ndarray, np.ndarray, np.ndarray],
    c_xyy: tuple[np.ndarray, np.ndarray, np.ndarray],
    c_yxy: tuple[np.ndarray, np.ndarray, np.ndarray],
    c_yyx: tuple[np.ndarray, np.ndarray, np.ndarray],
    gate_k: float,
) -> tuple[float, float]:
    exxx, r1 = e3_gated(c_xxx[0], c_xxx[1], c_xxx[2], gate_k)
    exyy, r2 = e3_gated(c_xyy[0], c_xyy[1], c_xyy[2], gate_k)
    eyxy, r3 = e3_gated(c_yxy[0], c_yxy[1], c_yxy[2], gate_k)
    eyyx, r4 = e3_gated(c_yyx[0], c_yyx[1], c_yyx[2], gate_k)
    f = exxx - exyy - eyxy - eyyx
    return float(f), float(np.mean([r1, r2, r3, r4]))


def ghz_f_r_geometric(lams: np.ndarray, d: np.ndarray, lambda_w: float, gate_k: float) -> tuple[float, float]:
    x, y = 0.0, PI / 2.0
    ax = observer_signal(lams, 0, x, d, lambda_w)
    bx = observer_signal(lams, 1, x, d, lambda_w)
    cx = observer_signal(lams, 2, x, d, lambda_w)
    ay = observer_signal(lams, 0, y, d, lambda_w)
    by = observer_signal(lams, 1, y, d, lambda_w)
    cy = observer_signal(lams, 2, y, d, lambda_w)
    return ghz_f_r_from_contexts(
        (ax, bx, cx),
        (ax, by, cy),
        (ay, bx, cy),
        (ay, by, cx),
        gate_k,
    )


def bootstrap_ci(rng: np.random.Generator, lams: np.ndarray, d: np.ndarray, lambda_w: float, gate_k: float, draws: int, subsample: int) -> tuple[float, float]:
    n = lams.shape[1]
    m = min(n, subsample)
    vals = []
    for _ in range(draws):
        idx = rng.integers(0, n, size=m)
        f, _ = ghz_f_r_geometric(lams[:, idx], d, lambda_w, gate_k)
        vals.append(f)
    q = np.quantile(np.array(vals), [0.025, 0.975])
    return float(q[0]), float(q[1])


def qm_mock_contexts(
    rng: np.random.Generator, n: int, noise_sigma: float = 0.12
) -> tuple[
    tuple[np.ndarray, np.ndarray, np.ndarray],
    tuple[np.ndarray, np.ndarray, np.ndarray],
    tuple[np.ndarray, np.ndarray, np.ndarray],
    tuple[np.ndarray, np.ndarray, np.ndarray],
]:
    """
    Build synthetic 'ideal GHZ-like' continuous fields for XXX, XYY, YXY, YYX.
    We enforce sign pattern (+,-,-,-) with small Gaussian perturbations.
    This is a transparent surrogate when raw per-shot experiment data is unavailable.
    """
    amp = np.maximum(0.2, 1.0 + rng.normal(0.0, noise_sigma, size=n))
    eps = rng.normal(0.0, noise_sigma * 0.08, size=n)
    c_xxx = (amp + eps, amp - eps, amp + eps)
    c_xyy = (-amp + eps, amp - eps, amp + eps)
    c_yxy = (amp + eps, -amp + eps, amp - eps)
    c_yyx = (amp - eps, amp + eps, -amp + eps)
    return c_xxx, c_xyy, c_yxy, c_yyx


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="GHZ v4: high-res re-audit + QM alignment")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=160_000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    ap.add_argument("--r-src-steps", type=int, default=20)
    ap.add_argument("--lambda-steps", type=int, default=20)
    ap.add_argument("--bootstrap-draws", type=int, default=20)
    ap.add_argument("--bootstrap-subsample", type=int, default=30000)
    ap.add_argument("--r-min-focus", type=float, default=0.35)
    args = ap.parse_args()

    out = Path("artifacts/ghz_geometric_v4")
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    n = int(args.samples)

    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    lams = np.stack([l1, l2, l3], axis=0)

    r_vals = np.linspace(0.05, 0.8, int(args.r_src_steps))
    w_vals = np.linspace(0.1, 2.0, int(args.lambda_steps))
    rows = []
    for r_src in r_vals:
        d = compute_distances(float(r_src))
        for lw in w_vals:
            f, r = ghz_f_r_geometric(lams, d, float(lw), float(args.gate_k))
            rows.append({"r_src": float(r_src), "lambda_w": float(lw), "F": float(f), "R": float(r)})

    # Q1: CI on selected high-F points
    top = sorted(rows, key=lambda p: p["F"], reverse=True)[:15]
    ci_rows = []
    for p in top:
        d = compute_distances(p["r_src"])
        lo, hi = bootstrap_ci(rng, lams, d, p["lambda_w"], float(args.gate_k), int(args.bootstrap_draws), int(args.bootstrap_subsample))
        ci_rows.append({**p, "F_ci95_lo": lo, "F_ci95_hi": hi})

    # Q2: local refinement around R_min focus
    r_target = float(args.r_min_focus)
    coarse_best = max([p for p in rows if p["R"] >= r_target], key=lambda x: x["F"], default=None)
    fine_rows = []
    fine_best = None
    if coarse_best is not None:
        r0, w0 = coarse_best["r_src"], coarse_best["lambda_w"]
        r_fine = np.linspace(max(0.05, r0 - 0.05), min(0.8, r0 + 0.05), 51)
        w_fine = np.linspace(max(0.1, w0 - 0.2), min(2.0, w0 + 0.2), 51)
        for rr in r_fine:
            d = compute_distances(float(rr))
            for ww in w_fine:
                f, r = ghz_f_r_geometric(lams, d, float(ww), float(args.gate_k))
                fine_rows.append({"r_src": float(rr), "lambda_w": float(ww), "F": float(f), "R": float(r)})
        fine_best = max([p for p in fine_rows if p["R"] >= r_target], key=lambda x: x["F"], default=None)

    # Q3: confound checks
    f_arr = np.array([p["F"] for p in rows], dtype=np.float64)
    r_arr = np.array([p["R"] for p in rows], dtype=np.float64)
    rs_arr = np.array([p["r_src"] for p in rows], dtype=np.float64)
    lw_arr = np.array([p["lambda_w"] for p in rows], dtype=np.float64)
    corr = {
        "corr_R_r_src": float(np.corrcoef(r_arr, rs_arr)[0, 1]),
        "corr_R_lambda_w": float(np.corrcoef(r_arr, lw_arr)[0, 1]),
        "corr_F_r_src": float(np.corrcoef(f_arr, rs_arr)[0, 1]),
        "corr_F_lambda_w": float(np.corrcoef(f_arr, lw_arr)[0, 1]),
    }

    # Q4: QM alignment surrogate
    qm_rows = []
    for noise_sigma in [0.05, 0.08, 0.12, 0.16, 0.22]:
        c_xxx, c_xyy, c_yxy, c_yyx = qm_mock_contexts(rng, n, noise_sigma=noise_sigma)
        f_qm, r_qm = ghz_f_r_from_contexts(c_xxx, c_xyy, c_yxy, c_yyx, float(args.gate_k))
        qm_rows.append({"noise_sigma": noise_sigma, "F": float(f_qm), "R": float(r_qm), "type": "qm_surrogate"})

    model_top = sorted(rows, key=lambda p: p["F"], reverse=True)[:40]

    # Plot 1 high-res Pareto + CI
    fig1, ax1 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax1.scatter(r_arr, f_arr, s=12, alpha=0.25, label="geometric grid")
    ax1.axhline(2.0, color="gray", ls="--", lw=1.0, label="F=2")
    ax1.axhline(4.0, color="green", ls="--", lw=1.0, label="F=4")
    for p in ci_rows:
        ax1.vlines(p["R"], p["F_ci95_lo"], p["F_ci95_hi"], color="#d62728", alpha=0.8, lw=1.1)
    ax1.scatter([p["R"] for p in ci_rows], [p["F"] for p in ci_rows], s=18, color="#d62728", label="top-F with CI")
    ax1.set_xlabel("R")
    ax1.set_ylabel("F")
    ax1.set_title("V4 Q1 High-resolution Pareto + CI")
    ax1.grid(alpha=0.25)
    ax1.legend(fontsize=8)
    fig1.tight_layout()
    fig1.savefig(out / "V4_Q1_HIGHRES_PARETO_CI.png", dpi=160)
    plt.close(fig1)

    # Plot 2 cliff coarse vs fine
    rmins = np.linspace(0.05, 0.85, 41)
    coarse_curve = []
    fine_curve = []
    for rm in rmins:
        fs = [p["F"] for p in rows if p["R"] >= float(rm)]
        coarse_curve.append(float(max(fs)) if fs else np.nan)
        fs2 = [p["F"] for p in fine_rows if p["R"] >= float(rm)] if fine_rows else []
        fine_curve.append(float(max(fs2)) if fs2 else np.nan)
    fig2, ax2 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax2.plot(rmins, coarse_curve, "-o", ms=3.0, lw=1.4, label="coarse")
    ax2.plot(rmins, fine_curve, "-o", ms=2.6, lw=1.3, label="fine local")
    ax2.axvline(r_target, color="#444", ls=":", lw=1.0, label=f"R_min={r_target:.2f}")
    ax2.axhline(2.0, color="gray", ls="--", lw=1.0)
    ax2.axhline(4.0, color="green", ls="--", lw=1.0)
    ax2.set_xlabel("R_min")
    ax2.set_ylabel("best feasible F")
    ax2.set_title("V4 Q2 Cliff robustness")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out / "V4_Q2_CLIFF_COARSE_VS_FINE.png", dpi=160)
    plt.close(fig2)

    # Plot 3 QM vs model F-R
    fig3, ax3 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax3.scatter([p["R"] for p in model_top], [p["F"] for p in model_top], s=20, alpha=0.7, label="geometric top-40")
    ax3.scatter([p["R"] for p in qm_rows], [p["F"] for p in qm_rows], s=42, marker="D", label="QM surrogate")
    ax3.axhline(2.0, color="gray", ls="--", lw=1.0)
    ax3.axhline(4.0, color="green", ls="--", lw=1.0)
    ax3.set_xlabel("R")
    ax3.set_ylabel("F")
    ax3.set_title("V4 Q4 F-R: geometric vs QM surrogate")
    ax3.grid(alpha=0.25)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(out / "V4_Q4_QM_SURROGATE_FR.png", dpi=160)
    plt.close(fig3)

    result = {
        "seed": int(args.seed),
        "samples": int(args.samples),
        "grid": [int(args.r_src_steps), int(args.lambda_steps)],
        "gate_k": float(args.gate_k),
        "q1_top_ci": ci_rows,
        "q2_cliff": {
            "r_min_focus": r_target,
            "coarse_best_at_focus": coarse_best,
            "fine_best_at_focus": fine_best,
            "fine_grid_shape": [51, 51] if fine_rows else [0, 0],
        },
        "q3_correlations": corr,
        "q4_qm_surrogate": qm_rows,
    }
    (out / "GEOMETRIC_V4_REAUDIT_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    report = [
        "# Geometric V4 Re-audit",
        "",
        "## Scope",
        "- High-resolution internal re-audit for Q1/Q2/Q3",
        "- Q4 closure step via transparent QM surrogate under same gated metric",
        "",
        "## Output",
        "- `V4_Q1_HIGHRES_PARETO_CI.png`",
        "- `V4_Q2_CLIFF_COARSE_VS_FINE.png`",
        "- `V4_Q4_QM_SURROGATE_FR.png`",
        "- `GEOMETRIC_V4_REAUDIT_RESULTS.json`",
    ]
    (out / "GEOMETRIC_V4_REAUDIT_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    print("wrote", out / "GEOMETRIC_V4_REAUDIT_RESULTS.json")
    print("wrote", out / "V4_Q1_HIGHRES_PARETO_CI.png")
    print("wrote", out / "V4_Q2_CLIFF_COARSE_VS_FINE.png")
    print("wrote", out / "V4_Q4_QM_SURROGATE_FR.png")


if __name__ == "__main__":
    main()

