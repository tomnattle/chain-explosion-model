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

    ap = argparse.ArgumentParser(description="V8 peak-degeneracy scan (r_src->0)")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=60000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    ap.add_argument("--r-src-steps", type=int, default=21)
    ap.add_argument("--offset-steps", type=int, default=121)
    ap.add_argument("--lambda-list", type=str, default="0.10,0.50,1.00,1.60")
    args = ap.parse_args()

    out = Path("artifacts/ghz_geometric_v8")
    out.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    n = int(args.samples)
    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    lams = np.stack([l1, l2, l3], axis=0)

    lambda_list = [float(x.strip()) for x in args.lambda_list.split(",") if x.strip()]
    r_vals = np.linspace(0.02, 0.8, int(args.r_src_steps))
    off_vals = np.linspace(0.0, PI / 3.0, int(args.offset_steps))

    rows = []
    for lw in lambda_list:
        for r_src in r_vals:
            best = None
            for off in off_vals:
                f, r, d = ghz_eval(lams, float(r_src), float(lw), float(args.gate_k), float(off))
                item = {"lambda_w": lw, "r_src": float(r_src), "offset_deg": float(np.degrees(off)), "F": f, "R": r, "D": d}
                if best is None or item["F"] > best["F"]:
                    best = item
            rows.append(best)

    # classify closest reference
    refs = [0.0, 22.5, 23.3, 24.0]
    for x in rows:
        rr = min(refs, key=lambda z: abs(x["offset_deg"] - z))
        x["closest_ref_deg"] = rr
        x["delta_ref_deg"] = abs(x["offset_deg"] - rr)

    # plot: peak offset vs r_src (for each lambda)
    fig1, ax1 = plt.subplots(figsize=(8.0, 5.4), dpi=150)
    for lw in lambda_list:
        sub = [x for x in rows if abs(x["lambda_w"] - lw) < 1e-12]
        sub = sorted(sub, key=lambda z: z["r_src"])
        ax1.plot([x["r_src"] for x in sub], [x["offset_deg"] for x in sub], marker="o", ms=3, lw=1.2, label=f"lambda={lw:.2f}")
    for ref, style in [(0.0, ":"), (22.5, "--"), (23.3, "--"), (24.0, "--")]:
        ax1.axhline(ref, color="gray", ls=style, lw=0.9)
    ax1.set_xlabel("r_src")
    ax1.set_ylabel("peak offset (deg, max F)")
    ax1.set_title("V8 peak-angle degeneracy vs r_src")
    ax1.grid(alpha=0.25)
    ax1.legend(fontsize=8)
    fig1.tight_layout()
    fig1.savefig(out / "V8_PEAK_OFFSET_VS_RSRC.png", dpi=160)
    plt.close(fig1)

    # plot: D at that peak
    fig2, ax2 = plt.subplots(figsize=(8.0, 5.4), dpi=150)
    for lw in lambda_list:
        sub = [x for x in rows if abs(x["lambda_w"] - lw) < 1e-12]
        sub = sorted(sub, key=lambda z: z["r_src"])
        ax2.plot([x["r_src"] for x in sub], [x["D"] for x in sub], marker="o", ms=3, lw=1.2, label=f"lambda={lw:.2f}")
    ax2.set_xlabel("r_src")
    ax2.set_ylabel("D at peak-F offset")
    ax2.set_title("V8 density curve under peak-angle selection")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out / "V8_DENSITY_AT_PEAK_OFFSET.png", dpi=160)
    plt.close(fig2)

    # summary near r_src -> 0
    small_r = sorted(rows, key=lambda x: x["r_src"])[: len(lambda_list)]
    result = {
        "seed": int(args.seed),
        "samples": int(args.samples),
        "lambda_list": lambda_list,
        "grid": {"r_src_steps": int(args.r_src_steps), "offset_steps": int(args.offset_steps)},
        "small_r_behavior": small_r,
        "rows": rows,
    }
    (out / "V8_PEAK_DEGENERACY_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    report = [
        "# V8 Peak Degeneracy Scan",
        "",
        "Tracks how best-F offset changes when r_src shrinks.",
        "",
        "## Reference lines",
        "- 0 deg (full alignment)",
        "- 22.5 deg (Bell-style orthogonal magic)",
        "- 23.3 deg (observed side-peak)",
        "- 24.0 deg (120/5 heuristic)",
        "",
        "## Outputs",
        "- `V8_PEAK_OFFSET_VS_RSRC.png`",
        "- `V8_DENSITY_AT_PEAK_OFFSET.png`",
        "- `V8_PEAK_DEGENERACY_RESULTS.json`",
    ]
    (out / "V8_PEAK_DEGENERACY_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print("wrote", out / "V8_PEAK_DEGENERACY_RESULTS.json")
    print("wrote", out / "V8_PEAK_OFFSET_VS_RSRC.png")
    print("wrote", out / "V8_DENSITY_AT_PEAK_OFFSET.png")


if __name__ == "__main__":
    main()

