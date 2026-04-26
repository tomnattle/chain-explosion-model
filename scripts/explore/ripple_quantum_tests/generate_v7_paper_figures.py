#!/usr/bin/env python3
"""Generate v7 rigidity / counterfactual / seed figures from archived JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        default="artifacts/ripple_quantum_tests_v7_three/RIPPLE_V7_THREE_RESULTS.json",
    )
    parser.add_argument(
        "--out-dir",
        default="papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/figures",
    )
    args = parser.parse_args()
    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rob = data["robustness"]
    cf = data["counterfactual"]
    ss = data["seed_stability"]

    # Fig 1: rigidity pass rates
    fig, ax = plt.subplots(figsize=(6.5, 4), dpi=160)
    labels = ["Local\n27/27", "Random\n18/20"]
    rates = [rob["local_pass_rate"], rob["random_pass_rate"]]
    colors = ["#2563eb", "#7c3aed"]
    ax.bar(labels, rates, color=colors, edgecolor="#1e293b", linewidth=1)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Pass rate")
    ax.set_title("v7 Parameter rigidity scans")
    for i, v in enumerate(rates):
        ax.text(i, v + 0.03, f"{v:.0%}", ha="center", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p1 = out_dir / "v7_fig01_rigidity_pass_rates.png"
    fig.savefig(p1)
    plt.close(fig)

    # Fig 2: counterfactual NRMSE (should fail)
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=160)
    names = [r["name"].replace("cf_", "") for r in cf["rows"]]
    vals = [r["nrmse_y"] for r in cf["rows"]]
    x = np.arange(len(names))
    ax.bar(x, vals, color="#dc2626", edgecolor="#7f1d1d")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=18, ha="right")
    ax.set_ylabel("NRMSE (spin branch)")
    ax.set_title("v7 Counterfactual suite (expected fail)")
    ax.axhline(0.18, color="#64748b", linestyle="--", label="gate ref (0.18)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p2 = out_dir / "v7_fig02_counterfactual_nrmse.png"
    fig.savefig(p2)
    plt.close(fig)

    # Fig 3: seed stability
    fig, ax = plt.subplots(figsize=(7.2, 4), dpi=160)
    seeds = [r["seed"] for r in ss["rows"]]
    nrmse = [r["nrmse_y"] for r in ss["rows"]]
    ax.plot(seeds, nrmse, "o-", color="#059669", linewidth=2, markersize=7)
    ax.set_xlabel("RNG seed")
    ax.set_ylabel("spin_cos2 NRMSE")
    ax.set_title("v7 Monte Carlo seed stability (7 seeds)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p3 = out_dir / "v7_fig03_seed_stability.png"
    fig.savefig(p3)
    plt.close(fig)

    print("Wrote:", p1.as_posix())
    print("Wrote:", p2.as_posix())
    print("Wrote:", p3.as_posix())


if __name__ == "__main__":
    main()
