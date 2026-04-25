#!/usr/bin/env python3
"""
GHZ Phase-Loop Cost-Curve — v14

PURPOSE
-------
Measure the ACTUAL relationship between event retention and Mermin F
using the "Three Stones" Phase-Loop model. 

METHOD
------
1. Generate N events using the Phase-Loop interference model.
2. For each event, compute a "Coherence Score": score = |A * B * C|.
3. Sweep retention levels from 1% to 100%.
4. Report both Spherical (NCC) and Binarized F values.
"""

import numpy as np
import json
import math
import matplotlib.pyplot as plt
from pathlib import Path

def run_audit():
    N = 1_000_000
    rng = np.random.default_rng(42)
    
    # 1. Generate local hidden phases
    L1 = rng.uniform(0, 2*np.pi, N)
    L2 = rng.uniform(0, 2*np.pi, N)
    L3 = rng.uniform(0, 2*np.pi, N)
    
    PI = np.pi
    X, Y = 0.0, PI / 2
    
    # Pre-compute outcomes for the 4 GHZ bases
    def get_waves(a, b, c):
        phi_a = (L1 - L2) - a
        phi_b = (L2 - L3) - b
        phi_c = (L3 - L1) - c
        return np.cos(phi_a), np.cos(phi_b), np.cos(phi_c)

    # We use XXX as the "Selection Base" (Standard procedure in experimental selection)
    A_xxx, B_xxx, C_xxx = get_waves(X, X, X)
    A_xyy, B_xyy, C_xyy = get_waves(X, Y, Y)
    A_yxy, B_yxy, C_yxy = get_waves(Y, X, Y)
    A_yyx, B_yyx, C_yyx = get_waves(Y, Y, X)
    
    # Score = product of magnitudes (Coherence proxy)
    score = np.abs(A_xxx * B_xxx * C_xxx)
    order = np.argsort(-score) # Best first
    
    retention_grid = np.linspace(0.01, 1.0, 100)
    results = []

    def ncc_triple(a, b, c):
        num = np.mean(a * b * c)
        den = np.sqrt(np.mean(a**2) * np.mean(b**2) * np.mean(c**2))
        return num / den

    def bin_triple(a, b, c):
        return np.mean(np.sign(a) * np.sign(b) * np.sign(c))

    for r in retention_grid:
        k = int(r * N)
        mask = order[:k]
        
        # NCC F
        e_xxx_s = ncc_triple(A_xxx[mask], B_xxx[mask], C_xxx[mask])
        e_xyy_s = ncc_triple(A_xyy[mask], B_xyy[mask], C_xyy[mask])
        e_yxy_s = ncc_triple(A_yxy[mask], B_yxy[mask], C_yxy[mask])
        e_yyx_s = ncc_triple(A_yyx[mask], B_yyx[mask], C_yyx[mask])
        F_s = e_xxx_s - e_xyy_s - e_yxy_s - e_yyx_s
        
        # Binarized F
        e_xxx_b = bin_triple(A_xxx[mask], B_xxx[mask], C_xxx[mask])
        e_xyy_b = bin_triple(A_xyy[mask], B_xyy[mask], C_xyy[mask])
        e_yxy_b = bin_triple(A_yxy[mask], B_yxy[mask], C_yxy[mask])
        e_yyx_b = bin_triple(A_yyx[mask], B_yyx[mask], C_yyx[mask])
        F_b = e_xxx_b - e_xyy_b - e_yxy_b - e_yyx_b
        
        results.append({
            "retention": float(r),
            "F_spherical": float(F_s),
            "F_binarized": float(F_b)
        })

    # Plotting
    plt.figure(figsize=(10, 6))
    ret = [r["retention"] for r in results]
    f_s = [r["F_spherical"] for r in results]
    f_b = [r["F_binarized"] for r in results]
    
    plt.plot(ret, f_s, label="Spherical (NCC) - Geometric Truth")
    plt.plot(ret, f_b, label="Binarized (Sign) - Particle Logic")
    plt.axhline(4.0, color='r', linestyle='--', label="Quantum Target (F=4)")
    plt.axhline(2.0, color='g', linestyle='--', label="Classical Limit (F=2)")
    
    plt.xlabel("Retention Ratio (kept / total)")
    plt.ylabel("Mermin F Value")
    plt.title("GHZ Cost-Benefit Curve: The Price of Quantum Appearance")
    plt.legend()
    plt.grid(True)
    
    out_dir = Path("artifacts/ghz_audit_v14")
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_dir / "GHZ_COST_CURVE_V14.png")
    
    # Save CSV
    with open(out_dir / "GHZ_COST_CURVE_V14.csv", "w") as f:
        f.write("retention,F_spherical,F_binarized\n")
        for r in results:
            f.write(f"{r['retention']},{r['F_spherical']},{r['F_binarized']}\n")
            
    print(f"GHZ Audit v14 Complete. Results saved to {out_dir}")
    # Show values at key points
    for r in [0.01, 0.1, 0.25, 0.5, 1.0]:
        row = next(res for res in results if abs(res["retention"] - r) < 0.005)
        print(f"Retention {r*100:3.0f}%: NCC F = {row['F_spherical']:.4f}, Bin F = {row['F_binarized']:.4f}")

if __name__ == "__main__":
    run_audit()
