#!/usr/bin/env python3
"""
GHZ vs spherical hidden-variable model (same λ on the circle as explore_bell_metric_comparison).

Two-body repo convention (binary):
  A(a,λ) =  sign(cos(λ - a))
  B(b,λ) = -sign(cos(λ - b))

Three-body extension used here (alternating signs on parties 1..3):
  O_k(angle, λ) = s_k * sign(cos(λ - angle)),  s = (+1, -1, +1).

Pauli X / Y as two measurement directions per party (same Bloch-plane offset as bipartite CHSH):
  X_k: angle φ_k
  Y_k: angle φ_k + π/2

Mermin witness (same linear combination as standard QM GHZ example for |GHZ⟩ = (|000⟩+|111⟩)/√2):
  F = ⟨X1 X2 X3⟩ - ⟨X1 Y2 Y3⟩ - ⟨Y1 X2 Y3⟩ - ⟨Y1 Y2 X3⟩
QM: F = 4.  Any local ±1 model: F ≤ 2 (Mermin).

This script:
  1) Analytic / numeric check: ⟨cos(λ-a)cos(λ-b)cos(λ-c)⟩ = 0 for λ ~ U[0,2π).
  2) Triple "NCC-style" continuous product with alternating cos signs → numerator 0.
  3) Random search for max F over (φ1,φ2,φ3) under the binary spherical rules → should stay ≤ 2.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def sign_cos(x: "np.ndarray") -> "np.ndarray":
    import numpy as np

    return np.where(np.cos(x) >= 0.0, 1.0, -1.0)


def mermin_F(
    lam: "np.ndarray",
    phi1: float,
    phi2: float,
    phi3: float,
) -> dict[str, float]:
    """
    φ_k: reference angle for party k's "X" direction; Y is +π/2 on the circle.
    """
    import numpy as np

    s1, s2, s3 = 1.0, -1.0, 1.0

    # X / Y responses (before party sign s_k)
    x1 = s1 * sign_cos(lam - phi1)
    y1 = s1 * sign_cos(lam - phi1 - math.pi / 2)
    x2 = s2 * sign_cos(lam - phi2)
    y2 = s2 * sign_cos(lam - phi2 - math.pi / 2)
    x3 = s3 * sign_cos(lam - phi3)
    y3 = s3 * sign_cos(lam - phi3 - math.pi / 2)

    exxx = float(np.mean(x1 * x2 * x3))
    exyy = float(np.mean(x1 * y2 * y3))
    eyxy = float(np.mean(y1 * x2 * y3))
    eyyx = float(np.mean(y1 * y2 * x3))
    f_val = exxx - exyy - eyxy - eyyx
    return {"E_XXX": exxx, "E_XYY": exyy, "E_YXY": eyxy, "E_YYX": eyyx, "F": f_val}


def triple_cos_mean_numeric(a: float, b: float, c: float, lam: "np.ndarray") -> float:
    import numpy as np

    return float(np.mean(np.cos(lam - a) * np.cos(lam - b) * np.cos(lam - c)))


def main() -> int:
    import numpy as np

    ap = argparse.ArgumentParser(description="GHZ-style Mermin value vs spherical λ model")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--samples", type=int, default=400_000)
    ap.add_argument("--search-trials", type=int, default=30_000)
    ap.add_argument("--json-out", type=str, default="")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    lam = rng.uniform(0.0, 2.0 * math.pi, size=int(args.samples))

    # --- 1) Triple cosine average (any angles) ---
    a, b, c = 0.1, 0.7, 1.2
    m3 = triple_cos_mean_numeric(a, b, c, lam)
    # With alternating signs as in two-body extension: -cos(a)cos(b)cos(c) same mean 0
    m3_alt = float(np.mean(np.cos(lam - a) * (-np.cos(lam - b)) * np.cos(lam - c)))

    # --- 2) Random search for max Mermin F ---
    best = {"F": -1e9, "phi": (0.0, 0.0, 0.0)}
    for _ in range(int(args.search_trials)):
        p1, p2, p3 = rng.uniform(0.0, 2.0 * math.pi, size=3)
        d = mermin_F(lam, float(p1), float(p2), float(p3))
        if d["F"] > best["F"]:
            best = {"F": d["F"], "phi": (p1, p2, p3), **d}

    # Optional local polish: small grid around best
    p1, p2, p3 = best["phi"]
    step = math.pi / 16
    for _ in range(400):
        dp1, dp2, dp3 = rng.uniform(-step, step), rng.uniform(-step, step), rng.uniform(-step, step)
        q1 = (p1 + dp1) % (2 * math.pi)
        q2 = (p2 + dp2) % (2 * math.pi)
        q3 = (p3 + dp3) % (2 * math.pi)
        d = mermin_F(lam, float(q1), float(q2), float(q3))
        if d["F"] > best["F"]:
            best = {"F": d["F"], "phi": (q1, q2, q3), **d}
            p1, p2, p3 = q1, q2, q3

    # QM reference (analytic)
    qm = {"E_XXX": 1.0, "E_XYY": -1.0, "E_YXY": -1.0, "E_YYX": -1.0, "F": 4.0}

    report = {
        "model": "spherical_shared_lambda_sign_cos",
        "party_signs": [1, -1, 1],
        "triple_cos_mean_numeric_example": {
            "angles_rad": [a, b, c],
            "mean_cos_cos_cos": m3,
            "mean_cos_minuscos_cos": m3_alt,
            "note": "Both ~0: ∫cos(λ-a)cos(λ-b)cos(λ-c)dλ/2π=0 for uniform λ (no DC term in trig expansion).",
        },
        "mermin_random_search": {
            "samples": int(args.samples),
            "search_trials": int(args.search_trials),
            "best_spherical": {k: best[k] for k in best if k != "phi"},
            "best_phi_rad": list(best["phi"]),
        },
        "qm_ghz_reference": qm,
        "mermin_lhv_bound": 2.0,
        "interpretation": (
            "Binary spherical model is a deterministic LHV; it cannot exceed Mermin bound F≤2, "
            "while ideal |GHZ⟩ gives F=4. Continuous triple-cosine *expectation* is identically 0 "
            "for uniform λ (different object from Pauli correlators)."
        ),
    }

    print(json.dumps(report, indent=2))

    if args.json_out:
        p = Path(args.json_out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("wrote", p, file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
