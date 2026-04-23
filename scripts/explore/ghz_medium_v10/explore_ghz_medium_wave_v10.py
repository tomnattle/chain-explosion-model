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
    """
    Continuous medium field at one observer:
      s = sum_i (1 / d_ij^p) * cos(phi_i - probe_angle - 2*pi*d_ij/lambda)
    """
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
    """
    Saturated but still continuous readout (no threshold, no event rejection).
    """
    a = np.tanh(sat_gain * sa)
    b = np.tanh(sat_gain * sb)
    c = np.tanh(sat_gain * sc)
    num = float(np.mean(a * b * c))
    den = float((np.mean(a * a) * np.mean(b * b) * np.mean(c * c)) ** (1.0 / 3.0))
    return num / den if den > 1e-12 else 0.0


def ghz_bundle(
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

    # Pure continuous metric
    exxx_c = e3_continuous(ax, bx, cx)
    exyy_c = e3_continuous(ax, by, cy)
    eyxy_c = e3_continuous(ay, bx, cy)
    eyyx_c = e3_continuous(ay, by, cx)
    f_cont = exxx_c - exyy_c - eyxy_c - eyyx_c

    # Continuous saturated metric (still no threshold/gating)
    exxx_s = e3_saturated(ax, bx, cx, sat_gain)
    exyy_s = e3_saturated(ax, by, cy, sat_gain)
    eyxy_s = e3_saturated(ay, bx, cy, sat_gain)
    eyyx_s = e3_saturated(ay, by, cx, sat_gain)
    f_sat = exxx_s - exyy_s - eyxy_s - eyyx_s

    return {
        "EXXX_cont": exxx_c,
        "EXYY_cont": exyy_c,
        "EYXY_cont": eyxy_c,
        "EYYX_cont": eyyx_c,
        "F_cont": float(f_cont),
        "EXXX_sat": exxx_s,
        "EXYY_sat": exyy_s,
        "EYXY_sat": eyxy_s,
        "EYYX_sat": eyyx_s,
        "F_sat": float(f_sat),
    }


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="GHZ medium-only spherical propagation audit v10")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--states", type=int, default=120000)
    ap.add_argument("--attenuation-power", type=float, default=1.0)
    ap.add_argument("--sat-gain", type=float, default=0.8)
    ap.add_argument("--r-steps", type=int, default=20)
    ap.add_argument("--w-steps", type=int, default=20)
    ap.add_argument("--offset-steps", type=int, default=25)
    args = ap.parse_args()

    out = Path("artifacts/ghz_medium_v10")
    out.mkdir(parents=True, exist_ok=True)

    phases = medium_phase_states(args.seed, int(args.states))

    r_vals = np.linspace(0.05, 0.8, int(args.r_steps))
    w_vals = np.linspace(0.1, 2.0, int(args.w_steps))
    rows = []
    for r in r_vals:
        for w in w_vals:
            ev = ghz_bundle(
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

    # offset drift at best saturated point
    off_vals = np.linspace(0.0, 60.0, int(args.offset_steps))
    drift = []
    for off in off_vals:
        ev = ghz_bundle(
            phases=phases,
            r_inner=best_sat["r_inner"],
            wavelength=best_sat["wavelength"],
            inner_offset_deg=float(off),
            attenuation_power=float(args.attenuation_power),
            sat_gain=float(args.sat_gain),
        )
        drift.append({"offset_deg": float(off), **ev})
    drift_best = max(drift, key=lambda x: abs(x["F_sat"]))

    # plots
    fcm = np.array([x["F_cont"] for x in rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))
    fsm = np.array([x["F_sat"] for x in rows], dtype=np.float64).reshape((len(r_vals), len(w_vals)))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.8), dpi=150)
    im1 = a1.contourf(w_vals, r_vals, fcm, levels=22, cmap="coolwarm")
    fig.colorbar(im1, ax=a1)
    a1.set_title("F_cont (continuous only)")
    a1.set_xlabel("wavelength")
    a1.set_ylabel("r_inner")

    im2 = a2.contourf(w_vals, r_vals, fsm, levels=22, cmap="coolwarm")
    fig.colorbar(im2, ax=a2)
    a2.set_title("F_sat (continuous saturated)")
    a2.set_xlabel("wavelength")
    a2.set_ylabel("r_inner")
    fig.tight_layout()
    fig.savefig(out / "V10_F_CONT_VS_F_SAT_MAPS.png", dpi=160)
    plt.close(fig)

    fig2, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    ax.plot([x["offset_deg"] for x in drift], [x["F_sat"] for x in drift], "-o", ms=3.2, lw=1.2, label="F_sat")
    ax.plot([x["offset_deg"] for x in drift], [x["F_cont"] for x in drift], "-o", ms=2.8, lw=1.0, label="F_cont")
    ax.axhline(2.0, color="gray", ls="--", lw=0.9)
    ax.axhline(4.0, color="green", ls="--", lw=0.9)
    ax.set_xlabel("inner ring offset (deg)")
    ax.set_ylabel("F")
    ax.set_title("Offset drift without binary gating")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out / "V10_OFFSET_DRIFT_CONTINUOUS.png", dpi=160)
    plt.close(fig2)

    result = {
        "seed": int(args.seed),
        "states": int(args.states),
        "attenuation_power": float(args.attenuation_power),
        "sat_gain": float(args.sat_gain),
        "grid": {"r_steps": int(args.r_steps), "w_steps": int(args.w_steps)},
        "best_abs_F_cont": best_cont,
        "best_abs_F_sat": best_sat,
        "offset_drift_best_abs_F_sat": drift_best,
    }
    (out / "V10_MEDIUM_ONLY_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "V10_MEDIUM_ONLY_REPORT.md").write_text(
        "\n".join(
            [
                "# V10 介质传播重构",
                "",
                "禁止二值点击/门控，仅保留连续球面传播与连续读出。",
                "",
                "## Outputs",
                "- `V10_F_CONT_VS_F_SAT_MAPS.png`",
                "- `V10_OFFSET_DRIFT_CONTINUOUS.png`",
                "- `V10_MEDIUM_ONLY_RESULTS.json`",
                "",
                f"- best |F_cont|: {abs(best_cont['F_cont']):.6f}",
                f"- best |F_sat|: {abs(best_sat['F_sat']):.6f}",
                f"- drift best |F_sat| at offset={drift_best['offset_deg']:.3f} deg",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out / "V10_MEDIUM_ONLY_RESULTS.json")
    print("wrote", out / "V10_F_CONT_VS_F_SAT_MAPS.png")
    print("wrote", out / "V10_OFFSET_DRIFT_CONTINUOUS.png")


if __name__ == "__main__":
    main()

