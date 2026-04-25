#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate a quick-look Bell threshold figure for S=2.828"
    )
    ap.add_argument("--s-value", type=float, default=2.828)
    ap.add_argument("--lhv-bound", type=float, default=2.0)
    ap.add_argument("--tsirelson-bound", type=float, default=2.8284271247461903)
    ap.add_argument("--x-min", type=float, default=1.6)
    ap.add_argument("--x-max", type=float, default=3.0)
    ap.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ghz_threshold_experiment",
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    s_value = float(args.s_value)
    lhv = float(args.lhv_bound)
    ts = float(args.tsirelson_bound)

    fig, ax = plt.subplots(figsize=(9.4, 4.2))

    ax.axvspan(args.x_min, lhv, alpha=0.18, color="#999999", label="Classical region (S <= 2)")
    ax.axvspan(lhv, ts, alpha=0.15, color="#4daf4a", label="Quantum-allowed region (2 < S <= 2.828)")
    ax.axvspan(ts, args.x_max, alpha=0.12, color="#e41a1c", label="Beyond Tsirelson bound")

    ax.axvline(lhv, color="#666666", ls="--", lw=1.8)
    ax.axvline(ts, color="#984ea3", ls="--", lw=1.8)
    ax.axvline(s_value, color="#1f78b4", ls="-", lw=2.6)

    ax.scatter([s_value], [0.5], s=80, color="#1f78b4", zorder=5)
    ax.annotate(
        f"Observed S = {s_value:.3f}",
        xy=(s_value, 0.5),
        xytext=(18, 22),
        textcoords="offset points",
        fontsize=10,
        arrowprops={"arrowstyle": "->", "lw": 1.0},
    )
    ax.annotate("LHV bound = 2", xy=(lhv, 0.15), xytext=(8, -18), textcoords="offset points", fontsize=9)
    ax.annotate(
        "Tsirelson bound = 2.828",
        xy=(ts, 0.15),
        xytext=(8, -18),
        textcoords="offset points",
        fontsize=9,
    )

    ax.set_xlim(float(args.x_min), float(args.x_max))
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("Bell/CHSH value S")
    ax.set_title("Quick-look interpretation of S = 2.828")
    ax.grid(axis="x", alpha=0.25, linestyle="--")
    ax.legend(loc="upper left", fontsize=8, frameon=True)
    fig.tight_layout()

    out_png = out_dir / "bell_s_2828_quicklook.png"
    fig.savefig(out_png, dpi=180)
    plt.close(fig)

    out_txt = out_dir / "bell_s_2828_quicklook_caption.txt"
    out_txt.write_text(
        (
            "Observed S=2.828 is above the classical LHV bound (2.0), "
            "within the quantum-allowed interval (2.0, 2.828], "
            "and clearly below the Tsirelson limit."
        ),
        encoding="utf-8",
    )

    print(str(out_png).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
