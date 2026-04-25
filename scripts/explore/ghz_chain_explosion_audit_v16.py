#!/usr/bin/env python3
"""
GHZ Chain Explosion Audit — v16
-------------------------------
AUDIT MODEL: Measures correlations in the "Explosive Collision" model.
Calculates Mermin F for both Spherical (NCC) and Binarized statistics.
Includes:
- Asymmetric source forces.
- Secondary explosion energy boost at collision points.
"""

import numpy as np
import json
from pathlib import Path

def run_audit():
    N = 1_000_000
    rng = np.random.default_rng(99)
    
    # 1. Random Hidden Phases
    L1 = rng.uniform(0, 2*np.pi, N)
    L2 = rng.uniform(0, 2*np.pi, N)
    L3 = rng.uniform(0, 2*np.pi, N)
    
    # 2. Asymmetric Source Forces (User's request)
    F1 = 1.5
    F2 = 0.8
    F3 = 1.2
    
    PI = np.pi
    X, Y = 0.0, PI / 2

    def get_explosive_outcomes(a, b, c):
        # Primary Waves (Phase Loop)
        phi_a = (L1 - L2) - a
        phi_b = (L2 - L3) - b
        phi_c = (L3 - L1) - c
        
        # Primary Amplitudes with asymmetric force
        wa = F1 * np.cos(phi_a)
        wb = F2 * np.cos(phi_b)
        wc = F3 * np.cos(phi_c)
        
        # 3. "Explosion" Factor: When waves are in phase, energy 'explodes'
        # This is a non-linear interaction term
        explosion_boost = 0.5 * (np.cos(phi_a) * np.cos(phi_b) * np.cos(phi_c))
        
        # The secondary ripples push the detected signal
        wa_final = wa + explosion_boost
        wb_final = wb + explosion_boost
        wc_final = wc + explosion_boost
        
        return wa_final, wb_final, wc_final

    def ncc_triple(a, b, c):
        num = np.mean(a * b * c)
        den = np.sqrt(np.mean(a**2) * np.mean(b**2) * np.mean(c**2))
        return num / den

    def bin_triple(a, b, c):
        return np.mean(np.sign(a) * np.sign(b) * np.sign(c))

    def compute_stats(a, b, c):
        wa, wb, wc = get_explosive_outcomes(a, b, c)
        return ncc_triple(wa, wb, wc), bin_triple(wa, wb, wc)

    # Calculate Mermin F
    s_xxx, b_xxx = compute_stats(X, X, X)
    s_xyy, b_xyy = compute_stats(X, Y, Y)
    s_yxy, b_yxy = compute_stats(Y, X, Y)
    s_yyx, b_yyx = compute_stats(Y, Y, X)
    
    F_spherical = s_xxx - s_xyy - s_yxy - s_yyx
    F_binarized = b_xxx - b_xyy - b_yxy - b_yyx
    
    report = {
        "model": "GHZ Chain Explosion v16",
        "parameters": {"F1": F1, "F2": F2, "F3": F3},
        "results": {
            "Spherical_NCC": {
                "E_XXX": s_xxx,
                "E_XYY": s_xyy,
                "Mermin_F": F_spherical
            },
            "Binarized": {
                "E_XXX": b_xxx,
                "E_XYY": b_xyy,
                "Mermin_F": F_binarized
            }
        }
    }
    
    print(f"GHZ Audit v16 (Chain Explosion) Results:")
    print(f"--- Spherical (NCC) ---")
    print(f"  Mermin F: {F_spherical:.6f}")
    print(f"--- Binarized (Sign) ---")
    print(f"  Mermin F: {F_binarized:.6f}")
    
    out_dir = Path("artifacts/ghz_audit_v16")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "GHZ_V16_DATA.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    run_audit()
