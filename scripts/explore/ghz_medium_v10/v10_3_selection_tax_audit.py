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


def field_at_observer(phases: np.ndarray, observer_idx: int, probe_angle: float, d: np.ndarray, wavelength: float, attenuation_power: float) -> np.ndarray:
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


def ghz_cont_and_gated(phases: np.ndarray, r_inner: float, wavelength: float, offset_deg: float, attenuation_power: float, gate_k: float) -> dict:
    d = distance_matrix(r_inner, inner_offset=math.radians(offset_deg))
    x, y = 0.0, PI / 2.0
    ax = field_at_observer(phases, 0, x, d, wavelength, attenuation_power)
    bx = field_at_observer(phases, 1, x, d, wavelength, attenuation_power)
    cx = field_at_observer(phases, 2, x, d, wavelength, attenuation_power)
    ay = field_at_observer(phases, 0, y, d, wavelength, attenuation_power)
    by = field_at_observer(phases, 1, y, d, wavelength, attenuation_power)
    cy = field_at_observer(phases, 2, y, d, wavelength, attenuation_power)

    # continuous (no selection)
    exxx_c, exyy_c, eyxy_c, eyyx_c = e3_cont(ax, bx, cx), e3_cont(ax, by, cy), e3_cont(ay, bx, cy), e3_cont(ay, by, cx)
    f_cont = exxx_c - exyy_c - eyxy_c - eyyx_c

    # gated binary (selection)
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

    ap = argparse.ArgumentParser(description="V10.3 selection-tax audit")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--states", type=int, default=120000)
    ap.add_argument("--r-inner", type=float, default=0.8)
    ap.add_argument("--wavelength", type=float, default=0.3)
    ap.add_argument("--offset-deg", type=float, default=0.0)
    ap.add_argument("--attenuation-power", type=float, default=1.0)
    args = ap.parse_args()

    out = Path("artifacts/ghz_medium_v10")
    out.mkdir(parents=True, exist_ok=True)
    phases = medium_phase_states(args.seed, int(args.states))

    # gate ladder from weak to strong selection
    gate_vals = np.linspace(0.35, 0.95, 13)
    rows = []
    for gk in gate_vals:
        ev = ghz_cont_and_gated(
            phases=phases,
            r_inner=float(args.r_inner),
            wavelength=float(args.wavelength),
            offset_deg=float(args.offset_deg),
            attenuation_power=float(args.attenuation_power),
            gate_k=float(gk),
        )
        rows.append({"gate_k": float(gk), **ev})

    best_f = max(rows, key=lambda x: x["F_gated"])
    best_d = max(rows, key=lambda x: x["D_gated"])

    # figures
    fig, ax1 = plt.subplots(figsize=(7.6, 5.0), dpi=150)
    x = [r["gate_k"] for r in rows]
    ax1.plot(x, [r["F_gated"] for r in rows], "-o", label="F_gated")
    ax1.plot(x, [r["D_gated"] for r in rows], "-o", label="D_gated")
    ax1.set_xlabel("gate_k (selection strength)")
    ax1.set_ylabel("F / D")
    ax1.grid(alpha=0.25)
    ax1.legend(loc="upper left", fontsize=8)

    ax2 = ax1.twinx()
    ax2.plot(x, [r["R_gated"] for r in rows], "-s", color="#8e44ad", label="R_gated")
    ax2.set_ylabel("R")
    ax2.set_ylim(0.0, 1.0)
    fig.tight_layout()
    fig.savefig(out / "V10_3_SELECTION_TAX_CURVES.png", dpi=160)
    plt.close(fig)

    fig2, ax = plt.subplots(figsize=(7.0, 4.8), dpi=150)
    ax.scatter([r["R_gated"] for r in rows], [r["F_gated"] for r in rows], c=[r["gate_k"] for r in rows], cmap="viridis", s=42)
    ax.axhline(2.0, color="gray", ls="--", lw=0.9)
    ax.axhline(4.0, color="green", ls="--", lw=0.9)
    ax.set_xlabel("R_gated")
    ax.set_ylabel("F_gated")
    ax.set_title("Selection tradeoff: F vs R")
    ax.grid(alpha=0.25)
    fig2.tight_layout()
    fig2.savefig(out / "V10_3_F_VS_R_SELECTION.png", dpi=160)
    plt.close(fig2)

    result = {
        "reference_physics": {
            "r_inner": float(args.r_inner),
            "wavelength": float(args.wavelength),
            "offset_deg": float(args.offset_deg),
            "attenuation_power": float(args.attenuation_power),
            "states": int(args.states),
        },
        "gate_scan_rows": rows,
        "best_by_F_gated": best_f,
        "best_by_D_gated": best_d,
        "continuous_reference_F": rows[0]["F_cont"],  # same for all gate_k
    }
    (out / "V10_3_SELECTION_TAX_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "V10_3_SELECTION_TAX_REPORT.md").write_text(
        "\n".join(
            [
                "# V10.3 选择税审计",
                "",
                "同一传播机制下，仅改变门控强度 gate_k，量化 F、R、D 的联动。",
                "",
                f"- best F_gated: {best_f['F_gated']:.6f} @ R={best_f['R_gated']:.6f}, tax={best_f['selection_tax']:.3f}",
                f"- best D_gated: {best_d['D_gated']:.6f} (F={best_d['F_gated']:.6f}, R={best_d['R_gated']:.6f}, tax={best_d['selection_tax']:.3f})",
                "",
                "## Outputs",
                "- `V10_3_SELECTION_TAX_RESULTS.json`",
                "- `V10_3_SELECTION_TAX_CURVES.png`",
                "- `V10_3_F_VS_R_SELECTION.png`",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out / "V10_3_SELECTION_TAX_RESULTS.json")
    print("wrote", out / "V10_3_SELECTION_TAX_CURVES.png")
    print("wrote", out / "V10_3_F_VS_R_SELECTION.png")


if __name__ == "__main__":
    main()

