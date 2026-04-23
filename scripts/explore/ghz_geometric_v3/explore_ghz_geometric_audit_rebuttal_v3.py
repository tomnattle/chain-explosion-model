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
    return float(f), float(np.mean([r1, r2, r3, r4]))


def bootstrap_f_ci(
    rng: np.random.Generator,
    lams: np.ndarray,
    d: np.ndarray,
    lambda_w: float,
    gate_k: float,
    draws: int,
    subsample: int,
) -> tuple[float, float]:
    n = lams.shape[1]
    m = min(n, subsample)
    fs = []
    for _ in range(draws):
        idx = rng.integers(0, n, size=m)
        f, _ = ghz_f_r(lams[:, idx], d, lambda_w, gate_k)
        fs.append(f)
    q = np.quantile(np.array(fs), [0.025, 0.975])
    return float(q[0]), float(q[1])


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


def analyze_real_experiment_stub(path: str | None) -> dict:
    """
    Optional experiment alignment hook.
    Expected JSON format:
      {"rows":[{"F":..., "R":...}, ...]}
    """
    if not path:
        return {
            "status": "NO_EXTERNAL_DATA_PROVIDED",
            "note": "Provide --external-f-r-json to compare model R/F with external experiment pipeline.",
        }
    p = Path(path)
    if not p.exists():
        return {"status": "EXTERNAL_FILE_NOT_FOUND", "path": str(p)}
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        rows = obj.get("rows", [])
        if not rows:
            return {"status": "EXTERNAL_FILE_INVALID", "path": str(p)}
        f_vals = np.array([float(r["F"]) for r in rows], dtype=np.float64)
        r_vals = np.array([float(r["R"]) for r in rows], dtype=np.float64)
        return {
            "status": "OK",
            "path": str(p),
            "n_rows": int(len(rows)),
            "F_mean": float(np.mean(f_vals)),
            "R_mean": float(np.mean(r_vals)),
            "F_max": float(np.max(f_vals)),
            "R_max": float(np.max(r_vals)),
        }
    except Exception as e:
        return {"status": "EXTERNAL_FILE_PARSE_ERROR", "path": str(p), "error": str(e)}


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="GHZ geometric rebuttal audit v3")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--samples", type=int, default=500_000)
    ap.add_argument("--gate-k", type=float, default=0.65)
    ap.add_argument("--r-src-steps", type=int, default=16)
    ap.add_argument("--lambda-steps", type=int, default=16)
    ap.add_argument("--r-min-focus", type=float, default=0.35)
    ap.add_argument("--bootstrap-draws", type=int, default=40)
    ap.add_argument("--bootstrap-subsample", type=int, default=80_000)
    ap.add_argument("--external-f-r-json", type=str, default="")
    args = ap.parse_args()

    out_dir = Path("artifacts/ghz_geometric_v3")
    out_dir.mkdir(parents=True, exist_ok=True)

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
            f, r = ghz_f_r(lams, d, float(lw), float(args.gate_k))
            rows.append({"r_src": float(r_src), "lambda_w": float(lw), "F": f, "R": r})

    # --- Q1: low-R stability -> bootstrap CIs for high-F region and Pareto points
    frontier = pareto_front(rows)
    high_f = sorted(rows, key=lambda x: x["F"], reverse=True)[:12]
    ci_targets = {(p["r_src"], p["lambda_w"]) for p in high_f + frontier[-12:]}
    ci_map = {}
    f_boot_by_rbin = {}
    r_bins = [(0.0, 0.2), (0.2, 0.35), (0.35, 0.5), (0.5, 1.0)]
    # pointwise CI (selected points)
    for (r_src, lw) in ci_targets:
        d = compute_distances(float(r_src))
        lo, hi = bootstrap_f_ci(
            rng, lams, d, float(lw), float(args.gate_k), int(args.bootstrap_draws), int(args.bootstrap_subsample)
        )
        ci_map[f"{r_src:.6f}|{lw:.6f}"] = {"F_ci95": [lo, hi]}
    # distribution per R-bin using top points in each bin
    for lo_r, hi_r in r_bins:
        pts = [p for p in rows if lo_r <= p["R"] < hi_r]
        pts = sorted(pts, key=lambda x: x["F"], reverse=True)[:8]
        vals = []
        for p in pts:
            d = compute_distances(p["r_src"])
            fs = []
            for _ in range(max(8, int(args.bootstrap_draws // 2))):
                idx = rng.integers(0, n, size=min(n, int(args.bootstrap_subsample)))
                f, _ = ghz_f_r(lams[:, idx], d, p["lambda_w"], float(args.gate_k))
                fs.append(f)
            vals.extend(fs)
        if vals:
            q = np.quantile(np.array(vals), [0.025, 0.5, 0.975])
            f_boot_by_rbin[f"{lo_r:.2f}-{hi_r:.2f}"] = [float(q[0]), float(q[1]), float(q[2])]

    # --- Q2: cliff near R_min maybe coarse-grid artifact -> local dense refinement
    r_target = float(args.r_min_focus)
    coarse_best = max([p for p in rows if p["R"] >= r_target], key=lambda x: x["F"], default=None)
    fine_rows = []
    if coarse_best is not None:
        r0, w0 = coarse_best["r_src"], coarse_best["lambda_w"]
        r_fine = np.linspace(max(0.05, r0 - 0.06), min(0.8, r0 + 0.06), 41)
        w_fine = np.linspace(max(0.1, w0 - 0.18), min(2.0, w0 + 0.18), 41)
        for rr in r_fine:
            d = compute_distances(float(rr))
            for ww in w_fine:
                f, r = ghz_f_r(lams, d, float(ww), float(args.gate_k))
                fine_rows.append({"r_src": float(rr), "lambda_w": float(ww), "F": f, "R": r})
    fine_best = max([p for p in fine_rows if p["R"] >= r_target], key=lambda x: x["F"], default=None)

    # --- Q3: third-variable check -> R vs params colored by F
    # direct from rows; saved as plots and simple correlations
    r_arr = np.array([p["R"] for p in rows], dtype=np.float64)
    f_arr = np.array([p["F"] for p in rows], dtype=np.float64)
    rs_arr = np.array([p["r_src"] for p in rows], dtype=np.float64)
    lw_arr = np.array([p["lambda_w"] for p in rows], dtype=np.float64)
    corr_r_lw = float(np.corrcoef(r_arr, lw_arr)[0, 1])
    corr_r_rs = float(np.corrcoef(r_arr, rs_arr)[0, 1])
    corr_f_lw = float(np.corrcoef(f_arr, lw_arr)[0, 1])
    corr_f_rs = float(np.corrcoef(f_arr, rs_arr)[0, 1])

    # --- Q4: external experiment condition alignment hook
    external = analyze_real_experiment_stub(args.external_f_r_json or None)

    # Pareto + CI bars for selected frontier points
    fig1, ax1 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax1.scatter(r_arr, f_arr, s=16, alpha=0.28, label="grid points")
    front = pareto_front(rows)
    ax1.plot([p["R"] for p in front], [p["F"] for p in front], "-o", lw=2.0, ms=3.5, label="Pareto frontier")
    # CI bars on top-F points
    for p in high_f[:8]:
        key = f"{p['r_src']:.6f}|{p['lambda_w']:.6f}"
        if key in ci_map:
            lo, hi = ci_map[key]["F_ci95"]
            ax1.vlines(p["R"], lo, hi, color="#d62728", lw=1.1, alpha=0.85)
    ax1.axhline(2.0, color="gray", ls="--", lw=1.0, label="F=2")
    ax1.axhline(4.0, color="green", ls="--", lw=1.0, label="F=4")
    ax1.set_xlabel("R (sample retention)")
    ax1.set_ylabel("F (gated)")
    ax1.set_title("Q1 Pareto with selected bootstrap CI bars")
    ax1.grid(alpha=0.25)
    ax1.legend(fontsize=8)
    fig1.tight_layout()
    fig1.savefig(out_dir / "Q1_PARETO_WITH_CI.png", dpi=160)
    plt.close(fig1)

    # R_min cost curve coarse vs fine
    rmins = np.linspace(0.05, 0.85, 33)
    coarse_curve = []
    fine_curve = []
    for rm in rmins:
        fs = [p["F"] for p in rows if p["R"] >= float(rm)]
        coarse_curve.append(float(max(fs)) if fs else np.nan)
        if fine_rows:
            fs2 = [p["F"] for p in fine_rows if p["R"] >= float(rm)]
            fine_curve.append(float(max(fs2)) if fs2 else np.nan)
        else:
            fine_curve.append(np.nan)

    fig2, ax2 = plt.subplots(figsize=(7.2, 5.2), dpi=150)
    ax2.plot(rmins, coarse_curve, "-o", ms=3.2, lw=1.5, label="coarse grid")
    ax2.plot(rmins, fine_curve, "-o", ms=2.8, lw=1.4, label="local fine grid")
    ax2.axvline(r_target, color="#444", ls=":", lw=1.0, label=f"R_min focus={r_target:.2f}")
    ax2.axhline(2.0, color="gray", ls="--", lw=1.0, label="F=2")
    ax2.axhline(4.0, color="green", ls="--", lw=1.0, label="F=4")
    ax2.set_xlabel("R_min constraint")
    ax2.set_ylabel("best feasible F")
    ax2.set_title("Q2 Coarse vs Fine around cliff")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out_dir / "Q2_RMIN_CLIFF_COARSE_VS_FINE.png", dpi=160)
    plt.close(fig2)

    # Third-variable scatter maps
    fig3, (a31, a32) = plt.subplots(1, 2, figsize=(11.8, 4.8), dpi=150)
    sc1 = a31.scatter(lw_arr, r_arr, c=f_arr, s=18, cmap="coolwarm", alpha=0.7)
    fig3.colorbar(sc1, ax=a31, label="F")
    a31.set_xlabel("lambda_w")
    a31.set_ylabel("R")
    a31.set_title("Q3 R vs lambda_w (colored by F)")
    a31.grid(alpha=0.2)
    sc2 = a32.scatter(rs_arr, r_arr, c=f_arr, s=18, cmap="coolwarm", alpha=0.7)
    fig3.colorbar(sc2, ax=a32, label="F")
    a32.set_xlabel("r_src")
    a32.set_ylabel("R")
    a32.set_title("Q3 R vs r_src (colored by F)")
    a32.grid(alpha=0.2)
    fig3.tight_layout()
    fig3.savefig(out_dir / "Q3_THIRD_VARIABLE_SCATTERS.png", dpi=160)
    plt.close(fig3)

    result = {
        "seed": int(args.seed),
        "samples": int(args.samples),
        "gate_k": float(args.gate_k),
        "coarse_grid_shape": [len(r_vals), len(w_vals)],
        "q1_bootstrap": {"ci_map": ci_map, "f_boot_by_rbin": f_boot_by_rbin},
        "q2_cliff_check": {
            "r_min_focus": r_target,
            "coarse_best_at_focus": coarse_best,
            "fine_best_at_focus": fine_best,
            "fine_grid_size": [41, 41] if fine_rows else [0, 0],
        },
        "q3_third_variable": {
            "corr_R_lambda_w": corr_r_lw,
            "corr_R_r_src": corr_r_rs,
            "corr_F_lambda_w": corr_f_lw,
            "corr_F_r_src": corr_f_rs,
        },
        "q4_external_alignment": external,
    }
    (out_dir / "GEOMETRIC_REBUTTAL_V3_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    report = [
        "# Geometric Rebuttal V3",
        "",
        "This package addresses 4 audit questions from cross-examination.",
        "",
        "## Q1 Low-R statistical stability",
        "- Added bootstrap CI bars for selected high-F points on Pareto scatter.",
        "- Added F bootstrap summaries by R bins.",
        "",
        "## Q2 Cliff realism vs coarse grid artifact",
        "- Added local dense refinement around R_min focus and compared coarse vs fine curves.",
        "",
        "## Q3 Third-variable confounding check",
        "- Added R-vs-parameter scatter maps colored by F.",
        "- Added simple correlation diagnostics in JSON.",
        "",
        "## Q4 External experiment condition alignment",
        "- Added optional external F/R JSON hook (`--external-f-r-json`).",
        "- Current run status: see JSON field `q4_external_alignment.status`.",
        "",
        "## Files",
        "- `Q1_PARETO_WITH_CI.png`",
        "- `Q2_RMIN_CLIFF_COARSE_VS_FINE.png`",
        "- `Q3_THIRD_VARIABLE_SCATTERS.png`",
        "- `GEOMETRIC_REBUTTAL_V3_RESULTS.json`",
    ]
    (out_dir / "GEOMETRIC_REBUTTAL_V3_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    print("wrote", out_dir / "GEOMETRIC_REBUTTAL_V3_RESULTS.json")
    print("wrote", out_dir / "Q1_PARETO_WITH_CI.png")
    print("wrote", out_dir / "Q2_RMIN_CLIFF_COARSE_VS_FINE.png")
    print("wrote", out_dir / "Q3_THIRD_VARIABLE_SCATTERS.png")


if __name__ == "__main__":
    main()

