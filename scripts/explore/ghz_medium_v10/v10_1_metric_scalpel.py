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
    angles = np.array([0.0, 2.0 * PI / 3.0, 4.0 * PI / 3.0], dtype=np.float64) + offset
    return np.stack([radius * np.cos(angles), radius * np.sin(angles)], axis=1)


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


def e3_continuous(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray) -> float:
    num = float(np.mean(sa * sb * sc))
    den = float((np.mean(sa * sa) * np.mean(sb * sb) * np.mean(sc * sc)) ** (1.0 / 3.0))
    return num / den if den > 1e-12 else 0.0


def e3_saturated(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray, sat_gain: float) -> float:
    a = np.tanh(sat_gain * sa)
    b = np.tanh(sat_gain * sb)
    c = np.tanh(sat_gain * sc)
    num = float(np.mean(a * b * c))
    den = float((np.mean(a * a) * np.mean(b * b) * np.mean(c * c)) ** (1.0 / 3.0))
    return num / den if den > 1e-12 else 0.0


def pearson_corr(x: np.ndarray, y: np.ndarray) -> float:
    x0 = x - float(np.mean(x))
    y0 = y - float(np.mean(y))
    den = float(np.sqrt(np.mean(x0 * x0) * np.mean(y0 * y0)))
    if den <= 1e-12:
        return 0.0
    return float(np.mean(x0 * y0) / den)


def e3_pearson(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray) -> float:
    # "标准统计尺子": corr(AB, C), bounded in [-1, 1]
    return pearson_corr(sa * sb, sc)


