#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


PI = math.pi
TWO_PI = 2.0 * PI


def compute_distances(r_src: float, r_obs: float = 1.0) -> np.ndarray:
    obs_angles = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0], dtype=np.float64)
    src_angles = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0], dtype=np.float64)
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


def ghz_f_r(lams: np.ndarray, d: np.ndarray, lambda_w: float, gate_k: float) -> tuple[float, float]:
    x, y = 0.0, np.pi / 2.0
    ax = observer_signal(lams, 0, x, d, lambda_w)
    bx = observer_signal(lams, 1, x, d, lambda_w)
    cx = observer_signal(lams, 2, x, d, lambda_w)
    ay = observer_signal(lams, 0, y, d, lambda_w)
    by = observer_signal(lams, 1, y, d, lambda_w)
    cy = observer_signal(lams, 2, y, d, lambda_w)

    exxx, r1 = e3_gated(ax, bx, cx, gate_k)
    exyy, r2 = e3_gated(ax, by, cy, gate_k)
    eyxy, r3 = e3_gated(ay, bx, cy, gate_k)
    eyyx, r4 = e3_gated(ay, by, cx, gate_k)
    f = exxx - exyy - eyxy - eyyx
    r = float(np.mean([r1, r2, r3, r4]))
    return float(f), r


def pareto_front(points: list[dict]) -> list[dict]:
    # maximize F and R simultaneously
    pts = sorted(points, key=lambda p: (p["R"], p["F"]))
    out = []
    best_f = -1e18
    for p in pts:
        if p["F"] > best_f:
            out.append(p)
            best_f = p["F"]
    return out


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    seed = 20260423
    n = 500_000
    gate_k = 0.65
    rng = np.random.default_rng(seed)
    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    lams = np.stack([l1, l2, l3], axis=0)

    r_vals = np.linspace(0.05, 0.8, 16)
    w_vals = np.linspace(0.1, 2.0, 16)

    rows = []
    for r_src in r_vals:
        d = compute_distances(float(r_src))
        for lw in w_vals:
            f, r = ghz_f_r(lams, d, float(lw), gate_k)
            rows.append({"r_src": float(r_src), "lambda_w": float(lw), "F": f, "R": r})

    # frontier by F-R
    frontier = pareto_front(rows)

    # R_min threshold curve
    rmins = np.linspace(0.05, 0.85, 33)
    threshold_curve = []
    for rm in rmins:
        feasible = [x for x in rows if x["R"] >= float(rm)]
        if feasible:
            best = max(feasible, key=lambda x: x["F"])
            threshold_curve.append(
                {
                    "R_min": float(rm),
                    "best_F": float(best["F"]),
                    "best_R": float(best["R"]),
                    "r_src": float(best["r_src"]),
                    "lambda_w": float(best["lambda_w"]),
                }
            )
        else:
            threshold_curve.append({"R_min": float(rm), "best_F": None, "best_R": None, "r_src": None, "lambda_w": None})

    out_dir = Path("artifacts/ghz_geometric_v2")
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "seed": seed,
        "samples": n,
        "gate_k": gate_k,
        "grid_shape": [len(r_vals), len(w_vals)],
        "rows": rows,
        "pareto_frontier": frontier,
        "rmin_curve": threshold_curve,
    }
    (out_dir / "GEOMETRIC_PARETO_V2.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Figure 1: Pareto scatter + frontier
    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax.scatter([p["R"] for p in rows], [p["F"] for p in rows], s=16, alpha=0.35, label="grid points")
    ax.plot([p["R"] for p in frontier], [p["F"] for p in frontier], "-o", lw=2.0, ms=4, label="Pareto frontier")
    ax.axhline(2.0, color="gray", ls="--", lw=1.0, label="F=2")
    ax.axhline(4.0, color="green", ls="--", lw=1.0, label="F=4")
    ax.set_xlabel("R (sample retention)")
    ax.set_ylabel("F (gated)")
    ax.set_title("Pareto Audit: F vs R")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "GEOMETRIC_PARETO_FRONTIER.png", dpi=160)
    plt.close(fig)

    # Figure 2: R_min -> best F
    x = [p["R_min"] for p in threshold_curve]
    y = [np.nan if p["best_F"] is None else p["best_F"] for p in threshold_curve]
    fig2, ax2 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax2.plot(x, y, "-o", lw=1.8, ms=3.5)
    ax2.axhline(2.0, color="gray", ls="--", lw=1.0, label="F=2")
    ax2.axhline(4.0, color="green", ls="--", lw=1.0, label="F=4")
    ax2.set_xlabel("R_min constraint")
    ax2.set_ylabel("best feasible F")
    ax2.set_title("Cost Curve: R_min vs Best F")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out_dir / "GEOMETRIC_RMIN_COST_CURVE.png", dpi=160)
    plt.close(fig2)

    md = [
        "# Geometric Pareto Audit V2",
        "",
        f"- samples: **{n}**, gate_k: **{gate_k:.2f}**",
        f"- grid: **{len(r_vals)} x {len(w_vals)}**",
        "",
        "## Key Outputs",
        "",
        "- `GEOMETRIC_PARETO_FRONTIER.png`",
        "- `GEOMETRIC_RMIN_COST_CURVE.png`",
        "- `GEOMETRIC_PARETO_V2.json`",
    ]
    (out_dir / "GEOMETRIC_PARETO_V2_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    print("wrote", out_dir / "GEOMETRIC_PARETO_V2.json")
    print("wrote", out_dir / "GEOMETRIC_PARETO_FRONTIER.png")
    print("wrote", out_dir / "GEOMETRIC_RMIN_COST_CURVE.png")


if __name__ == "__main__":
    main()

