#!/usr/bin/env python3
"""
Joint_pass feasible region for fixed eta: scan rho (optimize bw) and mu×rho grid.

Reuses v6 eval_joint_loss + state_after_de (same gates as v6 main).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

try:
    from scipy.optimize import differential_evolution
except Exception:  # pragma: no cover
    differential_evolution = None

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


def load_v6(repo_root: Path):
    p = repo_root / "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py"
    spec = importlib.util.spec_from_file_location("v6_joint_feas", p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {p}")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def jcfg_for_v6(m) -> dict[str, Any]:
    args = SimpleNamespace(
        wave_speed="constant_c",
        disp_expo_mu=0.25,
        disp_expo_rho=0.25,
        disp_k_eta=0.0,
        c_ref_m_s=m.C_LIGHT_M_S,
    )
    return m.joint_cfg_from_args(args)


def fake_de_result(x4: np.ndarray, fun: float):
    return SimpleNamespace(x=np.array(x4, dtype=float), fun=float(fun), nit=0, success=True)


def contiguous_true_segments(rho: np.ndarray, pass_mask: np.ndarray) -> list[tuple[float, float]]:
    """Return list of (rho_min, rho_max) for each maximal contiguous True run (in index order)."""
    n = len(rho)
    segs: list[tuple[float, float]] = []
    i = 0
    while i < n:
        if not pass_mask[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and pass_mask[j + 1]:
            j += 1
        segs.append((float(rho[i]), float(rho[j])))
        i = j + 1
    return segs


def main() -> int:
    ap = argparse.ArgumentParser(description="rho–mu joint_pass feasibility map (eta fixed, bw optimized)")
    ap.add_argument("--mu-lock", type=float, default=1.5495)
    ap.add_argument("--eta", type=float, default=0.08)
    ap.add_argument("--rho-min", type=float, default=2.10)
    ap.add_argument("--rho-max", type=float, default=2.60)
    ap.add_argument("--rho-points", type=int, default=50)
    ap.add_argument("--mu-min", type=float, default=1.45)
    ap.add_argument("--mu-max", type=float, default=1.65)
    ap.add_argument("--grid-n", type=int, default=20)
    ap.add_argument("--atomic-rho-exponent", type=float, default=0.35)
    ap.add_argument("--shape-threshold-x", type=float, default=0.18)
    ap.add_argument("--shape-threshold-y", type=float, default=0.18)
    ap.add_argument("--r2-min", type=float, default=0.999)
    ap.add_argument("--mri-quad", type=float, default=0.0)
    ap.add_argument("--atomic-mode-n", type=int, default=1)
    ap.add_argument("--w-f0", type=float, default=800.0)
    ap.add_argument("--w-gamma", type=float, default=400.0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=100)
    ap.add_argument(
        "--pass-tries",
        type=int,
        default=5,
        help="DE restarts per (mu,rho); joint_pass True if any try passes (feasibility, not unique bw)",
    )
    ap.add_argument(
        "--bw-scan-points",
        type=int,
        default=64,
        help="if DE finds no passing bw, scan this many bw values in bounds for existential joint_pass",
    )
    ap.add_argument(
        "--no-snap-lock-to-grid",
        action="store_false",
        dest="snap_lock_to_grid",
        help="do not snap nearest grid nodes to exact lock (1.5495, 2.35)",
    )
    ap.set_defaults(snap_lock_to_grid=True)
    ap.add_argument("--out-dir", type=str, default="artifacts/rho_mu_feasibility_map")
    args = ap.parse_args()

    if differential_evolution is None:
        raise RuntimeError("scipy required")
    if plt is None:
        raise RuntimeError("matplotlib required")

    repo = Path(__file__).resolve().parents[3]
    m = load_v6(repo)
    jcfg = jcfg_for_v6(m)
    alpha = float(args.atomic_rho_exponent)
    mode_n = int(args.atomic_mode_n)
    mri_quad = float(args.mri_quad)
    w_f0 = float(args.w_f0)
    w_gamma = float(args.w_gamma)
    th_x = float(args.shape_threshold_x)
    th_y = float(args.shape_threshold_y)
    r2_min: float | None = None if args.r2_min < 0 else float(args.r2_min)
    eta_fixed = float(args.eta)
    mu_lock = float(args.mu_lock)
    rho_lock = 2.35

    bw_bounds = [(1.8e-5, 8.5e-5)]

    def loss_full(vec4: np.ndarray) -> float:
        return float(
            m.eval_joint_loss(
                np.asarray(vec4, dtype=float),
                mode_n,
                alpha,
                mri_quad,
                w_f0,
                w_gamma,
                jcfg,
            )
        )

    def state_from_vec4(vec4: np.ndarray) -> dict[str, Any]:
        fun = loss_full(vec4)
        res = fake_de_result(vec4, fun)
        return m.state_after_de(res, mode_n, alpha, mri_quad, th_x, th_y, r2_min, jcfg)

    def optimize_bw(
        mu: float, rho: float, base_seed: int, n_tries: int | None = None
    ) -> tuple[float, float, bool, float, int]:
        """Return (loss_report, bw_report, joint_pass_any, max_ny, tries_used)."""
        tries = int(args.pass_tries) if n_tries is None else int(n_tries)
        best_loss = float("inf")
        best_bw = float("nan")
        best_pass_loss = float("inf")
        best_pass_bw = float("nan")
        any_pass = False
        best_ny = float("nan")
        for t in range(tries):

            def obj(bw_v: np.ndarray) -> float:
                bw = float(bw_v[0])
                return loss_full(np.array([mu, rho, eta_fixed, bw], dtype=float))

            r = differential_evolution(
                obj, bw_bounds, seed=int(base_seed) + t * 10007, maxiter=int(args.maxiter), polish=True
            )
            bw_opt = float(r.x[0])
            vec = np.array([mu, rho, eta_fixed, bw_opt], dtype=float)
            st = state_from_vec4(vec)
            fun = float(r.fun)
            jp = bool(st["joint_pass"])
            ny = float(st.get("max_nrmse_y", float("nan")))
            if fun < best_loss:
                best_loss, best_bw = fun, bw_opt
                if not any_pass:
                    best_ny = ny
            if jp:
                any_pass = True
                if fun < best_pass_loss:
                    best_pass_loss, best_pass_bw = fun, bw_opt
                    best_ny = ny
        if any_pass:
            return best_pass_loss, best_pass_bw, True, best_ny, tries
        nscan = int(args.bw_scan_points)
        if nscan > 0:
            lo, hi = bw_bounds[0]
            for bw in np.linspace(lo, hi, nscan):
                vec = np.array([mu, rho, eta_fixed, float(bw)], dtype=float)
                st = state_from_vec4(vec)
                if st["joint_pass"]:
                    fun = loss_full(vec)
                    if fun < best_pass_loss:
                        best_pass_loss, best_pass_bw = fun, float(bw)
                        best_ny = float(st.get("max_nrmse_y", float("nan")))
                    any_pass = True
            if any_pass:
                return best_pass_loss, best_pass_bw, True, best_ny, tries
        return best_loss, best_bw, False, best_ny, tries

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- 1D: rho scan at fixed mu_lock ---
    rhos_1d = np.linspace(float(args.rho_min), float(args.rho_max), int(args.rho_points))
    if args.snap_lock_to_grid and float(args.rho_min) <= rho_lock <= float(args.rho_max):
        if np.min(np.abs(rhos_1d - rho_lock)) > 1e-12:
            rhos_1d = np.sort(np.unique(np.concatenate([rhos_1d, np.array([rho_lock])])))
    rows_1d = []
    for k, rho in enumerate(rhos_1d):
        fun, bw, jp, _, _tries = optimize_bw(mu_lock, float(rho), int(args.seed) + k * 17)
        rows_1d.append(
            {
                "rho": float(rho),
                "bw_opt": bw,
                "loss": fun,
                "joint_pass": jp,
                "pass_tries": int(args.pass_tries),
            }
        )

    pass_mask = np.array([r["joint_pass"] for r in rows_1d], dtype=bool)
    segs = contiguous_true_segments(rhos_1d, pass_mask)
    seg_widths = [(b - a, a, b) for a, b in segs]
    seg_widths.sort(reverse=True)
    primary = seg_widths[0] if seg_widths else None
    summary_1d: dict[str, Any] = {
        "mu_fixed": mu_lock,
        "eta_fixed": eta_fixed,
        "n_segments": len(segs),
        "segments_rho": [{"rho_min": a, "rho_max": b, "width": b - a} for a, b in segs],
        "widest_segment": None,
        "lock_rho": rho_lock,
        "needle_note": (
            "At fixed eta=0.08, joint_pass is extremely sensitive to rho (numeric pass band near rho=2.35 "
            "has width << 0.001 in rho-only probes), while along rho=2.35 the mu window in [1.45,1.65] "
            "can remain feasible when bw is optimized."
        ),
    }
    if primary:
        w, a, b = primary
        center = 0.5 * (a + b)
        summary_1d["widest_segment"] = {"rho_min": a, "rho_max": b, "width": w, "center": center}
        summary_1d["lock_in_widest"] = bool(a - 1e-9 <= rho_lock <= b + 1e-9)
        summary_1d["lock_offset_from_center"] = float(rho_lock - center)
        summary_1d["lock_position_fraction_along_width"] = (
            float((rho_lock - a) / w) if w > 1e-12 else 0.5
        )

    # Plots 1D
    fig1, ax1 = plt.subplots(figsize=(9, 4.5), dpi=120)
    ax1.plot([r["rho"] for r in rows_1d], [r["loss"] for r in rows_1d], "b.-", lw=1.2, ms=4)
    if segs:
        for a, b in segs:
            ax1.axvspan(a, b, color="green", alpha=0.12)
    ax1.axvline(rho_lock, color="k", ls="--", lw=1, label=f"lock rho={rho_lock}")
    ax1.axvline(mu_lock**2, color="purple", ls=":", lw=1.2, label=f"rho=mu^2={mu_lock**2:.4f}")
    ax1.set_xlabel("rho")
    ax1.set_ylabel("loss (bw optimized)")
    ax1.set_title(f"1D feasibility slice: mu={mu_lock}, eta={eta_fixed}, optimize bw")
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(alpha=0.3)
    fig1.tight_layout()
    p_loss = out_dir / "feas_rho_vs_loss.png"
    fig1.savefig(p_loss, dpi=160)
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(9, 2.8), dpi=120)
    y_pass = np.where(pass_mask, 1.0, 0.0)
    ax2.fill_between(rhos_1d, 0, y_pass, step="mid", color="green", alpha=0.45, label="joint_pass True")
    ax2.fill_between(rhos_1d, 0, 1 - y_pass, step="mid", color="red", alpha=0.35, label="joint_pass False")
    ax2.plot(rhos_1d, y_pass, "k-", lw=0.8, drawstyle="steps-mid")
    ax2.axvline(rho_lock, color="k", ls="--", lw=1)
    ax2.axvline(mu_lock**2, color="purple", ls=":", lw=1.2)
    ax2.set_xlabel("rho")
    ax2.set_ylabel("joint_pass (1/0)")
    ax2.set_yticks([0, 1])
    ax2.set_ylim(-0.1, 1.15)
    ax2.set_title("Feasible band (green) vs rho")
    ax2.legend(loc="upper right", fontsize=8)
    fig2.tight_layout()
    p_band = out_dir / "feas_rho_vs_joint_pass.png"
    fig2.savefig(p_band, dpi=160)
    plt.close(fig2)

    # --- 2D grid ---
    mus = np.linspace(float(args.mu_min), float(args.mu_max), int(args.grid_n))
    rhos_2d = np.linspace(float(args.rho_min), float(args.rho_max), int(args.grid_n))
    if args.snap_lock_to_grid:
        if float(args.mu_min) <= mu_lock <= float(args.mu_max):
            mus[int(np.argmin(np.abs(mus - mu_lock)))] = mu_lock
        if float(args.rho_min) <= rho_lock <= float(args.rho_max):
            rhos_2d[int(np.argmin(np.abs(rhos_2d - rho_lock)))] = rho_lock
    Z = np.zeros((len(rhos_2d), len(mus)), dtype=np.float32)  # 1 pass, 0 fail
    grid_rows = []
    t = 0
    for iy, rho in enumerate(rhos_2d):
        for ix, mu in enumerate(mus):
            fun, bw, jp, _, _tr = optimize_bw(float(mu), float(rho), int(args.seed) + t * 19 + iy * 997 + ix)
            Z[iy, ix] = 1.0 if jp else 0.0
            grid_rows.append(
                {
                    "mu": float(mu),
                    "rho": float(rho),
                    "bw_opt": bw,
                    "loss": fun,
                    "joint_pass": jp,
                }
            )
            t += 1

    pass_mu = [r["mu"] for r in grid_rows if r["joint_pass"]]
    pass_rho = [r["rho"] for r in grid_rows if r["joint_pass"]]
    summary_2d: dict[str, Any] = {
        "n_pass": len(pass_mu),
        "pass_fraction": float(len(pass_mu) / max(len(grid_rows), 1)),
    }
    if pass_mu:
        summary_2d["pass_centroid_mu"] = float(np.mean(pass_mu))
        summary_2d["pass_centroid_rho"] = float(np.mean(pass_rho))
        summary_2d["mu_pass_spread"] = float(np.max(pass_mu) - np.min(pass_mu))
        summary_2d["rho_pass_spread"] = float(np.max(pass_rho) - np.min(pass_rho))
    else:
        summary_2d["pass_centroid_mu"] = None
        summary_2d["pass_centroid_rho"] = None
        summary_2d["mu_pass_spread"] = None
        summary_2d["rho_pass_spread"] = None

    lfun, lbw, ljp, _, _ = optimize_bw(mu_lock, rho_lock, int(args.seed) + 999001)
    summary_2d["lock_point"] = {
        "mu": mu_lock,
        "rho": rho_lock,
        "bw_opt": lbw,
        "loss": lfun,
        "joint_pass": ljp,
    }
    if pass_mu and summary_2d["pass_centroid_mu"] is not None:
        summary_2d["lock_distance_to_pass_centroid"] = float(
            np.hypot(mu_lock - summary_2d["pass_centroid_mu"], rho_lock - summary_2d["pass_centroid_rho"])
        )

    # rho = mu^2 curve in box
    mu_curve = np.linspace(float(args.mu_min), float(args.mu_max), 400)
    rho_curve = mu_curve**2
    mask_curve = (rho_curve >= float(args.rho_min)) & (rho_curve <= float(args.rho_max))

    fig3, ax3 = plt.subplots(figsize=(8.2, 7.0), dpi=120)
    # Green = pass: use masked red/green
    cmap = plt.matplotlib.colors.ListedColormap(["#c44e52", "#55a868"])  # red, green
    im = ax3.imshow(
        Z,
        origin="lower",
        aspect="auto",
        extent=[mus[0], mus[-1], rhos_2d[0], rhos_2d[-1]],
        cmap=cmap,
        vmin=0,
        vmax=1,
        interpolation="nearest",
    )
    ax3.plot(mu_curve[mask_curve], rho_curve[mask_curve], color="white", lw=2.2, label=r"$\rho=\mu^2$")
    ax3.plot(mu_curve[mask_curve], rho_curve[mask_curve], color="black", lw=1.0, ls="--")
    ax3.scatter([mu_lock], [rho_lock], s=120, c="yellow", edgecolors="black", linewidths=1.2, zorder=5, label="lock (1.5495, 2.35)")
    ax3.set_xlabel(r"$\mu$")
    ax3.set_ylabel(r"$\rho$")
    ax3.set_title(f"joint_pass (green=True, red=False), eta={eta_fixed}, bw optimized\nmaxiter={args.maxiter}")
    ax3.legend(loc="upper left", fontsize=9)
    cbar = plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
    cbar.set_ticks([0.25, 0.75])
    cbar.set_ticklabels(["False", "True"])
    fig3.tight_layout()
    p_heat = out_dir / "feas_mu_rho_heatmap.png"
    fig3.savefig(p_heat, dpi=170)
    plt.close(fig3)

    # 2D: does rho=mu^2 pass anywhere?
    curve_pass_count = 0
    curve_samples = []
    for mu_s in np.linspace(float(args.mu_min), float(args.mu_max), 80):
        rho_s = float(mu_s**2)
        if not (float(args.rho_min) <= rho_s <= float(args.rho_max)):
            continue
        fun, bw, jp, _, _ = optimize_bw(float(mu_s), rho_s, int(args.seed) + 50000 + curve_pass_count)
        curve_samples.append({"mu": float(mu_s), "rho": rho_s, "joint_pass": jp, "loss": fun})
        if jp:
            curve_pass_count += 1

    payload = {
        "meta": {
            "script": "rho_mu_feasibility_map.py",
            "eta_fixed": eta_fixed,
            "bw_bounds": list(bw_bounds[0]),
            "maxiter": int(args.maxiter),
            "pass_tries": int(args.pass_tries),
            "bw_scan_points": int(args.bw_scan_points),
            "snap_lock_to_grid": bool(args.snap_lock_to_grid),
            "note": "joint_pass if any DE try passes, else optional dense bw scan in bounds",
        },
        "summary_1d": summary_1d,
        "series_1d": rows_1d,
        "grid_2d": {
            "mu_range": [float(mus[0]), float(mus[-1])],
            "rho_range": [float(rhos_2d[0]), float(rhos_2d[-1])],
            "grid_n": int(args.grid_n),
            "joint_pass_fraction": float(np.mean(Z)),
            "summary": summary_2d,
        },
        "rho_mu_squared_curve_in_box": {
            "samples_optimized_bw": curve_samples,
            "joint_pass_count": curve_pass_count,
            "joint_pass_fraction_on_curve": float(curve_pass_count / max(len(curve_samples), 1)),
        },
        "plots": {
            "rho_vs_loss": str(p_loss.as_posix()),
            "rho_vs_joint_pass": str(p_band.as_posix()),
            "mu_rho_heatmap": str(p_heat.as_posix()),
        },
    }

    json_path = out_dir / "RHO_MU_FEASIBILITY.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # CSVs
    csv1 = out_dir / "feas_1d_rho_scan.csv"
    with csv1.open("w", encoding="utf-8") as f:
        f.write("rho,bw_opt,loss,joint_pass\n")
        for r in rows_1d:
            f.write(f"{r['rho']},{r['bw_opt']},{r['loss']},{int(r['joint_pass'])}\n")

    csv2 = out_dir / "feas_2d_grid.csv"
    with csv2.open("w", encoding="utf-8") as f:
        f.write("mu,rho,bw_opt,loss,joint_pass\n")
        for r in grid_rows:
            f.write(f"{r['mu']},{r['rho']},{r['bw_opt']},{r['loss']},{int(r['joint_pass'])}\n")

    # Short markdown for user
    md_lines = [
        "# Rho–mu joint_pass feasibility",
        "",
        f"- Fixed eta={eta_fixed}, optimize bw per point.",
        f"- 1D: mu={mu_lock}, rho in [{args.rho_min}, {args.rho_max}], n={args.rho_points}.",
        "",
        "## 1D widest feasible segment (rho)",
    ]
    if summary_1d.get("widest_segment"):
        ws = summary_1d["widest_segment"]
        md_lines.append(f"- width: **{ws['width']:.6f}**")
        md_lines.append(f"- center: **{ws['center']:.6f}** (lock rho={rho_lock})")
        md_lines.append(f"- lock inside segment: {summary_1d.get('lock_in_widest')}")
        md_lines.append(f"- lock offset from center: {summary_1d.get('lock_offset_from_center')}")
    else:
        md_lines.append("- **no joint_pass True in 1D scan**")
    md_lines.extend(
        [
            "",
            f"- rho=mu^2 at lock: {mu_lock**2:.6f}",
            "",
            "## rho=mu^2 curve (in box, 80 samples, bw optimized)",
            f"- joint_pass count: {curve_pass_count} / {len(curve_samples)}",
            "",
            "## 2D grid",
            f"- joint_pass fraction: {payload['grid_2d']['joint_pass_fraction']:.4f}",
        ]
    )
    s2 = summary_2d
    md_lines.extend(
        [
            f"- lock point joint_pass: **{s2.get('lock_point', {}).get('joint_pass')}**",
            f"- pass centroid (mu,rho): ({s2.get('pass_centroid_mu')}, {s2.get('pass_centroid_rho')})",
            f"- lock distance to centroid: {s2.get('lock_distance_to_pass_centroid')}",
            f"- mu spread of passing cells: {s2.get('mu_pass_spread')}",
            f"- rho spread of passing cells: {s2.get('rho_pass_spread')}",
            "",
            "## Files",
            f"- {json_path}",
            f"- {p_loss}, {p_band}, {p_heat}",
        ]
    )
    (out_dir / "RHO_MU_FEASIBILITY.md").write_text("\n".join(md_lines), encoding="utf-8")

    print("wrote", json_path)
    print("wrote", p_loss, p_band, p_heat)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
