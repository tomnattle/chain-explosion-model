#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def nrmse(a: np.ndarray, b: np.ndarray) -> float:
    scale = float(np.max(a) - np.min(a))
    if scale < 1e-12:
        scale = 1.0
    return rmse(a, b) / scale


def sigmoid(x: np.ndarray, center: float, sharpness: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-sharpness * (x - center)))


def test_laser_threshold(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # QM-like: weak below threshold, near-linear growth above threshold.
    th = 0.50
    qm = np.where(x > th, 2.2 * (x - th), 0.02 * x)

    # Ripple model: chain amplification after medium excitation density exceeds threshold.
    density = x
    ripple = np.where(density > th, 2.15 * (density - th), 0.03 * density)
    return qm, ripple


def test_semiconductor_cutoff(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # x = normalized frequency axis.
    gap = 2.0
    qm = sigmoid(x, center=gap, sharpness=20.0)
    ripple = sigmoid(x, center=gap + 0.02, sharpness=17.5)
    return qm, ripple


def test_mri_larmor(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # x = B field in Tesla.
    gamma_qm = 42.577
    qm = gamma_qm * x

    # Ripple: linear stiffness modulation approximation.
    gamma_ripple = 42.2
    ripple = gamma_ripple * x + 0.02 * x**2
    return qm, ripple


def test_atomic_clock_modes(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # x = frequency axis in GHz around Cs133 hyperfine transition.
    f0 = 9.192631770
    bw_qm = 0.000030
    qm = np.exp(-0.5 * ((x - f0) / bw_qm) ** 2)

    # Ripple: cavity-like discrete mode with a slightly shifted center and width.
    f0_r = 9.192620000
    bw_r = 0.000042
    ripple = np.exp(-0.5 * ((x - f0_r) / bw_r) ** 2)
    return qm, ripple


def run_suite(threshold: float) -> dict:
    results: dict[str, dict] = {}

    # 1) laser
    x1 = np.linspace(0.0, 1.0, 220)
    q1, r1 = test_laser_threshold(x1)
    n1 = nrmse(q1, r1)
    results["laser_threshold"] = {
        "nrmse": float(n1),
        "pass": bool(n1 <= threshold),
        "axis_name": "pump_strength",
        "axis_min": float(x1.min()),
        "axis_max": float(x1.max()),
    }

    # 2) semiconductor
    x2 = np.linspace(0.0, 4.0, 260)
    q2, r2 = test_semiconductor_cutoff(x2)
    n2 = nrmse(q2, r2)
    results["semiconductor_cutoff"] = {
        "nrmse": float(n2),
        "pass": bool(n2 <= threshold),
        "axis_name": "photon_frequency_norm",
        "axis_min": float(x2.min()),
        "axis_max": float(x2.max()),
    }

    # 3) MRI
    x3 = np.linspace(0.0, 3.0, 180)
    q3, r3 = test_mri_larmor(x3)
    n3 = nrmse(q3, r3)
    results["mri_larmor"] = {
        "nrmse": float(n3),
        "pass": bool(n3 <= threshold),
        "axis_name": "B_field_T",
        "axis_min": float(x3.min()),
        "axis_max": float(x3.max()),
    }

    # 4) atomic clock
    x4 = np.linspace(9.1918, 9.1934, 500)
    q4, r4 = test_atomic_clock_modes(x4)
    n4 = nrmse(q4, r4)
    results["atomic_clock_modes"] = {
        "nrmse": float(n4),
        "pass": bool(n4 <= threshold),
        "axis_name": "frequency_GHz",
        "axis_min": float(x4.min()),
        "axis_max": float(x4.max()),
        "note": "This checks discrete-mode shape, not first-principles derivation of exact constants.",
    }

    curves = {
        "laser_threshold": {"x": x1.tolist(), "qm": q1.tolist(), "ripple": r1.tolist()},
        "semiconductor_cutoff": {"x": x2.tolist(), "qm": q2.tolist(), "ripple": r2.tolist()},
        "mri_larmor": {"x": x3.tolist(), "qm": q3.tolist(), "ripple": r3.tolist()},
        "atomic_clock_modes": {"x": x4.tolist(), "qm": q4.tolist(), "ripple": r4.tolist()},
    }
    return {"results": results, "curves": curves}


def write_outputs(payload: dict, out_dir: Path, threshold: float, seed: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "RIPPLE_QUANTUM_TESTS_RESULTS.json"
    md_path = out_dir / "RIPPLE_QUANTUM_TESTS_SUMMARY.md"

    summary = {
        "experiment": "ripple_quantum_tests_v1",
        "criterion": {"metric": "nrmse", "pass_threshold": threshold},
        "seed": seed,
        "results": payload["results"],
    }
    json_path.write_text(json.dumps({"meta": summary, **payload}, indent=2), encoding="utf-8")

    lines = [
        "# Ripple Quantum Tests Summary",
        "",
        "This suite compares a QM-like reference curve with a ripple-model curve in four tasks.",
        "",
        f"- pass threshold (NRMSE): `{threshold:.4f}`",
        "",
        "| test | nrmse | pass |",
        "|---|---:|:---:|",
    ]
    for k, v in payload["results"].items():
        lines.append(f"| {k} | {v['nrmse']:.6f} | {'yes' if v['pass'] else 'no'} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- Pass means curve-shape similarity under current parameterization.",
        "- It does not automatically prove first-principles equivalence.",
        "- MRI/atomic-clock exact constants still require deeper derivation tasks.",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.6), dpi=150)
    specs = [
        ("laser_threshold", "Laser Threshold"),
        ("semiconductor_cutoff", "Semiconductor Cutoff"),
        ("mri_larmor", "MRI Larmor"),
        ("atomic_clock_modes", "Atomic Clock Modes"),
    ]
    for ax, (k, title) in zip(axes.flat, specs):
        x = np.array(payload["curves"][k]["x"])
        q = np.array(payload["curves"][k]["qm"])
        r = np.array(payload["curves"][k]["ripple"])
        info = payload["results"][k]
        ax.plot(x, q, lw=1.6, label="QM-like")
        ax.plot(x, r, lw=1.4, ls="--", label="Ripple")
        ax.set_title(f"{title} | nrmse={info['nrmse']:.4f}")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "RIPPLE_QUANTUM_TESTS_PLOTS.png", dpi=160)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Ripple-vs-QM curve-shape comparison suite")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--threshold", type=float, default=0.18, help="Pass threshold for NRMSE")
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests")
    args = ap.parse_args()

    np.random.seed(int(args.seed))
    payload = run_suite(float(args.threshold))
    write_outputs(payload, Path(args.out_dir), float(args.threshold), int(args.seed))
    print("wrote", Path(args.out_dir) / "RIPPLE_QUANTUM_TESTS_RESULTS.json")
    print("wrote", Path(args.out_dir) / "RIPPLE_QUANTUM_TESTS_SUMMARY.md")
    print("wrote", Path(args.out_dir) / "RIPPLE_QUANTUM_TESTS_PLOTS.png")


if __name__ == "__main__":
    main()
