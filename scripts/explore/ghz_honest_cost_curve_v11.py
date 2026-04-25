#!/usr/bin/env python3
"""
GHZ Honest Cost-Benefit Curve — v11

PURPOSE
-------
Measure the ACTUAL relationship between sample-retention ratio and Mermin F,
using three hidden-variable GHZ schemes.  No anchors, no illustrative curves,
no pre-set endpoints.  Whatever F emerges from the data is what gets reported.

WHAT THIS FIXES
---------------
The earlier `ghz_cost_benefit_curve_2p2_to_4p0.csv` was flagged as
`"type": "illustrative_curve"` with `retention_anchor_at_f_max = 0.25`
pre-set by the user.  That means the 75 % / 25 % split was *input*, not
*discovered*.  This script removes every anchor and lets the simulation
decide the shape of the curve.

METHOD
------
For each hidden-variable scheme:
  1. Generate N events.  Each event carries three continuous outcomes
     (A, B, C) for each of the four GHZ measurement bases (XXX, XYY, YXY, YYX).
  2. Assign each event a "wave-front energy" score:
       score = |A_XXX| * |B_XXX| * |C_XXX|   (product of amplitudes)
     This is a physics-derived per-event quality score — NOT a user-chosen target.
  3. Sort events descending by score.
  4. At each retention ratio r in [0.05, 0.10, ..., 1.00]:
       keep top ceil(r * N) events
       compute F = E(XXX) - E(XYY) - E(YXY) - E(YYX)
       using NCC denominator: E = mean(ABC) / sqrt(mean(A²) mean(B²) mean(C²))
  5. Record (r, F, event_count).

No F value is prescribed.  The curve is whatever the data produces.

ANTI-CHEATING RULES (preregistered)
------------------------------------
- Seed is fixed and logged in output JSON before any data is generated.
- Retention thresholds are a fixed linear grid (0.05 to 1.00, step 0.05).
- The score function is |A_XXX * B_XXX * C_XXX| — defined before running.
- No post-hoc threshold shifting.
- All three schemes run unconditionally and all results are saved.
- If F for any scheme exceeds the LHV binary bound of 2.0 without binarization,
  that is noted but NOT suppressed.

RUN
---
  python scripts/explore/ghz_honest_cost_curve_v11.py
  python scripts/explore/ghz_honest_cost_curve_v11.py --samples 200000 --seed 42
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

PI = math.pi
TWO_PI = 2.0 * PI

# ── Preregistered retention grid (no anchors) ──────────────────────────────
RETENTION_GRID = [round(0.05 * k, 10) for k in range(1, 21)]  # 0.05 … 1.00


# ── NCC triple correlator ──────────────────────────────────────────────────
def ncc_triple(a, b, c, eps=1e-15):
    import numpy as np
    num = float(np.mean(a * b * c))
    den = (math.sqrt(
        float(np.mean(a * a)) *
        float(np.mean(b * b)) *
        float(np.mean(c * c))
    ) + eps)
    return num / den


# ── Outcome generators ─────────────────────────────────────────────────────

def make_outcomes_scheme1(lam_ab, lam_bc, lam_ac, lam0):
    """
    Scheme 1 — four independent pairwise phase variables.
    A = cos(lam_ab + lam_ac + lam0 - angle_a), etc.
    """
    import numpy as np

    def abc(a, b, c):
        pa = lam_ab + lam_ac + lam0
        pb = lam_ab + lam_bc + lam0
        pc = lam_bc + lam_ac + lam0
        return np.cos(pa - a), np.cos(pb - b), np.cos(pc - c)

    return abc


def make_outcomes_scheme2b(nx, ny):
    """
    Scheme 2b — Bloch-consistent sphere: X → nx, Y → ny.
    Angles are ignored (fixed projection); all settings yield same n.
    """
    def abc(a, b, c):
        # X measurement → nx component, Y measurement → ny component
        # For XXX: all three use X
        # For XYY: first uses X, second and third use Y
        # (a, b, c are dummy here — the outcomes are fixed projections)
        return nx, nx, nx  # overridden per call below

    return abc  # caller computes per setting


def make_outcomes_scheme3(lam, phi):
    """
    Scheme 3 — shared lambda, Charlie has a single phase offset phi.
    A = cos(lam - a), B = cos(lam - b), C = cos(lam - c + phi).
    """
    import numpy as np

    def abc(a, b, c):
        return np.cos(lam - a), np.cos(lam - b), np.cos(lam - c + phi)

    return abc


# ── Per-event score ────────────────────────────────────────────────────────

def compute_score(a_xxx, b_xxx, c_xxx):
    """
    Wave-front energy proxy for the XXX measurement:
      score_i = |A_i| * |B_i| * |C_i|
    Preregistered: chosen before running, not tuned to outcome.
    """
    import numpy as np
    return np.abs(a_xxx) * np.abs(b_xxx) * np.abs(c_xxx)


# ── F at a given mask ──────────────────────────────────────────────────────

def compute_f(abc_fn, mask):
    a_xxx, b_xxx, c_xxx = abc_fn(0.0,      0.0,      0.0)
    a_xyy, b_xyy, c_xyy = abc_fn(0.0,      PI / 2,   PI / 2)
    a_yxy, b_yxy, c_yxy = abc_fn(PI / 2,   0.0,      PI / 2)
    a_yyx, b_yyx, c_yyx = abc_fn(PI / 2,   PI / 2,   0.0)

    e_xxx = ncc_triple(a_xxx[mask], b_xxx[mask], c_xxx[mask])
    e_xyy = ncc_triple(a_xyy[mask], b_xyy[mask], c_xyy[mask])
    e_yxy = ncc_triple(a_yxy[mask], b_yxy[mask], c_yxy[mask])
    e_yyx = ncc_triple(a_yyx[mask], b_yyx[mask], c_yyx[mask])
    return e_xxx - e_xyy - e_yxy - e_yyx, e_xxx, e_xyy, e_yxy, e_yyx


# ── Cost-benefit curve for one scheme ─────────────────────────────────────

def cost_curve(abc_fn, score, n, label):
    """
    Returns list of dicts: {retention, kept, F, e_xxx, e_xyy, e_yxy, e_yyx}
    No anchoring — just sweep the preregistered grid.
    """
    import numpy as np

    order = np.argsort(-score)   # descending: highest-score events first
    records = []
    for r in RETENTION_GRID:
        k = max(1, math.ceil(r * n))
        mask = order[:k]
        f_val, e_xxx, e_xyy, e_yxy, e_yyx = compute_f(abc_fn, mask)
        records.append({
            "scheme": label,
            "retention": round(r, 10),
            "kept": k,
            "F": round(f_val, 8),
            "E_XXX": round(e_xxx, 8),
            "E_XYY": round(e_xyy, 8),
            "E_YXY": round(e_yxy, 8),
            "E_YYX": round(e_yyx, 8),
        })
    return records


# ── Scheme 2b needs special handling (fixed projections) ──────────────────

def cost_curve_scheme2b(nx, ny, score, n):
    """
    Scheme 2b: X → nx, Y → ny (same vector for all parties).
    Outcomes do not depend on angle, so abc_fn per-setting is explicit.
    """
    import numpy as np

    order = np.argsort(-score)
    records = []
    for r in RETENTION_GRID:
        k = max(1, math.ceil(r * n))
        mask = order[:k]

        e_xxx = ncc_triple(nx[mask], nx[mask], nx[mask])
        e_xyy = ncc_triple(nx[mask], ny[mask], ny[mask])
        e_yxy = ncc_triple(ny[mask], nx[mask], ny[mask])
        e_yyx = ncc_triple(ny[mask], ny[mask], nx[mask])
        f_val = e_xxx - e_xyy - e_yxy - e_yyx
        records.append({
            "scheme": "scheme2b_sphere_bloch",
            "retention": round(r, 10),
            "kept": k,
            "F": round(f_val, 8),
            "E_XXX": round(e_xxx, 8),
            "E_XYY": round(e_xyy, 8),
            "E_YXY": round(e_yxy, 8),
            "E_YYX": round(e_yyx, 8),
        })
    return records


# ── Find best phi for scheme 3 (honest single-knob search) ────────────────

def find_best_phi(lam, n_phi=360):
    """
    Grid-search phi on [0, 2π) to maximize |F|.
    Honest: uses the same NCC formula, no gradient tricks.
    """
    import numpy as np

    phi_grid = TWO_PI * np.arange(n_phi) / n_phi
    best_phi = 0.0
    best_absf = 0.0
    for phi in phi_grid:
        abc_fn = make_outcomes_scheme3(lam, phi)
        mask = np.ones(len(lam), dtype=bool)
        f_val, *_ = compute_f(abc_fn, mask)
        if abs(f_val) > best_absf:
            best_absf = abs(f_val)
            best_phi = phi
    return best_phi, best_absf


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> int:
    import os
    os.environ.setdefault("MPLBACKEND", "Agg")
    import numpy as np
    import matplotlib
    matplotlib.use(os.environ.get("MPLBACKEND", "Agg"))
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="GHZ honest cost-benefit curve v11")
    ap.add_argument("--seed",    type=int, default=0)
    ap.add_argument("--samples", type=int, default=100_000)
    ap.add_argument("--phi-grid", type=int, default=360,
                    help="Number of phi points for scheme3 best-phi search")
    ap.add_argument("--no-plot", action="store_true")
    ap.add_argument("--out-dir", type=str,
                    default="artifacts/ghz_honest_v11")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    n = int(args.samples)
    seed = int(args.seed)

    # ── Log experiment identity before generating any data ─────────────────
    meta = {
        "experiment": "ghz_honest_cost_curve_v11",
        "seed": seed,
        "samples": n,
        "retention_grid": RETENTION_GRID,
        "score_function": "abs(A_XXX) * abs(B_XXX) * abs(C_XXX)",
        "anchors": "NONE — no pre-set F target or retention endpoint",
        "phi_grid_points": args.phi_grid,
        "anti_cheat_note": (
            "All parameters above were logged before rng was seeded. "
            "Curve shape is determined entirely by simulation output."
        ),
    }
    (out_dir / "PREREG_V11.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )

    # ── Generate random variables ──────────────────────────────────────────
    rng = np.random.default_rng(seed)

    lam_ab  = rng.uniform(0.0, TWO_PI, size=n)
    lam_bc  = rng.uniform(0.0, TWO_PI, size=n)
    lam_ac  = rng.uniform(0.0, TWO_PI, size=n)
    lam0    = rng.uniform(0.0, TWO_PI, size=n)
    lam_shared = rng.uniform(0.0, TWO_PI, size=n)

    phi_s   = rng.uniform(0.0, TWO_PI, size=n)
    theta_s = np.arccos(rng.uniform(-1.0, 1.0, size=n))
    nx = np.sin(theta_s) * np.cos(phi_s)
    ny = np.sin(theta_s) * np.sin(phi_s)

    # ── Scheme 1 ───────────────────────────────────────────────────────────
    print("Running scheme 1 (four independent lambdas) …", file=sys.stderr)
    abc1 = make_outcomes_scheme1(lam_ab, lam_bc, lam_ac, lam0)
    a1_xxx, b1_xxx, c1_xxx = abc1(0.0, 0.0, 0.0)
    score1 = compute_score(a1_xxx, b1_xxx, c1_xxx)
    records1 = cost_curve(abc1, score1, n, "scheme1_four_lambdas")

    # ── Scheme 2b ──────────────────────────────────────────────────────────
    print("Running scheme 2b (Bloch sphere, X=nx, Y=ny) …", file=sys.stderr)
    score2b = compute_score(nx, nx, nx)   # XXX: all three use nx
    records2b = cost_curve_scheme2b(nx, ny, score2b, n)

    # ── Scheme 3: find best phi honestly, then run cost curve ──────────────
    print(f"Searching best phi for scheme 3 over {args.phi_grid} points …",
          file=sys.stderr)
    best_phi, best_absf_at_full = find_best_phi(lam_shared, args.phi_grid)
    print(f"  best phi = {best_phi:.4f} rad, |F|_full = {best_absf_at_full:.6f}",
          file=sys.stderr)
    abc3 = make_outcomes_scheme3(lam_shared, best_phi)
    a3_xxx, b3_xxx, c3_xxx = abc3(0.0, 0.0, 0.0)
    score3 = compute_score(a3_xxx, b3_xxx, c3_xxx)
    records3 = cost_curve(abc3, score3, n, f"scheme3_best_phi={best_phi:.4f}")

    all_records = records1 + records2b + records3

    # ── Save JSON ──────────────────────────────────────────────────────────
    payload = {
        "meta": meta,
        "scheme3_best_phi_rad": best_phi,
        "scheme3_best_absF_at_full_retention": best_absf_at_full,
        "qm_reference_F": 4.0,
        "lhv_binary_bound_F": 2.0,
        "records": all_records,
    }
    json_path = out_dir / "GHZ_HONEST_COST_CURVE_V11.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved JSON → {json_path}", file=sys.stderr)

    # ── Save CSV ───────────────────────────────────────────────────────────
    csv_lines = ["scheme,retention,kept,F,E_XXX,E_XYY,E_YXY,E_YYX"]
    for rec in all_records:
        csv_lines.append(
            f"{rec['scheme']},{rec['retention']},{rec['kept']},"
            f"{rec['F']},{rec['E_XXX']},{rec['E_XYY']},{rec['E_YXY']},{rec['E_YYX']}"
        )
    csv_path = out_dir / "GHZ_HONEST_COST_CURVE_V11.csv"
    csv_path.write_text("\n".join(csv_lines), encoding="utf-8")

    # ── Markdown summary ───────────────────────────────────────────────────
    md_lines = [
        "# GHZ Honest Cost-Benefit Curve — v11",
        "",
        "**No anchors. No illustrative curves. Data only.**",
        "",
        f"- seed: `{seed}`",
        f"- samples: `{n}`",
        f"- score function: `abs(A_XXX) * abs(B_XXX) * abs(C_XXX)` (preregistered)",
        f"- scheme3 best phi: `{best_phi:.6f}` rad (honest grid search over {args.phi_grid} points)",
        f"- scheme3 |F| at 100% retention: `{best_absf_at_full:.6f}`",
        "",
        "## Full-retention F values (retention = 1.00, no selection)",
        "",
        "| scheme | F |",
        "|---|---:|",
    ]
    full_rows = {r["scheme"]: r["F"] for r in all_records if r["retention"] == 1.0}
    for scheme, f_val in full_rows.items():
        md_lines.append(f"| {scheme} | {f_val:.6f} |")

    md_lines += [
        "",
        "## F at each retention level",
        "",
        "| retention | scheme1 F | scheme2b F | scheme3 F |",
        "|---:|---:|---:|---:|",
    ]
    s1_map  = {r["retention"]: r["F"] for r in records1}
    s2b_map = {r["retention"]: r["F"] for r in records2b}
    s3_map  = {r["retention"]: r["F"] for r in records3}
    for r in RETENTION_GRID:
        md_lines.append(
            f"| {r:.2f} | {s1_map.get(r, 'n/a'):.6f} "
            f"| {s2b_map.get(r, 'n/a'):.6f} "
            f"| {s3_map.get(r, 'n/a'):.6f} |"
        )

    md_lines += [
        "",
        "## Interpretation guardrails",
        "",
        "- F values above are NCC-continuous, not binary Mermin.  "
          "LHV binary bound is F ≤ 2; NCC scale is different.",
        "- Score-based selection is a proxy for 'events with strongest "
          "local wave-front product'.  It is not the same as random subsampling.",
        "- If F increases with stricter selection, that demonstrates selection "
          "can amplify apparent correlation (known phenomenon).  "
          "It does NOT prove the physical model is correct.",
        "- If F is flat across retention levels, the score function does not "
          "strongly filter by correlation strength.",
        "- QM reference F = 4 (binary ±1 Mermin).  NCC continuous outcomes "
          "will not reach 4 by construction.",
        "",
        "## Anti-cheat checklist",
        "",
        "- [x] Seed logged before data generation",
        "- [x] Retention grid fixed before running",
        "- [x] Score function defined and logged before running",
        "- [x] No F target or retention endpoint pre-set",
        "- [x] All three schemes run and saved unconditionally",
        "- [x] Negative / low F results are NOT suppressed",
    ]

    md_path = out_dir / "GHZ_HONEST_COST_CURVE_V11.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Saved MD  → {md_path}", file=sys.stderr)

    # ── Plot ───────────────────────────────────────────────────────────────
    if not args.no_plot:
        fig, ax = plt.subplots(figsize=(9, 5))
        ret_axis = RETENTION_GRID

        ax.plot(ret_axis, [s1_map[r]  for r in ret_axis],
                marker="o", ms=4, lw=1.4, label="scheme1 (four λ)")
        ax.plot(ret_axis, [s2b_map[r] for r in ret_axis],
                marker="s", ms=4, lw=1.4, label="scheme2b (Bloch nx/ny)")
        ax.plot(ret_axis, [s3_map[r]  for r in ret_axis],
                marker="^", ms=4, lw=1.4,
                label=f"scheme3 (best φ={best_phi:.2f})")

        ax.axhline(0.0,  color="#aaaaaa", lw=0.8, ls=":")
        ax.axhline(4.0,  color="#d95f02", lw=1.0, ls="--", label="QM ideal F=4 (binary)")
        ax.axhline(2.0,  color="#7570b3", lw=1.0, ls="--", label="LHV binary bound F=2")

        ax.set_xlabel("Retention ratio (fraction of events kept)")
        ax.set_ylabel("F  (NCC continuous)")
        ax.set_title("GHZ Honest Cost-Benefit Curve v11\n"
                     "No anchors — data-driven only")
        ax.legend(fontsize=8)
        fig.tight_layout()
        png_path = out_dir / "GHZ_HONEST_COST_CURVE_V11.png"
        fig.savefig(png_path, dpi=160)
        plt.close(fig)
        print(f"Saved PNG → {png_path}", file=sys.stderr)

    # ── Console summary ────────────────────────────────────────────────────
    print("\n=== GHZ Honest Cost-Benefit v11: FULL-RETENTION RESULTS ===")
    print(f"  scheme1  F(100%) = {s1_map[1.0]:.6f}")
    print(f"  scheme2b F(100%) = {s2b_map[1.0]:.6f}")
    print(f"  scheme3  F(100%) = {s3_map[1.0]:.6f}  (phi={best_phi:.4f})")
    print(f"  QM reference F   = 4.000000")
    print("")
    print("  F vs retention (scheme3):")
    for r in [0.10, 0.25, 0.50, 0.75, 1.00]:
        print(f"    keep {int(r*100):3d}% → F = {s3_map[r]:.6f}")
    print("")
    print(f"Artifacts written to: {out_dir.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
