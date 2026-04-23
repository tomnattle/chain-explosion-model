#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from ghz_data_connector import compute_fr_from_shots, load_any


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


def ghz_f_r(lams: np.ndarray, d: np.ndarray, lambda_w: float, gate_k: float) -> tuple[float, float]:
    x, y = 0.0, PI / 2.0
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
    return float(f), float(np.mean([r1, r2, r3, r4]))


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="GHZ geometric v5 external-closure audit")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=120_000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    ap.add_argument("--r-src-steps", type=int, default=24)
    ap.add_argument("--lambda-steps", type=int, default=24)
    ap.add_argument("--focus-r-center", type=float, default=0.4)
    ap.add_argument("--focus-r-half-width", type=float, default=0.12)
    ap.add_argument("--focus-lambda-min", type=float, default=0.1)
    ap.add_argument("--focus-lambda-max", type=float, default=0.8)
    ap.add_argument("--focus-steps", type=int, default=49)
    ap.add_argument("--external-shots", type=str, default="")
    args = ap.parse_args()

    out = Path("artifacts/ghz_geometric_v5")
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    n = int(args.samples)
    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    lams = np.stack([l1, l2, l3], axis=0)

    # --- coarse high-resolution exploration 24x24
    r_vals = np.linspace(0.05, 0.8, int(args.r_src_steps))
    w_vals = np.linspace(0.1, 2.0, int(args.lambda_steps))
    rows = []
    for r_src in r_vals:
        d = compute_distances(float(r_src))
        for lw in w_vals:
            f, r = ghz_f_r(lams, d, float(lw), float(args.gate_k))
            rows.append({"r_src": float(r_src), "lambda_w": float(lw), "F": float(f), "R": float(r), "D": float(f * r)})

    # --- focused deep sampling near r_src ~= 0.4
    r_lo = max(0.05, float(args.focus_r_center - args.focus_r_half_width))
    r_hi = min(0.8, float(args.focus_r_center + args.focus_r_half_width))
    fr_vals = np.linspace(r_lo, r_hi, int(args.focus_steps))
    fw_vals = np.linspace(float(args.focus_lambda_min), float(args.focus_lambda_max), int(args.focus_steps))
    focus_rows = []
    for rr in fr_vals:
        d = compute_distances(float(rr))
        for ww in fw_vals:
            f, r = ghz_f_r(lams, d, float(ww), float(args.gate_k))
            focus_rows.append({"r_src": float(rr), "lambda_w": float(ww), "F": float(f), "R": float(r), "D": float(f * r)})

    best_f = max(rows, key=lambda x: x["F"])
    best_d = max(rows, key=lambda x: x["D"])
    focus_best_f = max(focus_rows, key=lambda x: x["F"])
    focus_best_d = max(focus_rows, key=lambda x: x["D"])
    high_f_high_r = [r for r in rows if r["F"] > 3.5 and r["R"] > 0.5]

    # --- external real-data connector
    external_result = {"status": "NOT_PROVIDED"}
    if args.external_shots:
        try:
            shots = load_any(args.external_shots)
            metrics = compute_fr_from_shots(shots)
            external_result = {"status": "OK", "path": args.external_shots, **metrics}
        except Exception as e:
            external_result = {"status": "ERROR", "path": args.external_shots, "error": str(e)}

    # --- plots
    arr_r = np.array([x["R"] for x in rows], dtype=np.float64)
    arr_f = np.array([x["F"] for x in rows], dtype=np.float64)
    arr_d = np.array([x["D"] for x in rows], dtype=np.float64)
    fig1, ax1 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    sc = ax1.scatter(arr_r, arr_f, c=arr_d, s=18, cmap="viridis", alpha=0.72)
    fig1.colorbar(sc, ax=ax1, label="D = F*R")
    ax1.axhline(2.0, color="gray", ls="--", lw=1.0)
    ax1.axhline(4.0, color="green", ls="--", lw=1.0)
    ax1.set_xlabel("R")
    ax1.set_ylabel("F")
    ax1.set_title("V5 Coarse 24x24: F-R with density D")
    ax1.grid(alpha=0.25)
    fig1.tight_layout()
    fig1.savefig(out / "V5_FR_DENSITY_COARSE_24x24.png", dpi=160)
    plt.close(fig1)

    # focused heatmaps
    Fm = np.array([x["F"] for x in focus_rows], dtype=np.float64).reshape((len(fr_vals), len(fw_vals)))
    Rm = np.array([x["R"] for x in focus_rows], dtype=np.float64).reshape((len(fr_vals), len(fw_vals)))
    Dm = np.array([x["D"] for x in focus_rows], dtype=np.float64).reshape((len(fr_vals), len(fw_vals)))
    fig2, (a1, a2, a3) = plt.subplots(1, 3, figsize=(15.0, 4.8), dpi=150)
    i1 = a1.contourf(fw_vals, fr_vals, Fm, levels=22, cmap="coolwarm")
    fig2.colorbar(i1, ax=a1)
    a1.set_title("Focused F")
    a1.set_xlabel("lambda_w")
    a1.set_ylabel("r_src")
    i2 = a2.contourf(fw_vals, fr_vals, Rm, levels=22, cmap="plasma")
    fig2.colorbar(i2, ax=a2)
    a2.set_title("Focused R")
    a2.set_xlabel("lambda_w")
    i3 = a3.contourf(fw_vals, fr_vals, Dm, levels=22, cmap="viridis")
    fig2.colorbar(i3, ax=a3)
    a3.set_title("Focused D=F*R")
    a3.set_xlabel("lambda_w")
    fig2.tight_layout()
    fig2.savefig(out / "V5_FOCUSED_HEATMAPS_F_R_D.png", dpi=160)
    plt.close(fig2)

    result = {
        "seed": int(args.seed),
        "samples": int(args.samples),
        "gate_k": float(args.gate_k),
        "coarse_grid": [int(args.r_src_steps), int(args.lambda_steps)],
        "focus_grid": [int(args.focus_steps), int(args.focus_steps)],
        "best_by_F_coarse": best_f,
        "best_by_D_coarse": best_d,
        "best_by_F_focus": focus_best_f,
        "best_by_D_focus": focus_best_d,
        "n_high_F_gt_3_5_and_R_gt_0_5": int(len(high_f_high_r)),
        "external_audit": external_result,
    }
    (out / "GEOMETRIC_V5_CLOSURE_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    report = [
        "# Geometric V5 External-Closure Audit",
        "",
        "## Goals",
        "- External connector for real GHZ shot-level data",
        "- 24x24 coarse exploration + focused local deep sampling",
        "- New objective: density `D = F * R`",
        "",
        "## Main Results",
        f"- coarse best F: {best_f['F']:.6f} at R={best_f['R']:.6f}, D={best_f['D']:.6f}",
        f"- coarse best D: {best_d['D']:.6f} with F={best_d['F']:.6f}, R={best_d['R']:.6f}",
        f"- focus best F: {focus_best_f['F']:.6f} at R={focus_best_f['R']:.6f}, D={focus_best_f['D']:.6f}",
        f"- focus best D: {focus_best_d['D']:.6f} with F={focus_best_d['F']:.6f}, R={focus_best_d['R']:.6f}",
        f"- count(F>3.5 and R>0.5): {len(high_f_high_r)}",
        "",
        "## External Audit",
        f"- status: {external_result['status']}",
        "- use `--external-shots <path>` with CSV/JSON shot file.",
    ]
    (out / "GEOMETRIC_V5_CLOSURE_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    print("wrote", out / "GEOMETRIC_V5_CLOSURE_RESULTS.json")
    print("wrote", out / "V5_FR_DENSITY_COARSE_24x24.png")
    print("wrote", out / "V5_FOCUSED_HEATMAPS_F_R_D.png")


if __name__ == "__main__":
    main()