def ghz_all_metrics(
    phases: np.ndarray,
    r_inner: float,
    wavelength: float,
    inner_offset_deg: float,
    attenuation_power: float,
    sat_gain: float,
) -> dict:
    d = distance_matrix(r_inner, inner_offset=math.radians(inner_offset_deg))
    x, y = 0.0, PI / 2.0
    ax = field_at_observer(phases, 0, x, d, wavelength, attenuation_power)
    bx = field_at_observer(phases, 1, x, d, wavelength, attenuation_power)
    cx = field_at_observer(phases, 2, x, d, wavelength, attenuation_power)
    ay = field_at_observer(phases, 0, y, d, wavelength, attenuation_power)
    by = field_at_observer(phases, 1, y, d, wavelength, attenuation_power)
    cy = field_at_observer(phases, 2, y, d, wavelength, attenuation_power)

    # old ruler
    exxx_c = e3_continuous(ax, bx, cx)
    exyy_c = e3_continuous(ax, by, cy)
    eyxy_c = e3_continuous(ay, bx, cy)
    eyyx_c = e3_continuous(ay, by, cx)
    f_cont = exxx_c - exyy_c - eyxy_c - eyyx_c

    # bounded ruler A
    exxx_s = e3_saturated(ax, bx, cx, sat_gain)
    exyy_s = e3_saturated(ax, by, cy, sat_gain)
    eyxy_s = e3_saturated(ay, bx, cy, sat_gain)
    eyyx_s = e3_saturated(ay, by, cx, sat_gain)
    f_sat = exxx_s - exyy_s - eyxy_s - eyyx_s

    # bounded ruler B (Pearson)
    exxx_p = e3_pearson(ax, bx, cx)
    exyy_p = e3_pearson(ax, by, cy)
    eyxy_p = e3_pearson(ay, bx, cy)
    eyyx_p = e3_pearson(ay, by, cx)
    f_prs = exxx_p - exyy_p - eyxy_p - eyyx_p

    return {
        "F_cont": float(f_cont),
        "F_sat": float(f_sat),
        "F_prs": float(f_prs),
        "EXXX_cont": exxx_c,
        "EXYY_cont": exyy_c,
        "EYXY_cont": eyxy_c,
        "EYYX_cont": eyyx_c,
        "EXXX_sat": exxx_s,
        "EXYY_sat": exyy_s,
        "EYXY_sat": eyxy_s,
        "EYYX_sat": eyyx_s,
        "EXXX_prs": exxx_p,
        "EXYY_prs": exyy_p,
        "EYXY_prs": eyxy_p,
        "EYYX_prs": eyyx_p,
    }


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="V10.1 metric scalpel")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--states", type=int, default=120000)
    ap.add_argument("--attenuation-power", type=float, default=1.0)
    ap.add_argument("--sat-gain", type=float, default=0.8)
    ap.add_argument("--r-steps", type=int, default=20)
    ap.add_argument("--w-steps", type=int, default=20)
    args = ap.parse_args()

    out = Path("artifacts/ghz_medium_v10")
    out.mkdir(parents=True, exist_ok=True)
    phases = medium_phase_states(args.seed, int(args.states))

    r_vals = np.linspace(0.05, 0.8, int(args.r_steps))
    w_vals = np.linspace(0.1, 2.0, int(args.w_steps))
    rows = []
    for r in r_vals:
        for w in w_vals:
            ev = ghz_all_metrics(
                phases=phases,
                r_inner=float(r),
                wavelength=float(w),
                inner_offset_deg=0.0,
                attenuation_power=float(args.attenuation_power),
                sat_gain=float(args.sat_gain),
            )
            rows.append({"r_inner": float(r), "wavelength": float(w), **ev})

    best_cont = max(rows, key=lambda x: abs(x["F_cont"]))
    best_sat = max(rows, key=lambda x: abs(x["F_sat"]))
    best_prs = max(rows, key=lambda x: abs(x["F_prs"]))

    # Compare three rulers at same physical point (choose cont-best point)
    ref = ghz_all_metrics(
        phases=phases,
        r_inner=best_cont["r_inner"],
        wavelength=best_cont["wavelength"],
        inner_offset_deg=0.0,
        attenuation_power=float(args.attenuation_power),
        sat_gain=float(args.sat_gain),
    )

    fcm = np.array([x["F_cont"] for x in rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))
    fsm = np.array([x["F_sat"] for x in rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))
    fpm = np.array([x["F_prs"] for x in rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))

    fig, axes = plt.subplots(1, 3, figsize=(15.8, 4.8), dpi=150)
    for ax, mat, ttl in [
        (axes[0], fcm, "F_cont (legacy unbounded)"),
        (axes[1], fsm, "F_sat (bounded tanh)"),
        (axes[2], fpm, "F_prs (bounded Pearson)"),
    ]:
        im = ax.contourf(w_vals, r_vals, mat, levels=22, cmap="coolwarm")
        fig.colorbar(im, ax=ax)
        ax.set_xlabel("wavelength")
        ax.set_ylabel("r_inner")
        ax.set_title(ttl)
    fig.tight_layout()
    fig.savefig(out / "V10_1_THREE_RULERS_MAPS.png", dpi=160)
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    names = ["F_cont", "F_sat", "F_prs"]
    vals = [ref["F_cont"], ref["F_sat"], ref["F_prs"]]
    ax2.bar(names, vals, color=["#c0392b", "#2980b9", "#27ae60"], alpha=0.86)
    ax2.axhline(2.0, color="gray", ls="--", lw=1.0)
    ax2.axhline(4.0, color="green", ls="--", lw=1.0)
    ax2.set_title("Same physics, different rulers (at cont-best point)")
    ax2.set_ylabel("F")
    for i, v in enumerate(vals):
        ax2.text(i, v + (0.08 if v >= 0 else -0.12), f"{v:.3f}", ha="center")
    fig2.tight_layout()
    fig2.savefig(out / "V10_1_THREE_RULERS_BAR.png", dpi=160)
    plt.close(fig2)

    result = {
        "seed": int(args.seed),
        "states": int(args.states),
        "best_abs_F_cont": best_cont,
        "best_abs_F_sat": best_sat,
        "best_abs_F_prs": best_prs,
        "same_point_ruler_compare_at_cont_best": {
            "r_inner": best_cont["r_inner"],
            "wavelength": best_cont["wavelength"],
            "F_cont": ref["F_cont"],
            "F_sat": ref["F_sat"],
            "F_prs": ref["F_prs"],
        },
    }
    (out / "V10_1_METRIC_SCALPEL_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "V10_1_METRIC_SCALPEL_REPORT.md").write_text(
        "\n".join(
            [
                "# V10.1 口径手术",
                "",
                "同一介质传播过程，三把尺子并行对照：",
                "- legacy continuous (unbounded)",
                "- tanh bounded",
                "- Pearson bounded",
                "",
                "## Outputs",
                "- `V10_1_THREE_RULERS_MAPS.png`",
                "- `V10_1_THREE_RULERS_BAR.png`",
                "- `V10_1_METRIC_SCALPEL_RESULTS.json`",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out / "V10_1_METRIC_SCALPEL_RESULTS.json")
    print("wrote", out / "V10_1_THREE_RULERS_MAPS.png")
    print("wrote", out / "V10_1_THREE_RULERS_BAR.png")


if __name__ == "__main__":
    main()

