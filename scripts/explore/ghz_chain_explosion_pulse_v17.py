#!/usr/bin/env python3
"""
GHZ Global Pulse Synchrony Audit — v17
---------------------------------------
MODEL: The "Chain Explosion" Secondary Emitter.
Logic:
1. Local waves (A, B, C) interfere.
2. Constructive interference triggers a "Chain Explosion" (Secondary Source).
3. This secondary source emits a phase-locked pulse reaching all 3 observers.
4. Total Signal = (1-w)*LocalWaves + w*ExplosionPulse.
"""

import numpy as np
import json
from pathlib import Path

def run_audit():
    N = 1_000_000
    rng = np.random.default_rng(2026)
    
    # 1. Local Hidden Phases
    L1 = rng.uniform(0, 2*np.pi, N)
    L2 = rng.uniform(0, 2*np.pi, N)
    L3 = rng.uniform(0, 2*np.pi, N)
    
    PI = np.pi
    X, Y = 0.0, PI / 2

    def get_pulse_outcomes(a, b, c, weight=0.5):
        # Phase Loop Phases
        phi_a = (L1 - L2) - a
        phi_b = (L2 - L3) - b
        phi_c = (L3 - L1) - c
        
        # Primary Waves
        wa = np.cos(phi_a)
        wb = np.cos(phi_b)
        wc = np.cos(phi_c)
        
        # 2. Triggering the "Chain Explosion"
        # The explosion happens when all three ripples are in a specific phase alignment
        # We use the Mermin identity cos(a+b+c) as the trigger probability
        # In a real water surface, this is the 'Constructive Interference Peak'
        trigger_phase = -(a + b + c)
        
        # The Explosion Pulse is a SHARED source (it's the same explosion)
        # Therefore, its phase is identical for all three observers.
        # Its sign is determined by the coherence of the trigger.
        pulse = np.cos(trigger_phase)
        
        # 3. Final Measured Signal: Mixture of local ripples and the global explosion pulse
        ra = (1 - weight) * wa + weight * pulse
        rb = (1 - weight) * wb + weight * pulse
        rc = (1 - weight) * wc + weight * pulse
        
        return ra, rb, rc

    def ncc_triple(a, b, c):
        num = np.mean(a * b * c)
        den = np.sqrt(np.mean(a**2) * np.mean(b**2) * np.mean(c**2))
        return num / den

    print(f"GHZ Audit v17: The Rise of the Chain Explosion (Weight w)")
    print("-" * 50)
    
    results = []
    # Sweeping the explosion strength
    for w in [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]:
        wa, wb, wc = get_pulse_outcomes(X, X, X, w)
        e_xxx = ncc_triple(wa, wb, wc)
        
        wa, wb, wc = get_pulse_outcomes(X, Y, Y, w)
        e_xyy = ncc_triple(wa, wb, wc)
        
        wa, wb, wc = get_pulse_outcomes(Y, X, Y, w)
        e_yxy = ncc_triple(wa, wb, wc)
        
        wa, wb, wc = get_pulse_outcomes(Y, Y, X, w)
        e_yyx = ncc_triple(wa, wb, wc)
        
        F = e_xxx - e_xyy - e_yxy - e_yyx
        print(f"Explosion Weight w={w:.1f} -> Mermin F = {F:.6f}")
        results.append({"w": w, "F": F})

    out_dir = Path("artifacts/ghz_audit_v17")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "GHZ_V17_PULSE_DATA.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_audit()
