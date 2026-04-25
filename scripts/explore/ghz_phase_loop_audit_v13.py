#!/usr/bin/env python3
"""
GHZ Phase-Loop Audit — v13

MODEL: The "Three Stones" Ripple Model
--------------------------------------
1. Three emitters (S1, S2, S3) with random phases (L1, L2, L3).
2. Three detectors (A, B, C) measuring the interference (phase difference) 
   between adjacent emitters.
3. The geometric closure (L1-L2) + (L2-L3) + (L3-L1) = 0 ensures that 
   the sum of phases is independent of the random sources.

STATISTICS:
- Spherical (NCC): Preservation of wave curvature.
- Binarized (+/- 1): Crushing the wave logic into discrete bits.
"""

import numpy as np
import json
import math
from pathlib import Path

def run_audit():
    N = 1_000_000
    rng = np.random.default_rng(42)
    
    # Random phases for the 3 emitters (the 3 stones)
    L1 = rng.uniform(0, 2*np.pi, N)
    L2 = rng.uniform(0, 2*np.pi, N)
    L3 = rng.uniform(0, 2*np.pi, N)
    
    PI = np.pi
    
    def get_wave_outcomes(a, b, c):
        # Detectors measure the interference (ripple interaction)
        # Alice: between S1 and S2
        # Bob:   between S2 and S3
        # Charlie: between S3 and S1
        # We add the measurement angle to the interference phase
        phi_a = (L1 - L2) - a
        phi_b = (L2 - L3) - b
        phi_c = (L3 - L1) - c
        
        return np.cos(phi_a), np.cos(phi_b), np.cos(phi_c)

    def ncc_triple(a, b, c):
        num = np.mean(a * b * c)
        # For pure cosines, mean(cos^2) = 0.5. 
        # Denominator = sqrt(0.5 * 0.5 * 0.5) = 0.35355
        den = np.sqrt(np.mean(a**2) * np.mean(b**2) * np.mean(c**2))
        return num / den

    def compute_E_spherical(a, b, c):
        wa, wb, wc = get_wave_outcomes(a, b, c)
        return ncc_triple(wa, wb, wc)

    def compute_E_binarized(a, b, c):
        wa, wb, wc = get_wave_outcomes(a, b, c)
        ba = np.where(wa >= 0, 1, -1)
        bb = np.where(wb >= 0, 1, -1)
        bc = np.where(wc >= 0, 1, -1)
        return np.mean(ba * bb * bc)

    # GHZ Mermin Settings
    # F = E(0,0,0) - E(0,pi/2,pi/2) - E(pi/2,0,pi/2) - E(pi/2,pi/2,0)
    X = 0.0
    Y = PI / 2
    
    # --- Spherical (NCC) Audit ---
    E_xxx_s = compute_E_spherical(X, X, X)
    E_xyy_s = compute_E_spherical(X, Y, Y)
    E_yxy_s = compute_E_spherical(Y, X, Y)
    E_yyx_s = compute_E_spherical(Y, Y, X)
    F_spherical = E_xxx_s - E_xyy_s - E_yxy_s - E_yyx_s
    
    # --- Binarized Audit ---
    E_xxx_b = compute_E_binarized(X, X, X)
    E_xyy_b = compute_E_binarized(X, Y, Y)
    E_yxy_b = compute_E_binarized(Y, X, Y)
    E_yyx_b = compute_E_binarized(Y, Y, X)
    F_binarized = E_xxx_b - E_xyy_b - E_yxy_b - E_yyx_b

    report = {
        "model": "GHZ Phase-Loop (Three Stones) v13",
        "logic": "Interference phase difference between 3 closed-loop emitters.",
        "results": {
            "Spherical_NCC": {
                "E_XXX": E_xxx_s,
                "E_XYY": E_xyy_s,
                "E_YXY": E_yxy_s,
                "E_YYX": E_yyx_s,
                "Mermin_F": F_spherical
            },
            "Binarized_Logic": {
                "E_XXX": E_xxx_b,
                "E_XYY": E_xyy_b,
                "E_YXY": E_yxy_b,
                "E_YYX": E_yyx_b,
                "Mermin_F": F_binarized
            }
        },
        "interpretation": {
            "Spherical_F_Goal": "Reveals cosine curvature through NCC",
            "Binarized_F_Limit": 2.0
        }
    }
    
    print(f"GHZ Audit v13 Complete.")
    print(f"--- Spherical (Wave Geometry) ---")
    print(f"  E_XXX: {E_xxx_s:.4f}, E_XYY: {E_xyy_s:.4f}")
    print(f"  Mermin F (NCC): {F_spherical:.6f}")
    print(f"--- Binarized (Particle Logic) ---")
    print(f"  E_XXX: {E_xxx_b:.4f}, E_XYY: {E_xyy_b:.4f}")
    print(f"  Mermin F (Bin): {F_binarized:.6f}")
    
    # Save results
    out_dir = Path("artifacts/ghz_audit_v13")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "GHZ_V13_RESULTS.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    run_audit()
