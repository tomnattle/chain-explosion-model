#!/usr/bin/env python3
"""
V10.4 — Computed GHZ cost curve (medium wave model), not illustrative.

Sweeps soft-detector gate strength gate_k; at each setting evaluates F_gated and
the measured simultaneous-hit retention R_gated (same definitions as v10.3).
Every (R_gated, F_gated) pair comes from the fixed phase sample — no parametric
anchor between F and retention.
"""
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


def distance_matrix(r_inner: float, r_outer: float = 1.0, inner_offset: float = 0.0) -> np.ndarray:
    inner = ring_positions(r_inner, inner_offset)
    outer = ring_positions(r_outer, 0.0)
    d = np.zeros((3, 3), dtype=np.float64)
    for i in range(3):
        for j in range(3):
            u = inner[i] - outer[j]
            d[i, j] = np.sqrt(np.sum(u * u))
    return d


def medium_phase_states(seed: int, n_states: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    p1 = rng.uniform(0.0, TWO_PI, size=n_states)
    p2 = rng.uniform(0.0, TWO_PI, size=n_states)
    p3 = (-p1 - p2) % TWO_PI
    return np.stack([p1, p2, p3], axis=0)


def field_at_observer(
    phases: np.ndarray,
    observer_idx: int,
    probe_angle: float,
    d: np.ndarray,
    wavelength: float,
    attenuation_power: float,
) -> np.ndarray:
    out = np.zeros(phases.shape[1], dtype=np.float64)
    for i in range(3):
        dij = float(d[i, observer_idx])
        amp = 1.0 / (dij**attenuation_power)
        delay = TWO_PI * dij / wavelength
        out += amp * np.cos(phases[i] - probe_angle - delay)
    return out


def e3_cont(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray) -> float:
    num = float(np.mean(sa * sb * sc))
    den = float((np.mean(sa * sa) * np.mean(sb * sb) * np.mean(sc * sc)) ** (1.0 / 3.0))
    return num / den if den > 1e-12 else 0.0


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


def e3_gated_details(
    sa: np.ndarray, sb: np.ndarray, sc: np.ndarray, gate_k: float
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray]:
    ta = gate_k * float(np.sqrt(np.mean(sa * sa)))
    tb = gate_k * float(np.sqrt(np.mean(sb * sb)))
    tc = gate_k * float(np.sqrt(np.mean(sc * sc)))
    a = soft_detector(sa, ta)
    b = soft_detector(sb, tb)
    c = soft_detector(sc, tc)
    m = (np.abs(a) > 0.0) & (np.abs(b) > 0.0) & (np.abs(c) > 0.0)
    if not np.any(m):
        return 0.0, 0.0, a, b, c
    return float(np.mean(a[m] * b[m] * c[m])), float(np.mean(m)), a, b, c


def random_control_f(
    a_xxx: np.ndarray,
    b_xxx: np.ndarray,
    c_xxx: np.ndarray,
    a_xyy: np.ndarray,
    b_xyy: np.ndarray,
    c_xyy: np.ndarray,
    a_yxy: np.ndarray,
    b_yxy: np.ndarray,
    c_yxy: np.ndarray,
    a_yyx: np.ndarray,
    b_yyx: np.ndarray,
    c_yyx: np.ndarray,
    r_xxx: float,
    r_xyy: float,
    r_yxy: float,
    r_yyx: float,
    rng: np.random.Generator,
    n_trials: int,
) -> tuple[float, float]:
    n = len(a_xxx)
    vals = np.zeros(n_trials, dtype=np.float64)
    for i in range(n_trials):
        k1 = max(1, int(round(r_xxx * n)))
        k2 = max(1, int(round(r_xyy * n)))
        k3 = max(1, int(round(r_yxy * n)))
        k4 = max(1, int(round(r_yyx * n)))
        idx1 = rng.choice(n, size=k1, replace=False)
        idx2 = rng.choice(n, size=k2, replace=False)
        idx3 = rng.choice(n, size=k3, replace=False)
        idx4 = rng.choice(n, size=k4, replace=False)
        exxx = float(np.mean(a_xxx[idx1] * b_xxx[idx1] * c_xxx[idx1]))
        exyy = float(np.mean(a_xyy[idx2] * b_xyy[idx2] * c_xyy[idx2]))
        eyxy = float(np.mean(a_yxy[idx3] * b_yxy[idx3] * c_yxy[idx3]))
        eyyx = float(np.mean(a_yyx[idx4] * b_yyx[idx4] * c_yyx[idx4]))
        vals[i] = exxx - exyy - eyxy - eyyx
    return float(np.mean(vals)), float(np.std(vals))


def ghz_cont_and_gated(
    phases: np.ndarray,
    r_inner: float,
    wavelength: float,
    offset_deg: float,
    attenuation_power: float,
    gate_k: float,
) -> dict:
    d = distance_matrix(r_inner, inner_offset=math.radians(offset_deg))
    x, y = 0.0, PI / 2.0
    ax = field_at_observer(phases, 0, x, d, wavelength, attenuation_power)
    bx = field_at_observer(phases, 1, x, d, wavelength, attenuation_power)
    cx = field_at_observer(phases, 2, x, d, wavelength, attenuation_power)
    ay = field_at_observer(phases, 0, y, d, wavelength, attenuation_power)
    by = field_at_observer(phases, 1, y, d, wavelength, attenuation_power)
    cy = field_at_observer(phases, 2, y, d, wavelength, attenuation_power)

    exxx_c, exyy_c, eyxy_c, eyyx_c = (
        e3_cont(ax, bx, cx),
        e3_cont(ax, by, cy),
        e3_cont(ay, bx, cy),
        e3_cont(ay, by, cx),
    )
    f_cont = exxx_c - exyy_c - eyxy_c - eyyx_c

    exxx_g, r1 = e3_gated(ax, bx, cx, gate_k)
    exyy_g, r2 = e3_gated(ax, by, cy, gate_k)
    eyxy_g, r3 = e3_gated(ay, bx, cy, gate_k)
    eyyx_g, r4 = e3_gated(ay, by, cx, gate_k)
    f_g = exxx_g - exyy_g - eyxy_g - eyyx_g
    r_g = float(np.mean([r1, r2, r3, r4]))
    return {
        "F_cont": float(f_cont),
        "F_gated": float(f_g),
        "R_gated": r_g,
        "D_gated": float(f_g * r_g),
        "selection_tax": float(1.0 - r_g),
    }


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="V10.4 computed cost curve (medium model)")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--states", type=int, default=120000)
    ap.add_argument("--r-inner", type=float, default=0.8)
    ap.add_argument("--wavelength", type=float, default=0.3)
    ap.add_argument("--offset-deg", type=float, default=0.0)
    ap.add_argument("--attenuation-power", type=float, default=1.0)
    ap.add_argument("--gate-min", type=float, default=0.35)
    ap.add_argument("--gate-max", type=float, default=0.95)
    ap.add_argument("--gate-points", type=int, default=40)
    ap.add_argument("--random-trials", type=int, default=120)
    ap.add_argument("--random-seed", type=int, default=20260424)
    args = ap.parse_args()

    out = Path("artifacts/ghz_medium_v10")
    out.mkdir(parents=True, exist_ok=True)

    gate_vals = np.linspace(float(args.gate_min), float(args.gate_max), max(5, int(args.gate_points)))
    phases = medium_phase_states(int(args.seed), int(args.states))

    d = distance_matrix(float(args.r_inner), inner_offset=math.radians(float(args.offset_deg)))
    x, y = 0.0, PI / 2.0
    ax = field_at_observer(phases, 0, x, d, float(args.wavelength), float(args.attenuation_power))
    bx = field_at_observer(phases, 1, x, d, float(args.wavelength), float(args.attenuation_power))
    cx = field_at_observer(phases, 2, x, d, float(args.wavelength), float(args.attenuation_power))
    ay = field_at_observer(phases, 0, y, d, float(args.wavelength), float(args.attenuation_power))
    by = field_at_observer(phases, 1, y, d, float(args.wavelength), float(args.attenuation_power))
    cy = field_at_observer(phases, 2, y, d, float(args.wavelength), float(args.attenuation_power))

    # setting-independent continuous reference (no gate)
    exxx_c = e3_cont(ax, bx, cx)
    exyy_c = e3_cont(ax, by, cy)
    eyxy_c = e3_cont(ay, bx, cy)
    eyyx_c = e3_cont(ay, by, cx)
    f_cont_ref = float(exxx_c - exyy_c - eyxy_c - eyyx_c)

    rows: list[dict] = []
    rng_random = np.random.default_rng(int(args.random_seed))
    for gk in gate_vals:
        exxx_g, r1, a_xxx, b_xxx, c_xxx = e3_gated_details(ax, bx, cx, float(gk))
        exyy_g, r2, a_xyy, b_xyy, c_xyy = e3_gated_details(ax, by, cy, float(gk))
        eyxy_g, r3, a_yxy, b_yxy, c_yxy = e3_gated_details(ay, bx, cy, float(gk))
        eyyx_g, r4, a_yyx, b_yyx, c_yyx = e3_gated_details(ay, by, cx, float(gk))
        f_g = float(exxx_g - exyy_g - eyxy_g - eyyx_g)
        r = float(np.mean([r1, r2, r3, r4]))
        f_rand_mean, f_rand_std = random_control_f(
            a_xxx,
            b_xxx,
            c_xxx,
            a_xyy,
            b_xyy,
            c_xyy,
            a_yxy,
            b_yxy,
            c_yxy,
            a_yyx,
            b_yyx,
            c_yyx,
            r1,
            r2,
            r3,
            r4,
            rng_random,
            int(args.random_trials),
        )
        rows.append(
            {
                "gate_k": float(gk),
                "retained_ratio_R_gated": r,
                "discarded_ratio": float(1.0 - r),
                "F_gated": f_g,
                "F_random_mean": f_rand_mean,
                "F_random_std": f_rand_std,
                "F_cont": f_cont_ref,
                "D_gated": float(f_g * r),
                "selection_tax": float(1.0 - r),
            }
        )

    # Plot in order of decreasing retention (weak → strong selection reads left→right)
    order = np.argsort([-r["retained_ratio_R_gated"] for r in rows])
    rows_sorted = [rows[i] for i in order]

    r_pct = [100.0 * r["retained_ratio_R_gated"] for r in rows_sorted]
    f_vals = [r["F_gated"] for r in rows_sorted]
    f_rand_mean = [r["F_random_mean"] for r in rows_sorted]
    f_rand_std = [r["F_random_std"] for r in rows_sorted]
    f_rand_lo = [m - s for m, s in zip(f_rand_mean, f_rand_std)]
    f_rand_hi = [m + s for m, s in zip(f_rand_mean, f_rand_std)]

    fig, ax1 = plt.subplots(figsize=(8.2, 5.0), dpi=150)
    ax1.plot(r_pct, f_vals, "-o", ms=4, lw=1.5, color="#1f77b4", label="F_gated (computed)")
    ax1.plot(r_pct, f_rand_mean, "-s", ms=3.5, lw=1.2, color="#2ca02c", label="F_random_mean (same retention)")
    ax1.fill_between(r_pct, f_rand_lo, f_rand_hi, color="#2ca02c", alpha=0.15, label="random ±1σ")
    ax1.set_xlabel("Retained ratio R_gated (%, mean over 4 settings)")
    ax1.set_ylabel("F_gated")
    ax1.axhline(2.0, color="#7570b3", ls="--", lw=1.0, label="binary LHV ref. 2")
    ax1.axhline(4.0, color="#d95f02", ls="--", lw=1.0, label="QM binary ideal 4")
    ax1.set_xlim(0.0, 105.0)
    ax1.grid(alpha=0.25)
    ax1.legend(loc="best", fontsize=8)
    ax1.set_title("V10.4 computed cost curve — medium wave + soft gate sweep\n(no illustrative anchors)")

    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    ax1_ticks = ax1.get_xticks()
    ax2.set_xticks(ax1_ticks)
    ax2.set_xticklabels([f"{100.0 - t:.0f}" for t in ax1_ticks])
    ax2.set_xlabel("Discarded % (derived from R_gated)")

    fig.tight_layout()
    png_path = out / "V10_4_REAL_COST_CURVE.png"
    fig.savefig(png_path, dpi=160)
    plt.close(fig)

    csv_path = out / "V10_4_REAL_COST_CURVE.csv"
    hdr = (
        "gate_k,retained_ratio_R_gated,discarded_ratio,F_gated,F_random_mean,"
        "F_random_std,F_cont,D_gated,selection_tax"
    )
    lines = [hdr]
    for r in rows:
        lines.append(
            f"{r['gate_k']:.8f},{r['retained_ratio_R_gated']:.8f},{r['discarded_ratio']:.8f},"
            f"{r['F_gated']:.8f},{r['F_random_mean']:.8f},{r['F_random_std']:.8f},"
            f"{r['F_cont']:.8f},{r['D_gated']:.8f},{r['selection_tax']:.8f}"
        )
    csv_path.write_text("\n".join(lines), encoding="utf-8")

    meta = {
        "type": "computed_curve",
        "model": "ghz_medium_v10",
        "script": "scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py",
        "note": (
            "F_gated and R_gated are evaluated on a fixed RNG phase sample; "
            "gate_k is swept on a linear grid. No F–retention endpoint is prescribed."
        ),
        "selection_definition": "soft_detector gate_k * RMS per channel; R_gated = mean of 4 setting hit rates",
        "random_control": {
            "definition": "random subsampling with the same per-setting retention as amplitude-gated events",
            "trials_per_gate": int(args.random_trials),
            "seed": int(args.random_seed),
        },
        "seed": int(args.seed),
        "states": int(args.states),
        "physics": {
            "r_inner": float(args.r_inner),
            "wavelength": float(args.wavelength),
            "offset_deg": float(args.offset_deg),
            "attenuation_power": float(args.attenuation_power),
        },
        "gate_scan": {
            "gate_min": float(args.gate_min),
            "gate_max": float(args.gate_max),
            "gate_points": int(args.gate_points),
        },
        "F_cont_constant_across_scan": f_cont_ref,
        "outputs": {
            "png": str(png_path).replace("\\", "/"),
            "csv": str(csv_path).replace("\\", "/"),
        },
    }
    (out / "V10_4_REAL_COST_CURVE.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    (out / "V10_4_REAL_COST_CURVE_REPORT.md").write_text(
        "\n".join(
            [
                "# V10.4 真实代价曲线（计算，非示意）",
                "",
                "与 `v10_3_selection_tax_audit.py` 同一套介质相位与门控定义；对 `gate_k` 做线性扫描，",
                "每个点的 `F_gated`、`R_gated` 均由同一份固定样本算出，**未**使用 `plot_f_target_cost_curve.py` 类参数锚点。",
                "并加入随机同保留率对照：`F_random_mean ± 1σ`，用于区分门控选择效应与随机抽样基线。",
                "",
                "## 产物",
                "- `V10_4_REAL_COST_CURVE.png`",
                "- `V10_4_REAL_COST_CURVE.csv`",
                "- `V10_4_REAL_COST_CURVE.meta.json`（`type`: `computed_curve`）",
                "",
                f"- 参考 F_cont（与 gate_k 无关）: {f_cont_ref:.6f}",
            ]
        ),
        encoding="utf-8",
    )

    print("wrote", png_path)
    print("wrote", csv_path)
    print("wrote", out / "V10_4_REAL_COST_CURVE.meta.json")
    print("wrote", out / "V10_4_REAL_COST_CURVE_REPORT.md")


if __name__ == "__main__":
    main()
