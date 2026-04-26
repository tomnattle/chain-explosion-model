#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path("artifacts")
DERIVED = ROOT / "ripple_quantum_tests_v3_derived" / "RIPPLE_QUANTUM_TESTS_V3_RESULTS.json"
CALIB = ROOT / "ripple_quantum_tests_v3_calibrated" / "RIPPLE_QUANTUM_TESTS_V3_RESULTS.json"
OUT_DIR = ROOT / "ripple_quantum_tests_v3"


def load_results(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["name"]: row for row in data["results"]}


def pass01(v: bool) -> int:
    return 1 if v else 0


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load_results(DERIVED)
    c = load_results(CALIB)

    tests = ["laser_threshold", "semiconductor_cutoff", "mri_larmor", "atomic_clock_modes"]
    labels = ["Laser", "Semiconductor", "MRI", "Atomic clock"]

    x = np.arange(len(tests))
    w = 0.34

    fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.2), dpi=150)

    # Top: nrmse comparison
    nrmse_d = [d[t]["nrmse"] for t in tests]
    nrmse_c = [c[t]["nrmse"] for t in tests]
    ax0 = axes[0]
    ax0.bar(x - w / 2, nrmse_d, w, label="derived", color="#e74c3c")
    ax0.bar(x + w / 2, nrmse_c, w, label="calibrated", color="#3498db")
    ax0.axhline(0.18, color="#7f8c8d", ls="--", lw=1.0, label="shape threshold=0.18")
    ax0.set_xticks(x, labels)
    ax0.set_ylabel("NRMSE")
    ax0.set_title("v3 curve-shape error comparison")
    ax0.grid(alpha=0.25, axis="y")
    ax0.legend(fontsize=8)

    # Bottom: pass matrix (final pass emphasis)
    ax1 = axes[1]
    y_d = [pass01(d[t]["final_pass"]) for t in tests]
    y_c = [pass01(c[t]["final_pass"]) for t in tests]
    ax1.bar(x - w / 2, y_d, w, label="derived final_pass", color="#c0392b")
    ax1.bar(x + w / 2, y_c, w, label="calibrated final_pass", color="#2980b9")
    ax1.set_yticks([0, 1], ["fail", "pass"])
    ax1.set_ylim(-0.05, 1.15)
    ax1.set_xticks(x, labels)
    ax1.set_title("v3 final pass (shape AND constant)")
    ax1.grid(alpha=0.25, axis="y")
    ax1.legend(fontsize=8, loc="upper right")

    for i, t in enumerate(tests):
        ax1.text(
            x[i] - w / 2,
            y_d[i] + 0.03,
            f"S:{'Y' if d[t]['shape_pass'] else 'N'} C:{'Y' if d[t]['constant_pass'] else 'N'}",
            ha="center",
            va="bottom",
            fontsize=7,
            color="#7b241c",
        )
        ax1.text(
            x[i] + w / 2,
            y_c[i] + 0.03,
            f"S:{'Y' if c[t]['shape_pass'] else 'N'} C:{'Y' if c[t]['constant_pass'] else 'N'}",
            ha="center",
            va="bottom",
            fontsize=7,
            color="#1b4f72",
        )

    fig.suptitle("Ripple tests v3: Derived vs Calibrated (intuitive view)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    png = OUT_DIR / "RIPPLE_QUANTUM_TESTS_V3_MODE_COMPARISON.png"
    fig.savefig(png, dpi=170)
    plt.close(fig)
    print("wrote", png)


if __name__ == "__main__":
    main()
