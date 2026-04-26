#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent / "figures"


def load_results(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def branch_payloads() -> dict[str, dict]:
    return {
        "v6_default": load_results(ROOT / "artifacts/ripple_quantum_tests_v6/RIPPLE_QUANTUM_TESTS_V6_RESULTS.json"),
        "v6_derived_fail": load_results(
            ROOT / "artifacts/ripple_quantum_tests_v6_derived_v2/RIPPLE_QUANTUM_TESTS_V6_RESULTS.json"
        ),
        "v6_derived_alpha0": load_results(
            ROOT / "artifacts/ripple_quantum_tests_v6_derived_alpha0/RIPPLE_QUANTUM_TESTS_V6_RESULTS.json"
        ),
    }


def fig_branch_metrics(payloads: dict[str, dict]) -> None:
    tests = ["laser_threshold", "semiconductor_cutoff", "mri_larmor", "atomic_clock_modes"]
    labels = ["Laser", "Semi", "MRI", "Atomic"]
    branch_names = list(payloads.keys())
    colors = ["#2ecc71", "#e74c3c", "#3498db"]

    # build matrix nrmse_y
    mat = np.zeros((len(branch_names), len(tests)))
    pass_flags = np.zeros_like(mat)
    for bi, b in enumerate(branch_names):
        per = {r["name"]: r for r in payloads[b]["per_test"]}
        for ti, t in enumerate(tests):
            mat[bi, ti] = float(per[t]["nrmse_y"])
            pass_flags[bi, ti] = 1.0 if per[t]["shape_pass"] else 0.0

    x = np.arange(len(tests))
    w = 0.25
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.2), dpi=150, sharex=True)

    for bi, b in enumerate(branch_names):
        axes[0].bar(x + (bi - 1) * w, mat[bi], width=w, label=b, color=colors[bi], alpha=0.9)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("nrmse_y (log scale)")
    axes[0].set_title("Branch comparison: shape error by test")
    axes[0].grid(alpha=0.25, axis="y")
    axes[0].legend(fontsize=8)

    for bi, b in enumerate(branch_names):
        axes[1].bar(x + (bi - 1) * w, pass_flags[bi], width=w, label=b, color=colors[bi], alpha=0.9)
    axes[1].set_yticks([0, 1], ["N", "Y"])
    axes[1].set_ylim(-0.05, 1.15)
    axes[1].set_ylabel("shape_ok")
    axes[1].set_title("Branch comparison: per-test shape gate")
    axes[1].set_xticks(x, labels)
    axes[1].grid(alpha=0.25, axis="y")

    fig.tight_layout()
    fig.savefig(OUT / "fig_branch_metrics.png", dpi=170)
    plt.close(fig)


def fig_shared_params(payloads: dict[str, dict]) -> None:
    keys = ["mu", "rho", "eta", "wave_speed_m_s"]
    labels = [r"$\mu$", r"$\rho$", r"$\eta$", "v (m/s)"]
    branch_names = list(payloads.keys())
    colors = ["#2ecc71", "#e74c3c", "#3498db"]

    vals = []
    for b in branch_names:
        sp = payloads[b]["shared_parameters"]
        vals.append(
            [
                float(sp["mu"]),
                float(sp["rho"]),
                float(sp["eta"]),
                float(sp.get("wave_speed_m_s", 299792458.0)),
            ]
        )
    arr = np.array(vals)

    # normalize first three by reference branch to show drift
    norm = arr.copy()
    norm[:, :3] = norm[:, :3] / np.maximum(arr[0, :3], 1e-12)
    norm[:, 3] = norm[:, 3] / 299792458.0

    x = np.arange(len(keys))
    w = 0.25
    fig, ax = plt.subplots(figsize=(9.6, 4.6), dpi=150)
    for i, b in enumerate(branch_names):
        ax.bar(x + (i - 1) * w, norm[i], width=w, color=colors[i], label=b)
    ax.axhline(1.0, color="#7f8c8d", ls="--", lw=1.0)
    ax.set_xticks(x, labels)
    ax.set_ylabel("normalized to v6_default")
    ax.set_title("Shared-parameter drift across branches")
    ax.grid(alpha=0.25, axis="y")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_shared_parameter_drift.png", dpi=170)
    plt.close(fig)


