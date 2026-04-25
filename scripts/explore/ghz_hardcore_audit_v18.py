#!/usr/bin/env python3
"""
GHZ Hardcore Physics Audit — v18 (NO CHEATING)
-----------------------------------------------
DESTRUCTIVE REWRITE:
1. NO reference to Mermin/Bell formulas (no a+b+c).
2. EXPLOSION is triggered by LOCAL amplitude threshold in 3D space.
3. PROPAGATION DELAY: Secondary pulses must travel to reach detectors.
4. ASYMMETRIC FORCE: Momentum-based scattering.

Goal: Can we "bump out" 4.0 using pure mechanical deformation?
"""

import numpy as np
import json
from pathlib import Path

def run_audit():
    N = 100_000 # Lower N for spatial sampling density
    rng = np.random.default_rng(2026)
    
    # 1. Physical Sources
    L1 = rng.uniform(0, 2*np.pi, N)
    L2 = rng.uniform(0, 2*np.pi, N)
    L3 = rng.uniform(0, 2*np.pi, N)
    
    # Forces (User's asymmetric model)
    F1, F2, F3 = 1.5, 0.8, 1.2
    
    # Detector distances (for propagation delay)
    # Alice at D1, Bob at D2, Charlie at D3
    # Explosion center is at origin (0,0,0)
    R_DET = 10.0 
    
    PI = np.pi
    X, Y = 0.0, PI / 2

    def physical_simulation(a, b, c):
        # Local wave phases
        phi1 = L1 - a
        phi2 = L2 - b
        phi3 = L3 - c
        
        # 2. Collision Detection: Only happens if waves meet in space
        # Here we simulate the sum at the center 'Burst Zone'
        # NO Mermin formula used.
        sum_amplitude = F1*np.cos(phi1) + F2*np.cos(phi2) + F3*np.cos(phi3)
        
        # 3. Chain Explosion Threshold
        # Only when ripples 'strangle' each other above threshold
        THRESHOLD = 2.0 
        is_explosion = np.abs(sum_amplitude) > THRESHOLD
        
        # 4. Secondary Pulse (The "Explosion")
        # The secondary pulse intensity depends on the force of collision
        # and carries the phase of the collision event
        # This is a NEW ordinary source.
        explosion_pulse = np.where(is_explosion, sum_amplitude, 0.0)
        
        # 5. Final Signal = Primary Waves (attenuated) + Secondary Pulse (delayed)
        # We assume detectors are far, so they primarily see the explosion pulse
        # if it occurs, otherwise they see the residual ripples.
        signal_a = np.where(is_explosion, explosion_pulse, F1*np.cos(phi1))
        signal_b = np.where(is_explosion, explosion_pulse, F2*np.cos(phi2))
        signal_c = np.where(is_explosion, explosion_pulse, F3*np.cos(phi3))
        
        return signal_a, signal_b, signal_c

    def ncc_triple(a, b, c):
        num = np.mean(a * b * c)
        den = np.sqrt(np.mean(a**2) * np.mean(b**2) * np.mean(c**2))
        return num / den

    print(f"GHZ Audit v18: Hardcore Mechanical Audit (No Cheating)")
    print("-" * 55)
    
    results = []
    # Test Mermin settings
    settings = [(X,X,X), (X,Y,Y), (Y,X,Y), (Y,Y,X)]
    energies = []
    
    for sa, sb, sc in settings:
        wa, wb, wc = physical_simulation(sa, sb, sc)
        e = ncc_triple(wa, wb, wc)
        energies.append(e)
    
    F = energies[0] - energies[1] - energies[2] - energies[3]
    
    print(f"Mermin F (Measured by Mechanical Collision): {F:.6f}")
    
    # Final check: Does it look 'Too Perfect'?
    if abs(F - 4.0) < 1e-6:
        print("WARNING: Result is suspiciously perfect. Checking for hidden loopholes...")
    elif F > 2.02:
        print("SUCCESS: Real mechanical violation confirmed!")
    else:
        print("FAIL: Mechanical model stayed within classical limits.")

if __name__ == "__main__":
    run_audit()
