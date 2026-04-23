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


def ghz_eval(lams: np.ndarray, r_src: float, lambda_w: float, gate_k: float, offset: float = 0.0) -> dict:
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
    return {
        "EXXX": exxx,
        "EXYY": exyy,
        "EYXY": eyxy,
        "EYYX": eyyx,
        "F": float(f),
        "R": r,
        "D": float(f * r),
    }


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="V7 holographic GHZ audit")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=100000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    ap.add_argument("--r-src-steps", type=int, default=24)
    ap.add_argument("--lambda-steps", type=int, default=24)
    ap.add_argument("--offset-steps", type=int, default=91)
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
    rows = []
    for r in r_vals:
        for w in w_vals:
            ev = ghz_eval(lams, float(r), float(w), float(args.gate_k), offset=0.0)
            rows.append({"r_src": float(r), "lambda_w": float(w), **ev})

    best_f = max(rows, key=lambda x: x["F"])
    best_d = max(rows, key=lambda x: x["D"])

    # magic-angle drift evidence
    off_vals = np.linspace(0.0, PI / 3.0, int(args.offset_steps))
    drift = []
    for off in off_vals:
        ev = ghz_eval(lams, float(best_d["r_src"]), float(best_d["lambda_w"]), float(args.gate_k), offset=float(off))
        drift.append({"offset_rad": float(off), "offset_deg": float(np.degrees(off)), **ev})
    best_off = max(drift, key=lambda x: x["F"])

    # figure 1: F-R colored by D
    arr_f = np.array([x["F"] for x in rows], dtype=np.float64)
    arr_r = np.array([x["R"] for x in rows], dtype=np.float64)
    arr_d = np.array([x["D"] for x in rows], dtype=np.float64)
    fig1, ax1 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    sc = ax1.scatter(arr_r, arr_f, c=arr_d, s=20, cmap="viridis", alpha=0.75)
    fig1.colorbar(sc, ax=ax1, label="D=F*R")
    ax1.axhline(2.0, color="gray", ls="--", lw=1.0)
    ax1.axhline(4.0, color="green", ls="--", lw=1.0)
    ax1.set_xlabel("R")
    ax1.set_ylabel("F")
    ax1.set_title("V7 F-R-D joint landscape")
    ax1.grid(alpha=0.25)
    fig1.tight_layout()
    fig1.savefig(out / "V7_FR_D_JOINT.png", dpi=160)
    plt.close(fig1)

    # figure 2: holographic shadow scene
    fig2, (a21, a22) = plt.subplots(1, 2, figsize=(11.8, 5.0), dpi=150)
    src = ring_positions(float(best_d["r_src"]), 0.0)
    obs = ring_positions(1.0, 0.0)
    center = np.array([[0.0, 0.0]])
    a21.scatter(center[:, 0], center[:, 1], s=80, c="k", marker="x", label="center")
    a21.scatter(src[:, 0], src[:, 1], s=95, c="#f39c12", label="inner sources")
    a21.scatter(obs[:, 0], obs[:, 1], s=95, c="#3498db", label="outer observers")
    for i in range(3):
        for j in range(3):
            a21.plot([src[i, 0], obs[j, 0]], [src[i, 1], obs[j, 1]], color="gray", alpha=0.28, lw=1.0)
    a21.add_artist(plt.Circle((0, 0), float(best_d["r_src"]), fill=False, ls="--", color="#f39c12", alpha=0.6))
    a21.add_artist(plt.Circle((0, 0), 1.0, fill=False, ls="--", color="#3498db", alpha=0.6))
    a21.set_aspect("equal")
    a21.set_title("Holographic scene reconstruction")
    a21.legend(fontsize=8, loc="upper right")
    a21.grid(alpha=0.22)

    # shadow bars: E-values
    labels = ["XXX", "XYY", "YXY", "YYX"]
    vals = [best_d["EXXX"], best_d["EXYY"], best_d["EYXY"], best_d["EYYX"]]
    a22.bar(labels, vals, color=["#2ecc71", "#e74c3c", "#e74c3c", "#e74c3c"], alpha=0.82)
    a22.axhline(0.0, color="gray", lw=0.8)
    a22.set_ylim(-1.15, 1.15)
    a22.set_title(f"Shadow logic at best-D point\nF={best_d['F']:.3f}, R={best_d['R']:.3f}, D={best_d['D']:.3f}")
    for i, v in enumerate(vals):
        a22.text(i, v + (0.05 if v >= 0 else -0.08), f"{v:+.2f}", ha="center", fontsize=9)
    fig2.tight_layout()
    fig2.savefig(out / "V7_HOLOGRAPHIC_SHADOW_VIEW.png", dpi=160)
    plt.close(fig2)

    # figure 3: magic-angle drift
    deg = np.array([x["offset_deg"] for x in drift], dtype=np.float64)
    ff = np.array([x["F"] for x in drift], dtype=np.float64)
    rr = np.array([x["R"] for x in drift], dtype=np.float64)
    dd = np.array([x["D"] for x in drift], dtype=np.float64)
    fig3, ax3 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax3.plot(deg, ff, label="F(offset)", color="#2c3e50", lw=1.8)
    ax3.plot(deg, rr * 4.0, label="4*R(offset)", color="#8e44ad", lw=1.2, alpha=0.85)
    ax3.plot(deg, dd, label="D(offset)", color="#16a085", lw=1.6)
    ax3.axvline(22.5, color="#d35400", ls="--", lw=1.1, label="22.5 deg")
    ax3.axvline(23.3, color="#c0392b", ls=":", lw=1.1, label="23.3 deg")
    ax3.set_xlabel("offset angle (deg)")
    ax3.set_ylabel("value")
    ax3.set_title("V7 magic-angle drift evidence")
    ax3.grid(alpha=0.25)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(out / "V7_MAGIC_ANGLE_DRIFT.png", dpi=160)
    plt.close(fig3)

    result = {
        "seed": int(args.seed),
        "samples": int(args.samples),
        "gate_k": float(args.gate_k),
        "grid": [int(args.r_src_steps), int(args.lambda_steps)],
        "best_by_F": best_f,
        "best_by_D": best_d,
        "magic_angle_scan": {
            "offset_range_deg": [0.0, 60.0],
            "best_by_F_offset": best_off,
        },
        "counts": {
            "n_high_F_gt_3_5_and_R_gt_0_5": int(sum(1 for x in rows if x["F"] > 3.5 and x["R"] > 0.5)),
        },
    }
    (out / "V7_HOLOGRAPHIC_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "V7_HOLOGRAPHIC_REPORT.md").write_text(
        "\n".join(
            [
                "# V7 Holographic Audit",
                "",
                "## Outputs",
                "- `V7_FR_D_JOINT.png`",
                "- `V7_HOLOGRAPHIC_SHADOW_VIEW.png`",
                "- `V7_MAGIC_ANGLE_DRIFT.png`",
                "- `V7_HOLOGRAPHIC_RESULTS.json`",
                "",
                "## Key points",
                f"- best F = {best_f['F']:.6f} @ R={best_f['R']:.6f}, D={best_f['D']:.6f}",
                f"- best D = {best_d['D']:.6f} with F={best_d['F']:.6f}, R={best_d['R']:.6f}",
                f"- best offset for F in drift = {best_off['offset_deg']:.3f} deg",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out / "V7_HOLOGRAPHIC_RESULTS.json")
    print("wrote", out / "V7_FR_D_JOINT.png")
    print("wrote", out / "V7_HOLOGRAPHIC_SHADOW_VIEW.png")
    print("wrote", out / "V7_MAGIC_ANGLE_DRIFT.png")


if __name__ == "__main__":
    main()

