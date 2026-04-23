#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


PI = math.pi
TWO_PI = 2.0 * PI


def ring_positions(radius: float, offset: float = 0.0) -> np.ndarray:
    ang = np.array([0.0, 2.0 * PI / 3.0, 4.0 * PI / 3.0], dtype=np.float64) + offset
    return np.stack([radius * np.cos(ang), radius * np.sin(ang)], axis=1)


def compute_distances(r_src: float, r_obs: float = 1.0, offset: float = 0.0) -> np.ndarray:
    obs = ring_positions(r_obs, 0.0)
    src = ring_positions(r_src, offset)
    d = np.zeros((3, 3), dtype=np.float64)
    for i in range(3):
        for j in range(3):
            u = src[i] - obs[j]
            d[i, j] = np.sqrt(np.sum(u * u))
    return d


def observer_signal(lams: np.ndarray, obs_idx: int, meas_angle: float, d: np.ndarray, lambda_w: float) -> np.ndarray:
    out = np.zeros(lams.shape[1], dtype=np.float64)
    for i in range(3):
        dij = float(d[i, obs_idx])
        out += (1.0 / dij) * np.cos(lams[i] - meas_angle - (TWO_PI * dij / lambda_w))
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


def ghz_eval(lams: np.ndarray, r_src: float, lambda_w: float, gate_k: float, offset: float) -> tuple[float, float, float]:
    x, y = 0.0, PI / 2.0
    d = compute_distances(r_src, offset=offset)
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
    return float(f), r, float(f * r)


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="v7.1 magic-angle phase map")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=90000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    ap.add_argument("--r-src-steps", type=int, default=18)
    ap.add_argument("--lambda-steps", type=int, default=18)
    ap.add_argument("--offset-steps", type=int, default=121)
    args = ap.parse_args()

    out = Path("artifacts/ghz_geometric_v7")
    out.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    n = int(args.samples)
    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    lams = np.stack([l1, l2, l3], axis=0)

    r_vals = np.linspace(0.05, 0.8, int(args.r_src_steps))
    w_vals = np.linspace(0.1, 2.0, int(args.lambda_steps))
    off_vals = np.linspace(0.0, PI / 3.0, int(args.offset_steps))

    best_offset_deg = np.zeros((len(r_vals), len(w_vals)), dtype=np.float64)
    best_f = np.zeros((len(r_vals), len(w_vals)), dtype=np.float64)
    best_r = np.zeros((len(r_vals), len(w_vals)), dtype=np.float64)
    best_d = np.zeros((len(r_vals), len(w_vals)), dtype=np.float64)

    near_225 = []
    near_233 = []
    for i, r_src in enumerate(r_vals):
        for j, lw in enumerate(w_vals):
            loc = []
            for off in off_vals:
                f, rr, dd = ghz_eval(lams, float(r_src), float(lw), float(args.gate_k), float(off))
                loc.append((float(off), f, rr, dd))
            b = max(loc, key=lambda x: x[1])  # by F
            off_deg = float(np.degrees(b[0]))
            best_offset_deg[i, j] = off_deg
            best_f[i, j] = b[1]
            best_r[i, j] = b[2]
            best_d[i, j] = b[3]
            if abs(off_deg - 22.5) <= 1.0:
                near_225.append({"r_src": float(r_src), "lambda_w": float(lw), "offset_deg": off_deg, "F": b[1], "R": b[2], "D": b[3]})
            if abs(off_deg - 23.3) <= 1.0:
                near_233.append({"r_src": float(r_src), "lambda_w": float(lw), "offset_deg": off_deg, "F": b[1], "R": b[2], "D": b[3]})

    # Plot map: best offset by parameter pair
    fig1, ax1 = plt.subplots(figsize=(7.6, 5.6), dpi=150)
    im = ax1.contourf(w_vals, r_vals, best_offset_deg, levels=24, cmap="turbo")
    fig1.colorbar(im, ax=ax1, label="best offset (deg) for max F")
    ax1.set_xlabel("lambda_w")
    ax1.set_ylabel("r_src")
    ax1.set_title("V7.1 Magic-angle peak map")
    fig1.tight_layout()
    fig1.savefig(out / "V7_1_MAGIC_ANGLE_PEAK_MAP.png", dpi=160)
    plt.close(fig1)

    # Plot two reference-band overlays
    fig2, ax2 = plt.subplots(figsize=(7.6, 5.6), dpi=150)
    ax2.scatter([x["lambda_w"] for x in near_225], [x["r_src"] for x in near_225], s=35, alpha=0.8, label="near 22.5±1deg")
    ax2.scatter([x["lambda_w"] for x in near_233], [x["r_src"] for x in near_233], s=35, alpha=0.8, label="near 23.3±1deg")
    ax2.set_xlabel("lambda_w")
    ax2.set_ylabel("r_src")
    ax2.set_title("V7.1 Parameter islands near magic-angle bands")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out / "V7_1_MAGIC_ANGLE_ISLANDS.png", dpi=160)
    plt.close(fig2)

    result = {
        "seed": int(args.seed),
        "samples": int(args.samples),
        "grid": [int(args.r_src_steps), int(args.lambda_steps), int(args.offset_steps)],
        "near_22_5_count": len(near_225),
        "near_23_3_count": len(near_233),
        "near_22_5_topD": max(near_225, key=lambda x: x["D"]) if near_225 else None,
        "near_23_3_topD": max(near_233, key=lambda x: x["D"]) if near_233 else None,
        "global_best_F_after_offset_opt": {
            "F": float(np.max(best_f)),
            "R": float(best_r[np.unravel_index(np.argmax(best_f), best_f.shape)]),
            "D": float(best_d[np.unravel_index(np.argmax(best_f), best_f.shape)]),
            "offset_deg": float(best_offset_deg[np.unravel_index(np.argmax(best_f), best_f.shape)]),
            "r_src": float(r_vals[np.unravel_index(np.argmax(best_f), best_f.shape)[0]]),
            "lambda_w": float(w_vals[np.unravel_index(np.argmax(best_f), best_f.shape)[1]]),
        },
    }
    (out / "V7_1_MAGIC_ANGLE_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "V7_1_MAGIC_ANGLE_REPORT.md").write_text(
        "\n".join(
            [
                "# V7.1 Magic-angle专项",
                "",
                "## Outputs",
                "- `V7_1_MAGIC_ANGLE_PEAK_MAP.png`",
                "- `V7_1_MAGIC_ANGLE_ISLANDS.png`",
                "- `V7_1_MAGIC_ANGLE_RESULTS.json`",
                "",
                f"- near 22.5 deg islands: {len(near_225)}",
                f"- near 23.3 deg islands: {len(near_233)}",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out / "V7_1_MAGIC_ANGLE_RESULTS.json")
    print("wrote", out / "V7_1_MAGIC_ANGLE_PEAK_MAP.png")
    print("wrote", out / "V7_1_MAGIC_ANGLE_ISLANDS.png")


if __name__ == "__main__":
    main()

