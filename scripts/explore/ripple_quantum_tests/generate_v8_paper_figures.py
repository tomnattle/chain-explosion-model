#!/usr/bin/env python3
"""
Generate v8 publication figures for merged v7+v8 manuscript.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

import ripple_quantum_tests_v8_unify as v8


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def plot_radial_levels(out_dir: Path) -> str:
    n = np.arange(1, 6)
    y_qm = v8.hydrogen_levels_qm(n)
    y_r = v8.radial_standing_wave_ripple(n, v8.MU_REF, v8.RHO_REF, v8.ETA_REF)
    y_qm_n = y_qm / y_qm[0]
    y_r_n = y_r / y_r[0]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=160)
    ax.plot(n, y_qm_n, "o-", linewidth=2, label="QM ref (1/n^2)")
    ax.plot(n, y_r_n, "s--", linewidth=2, label="Ripple (locked)")
    ax.set_xlabel("Level n")
    ax.set_ylabel("Normalized level")
    ax.set_title("v8 Radial Standing-Wave Levels")
    ax.grid(alpha=0.3)
    ax.legend()
    out = out_dir / "v8_fig01_radial_levels.png"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out.name


def plot_decoherence(out_dir: Path) -> str:
    t = np.linspace(0, 10, 200)
    sigma = 0.5
    y_qm = v8.decoherence_qm(t, sigma)
    y_r = v8.decoherence_ripple(t, sigma, v8.MU_REF, v8.RHO_REF, v8.ETA_REF)

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=160)
    ax.plot(t, y_qm, linewidth=2, label="QM ref")
    ax.plot(t, y_r, "--", linewidth=2, label="Ripple (locked)")
    ax.set_xlabel("Time t")
    ax.set_ylabel("Coherence")
    ax.set_title("v8 Environment Decoherence")
    ax.grid(alpha=0.3)
    ax.legend()
    out = out_dir / "v8_fig02_decoherence.png"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out.name


def plot_compton(out_dir: Path) -> str:
    th = np.linspace(0, np.pi, 200)
    y_qm = v8.compton_shift_qm(th)
    y_lock = v8.compton_shift_ripple(th, v8.MU_REF, v8.RHO_REF, v8.ETA_REF)
    y_cf = v8.compton_shift_ripple(th, v8.MU_REF, v8.RHO_REF, 0.001)

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=160)
    ax.plot(th, y_qm, linewidth=2, label="QM ref")
    ax.plot(th, y_lock, "--", linewidth=2, label="Ripple locked")
    ax.plot(th, y_cf, ":", linewidth=2.4, label="Counterfactual eta=0.001")
    ax.set_xlabel("Scattering angle theta (rad)")
    ax.set_ylabel("Normalized shift")
    ax.set_title("v8 Compton-Style Shift and Counterfactual")
    ax.grid(alpha=0.3)
    ax.legend()
    out = out_dir / "v8_fig03_compton_counterfactual.png"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out.name


def plot_hardening_summary(out_dir: Path, payload_path: Path) -> str:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    rounds = payload["multi_round_hardening"]["rounds"]
    x = np.array([r["round"] for r in rounds], dtype=int)
    y = np.array([1 if r["round_pass"] else 0 for r in rounds], dtype=int)

    fig, ax = plt.subplots(figsize=(8, 3.8), dpi=160)
    ax.plot(x, y, linewidth=1.8, marker="o", markersize=3.5)
    ax.set_ylim(-0.1, 1.1)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["FAIL", "PASS"])
    ax.set_xlabel("Hardening round")
    ax.set_ylabel("Round status")
    ax.set_title("v8 Multi-round Hardening Audit (100 rounds)")
    ax.grid(alpha=0.3)
    out = out_dir / "v8_fig04_hardening_rounds.png"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out.name


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate v8 manuscript figures.")
    parser.add_argument(
        "--out-dir",
        default="papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/figures",
    )
    parser.add_argument(
        "--v8-json",
        default="artifacts/ripple_quantum_tests_v8_unify/v8_quantum_grand_unification.json",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    payload_path = Path(args.v8_json)
    _ensure_dir(out_dir)

    created = [
        plot_radial_levels(out_dir),
        plot_decoherence(out_dir),
        plot_compton(out_dir),
        plot_hardening_summary(out_dir, payload_path),
    ]

    print("Generated figures:")
    for name in created:
        print(f"- {out_dir.as_posix()}/{name}")


if __name__ == "__main__":
    main()
