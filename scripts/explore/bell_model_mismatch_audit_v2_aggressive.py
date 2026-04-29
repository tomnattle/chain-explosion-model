#!/usr/bin/env python3
"""
Bell model-mismatch audit v2 (aggressive).

Keeps v1 intact, but stresses geometry/sampling perturbations harder.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

import bell_model_mismatch_audit_v1 as v1

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "artifacts" / "bell_model_mismatch_audit_v2_aggressive"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEEDS = [7, 19, 42]
N_SYNTH = 15_000
CAPS_DEG = [12.0, 25.0, 35.0]
BIASES = [0.25, 0.45]
WIN_GRID = [0.0, 1.0, 3.0, 5.0, 9.0, 11.0, 15.0]


def mean_std(xs: list[float]) -> tuple[float, float]:
    arr = np.asarray(xs, dtype=float)
    return float(np.mean(arr)), float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0


def main() -> int:
    report: dict[str, Any] = {
        "audit": "bell_model_mismatch_audit_v2_aggressive",
        "base_version": "v1 kept unchanged",
        "seeds": SEEDS,
        "n_per_seed_synth": N_SYNTH,
        "experiments": {},
    }

    # baseline
    s_base = []
    n_base = []
    for sd in SEEDS:
        s, n = v1.run_synthetic(sd, N_SYNTH, kernel="point")
        s_base.append(s)
        n_base.append(n)
    mb, sb = mean_std(s_base)
    report["experiments"]["baseline_point"] = {
        "S_mean": mb,
        "S_std": sb,
        "valid_pairs_mean": float(np.mean(n_base)),
    }

    # aggressive geometry caps
    geo_rows = []
    for cap in CAPS_DEG:
        s_cap = []
        n_cap = []
        for sd in SEEDS:
            s, n = v1.run_synthetic(sd, N_SYNTH, kernel="surface", cap_deg=cap, bias=0.0)
            s_cap.append(s)
            n_cap.append(n)
        m, st = mean_std(s_cap)
        geo_rows.append(
            {
                "cap_deg": cap,
                "S_mean": m,
                "S_std": st,
                "valid_pairs_mean": float(np.mean(n_cap)),
                "delta_vs_baseline": m - mb,
            }
        )
    report["experiments"]["exp1_geometry_caps"] = geo_rows

    # aggressive sampling bias
    bias_rows = []
    for bz in BIASES:
        s_b = []
        n_b = []
        for sd in SEEDS:
            s, n = v1.run_synthetic(sd + 1000, N_SYNTH, kernel="point", bias=bz)
            s_b.append(s)
            n_b.append(n)
        m, st = mean_std(s_b)
        bias_rows.append(
            {
                "bias_z": bz,
                "S_mean": m,
                "S_std": st,
                "valid_pairs_mean": float(np.mean(n_b)),
                "delta_vs_baseline": m - mb,
            }
        )
    report["experiments"]["exp2_sampling_bias_levels"] = bias_rows

    # keep NIST window track from v1 data source logic
    win_rows = []
    src = None
    if v1.EVENTS_CSV.exists():
        src = str(v1.EVENTS_CSV)
        a, b = v1.load_nist_events()
        for w in WIN_GRID:
            pairs = v1.pair_events(a, b, w)
            s, n = v1.chsh_from_events(pairs)
            win_rows.append({"window": w, "S": s, "valid_pairs": n})
    elif v1.WINDOW_SCAN_FALLBACK_CSV.exists():
        src = str(v1.WINDOW_SCAN_FALLBACK_CSV)
        import csv

        mp: dict[float, dict[str, Any]] = {}
        with v1.WINDOW_SCAN_FALLBACK_CSV.open(encoding="utf-8") as f:
            rd = csv.DictReader(f)
            for row in rd:
                w = float(row["window"])
                mp[round(w, 10)] = {
                    "window": w,
                    "S": float(row["S"]) if row.get("S") not in (None, "", "None") else float("nan"),
                    "valid_pairs": int(float(row["pair_count"])) if row.get("pair_count") else 0,
                }
        for w in WIN_GRID:
            if round(w, 10) in mp:
                win_rows.append(mp[round(w, 10)])
    report["experiments"]["exp3_nist_window_track"] = {"source": src, "rows": win_rows}

    jp = OUT_DIR / "BELL_AUDIT_REPORT_V2_AGGRESSIVE.json"
    jp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BELL_AUDIT_REPORT v2 (Aggressive)",
        "",
        "- v1 is preserved unchanged.",
        f"- synthetic N per seed: {N_SYNTH}",
        "",
        "## Baseline (point kernel, uniform sampling)",
        f"- S_mean={mb:.6f} ± {sb:.6f}",
        "",
        "## Exp1 Geometry cap stress",
    ]
    for r in geo_rows:
        lines.append(
            f"- cap={r['cap_deg']:.1f}°: S={r['S_mean']:.6f} ± {r['S_std']:.6f}, delta_vs_base={r['delta_vs_baseline']:.6f}"
        )
    lines += ["", "## Exp2 Sampling bias stress"]
    for r in bias_rows:
        lines.append(
            f"- bias_z={r['bias_z']:.2f}: S={r['S_mean']:.6f} ± {r['S_std']:.6f}, delta_vs_base={r['delta_vs_baseline']:.6f}"
        )
    lines += ["", "## Exp3 NIST window track", f"- source: {src if src else 'N/A'}"]
    for r in win_rows:
        lines.append(f"- window={r['window']:.1f}: S={r['S']:.6f}, pairs={r['valid_pairs']}")
    lines += [
        "",
        "## Readout",
        "- If geometry/bias deltas approach window-driven deltas, model-mismatch explanation gains strength.",
        "- If window effect dominates by orders of magnitude, pairing remains the primary sensitivity axis.",
    ]
    (OUT_DIR / "BELL_AUDIT_REPORT_V2_AGGRESSIVE.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {jp}")
    print(f"wrote {OUT_DIR / 'BELL_AUDIT_REPORT_V2_AGGRESSIVE.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

