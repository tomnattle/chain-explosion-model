#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def build_curve(
    f_min: float,
    f_max: float,
    points: int,
    retention_at_f_max: float,
    shape_alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build a monotone cost-benefit curve:
    - x: target F in [f_min, f_max]
    - y: retained sample ratio in [retention_at_f_max, 1]
    Boundary conditions:
    - at F=f_min, retention=1.0
    - at F=f_max, retention=retention_at_f_max
    """
    x = np.linspace(f_min, f_max, points)
    t = (x - f_min) / max(1e-12, (f_max - f_min))
    y = 1.0 - (1.0 - retention_at_f_max) * np.power(t, shape_alpha)
    return x, y


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Plot an illustrative GHZ cost-benefit curve from F=2.2 to F=4.0"
    )
    ap.add_argument("--f-min", type=float, default=2.2)
    ap.add_argument("--f-max", type=float, default=4.0)
    ap.add_argument("--points", type=int, default=80)
    ap.add_argument(
        "--retention-at-f-max",
        type=float,
        default=0.25,
        help="retained ratio at F=f_max (0.25 means 75%% discarded)",
    )
    ap.add_argument(
        "--shape-alpha",
        type=float,
        default=1.5,
        help="curve steepness; >1 means costs accelerate near high F",
    )
    ap.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ghz_threshold_experiment",
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    x, retention = build_curve(
        f_min=float(args.f_min),
        f_max=float(args.f_max),
        points=max(10, int(args.points)),
        retention_at_f_max=float(args.retention_at_f_max),
        shape_alpha=float(args.shape_alpha),
    )
    discard = 1.0 - retention

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.plot(x, retention * 100.0, color="#1f77b4", lw=2.2, label="retained sample ratio (%)")
    ax.plot(x, discard * 100.0, color="#d62728", lw=1.8, ls="--", label="discarded ratio (%)")

    ax.scatter([float(args.f_max)], [float(args.retention_at_f_max) * 100.0], color="#1f77b4", s=35, zorder=5)
    ax.annotate(
        f"F={args.f_max:.1f}, retained={args.retention_at_f_max*100:.0f}%",
        (float(args.f_max), float(args.retention_at_f_max) * 100.0),
        xytext=(-90, 18),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "lw": 0.9},
        fontsize=9,
    )

    ax.set_xlabel("Target GHZ score F")
    ax.set_ylabel("Sample ratio (%)")
    ax.set_title("Illustrative cost-benefit curve: higher F vs retained samples")
    ax.set_xlim(float(args.f_min), float(args.f_max))
    ax.set_ylim(0, 105)
    ax.grid(alpha=0.25, linestyle="--")
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()

    png_path = out_dir / "ghz_cost_benefit_curve_2p2_to_4p0.png"
    fig.savefig(png_path, dpi=180)
    plt.close(fig)

    csv_path = out_dir / "ghz_cost_benefit_curve_2p2_to_4p0.csv"
    csv_lines = ["F_target,retained_ratio,discarded_ratio"]
    for f, r, d in zip(x, retention, discard):
        csv_lines.append(f"{f:.6f},{r:.6f},{d:.6f}")
    csv_path.write_text("\n".join(csv_lines), encoding="utf-8")

    meta = {
        "type": "illustrative_curve",
        "f_range": [float(args.f_min), float(args.f_max)],
        "retention_anchor_at_f_max": float(args.retention_at_f_max),
        "discard_anchor_at_f_max": float(1.0 - args.retention_at_f_max),
        "shape_alpha": float(args.shape_alpha),
        "outputs": {
            "png": str(png_path).replace("\\", "/"),
            "csv": str(csv_path).replace("\\", "/"),
        },
        "note": "Illustrative curve anchored by user-specified trade-off, not direct experimental fit.",
    }
    (out_dir / "ghz_cost_benefit_curve_2p2_to_4p0.meta.json").write_text(
        json.dumps(meta, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
