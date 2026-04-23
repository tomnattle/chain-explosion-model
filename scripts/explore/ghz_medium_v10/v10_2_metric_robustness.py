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


def e3_sat(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray, gain: float) -> float:
    a = np.tanh(gain * sa)
    b = np.tanh(gain * sb)
    c = np.tanh(gain * sc)
    num = float(np.mean(a * b * c))
    den = float((np.mean(a * a) * np.mean(b * b) * np.mean(c * c)) ** (1.0 / 3.0))
    return num / den if den > 1e-12 else 0.0


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    x0 = x - float(np.mean(x))
    y0 = y - float(np.mean(y))
    den = float(np.sqrt(np.mean(x0 * x0) * np.mean(y0 * y0)))
    return float(np.mean(x0 * y0) / den) if den > 1e-12 else 0.0


def e3_prs(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray) -> float:
    return pearson(sa * sb, sc)


def eval_three_rulers(phases: np.ndarray, r_inner: float, wavelength: float, offset_deg: float, attenuation_power: float, sat_gain: float) -> dict:
    d = distance_matrix(r_inner, inner_offset=math.radians(offset_deg))
    x, y = 0.0, PI / 2.0
    ax = field_at_observer(phases, 0, x, d, wavelength, attenuation_power)
    bx = field_at_observer(phases, 1, x, d, wavelength, attenuation_power)
    cx = field_at_observer(phases, 2, x, d, wavelength, attenuation_power)
    ay = field_at_observer(phases, 0, y, d, wavelength, attenuation_power)
    by = field_at_observer(phases, 1, y, d, wavelength, attenuation_power)
    cy = field_at_observer(phases, 2, y, d, wavelength, attenuation_power)
    exxx_c, exyy_c, eyxy_c, eyyx_c = e3_cont(ax, bx, cx), e3_cont(ax, by, cy), e3_cont(ay, bx, cy), e3_cont(ay, by, cx)
    exxx_s, exyy_s, eyxy_s, eyyx_s = e3_sat(ax, bx, cx, sat_gain), e3_sat(ax, by, cy, sat_gain), e3_sat(ay, bx, cy, sat_gain), e3_sat(ay, by, cx, sat_gain)
    exxx_p, exyy_p, eyxy_p, eyyx_p = e3_prs(ax, bx, cx), e3_prs(ax, by, cy), e3_prs(ay, bx, cy), e3_prs(ay, by, cx)
    return {
        "F_cont": float(exxx_c - exyy_c - eyxy_c - eyyx_c),
        "F_sat": float(exxx_s - exyy_s - eyxy_s - eyyx_s),
        "F_prs": float(exxx_p - exyy_p - eyxy_p - eyyx_p),
    }


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="V10.2 three-ruler robustness")
    ap.add_argument("--seed", type=int, default=20260423)
    ap.add_argument("--states", type=int, default=120000)
    ap.add_argument("--attenuation-power", type=float, default=1.0)
    ap.add_argument("--sat-gain", type=float, default=0.8)
    ap.add_argument("--bootstrap-draws", type=int, default=80)
    ap.add_argument("--bootstrap-subsample", type=int, default=30000)
    args = ap.parse_args()

    out = Path("artifacts/ghz_medium_v10")
    out.mkdir(parents=True, exist_ok=True)

    # reference point from v10.1 best cont
    ref = {"r_inner": 0.8, "wavelength": 0.3, "offset_deg": 0.0}
    phases = medium_phase_states(args.seed, int(args.states))
    base = eval_three_rulers(phases, ref["r_inner"], ref["wavelength"], ref["offset_deg"], args.attenuation_power, args.sat_gain)

    rng = np.random.default_rng(args.seed + 7)
    n = phases.shape[1]
    m = min(n, int(args.bootstrap_subsample))
    bvals = {"F_cont": [], "F_sat": [], "F_prs": []}
    for _ in range(int(args.bootstrap_draws)):
        idx = rng.integers(0, n, size=m)
        ev = eval_three_rulers(phases[:, idx], ref["r_inner"], ref["wavelength"], ref["offset_deg"], args.attenuation_power, args.sat_gain)
        for k in bvals:
            bvals[k].append(ev[k])

    ci = {}
    for k, arr in bvals.items():
        q = np.quantile(np.array(arr), [0.025, 0.5, 0.975])
        ci[k] = {"lo": float(q[0]), "mid": float(q[1]), "hi": float(q[2])}

    seed_rows = []
    for s in [20260411, 20260417, 20260423, 20260429, 20260501]:
        ps = medium_phase_states(s, int(args.states))
        ev = eval_three_rulers(ps, ref["r_inner"], ref["wavelength"], ref["offset_deg"], args.attenuation_power, args.sat_gain)
        seed_rows.append({"seed": s, **ev})

    # plot CI
    labels = ["F_cont", "F_sat", "F_prs"]
    mids = [ci[k]["mid"] for k in labels]
    los = [ci[k]["mid"] - ci[k]["lo"] for k in labels]
    his = [ci[k]["hi"] - ci[k]["mid"] for k in labels]

    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    x = np.arange(len(labels))
    ax.errorbar(x, mids, yerr=[los, his], fmt="o", capsize=4)
    ax.set_xticks(x, labels)
    ax.set_ylabel("F")
    ax.set_title("V10.2 bootstrap CI by metric ruler")
    ax.axhline(2.0, color="gray", ls="--", lw=0.9)
    ax.axhline(4.0, color="green", ls="--", lw=0.9)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "V10_2_BOOTSTRAP_CI_RULERS.png", dpi=160)
    plt.close(fig)

    # seed stability plot
    fig2, ax2 = plt.subplots(figsize=(7.8, 4.8), dpi=150)
    ax2.plot([r["seed"] for r in seed_rows], [r["F_cont"] for r in seed_rows], "-o", label="F_cont")
    ax2.plot([r["seed"] for r in seed_rows], [r["F_sat"] for r in seed_rows], "-o", label="F_sat")
    ax2.plot([r["seed"] for r in seed_rows], [r["F_prs"] for r in seed_rows], "-o", label="F_prs")
    ax2.set_xlabel("seed")
    ax2.set_ylabel("F")
    ax2.set_title("V10.2 seed stability by ruler")
    ax2.grid(alpha=0.25)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out / "V10_2_SEED_STABILITY_RULERS.png", dpi=160)
    plt.close(fig2)

    result = {
        "reference_point": ref,
        "base_eval": base,
        "bootstrap_ci95": ci,
        "seed_sweep": seed_rows,
    }
    (out / "V10_2_METRIC_ROBUSTNESS_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "V10_2_METRIC_ROBUSTNESS_REPORT.md").write_text(
        "\n".join(
            [
                "# V10.2 尺子稳健性审计",
                "",
                "在同一物理点，比较三种口径的 bootstrap CI 与 seed 稳定性。",
                "",
                "## Outputs",
                "- `V10_2_BOOTSTRAP_CI_RULERS.png`",
                "- `V10_2_SEED_STABILITY_RULERS.png`",
                "- `V10_2_METRIC_ROBUSTNESS_RESULTS.json`",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", out / "V10_2_METRIC_ROBUSTNESS_RESULTS.json")
    print("wrote", out / "V10_2_BOOTSTRAP_CI_RULERS.png")
    print("wrote", out / "V10_2_SEED_STABILITY_RULERS.png")


if __name__ == "__main__":
    main()

