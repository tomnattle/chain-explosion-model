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
        phase = TWO_PI * dij / lambda_w
        out += (1.0 / dij) * np.cos(lams[i] - meas_angle - phase)
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


def ghz_eval(lams: np.ndarray, r_src: float, lambda_w: float, gate_k: float, offset_deg: float) -> dict:
    off = math.radians(offset_deg)
    x, y = 0.0, PI / 2.0
    d = compute_distances(r_src, offset=off)
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
    return {"F": float(f), "R": r, "D": float(f * r), "offset_deg": offset_deg}


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="V7.1b magic-band high-density hunt")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=100000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    ap.add_argument("--r-min", type=float, default=0.45)
    ap.add_argument("--r-max", type=float, default=0.70)
    ap.add_argument("--lambda-min", type=float, default=1.20)
    ap.add_argument("--lambda-max", type=float, default=1.90)
    ap.add_argument("--grid-steps", type=int, default=25)
    ap.add_argument("--offset-min", type=float, default=18.0)
    ap.add_argument("--offset-max", type=float, default=28.0)
    ap.add_argument("--offset-steps", type=int, default=11)
    args = ap.parse_args()

    out = Path("artifacts/ghz_geometric_v7")
    out.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    n = int(args.samples)
    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    lams = np.stack([l1, l2, l3], axis=0)

    r_vals = np.linspace(float(args.r_min), float(args.r_max), int(args.grid_steps))
    w_vals = np.linspace(float(args.lambda_min), float(args.lambda_max), int(args.grid_steps))
    off_vals = np.linspace(float(args.offset_min), float(args.offset_max), int(args.offset_steps))

    best_rows = []
    for r_src in r_vals:
        for lw in w_vals:
            local_best = None
            for off in off_vals:
                ev = ghz_eval(lams, float(r_src), float(lw), float(args.gate_k), float(off))
                row = {"r_src": float(r_src), "lambda_w": float(lw), **ev}
                if local_best is None or row["D"] > local_best["D"]:
                    local_best = row
            best_rows.append(local_best)

    best_d = max(best_rows, key=lambda x: x["D"])
    best_f = max(best_rows, key=lambda x: x["F"])
    cnt_high = sum(1 for x in best_rows if x["F"] >= 3.0 and x["R"] >= 0.4)

    # heatmap of best D in the magic band
    dm = np.array([x["D"] for x in best_rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))
    fm = np.array([x["F"] for x in best_rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))
    rm = np.array([x["R"] for x in best_rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))
    om = np.array([x["offset_deg"] for x in best_rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))

    fig, axes = plt.subplots(2, 2, figsize=(12.0, 9.0), dpi=150)
    im0 = axes[0, 0].contourf(w_vals, r_vals, dm, levels=20, cmap="viridis")
    fig.colorbar(im0, ax=axes[0, 0])
    axes[0, 0].set_title("best D in magic band")
    axes[0, 0].set_xlabel("lambda_w")
    axes[0, 0].set_ylabel("r_src")

    im1 = axes[0, 1].contourf(w_vals, r_vals, fm, levels=20, cmap="coolwarm")
    fig.colorbar(im1, ax=axes[0, 1])
    axes[0, 1].set_title("F at best-D offset")
    axes[0, 1].set_xlabel("lambda_w")
    axes[0, 1].set_ylabel("r_src")

    im2 = axes[1, 0].contourf(w_vals, r_vals, rm, levels=20, cmap="plasma")
    fig.colorbar(im2, ax=axes[1, 0])
    axes[1, 0].set_title("R at best-D offset")
    axes[1, 0].set_xlabel("lambda_w")
    axes[1, 0].set_ylabel("r_src")

    im3 = axes[1, 1].contourf(w_vals, r_vals, om, levels=20, cmap="turbo")
    fig.colorbar(im3, ax=axes[1, 1])
    axes[1, 1].set_title("offset(deg) chosen by best D")
    axes[1, 1].set_xlabel("lambda_w")
    axes[1, 1].set_ylabel("r_src")

    fig.tight_layout()
    fig.savefig(out / "V7_1B_MAGIC_BAND_DENSITY_MAPS.png", dpi=160)
    plt.close(fig)

    result = {
        "seed": int(args.seed),
        "samples": int(args.samples),
        "band": {"offset_min": float(args.offset_min), "offset_max": float(args.offset_max), "offset_steps": int(args.offset_steps)},
        "grid": {"r_min": float(args.r_min), "r_max": float(args.r_max), "lambda_min": float(args.lambda_min), "lambda_max": float(args.lambda_max), "steps": int(args.grid_steps)},
        "best_by_D": best_d,
        "best_by_F": best_f,
        "count_F_ge_3_and_R_ge_0_4": int(cnt_high),
    }
    (out / "V7_1B_MAGIC_BAND_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "V7_1B_MAGIC_BAND_REPORT.md").write_text(
        "\n".join(
            [
                "# V7.1b Magic-band density hunt",
                "",
                "Target: maximize D=F*R inside offset band [18,28] deg",
                "",
                "## Outputs",
                "- `V7_1B_MAGIC_BAND_DENSITY_MAPS.png`",
                "- `V7_1B_MAGIC_BAND_RESULTS.json`",
                "",
                f"- best D: {best_d['D']:.6f} (F={best_d['F']:.6f}, R={best_d['R']:.6f}, off={best_d['offset_deg']:.3f})",
                f"- count(F>=3 and R>=0.4): {cnt_high}",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out / "V7_1B_MAGIC_BAND_RESULTS.json")
    print("wrote", out / "V7_1B_MAGIC_BAND_DENSITY_MAPS.png")


if __name__ == "__main__":
    main()

