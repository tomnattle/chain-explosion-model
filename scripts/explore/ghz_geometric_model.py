#!/usr/bin/env python3
"""
Geometric GHZ sphere model with explicit path-delay phases.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


N = 500_000
SEED = 42
rng = np.random.default_rng(SEED)

R_OBS = 1.0
R_SRC = 0.3
LAMBDA_W = 0.5

obs_angles = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0])
src_angles = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0])

obs_pos = np.stack([R_OBS * np.cos(obs_angles), R_OBS * np.sin(obs_angles)], axis=1)


def compute_distances(r_src: float, r_obs: float = R_OBS, offset_angle: float = 0.0) -> np.ndarray:
    s_angles = src_angles + offset_angle
    s_pos = np.stack([r_src * np.cos(s_angles), r_src * np.sin(s_angles)], axis=1)
    d = np.zeros((3, 3), dtype=np.float64)
    for i in range(3):
        for j in range(3):
            diff = s_pos[i] - obs_pos[j]
            d[i, j] = np.sqrt(np.sum(diff * diff))
    return d


lam1 = rng.uniform(0.0, 2.0 * np.pi, N)
lam2 = rng.uniform(0.0, 2.0 * np.pi, N)
lam3 = (-lam1 - lam2) % (2.0 * np.pi)
lams = np.stack([lam1, lam2, lam3], axis=0)  # (3, N)


def observer_signal(obs_idx: int, meas_angle: float, d_matrix: np.ndarray, lambda_w: float) -> np.ndarray:
    signal = np.zeros(N, dtype=np.float64)
    for src_idx in range(3):
        d = float(d_matrix[src_idx, obs_idx])
        phase_delay = 2.0 * np.pi * d / lambda_w
        signal += (1.0 / d) * np.cos(lams[src_idx] - meas_angle - phase_delay)
    return signal


def e3_ncc(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray) -> float:
    num = float(np.mean(sa * sb * sc))
    # Keep the normalization exactly as proposed in user's draft.
    den = float(np.mean(sa * sa) * np.mean(sb * sb) * np.mean(sc * sc)) ** (1.0 / 3.0)
    return num / den if den > 1e-12 else 0.0


def soft_detector(x: np.ndarray, threshold: float) -> np.ndarray:
    y = np.zeros_like(x)
    y[x > threshold] = 1.0
    y[x < -threshold] = -1.0
    return y


def e3_gated_binary(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray, gate_k: float = 0.65) -> tuple[float, float]:
    # Threshold is proportional to each arm's RMS to keep scale comparable across settings.
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


def compute_f(d_matrix: np.ndarray, lambda_w: float, gate_k: float = 0.65) -> dict[str, float]:
    x, y = 0.0, np.pi / 2.0

    ax = observer_signal(0, x, d_matrix, lambda_w)
    bx = observer_signal(1, x, d_matrix, lambda_w)
    cx = observer_signal(2, x, d_matrix, lambda_w)
    ay = observer_signal(0, y, d_matrix, lambda_w)
    by = observer_signal(1, y, d_matrix, lambda_w)
    cy = observer_signal(2, y, d_matrix, lambda_w)

    exxx = e3_ncc(ax, bx, cx)
    exyy = e3_ncc(ax, by, cy)
    eyxy = e3_ncc(ay, bx, cy)
    eyyx = e3_ncc(ay, by, cx)
    f = exxx - exyy - eyxy - eyyx

    gxxx, r1 = e3_gated_binary(ax, bx, cx, gate_k=gate_k)
    gxyy, r2 = e3_gated_binary(ax, by, cy, gate_k=gate_k)
    gyxy, r3 = e3_gated_binary(ay, bx, cy, gate_k=gate_k)
    gyyx, r4 = e3_gated_binary(ay, by, cx, gate_k=gate_k)
    fg = gxxx - gxyy - gyxy - gyyx
    rg = float(np.mean([r1, r2, r3, r4]))

    return {
        "F": float(f),
        "EXXX": float(exxx),
        "EXYY": float(exyy),
        "EYXY": float(eyxy),
        "EYYX": float(eyyx),
        "F_gated": float(fg),
        "GXXX": float(gxxx),
        "GXYY": float(gxyy),
        "GYXY": float(gyxy),
        "GYYX": float(gyyx),
        "R_gated": float(rg),
    }


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print("=== 扫描 R_src × Lambda_w（双口径）===")
    r_src_vals = np.linspace(0.05, 0.8, 16)
    lambda_vals = np.linspace(0.1, 2.0, 16)

    results_grid = np.zeros((len(r_src_vals), len(lambda_vals)), dtype=np.float64)
    results_grid_g = np.zeros((len(r_src_vals), len(lambda_vals)), dtype=np.float64)
    best = {"F": 0.0}
    best_g = {"F_gated": 0.0}

    for i, r in enumerate(r_src_vals):
        for j, lw in enumerate(lambda_vals):
            d = compute_distances(float(r))
            res = compute_f(d, float(lw))
            results_grid[i, j] = res["F"]
            results_grid_g[i, j] = res["F_gated"]
            if abs(res["F"]) > abs(best["F"]):
                best = {**res, "r_src": float(r), "lambda_w": float(lw)}
            if abs(res["F_gated"]) > abs(best_g["F_gated"]):
                best_g = {**res, "r_src": float(r), "lambda_w": float(lw)}

    print(f"\n最优: F={best['F']:.5f}")
    print(f"  R_src={best['r_src']:.3f}, Lambda_w={best['lambda_w']:.3f}")
    print(f"  E(XXX)={best['EXXX']:+.4f}")
    print(f"  E(XYY)={best['EXYY']:+.4f}")
    print(f"  E(YXY)={best['EYXY']:+.4f}")
    print(f"  E(YYX)={best['EYYX']:+.4f}")
    print(f"\n最优(gated): Fg={best_g['F_gated']:.5f}, Rg={best_g['R_gated']:.4f}")
    print(f"  R_src={best_g['r_src']:.3f}, Lambda_w={best_g['lambda_w']:.3f}")
    print(f"  G(XXX)={best_g['GXXX']:+.4f}")
    print(f"  G(XYY)={best_g['GXYY']:+.4f}")
    print(f"  G(YXY)={best_g['GYXY']:+.4f}")
    print(f"  G(YYX)={best_g['GYYX']:+.4f}")

    print("\n=== 扫描内圈旋转偏移 ===")
    best_r = float(best["r_src"])
    best_lw = float(best["lambda_w"])

    offsets = np.linspace(0.0, np.pi / 3.0, 19)
    print(f"{'偏移角':>8}  {'F_legacy':>10}  {'Fg_gated':>10}  {'|Fg-4|':>10}")
    f_offs = []
    fg_offs = []
    for off in offsets:
        d = compute_distances(best_r, offset_angle=float(off))
        res = compute_f(d, best_lw)
        f_offs.append(res["F"])
        fg_offs.append(res["F_gated"])
        print(f"{np.degrees(off):>7.1f}°  {res['F']:>+10.5f}  {res['F_gated']:>+10.5f}  {abs(res['F_gated']-4):>10.5f}")

    out_dir = Path("artifacts/ghz_geometric")
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Geometric GHZ Sphere Model: Dual-Metric Audit", fontsize=13)

    ax00 = axes[0, 0]
    im = ax00.contourf(lambda_vals, r_src_vals, results_grid, levels=20, cmap="RdYlGn")
    plt.colorbar(im, ax=ax00)
    ax00.set_xlabel("Wave length lambda_w")
    ax00.set_ylabel("Inner radius R_src")
    ax00.set_title("F_legacy(R_src, lambda_w)")
    ax00.axhline(best_r, color="white", lw=1, ls="--")
    ax00.axvline(best_lw, color="white", lw=1, ls="--")

    ax01 = axes[0, 1]
    im2 = ax01.contourf(lambda_vals, r_src_vals, results_grid_g, levels=20, cmap="RdYlGn")
    plt.colorbar(im2, ax=ax01)
    ax01.set_xlabel("Wave length lambda_w")
    ax01.set_ylabel("Inner radius R_src")
    ax01.set_title("F_gated(R_src, lambda_w)")
    ax01.axhline(best_g["r_src"], color="white", lw=1, ls="--")
    ax01.axvline(best_g["lambda_w"], color="white", lw=1, ls="--")

    ax10 = axes[1, 0]
    ax10.plot(np.degrees(offsets), f_offs, "o-", color="steelblue", label="legacy")
    ax10.plot(np.degrees(offsets), fg_offs, "o-", color="#d62728", label="gated")
    ax10.axhline(2.0, color="red", ls="--", lw=1, label="LHV上限 F=2")
    ax10.axhline(4.0, color="green", ls="--", lw=1, label="QM目标 F=4")
    ax10.axhline(0.0, color="gray", ls=":", lw=1)
    ax10.set_xlabel("内圈旋转偏移 (度)")
    ax10.set_ylabel("F")
    ax10.set_title("F vs 几何错位（双口径）")
    ax10.legend(fontsize=8)
    ax10.grid(alpha=0.3)

    best_d = compute_distances(best_r)
    res_best = compute_f(best_d, best_lw)
    labels = ["E(XXX)\n目标+1", "E(XYY)\n目标-1", "E(YXY)\n目标-1", "E(YYX)\n目标-1"]
    vals = [res_best["EXXX"], res_best["EXYY"], res_best["EYXY"], res_best["EYYX"]]
    colors = ["#1D9E75" if abs(v - t) < 0.2 else "#E24B4A" for v, t in zip(vals, [1, -1, -1, -1])]
    ax11 = axes[1, 1]
    ax11.bar(labels, vals, color=colors, alpha=0.8, edgecolor="white")
    ax11.axhline(0.0, color="gray", lw=0.5)
    ax11.set_ylim(-3.0, 3.0)
    ax11.set_title(f"legacy四个E值（F={res_best['F']:.4f}）")
    ax11.set_ylabel("E值")
    for i, v in enumerate(vals):
        ax11.text(i, v + (0.08 if v >= 0 else -0.12), f"{v:+.3f}", ha="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_dir / "F_geometric_analysis.png", dpi=150)

    with (out_dir / "GHZ_GEOMETRIC_RESULTS.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "best_legacy": best,
                "best_gated": best_g,
                "grid_shape": list(results_grid.shape),
                "grid_max": float(results_grid.max()),
                "grid_min": float(results_grid.min()),
                "grid_gated_max": float(results_grid_g.max()),
                "grid_gated_min": float(results_grid_g.min()),
            },
            f,
            indent=2,
        )

    print("\n图已保存")
    print("JSON已保存")


if __name__ == "__main__":
    main()

