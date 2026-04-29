#!/usr/bin/env python3
"""
Triplet full-band transparency audit.

Goal:
- Compare a triplet-parameter medium against a canonical "glass-like" transparency window.
- Verify whether the triplet medium is broadband pass (full-domain pass) rather than
  only passing in the [10, 750] frequency window.

Notes:
- This is a model audit, not a claim of measured optical constants.
- Frequency unit is user-defined but should be used consistently.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_TRIPLET = {"mu": 1.5495, "rho": 2.35, "eta": 0.08}
DEFAULT_FREQ_MIN = 1.0
DEFAULT_FREQ_MAX = 2000.0
DEFAULT_POINTS = 4000
GLASS_WIN_MIN = 10.0
GLASS_WIN_MAX = 750.0


@dataclass
class AuditMetrics:
    mean_transmission: float
    min_transmission: float
    max_transmission: float
    pass_ratio: float
    inside_window_pass_ratio: float
    outside_window_pass_ratio: float
    outside_window_mean_transmission: float


@dataclass
class CounterfactualCheck:
    name: str
    mu: float
    rho: float
    eta: float
    fullband_pass: bool
    pass_ratio: float
    min_transmission: float


def _sigmoid(x: np.ndarray, center: float, k: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-k * (x - center)))


def glass_like_transmission(freq: np.ndarray, win_lo: float, win_hi: float) -> np.ndarray:
    """
    Canonical smooth band-pass reference:
    - near 0 outside passband
    - near 1 inside [win_lo, win_hi]
    """
    width = max(win_hi - win_lo, 1e-9)
    edge = 18.0 / width
    enter = _sigmoid(freq, win_lo, edge)
    leave = 1.0 - _sigmoid(freq, win_hi, edge)
    return np.clip(enter * leave, 0.0, 1.0)


def triplet_broadband_transmission(
    freq: np.ndarray,
    mu: float,
    rho: float,
    eta: float,
    *,
    f_ref: float = 100.0,
) -> np.ndarray:
    """
    Triplet medium toy attenuation model:
    T(f) = exp(-alpha(f)), alpha = eta * (f/f_ref)^p / gain(mu,rho)

    Design intent:
    - Lower eta => lower loss
    - Higher mu*rho => stronger transmission support
    - Frequency slope p kept small to represent weak dispersion attenuation
    """
    mu = max(float(mu), 1e-9)
    rho = max(float(rho), 1e-9)
    eta = max(float(eta), 1e-12)
    f_ref = max(float(f_ref), 1e-9)

    gain = (mu * rho) / (DEFAULT_TRIPLET["mu"] * DEFAULT_TRIPLET["rho"])
    p = 0.18 + 0.02 * (eta / DEFAULT_TRIPLET["eta"])
    alpha = (eta / max(gain, 1e-9)) * np.power(np.clip(freq / f_ref, 1e-9, None), p)
    return np.clip(np.exp(-alpha), 0.0, 1.0)


def compute_metrics(
    transmission: np.ndarray,
    inside_mask: np.ndarray,
    outside_mask: np.ndarray,
    pass_threshold: float,
) -> AuditMetrics:
    pass_mask = transmission >= pass_threshold
    inside_pass = pass_mask[inside_mask]
    outside_pass = pass_mask[outside_mask]
    outside_vals = transmission[outside_mask]
    return AuditMetrics(
        mean_transmission=float(np.mean(transmission)),
        min_transmission=float(np.min(transmission)),
        max_transmission=float(np.max(transmission)),
        pass_ratio=float(np.mean(pass_mask)),
        inside_window_pass_ratio=float(np.mean(inside_pass)) if inside_pass.size else 0.0,
        outside_window_pass_ratio=float(np.mean(outside_pass)) if outside_pass.size else 0.0,
        outside_window_mean_transmission=float(np.mean(outside_vals)) if outside_vals.size else 0.0,
    )


def _is_fullband_pass(m: AuditMetrics, args: argparse.Namespace) -> bool:
    return (m.pass_ratio >= float(args.fullband_ratio_min)) and (
        m.min_transmission >= float(args.min_transmission_floor)
    )


def run_counterfactual_expected_fail(
    freq: np.ndarray,
    inside_mask: np.ndarray,
    outside_mask: np.ndarray,
    args: argparse.Namespace,
) -> list[CounterfactualCheck]:
    cases = [
        ("high_loss_eta", float(args.mu), float(args.rho), float(args.eta) * 3.0),
        ("low_support_mu_rho", float(args.mu) * 0.72, float(args.rho) * 0.78, float(args.eta) * 1.5),
    ]
    out: list[CounterfactualCheck] = []
    for name, mu, rho, eta in cases:
        t = triplet_broadband_transmission(freq, mu, rho, eta, f_ref=float(args.freq_ref))
        m = compute_metrics(t, inside_mask, outside_mask, float(args.pass_threshold))
        out.append(
            CounterfactualCheck(
                name=name,
                mu=float(mu),
                rho=float(rho),
                eta=float(eta),
                fullband_pass=bool(_is_fullband_pass(m, args)),
                pass_ratio=float(m.pass_ratio),
                min_transmission=float(m.min_transmission),
            )
        )
    return out


def run_robustness_scan(
    freq: np.ndarray,
    inside_mask: np.ndarray,
    outside_mask: np.ndarray,
    args: argparse.Namespace,
) -> dict[str, Any]:
    scale = float(args.robust_delta)
    deltas = [-scale, 0.0, scale]
    passes = []
    rows = []
    for d_mu in deltas:
        for d_rho in deltas:
            for d_eta in deltas:
                mu = float(args.mu) * (1.0 + d_mu)
                rho = float(args.rho) * (1.0 + d_rho)
                eta = float(args.eta) * (1.0 + d_eta)
                t = triplet_broadband_transmission(freq, mu, rho, eta, f_ref=float(args.freq_ref))
                m = compute_metrics(t, inside_mask, outside_mask, float(args.pass_threshold))
                ok = _is_fullband_pass(m, args)
                passes.append(1.0 if ok else 0.0)
                rows.append(
                    {
                        "mu": mu,
                        "rho": rho,
                        "eta": eta,
                        "pass_ratio": float(m.pass_ratio),
                        "min_transmission": float(m.min_transmission),
                        "fullband_pass": bool(ok),
                    }
                )
    pass_rate = float(np.mean(np.array(passes, dtype=float)))
    return {
        "delta_fraction": scale,
        "samples": rows,
        "scan_pass_rate": pass_rate,
        "scan_pass": bool(pass_rate >= float(args.robust_pass_ratio_min)),
    }


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    freq = np.linspace(float(args.freq_min), float(args.freq_max), int(args.points))
    if not np.all(np.diff(freq) > 0.0):
        raise ValueError("Frequency axis must be strictly increasing.")

    inside_mask = (freq >= float(args.window_min)) & (freq <= float(args.window_max))
    outside_mask = ~inside_mask

    glass_t = glass_like_transmission(freq, float(args.window_min), float(args.window_max))
    triplet_t = triplet_broadband_transmission(
        freq,
        float(args.mu),
        float(args.rho),
        float(args.eta),
        f_ref=float(args.freq_ref),
    )

    pass_th = float(args.pass_threshold)
    glass_m = compute_metrics(glass_t, inside_mask, outside_mask, pass_th)
    triplet_m = compute_metrics(triplet_t, inside_mask, outside_mask, pass_th)

    fullband_pass = _is_fullband_pass(triplet_m, args)
    distinct_from_glass = (
        triplet_m.outside_window_pass_ratio - glass_m.outside_window_pass_ratio
        >= float(args.outside_pass_advantage_min)
    )
    counterfactuals = run_counterfactual_expected_fail(freq, inside_mask, outside_mask, args)
    expected_fail_pass = all(not c.fullband_pass for c in counterfactuals)
    robust = run_robustness_scan(freq, inside_mask, outside_mask, args)
    script_level_seated = bool(fullband_pass and distinct_from_glass and expected_fail_pass and robust["scan_pass"])

    return {
        "meta": {
            "suite": "ripple_triplet_fullband_transparency_audit",
            "frequency_unit": args.frequency_unit,
            "axis": {
                "freq_min": float(args.freq_min),
                "freq_max": float(args.freq_max),
                "points": int(args.points),
            },
            "glass_window": {"min": float(args.window_min), "max": float(args.window_max)},
            "thresholds": {
                "pass_threshold": pass_th,
                "fullband_ratio_min": float(args.fullband_ratio_min),
                "min_transmission_floor": float(args.min_transmission_floor),
                "outside_pass_advantage_min": float(args.outside_pass_advantage_min),
                "robust_delta": float(args.robust_delta),
                "robust_pass_ratio_min": float(args.robust_pass_ratio_min),
            },
            "model_note": (
                "Glass reference uses smooth band-pass envelope; triplet medium uses weak-loss "
                "broadband attenuation transform from (mu, rho, eta)."
            ),
        },
        "triplet_input": {"mu": float(args.mu), "rho": float(args.rho), "eta": float(args.eta)},
        "metrics": {
            "glass_like": asdict(glass_m),
            "triplet_medium": asdict(triplet_m),
        },
        "verdict": {
            "triplet_fullband_pass": bool(fullband_pass),
            "triplet_distinct_from_glass_window": bool(distinct_from_glass),
            "expected_fail_checks_pass": bool(expected_fail_pass),
            "robustness_scan_pass": bool(robust["scan_pass"]),
            "script_level_seated": script_level_seated,
            "final_pass": script_level_seated,
        },
        "counterfactual_expected_fail": [asdict(c) for c in counterfactuals],
        "robustness_scan": robust,
        "curves": {
            "freq": freq.tolist(),
            "glass_like_transmission": glass_t.tolist(),
            "triplet_transmission": triplet_t.tolist(),
        },
    }


def write_outputs(payload: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    p_json = out_dir / "RIPPLE_TRIPLET_FULLBAND_AUDIT.json"
    p_md = out_dir / "RIPPLE_TRIPLET_FULLBAND_AUDIT_SUMMARY.md"
    p_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    gm = payload["metrics"]["glass_like"]
    tm = payload["metrics"]["triplet_medium"]
    vd = payload["verdict"]
    lines = [
        "# Triplet Full-band Transparency Audit",
        "",
        f"- triplet: mu={payload['triplet_input']['mu']:.6f}, rho={payload['triplet_input']['rho']:.6f}, eta={payload['triplet_input']['eta']:.6f}",
        f"- glass window: [{payload['meta']['glass_window']['min']:.3f}, {payload['meta']['glass_window']['max']:.3f}] {payload['meta']['frequency_unit']}",
        "",
        "## Metrics",
        f"- glass outside-window pass ratio: `{gm['outside_window_pass_ratio']:.4f}`",
        f"- triplet outside-window pass ratio: `{tm['outside_window_pass_ratio']:.4f}`",
        f"- triplet min transmission: `{tm['min_transmission']:.4f}`",
        f"- triplet global pass ratio: `{tm['pass_ratio']:.4f}`",
        "",
        "## Verdict",
        f"- triplet_fullband_pass: **{vd['triplet_fullband_pass']}**",
        f"- triplet_distinct_from_glass_window: **{vd['triplet_distinct_from_glass_window']}**",
        f"- expected_fail_checks_pass: **{vd['expected_fail_checks_pass']}**",
        f"- robustness_scan_pass: **{vd['robustness_scan_pass']}**",
        f"- script_level_seated: **{vd['script_level_seated']}**",
        f"- final_pass: **{vd['final_pass']}**",
    ]
    p_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Triplet medium full-band transparency audit.")
    ap.add_argument("--mu", type=float, default=DEFAULT_TRIPLET["mu"])
    ap.add_argument("--rho", type=float, default=DEFAULT_TRIPLET["rho"])
    ap.add_argument("--eta", type=float, default=DEFAULT_TRIPLET["eta"])

    ap.add_argument("--freq-min", type=float, default=DEFAULT_FREQ_MIN)
    ap.add_argument("--freq-max", type=float, default=DEFAULT_FREQ_MAX)
    ap.add_argument("--points", type=int, default=DEFAULT_POINTS)
    ap.add_argument("--frequency-unit", type=str, default="THz-equivalent")
    ap.add_argument("--freq-ref", type=float, default=100.0)

    ap.add_argument("--window-min", type=float, default=GLASS_WIN_MIN)
    ap.add_argument("--window-max", type=float, default=GLASS_WIN_MAX)

    ap.add_argument("--pass-threshold", type=float, default=0.75)
    ap.add_argument("--fullband-ratio-min", type=float, default=0.95)
    ap.add_argument("--min-transmission-floor", type=float, default=0.62)
    ap.add_argument("--outside-pass-advantage-min", type=float, default=0.65)
    ap.add_argument("--robust-delta", type=float, default=0.05, help="Relative +-delta scan on mu/rho/eta.")
    ap.add_argument("--robust-pass-ratio-min", type=float, default=0.80, help="Minimum pass ratio over robustness scan.")

    ap.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ripple_triplet_fullband_transparency_audit",
    )
    args = ap.parse_args()

    if args.freq_max <= args.freq_min:
        raise ValueError("--freq-max must be greater than --freq-min.")
    if args.window_max <= args.window_min:
        raise ValueError("--window-max must be greater than --window-min.")
    if args.points < 64:
        raise ValueError("--points must be at least 64.")
    if not (0.0 < args.pass_threshold <= 1.0):
        raise ValueError("--pass-threshold must be in (0, 1].")

    payload = run_audit(args)
    write_outputs(payload, Path(args.out_dir))
    print("wrote", Path(args.out_dir, "RIPPLE_TRIPLET_FULLBAND_AUDIT.json").as_posix())
    print("wrote", Path(args.out_dir, "RIPPLE_TRIPLET_FULLBAND_AUDIT_SUMMARY.md").as_posix())
    print("final_pass:", payload["verdict"]["final_pass"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
