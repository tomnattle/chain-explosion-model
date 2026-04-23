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
    return {"F": float(f), "R": r, "D": float(f * r)}


def bootstrap_ci(rng: np.random.Generator, lams: np.ndarray, params: dict, draws: int, subsample: int) -> tuple[float, float]:
    n = lams.shape[1]
    m = min(n, subsample)
    vals = []
    for _ in range(draws):
        idx = rng.integers(0, n, size=m)
        ev = ghz_eval(lams[:, idx], params["r_src"], params["lambda_w"], params["gate_k"], params["offset_deg"])
        vals.append(ev["D"])
    q = np.quantile(np.array(vals), [0.025, 0.975])
    return float(q[0]), float(q[1])


def generate_lams(seed: int, n: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    return np.stack([l1, l2, l3], axis=0)


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="V9 red-team self-audit")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=80000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    args = ap.parse_args()

    out = Path("artifacts/ghz_geometric_v9")
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    lams = generate_lams(args.seed, int(args.samples))

    # Base band from prior v7.1b
    r_vals = np.linspace(0.45, 0.70, 18)
    w_vals = np.linspace(1.20, 1.90, 18)
    off_vals = np.linspace(18.0, 28.0, 9)

    # 1) baseline best-D search in magic band
    rows = []
    for r_src in r_vals:
        for lw in w_vals:
            best = None
            for off in off_vals:
                ev = ghz_eval(lams, float(r_src), float(lw), float(args.gate_k), float(off))
                row = {"r_src": float(r_src), "lambda_w": float(lw), "offset_deg": float(off), "gate_k": float(args.gate_k), **ev}
                if best is None or row["D"] > best["D"]:
                    best = row
            rows.append(best)
    best_d = max(rows, key=lambda x: x["D"])

    # 2) boundary-adhesion check: widen offset to [12, 30]
    off_wide = np.linspace(12.0, 30.0, 19)
    wide_best = None
    for off in off_wide:
        ev = ghz_eval(lams, best_d["r_src"], best_d["lambda_w"], best_d["gate_k"], float(off))
        row = {"offset_deg": float(off), **ev}
        if wide_best is None or row["D"] > wide_best["D"]:
            wide_best = row

    # 3) gate-k sensitivity around best point
    gate_list = [0.45, 0.55, 0.65, 0.75, 0.85]
    gate_rows = []
    for gk in gate_list:
        ev = ghz_eval(lams, best_d["r_src"], best_d["lambda_w"], float(gk), best_d["offset_deg"])
        gate_rows.append({"gate_k": gk, **ev})

    # 4) seed-sweep stability at best point
    seed_rows = []
    for s in [20260411, 20260417, 20260423, 20260429, 20260501]:
        ls = generate_lams(s, int(args.samples))
        ev = ghz_eval(ls, best_d["r_src"], best_d["lambda_w"], best_d["gate_k"], best_d["offset_deg"])
        seed_rows.append({"seed": s, **ev})

    # 5) bootstrap CI on D for best point
    lo, hi = bootstrap_ci(rng, lams, best_d, draws=40, subsample=min(30000, int(args.samples)))

    # 6) simple train/valid split anti-overfit check
    n = lams.shape[1]
    idx = np.arange(n)
    rng.shuffle(idx)
    cut = int(0.7 * n)
    tr, va = idx[:cut], idx[cut:]
    ltr, lva = lams[:, tr], lams[:, va]
    # train select
    train_best = None
    for r_src in np.linspace(0.45, 0.70, 12):
        for lw in np.linspace(1.20, 1.90, 12):
            for off in np.linspace(18.0, 28.0, 7):
                ev = ghz_eval(ltr, float(r_src), float(lw), float(args.gate_k), float(off))
                row = {"r_src": float(r_src), "lambda_w": float(lw), "offset_deg": float(off), **ev}
                if train_best is None or row["D"] > train_best["D"]:
                    train_best = row
    valid_eval = ghz_eval(lva, train_best["r_src"], train_best["lambda_w"], float(args.gate_k), train_best["offset_deg"])

    # plots
    fig1, ax1 = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    ax1.plot([x["gate_k"] for x in gate_rows], [x["D"] for x in gate_rows], "-o")
    ax1.set_xlabel("gate_k")
    ax1.set_ylabel("D")
    ax1.set_title("Gate sensitivity at best-D point")
    ax1.grid(alpha=0.25)
    fig1.tight_layout()
    fig1.savefig(out / "V9_GATE_SENSITIVITY.png", dpi=160)
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    ax2.plot([x["seed"] for x in seed_rows], [x["D"] for x in seed_rows], "-o")
    ax2.set_xlabel("seed")
    ax2.set_ylabel("D")
    ax2.set_title("Seed stability at best-D point")
    ax2.grid(alpha=0.25)
    fig2.tight_layout()
    fig2.savefig(out / "V9_SEED_STABILITY.png", dpi=160)
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    ax3.plot([x["offset_deg"] for x in sorted([{"offset_deg":x["offset_deg"],"D":x["D"]} for x in rows], key=lambda z: z["offset_deg"])], [x["D"] for x in sorted([{"offset_deg":x["offset_deg"],"D":x["D"]} for x in rows], key=lambda z: z["offset_deg"])], ".", alpha=0.2)
    ax3.axvline(best_d["offset_deg"], color="red", ls="--", lw=1.0)
    ax3.axvline(wide_best["offset_deg"], color="green", ls="--", lw=1.0)
    ax3.set_xlabel("offset_deg")
    ax3.set_ylabel("D (scatter from band best-per-cell)")
    ax3.set_title("Boundary-adhesion check")
    ax3.grid(alpha=0.25)
    fig3.tight_layout()
    fig3.savefig(out / "V9_BOUNDARY_ADHESION.png", dpi=160)
    plt.close(fig3)

    result = {
        "best_band_by_D": best_d,
        "wide_offset_best_at_same_params": wide_best,
        "bootstrap_D_ci95": [lo, hi],
        "seed_sweep": seed_rows,
        "gate_sensitivity": gate_rows,
        "train_best": train_best,
        "valid_eval_at_train_best": valid_eval,
        "risk_flags": {
            "boundary_adhesion": abs(best_d["offset_deg"] - 18.0) < 1e-9 or abs(best_d["offset_deg"] - 28.0) < 1e-9,
            "low_R_at_best_D": best_d["R"] < 0.4,
            "valid_drop_D": float(train_best["D"] - valid_eval["D"]),
        },
    }
    (out / "V9_REDTEAM_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    report = [
        "# V9 红队自审",
        "",
        "## 结论先行",
        f"- best D: {best_d['D']:.6f} (F={best_d['F']:.6f}, R={best_d['R']:.6f}, off={best_d['offset_deg']:.3f})",
        f"- bootstrap D CI95: [{lo:.6f}, {hi:.6f}]",
        f"- train D: {train_best['D']:.6f}, valid D: {valid_eval['D']:.6f}",
        "",
        "## 重点风险",
        f"- boundary adhesion: {result['risk_flags']['boundary_adhesion']}",
        f"- low R at best D: {result['risk_flags']['low_R_at_best_D']}",
        f"- D drop(train->valid): {result['risk_flags']['valid_drop_D']:.6f}",
        "",
        "## 图",
        "- `V9_GATE_SENSITIVITY.png`",
        "- `V9_SEED_STABILITY.png`",
        "- `V9_BOUNDARY_ADHESION.png`",
    ]
    (out / "V9_REDTEAM_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    print("wrote", out / "V9_REDTEAM_RESULTS.json")
    print("wrote", out / "V9_REDTEAM_REPORT.md")


if __name__ == "__main__":
    main()

