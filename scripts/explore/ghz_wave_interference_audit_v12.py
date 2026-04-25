#!/usr/bin/env python3
"""
GHZ Wave Interference Audit — v12

PURPOSE
-------
Implement the "6 waves, 3 observations" model as proposed by the user.
Each detector (Alice, Bob, Charlie) receives a physical sum of waves from 
three shared entanglement sources (S_ab, S_bc, S_ca).

MODEL
-----
1. Source S_ab (phase L_ab) sends waves to Alice and Bob.
2. Source S_bc (phase L_bc) sends waves to Bob and Charlie.
3. Source S_ca (phase L_ca) sends waves to Charlie and Alice.

Each Detector Signal = Sum of arriving waves.
Alice   A = cos(L_ab - a) + cos(L_ca - a)
Bob     B = -cos(L_ab - b) + cos(L_bc - b)
Charlie C = -cos(L_bc - c) - cos(L_ca - c)

(Signs are chosen to facilitate anti-correlations, but can be adjusted).

STATISTICS
----------
F = E(XXX) - E(XYY) - E(YXY) - E(YYX)
Using NCC: E = <A*B*C> / sqrt(<A^2><B^2><C^2>)
"""

import numpy as np
import json
import math
from pathlib import Path

def run_audit():
    N = 1_000_000
    rng = np.random.default_rng(42)
    
    # Hidden phases for the 3 sources
    L_ab = rng.uniform(0, 2*np.pi, N)
    L_bc = rng.uniform(0, 2*np.pi, N)
    L_ca = rng.uniform(0, 2*np.pi, N)
    
    PI = np.pi
    
    def get_outcomes(a, b, c):
        # Alice receives waves from S_ab and S_ca
        # Bob receives waves from S_ab and S_bc
        # Charlie receives waves from S_bc and S_ca
        
        # We introduce phase flips (-) to simulate the GHZ/singlet structure
        A = np.cos(L_ab - a) + np.cos(L_ca - a)
        B = -np.cos(L_ab - b) + np.cos(L_bc - b)
        C = -np.cos(L_bc - c) - np.cos(L_ca - c)
        
        return A, B, C

    def ncc_triple(a, b, c):
        num = np.mean(a * b * c)
        den = np.sqrt(np.mean(a**2) * np.mean(b**2) * np.mean(c**2))
        return num / den

    def compute_E(a, b, c):
        A, B, C = get_outcomes(a, b, c)
        return ncc_triple(A, B, C)

    # GHZ Bases:
    # XXX: (0, 0, 0)
    # XYY: (0, pi/2, pi/2)
    # YXY: (pi/2, 0, pi/2)
    # YYX: (pi/2, pi/2, 0)
    
    X = 0.0
    Y = PI / 2
    
    E_xxx = compute_E(X, X, X)
    E_xyy = compute_E(X, Y, Y)
    E_yxy = compute_E(Y, X, Y)
    E_yyx = compute_E(Y, Y, X)
    
    F = E_xxx - E_xyy - E_yxy - E_yyx
    
    # ── Comparison with Binarized version ──────────────────────────────────
    def compute_E_bin(a, b, c):
        A, B, C = get_outcomes(a, b, c)
        Ab = np.where(A >= 0, 1, -1)
        Bb = np.where(B >= 0, 1, -1)
        Cb = np.where(C >= 0, 1, -1)
        return np.mean(Ab * Bb * Cb)

    F_bin = (compute_E_bin(X, X, X) - 
             compute_E_bin(X, Y, Y) - 
             compute_E_bin(Y, X, Y) - 
             compute_E_bin(Y, Y, X))

    report = {
        "model": "GHZ Wave Sum Interference v12",
        "description": "3 sources (AB, BC, CA) contributing 2 waves each to 3 detectors.",
        "results": {
            "NCC_Continuous": {
                "E_XXX": E_xxx,
                "E_XYY": E_xyy,
                "E_YXY": E_yxy,
                "E_YYX": E_yyx,
                "Mermin_F": F
            },
            "Binarized": {
                "Mermin_F": F_bin
            }
        },
        "target_F": 4.0,
        "lhv_limit": 2.0
    }
    
    out_dir = Path("artifacts/ghz_audit_v12")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "GHZ_V12_RESULTS.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"GHZ Audit v12 Complete.")
    print(f"  NCC Mermin F: {F:.6f}")
    print(f"  Binarized F:  {F_bin:.6f}")
    print(f"  Target F:     4.000000")

if __name__ == "__main__":
    run_audit()