def fig_stress_1d(csv_path: Path) -> None:
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    if not rows:
        return

    alpha = np.array([float(r["alpha"]) for r in rows], dtype=float)
    loss_c = np.array([float(r["loss_coarse"]) for r in rows], dtype=float)
    loss_f = np.array([float(r["loss_final"]) for r in rows], dtype=float)
    pass_c = np.array([float(r["joint_pass_coarse"]) for r in rows], dtype=float)
    pass_f = np.array([float(r["joint_pass_final"]) for r in rows], dtype=float)

    fig, axes = plt.subplots(2, 1, figsize=(9.5, 6.4), dpi=150, sharex=True)
    axes[0].plot(alpha, loss_c, "o-", ms=3, lw=1.0, color="#c0392b", label="coarse")
    axes[0].plot(alpha, loss_f, "s--", ms=3, lw=1.0, color="#f39c12", label="after refine")
    axes[0].set_yscale("log")
    axes[0].set_ylabel("joint loss")
    axes[0].set_title("Stress 1D: alpha sweep and refine effect")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.25, axis="y")

    axes[1].step(alpha, pass_c, where="mid", color="#7fb3d5", label="coarse pass")
    axes[1].step(alpha, pass_f, where="mid", color="#27ae60", label="final pass")
    axes[1].set_ylim(-0.05, 1.1)
    axes[1].set_yticks([0, 1], ["N", "Y"])
    axes[1].set_xlabel(r"$\alpha$")
    axes[1].set_ylabel("joint_pass")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25, axis="y")

    fig.tight_layout()
    fig.savefig(OUT / "fig_stress_refine_effect.png", dpi=170)
    plt.close(fig)


def fig_pipeline_diagram() -> None:
    fig, ax = plt.subplots(figsize=(11, 3.6), dpi=150)
    ax.axis("off")
    boxes = [
        (0.03, 0.35, 0.2, 0.3, "Toy references\n(4 panels)"),
        (0.28, 0.35, 0.2, 0.3, "Joint params\n(mu,rho,eta,bw)"),
        (0.53, 0.35, 0.2, 0.3, "Metrics + gates\nnrmse_x/y, R²"),
        (0.78, 0.35, 0.19, 0.3, "joint_pass +\nstress/refine"),
    ]
    for x, y, w, h, txt in boxes:
        rect = plt.Rectangle((x, y), w, h, facecolor="#ecf0f1", edgecolor="#34495e", linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=10)
    for x0 in [0.23, 0.48, 0.73]:
        ax.annotate("", xy=(x0 + 0.04, 0.5), xytext=(x0, 0.5), arrowprops=dict(arrowstyle="->", lw=1.3))
    ax.set_title("v6-joint audit pipeline (publication-facing schematic)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_v6_pipeline_schematic.png", dpi=170)
    plt.close(fig)


def copy_reference_figures() -> None:
    src_map = {
        "fig_joint_2x2_default.png": ROOT / "artifacts/ripple_quantum_tests_v6/RIPPLE_V6_JOINT_2x2.png",
        "fig_joint_2x2_derived_fail.png": ROOT / "artifacts/ripple_quantum_tests_v6_derived_v2/RIPPLE_V6_JOINT_2x2.png",
        "fig_joint_2x2_derived_alpha0.png": ROOT / "artifacts/ripple_quantum_tests_v6_derived_alpha0/RIPPLE_V6_JOINT_2x2.png",
        "fig_stress_2d_demo.png": ROOT / "artifacts/ripple_quantum_tests_v6_stress_2d_demo/RIPPLE_V6_STRESS_2D.png",
    }
    for dst_name, src in src_map.items():
        if src.exists():
            shutil.copy2(src, OUT / dst_name)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    payloads = branch_payloads()
    fig_branch_metrics(payloads)
    fig_shared_params(payloads)
    fig_pipeline_diagram()
    copy_reference_figures()
    csv_1d = ROOT / "artifacts/ripple_quantum_tests_v6_refine_demo/RIPPLE_V6_STRESS_ALPHA.csv"
    if csv_1d.exists():
        fig_stress_1d(csv_1d)
    print("wrote figures to", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

