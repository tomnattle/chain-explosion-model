#!/usr/bin/env python3
"""
GHZ Non-linear Trigger Audit — v15

MODEL: Non-linear "Chain Explosion" Response
--------------------------------------------
Testing if a non-linear detection threshold (A^n) can suppress the 
geometric noise and push Mermin F from 2.828 toward 4.0.
"""

import numpy as np
import json
import math
from pathlib import Path

def run_audit():
    N = 1_000_000
    rng = np.random.default_rng(42)
    
    L1 = rng.uniform(0, 2*np.pi, N)
    L2 = rng.uniform(0, 2*np.pi, N)
    L3 = rng.uniform(0, 2*np.pi, N)
    
    PI = np.pi
    X, Y = 0.0, PI / 2
    
    # Power of non-linearity (The "Chain Explosion" factor)
    # n=1 is linear (v13), n=3 or higher is non-linear pulse
    N_POWER = 3 

    def get_outcomes(a, b, c, n=1):
        phi_a = (L1 - L2) - a
        phi_b = (L2 - L3) - b
        phi_c = (L3 - L1) - c
        
        # Non-linear response: sgn(cos)*|cos|^n preserves sign but sharpens peak
        wa = np.sign(np.cos(phi_a)) * np.abs(np.cos(phi_a))**n
        wb = np.sign(np.cos(phi_b)) * np.abs(np.cos(phi_b))**n
        wc = np.sign(np.cos(phi_c)) * np.abs(np.cos(phi_c))**n
        
        return wa, wb, wc

    def ncc_triple(a, b, c):
        num = np.mean(a * b * c)
        den = np.sqrt(np.mean(a**2) * np.mean(b**2) * np.mean(c**2))
        return num / den

    def compute_F(n):
        e_xxx = ncc_triple(*get_outcomes(X, X, X, n))
        e_xyy = ncc_triple(*get_outcomes(X, Y, Y, n))
        e_yxy = ncc_triple(*get_outcomes(Y, X, Y, n))
        e_yyx = ncc_triple(*get_outcomes(Y, Y, X, n))
        return e_xxx - e_xyy - e_yxy - e_yyx

    print(f"GHZ Audit v15: Non-linear 'Chain Explosion' (Power n)")
    print("-" * 40)
    for n in [1, 2, 3, 5, 10]:
        F = compute_F(n)
        print(f"Power n={n:2d} -> Mermin F = {F:.6f}")

if __name__ == "__main__":
    run_audit()
