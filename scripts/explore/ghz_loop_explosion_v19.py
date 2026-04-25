#!/usr/bin/env python3
"""
GHZ Honest Loop Explosion — v19
-------------------------------
AUDIT PROTOCOL:
1. RESTORE Geometric Phase Loop (L1-L2, L2-L3, L3-L1). This is the 'Three Stones' topology.
2. NO Mermin formulas.
3. TRIGGER: Only 'Dazzling' events (Amplitude > Threshold) are recorded.
4. NON-LINEAR: The explosion emits a secondary pulse that dominates the signal.
"""

import numpy as np
import json
from pathlib import Path

def run_audit():
    N = 1_000_000
    rng = np.random.default_rng(2026)
    
    # 1. Topology: 3 stones in a loop (Phase differences)
    L1 = rng.uniform(0, 2*np.pi, N)
    L2 = rng.uniform(0, 2*np.pi, N)
    L3 = rng.uniform(0, 2*np.pi, N)
    
    # Emitters are the DIFFERENCES (Interference as source)
    # This is the 'Ripple Interaction' you described.
    Phi_AB = L1 - L2
    Phi_BC = L2 - L3
    Phi_CA = L3 - L1
    
    PI = np.pi
    X, Y = 0.0, PI / 2

    def simulation(a, b, c, threshold=2.0):
        # Alice, Bob, Charlie measure the adjacent ripple pairs
        wa = np.cos(Phi_AB - a)
        wb = np.cos(Phi_BC - b)
        wc = np.cos(Phi_CA - c)
        
        # 2. Local Interference Intensity
        # This is the 'Mechanical Force' at each detector
        total_force = np.abs(wa + wb + wc)
        
        # 3. The "Chain Explosion" Trigger (The 'Dazzling Light')
        # We only record events where the interference is constructive and powerful
        is_burst = total_force > threshold
        
        # If burst, the signal is a sharp pulse; if not, it's near zero (suppressed)
        # This simulates the "Chain Explosion" where low-energy ripples are ignored
        sig_a = np.where(is_burst, np.sign(wa), 0.0)
        sig_b = np.where(is_burst, np.sign(wb), 0.0)
        sig_c = np.where(is_burst, np.sign(wc), 0.0)
        
        return sig_a, sig_b, sig_c

    def ncc_triple(a, b, c):
        # We only count indices where a burst occurred
        wa, wb, wc = simulation(a, b, c, threshold=2.2) # High threshold for 'Chain Explosion'
        mask = (wa != 0)
        if np.sum(mask) == 0: return 0.0
        
        num = np.mean(wa[mask] * wb[mask] * wc[mask])
        den = np.sqrt(np.mean(wa[mask]**2) * np.mean(wb[mask]**2) * np.mean(wc[mask]**2))
        return num / den

    print(f"GHZ Audit v19: Honest Loop Explosion (Threshold Trigger)")
    print("-" * 55)
    
    results = []
    settings = [(X,X,X), (X,Y,Y), (Y,X,Y), (Y,Y,X)]
    energies = []
    
    for sa, sb, sc in settings:
        e = ncc_triple(sa, sb, sc)
        energies.append(e)
    
    F = energies[0] - energies[1] - energies[2] - energies[3]
    
    print(f"E(XXX): {energies[0]:.4f}, E(XYY): {energies[1]:.4f}")
    print(f"Final Mermin F: {F:.6f}")
    
    if F > 3.0:
        print("ALERT: BREAKTHROUGH! The Loop-Explosion model has crossed 3.0!")
    elif F > 2.0:
        print("SUCCESS: Bell/Mermin violation via mechanical threshold.")
    else:
        print("FAIL: Still stuck in the classical mud.")

if __name__ == "__main__":
    run_audit()
