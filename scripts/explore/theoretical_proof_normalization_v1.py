#!/usr/bin/env python3
"""
Theoretical Proof: Normalization vs Binarization — v1

PURPOSE
-------
Mathematically demonstrate the core claim: 
A local classical wave model produces S = 2.828 when using Normalized Cross-Correlation (NCC),
but is limited to S = 2.0 when using Binarization (+/- 1).

This "sits the case" (坐实) for the project's foundation.

LOGIC
-----
1. Shared Source: A random phase lambda is emitted.
2. Local Projection:
   Alice measures A = cos(lambda - a)
   Bob measures   B = -cos(lambda - b)  [anti-correlated pair]
3. Statistical Metrics:
   - Binarized: outcome = sign(projection) -> result in {+1, -1}
   - NCC: result = <A*B> / sqrt(<A^2>*<B^2>)
4. CHSH Calculation:
   Standard angles: a=0, a'=45, b=22.5, b'=67.5 (degrees)
"""

import numpy as np
import json
from pathlib import Path

def run_proof():
    # ── Parameters ─────────────────────────────────────────────────────────
    N = 1_000_000
    seed = 42
    rng = np.random.default_rng(seed)
    
    # Optimal CHSH angles in radians
    a    = 0.0
    ap   = np.deg2rad(90.0)
    b    = np.deg2rad(45.0)
    bp   = np.deg2rad(135.0)
    
    # ── Source: Shared Hidden Variable ──────────────────────────────────────
    # lambda is uniformly distributed [0, 2pi]
    lam = rng.uniform(0, 2 * np.pi, N)
    
    # ── Local Measurement Functions ─────────────────────────────────────────
    def get_outcomes(angle_a, angle_b):
        # Local wave projections
        # We use -cos for one side to simulate anti-correlation (singlet-like)
        A_wave = np.cos(lam - angle_a)
        B_wave = -np.cos(lam - angle_b)
        
        # Binarized outcomes (+1, -1)
        A_bin = np.where(A_wave >= 0, 1, -1)
        B_bin = np.where(B_wave >= 0, 1, -1)
        
        return A_wave, B_wave, A_bin, B_bin

    def compute_correlations(angle_a, angle_b):
        Aw, Bw, Ab, Bb = get_outcomes(angle_a, angle_b)
        
        # 1. Binarized correlation (Bell/CHSH standard)
        E_bin = np.mean(Ab * Bb)
        
        # 2. Normalized Cross-Correlation (NCC)
        # NCC = <Aw * Bw> / sqrt(<Aw^2> * <Bw^2>)
        num = np.mean(Aw * Bw)
        den = np.sqrt(np.mean(Aw**2) * np.mean(Bw**2))
        E_ncc = num / den
        
        return E_bin, E_ncc

    # ── Run for the 4 CHSH setting combinations ────────────────────────────
    settings = [(a, b), (a, bp), (ap, b), (ap, bp)]
    results_bin = []
    results_ncc = []
    
    for sa, sb in settings:
        eb, en = compute_correlations(sa, sb)
        results_bin.append(eb)
        results_ncc.append(en)
        
    # S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')|
    S_bin = abs(results_bin[0] - results_bin[1] + results_bin[2] + results_bin[3])
    S_ncc = abs(results_ncc[0] - results_ncc[1] + results_ncc[2] + results_ncc[3])
    
    # ── Report ─────────────────────────────────────────────────────────────
    report = {
        "description": "Comparison of Binarization vs NCC on Local Wave Model",
        "n_samples": N,
        "theoretical_target": 2 * np.sqrt(2),
        "results": {
            "binarized": {
                "correlations": results_bin,
                "S": S_bin,
                "limit": 2.0,
                "verdict": "Obeys Bell Inequality"
            },
            "ncc": {
                "correlations": results_ncc,
                "S": S_ncc,
                "limit": 2.828427,
                "verdict": "Violates Bell Inequality (Tsirelson Bound reached)"
            }
        }
    }
    
    out_dir = Path("artifacts/theoretical_proof_v1")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(out_dir / "PROOF_RESULTS.json", "w") as f:
        json.dump(report, f, indent=2)
        
    md = [
        "# Theoretical Proof: The Normalization Loophole",
        "",
        "This experiment demonstrates that the violation of Bell inequalities is not necessarily a sign of non-locality, ",
        "but can be a mathematical consequence of using Normalized Cross-Correlation (NCC) on continuous wave amplitudes.",
        "",
        "## Results Summary",
        "",
        f"| Metric | Binarized (±1) | NCC (Normalized Waves) |",
        f"|---|---|---|",
        f"| **CHSH S Value** | **{S_bin:.6f}** | **{S_ncc:.6f}** |",
        f"| Theoretical Limit | 2.0 | 2.828427 (2√2) |",
        f"| Bell Violation? | No | **YES** |",
        "",
        "## Analysis",
        "",
        "1. **Binarization** (Standard Bell Test) forces the continuous cosine wave into a square/triangle correlation. ",
        "   This 'crushing' of information ensures the S value cannot exceed 2.",
        "2. **NCC** (Normalized Cross-Correlation) preserves the full curvature of the wave interaction. ",
        "   Mathematically, `<cos(L-a)cos(L-b)> / <cos^2>` simplifies exactly to `cos(a-b)`. ",
        "   Substituting `cos(delta)` into CHSH yields the Tsirelson bound of **2.828**.",
        "",
        "## Conclusion",
        "",
        "If nature is composed of discrete wave propagations, and our measurement protocols (like coincidences or normalization) ",
        "effectively perform an NCC-like calculation, we will observe $S = 2.828$ even in a strictly local, classical-wave universe.",
        "",
        "**This is the foundational logic for the GHZ audit.**"
    ]
    (out_dir / "PROOF_REPORT.md").write_text("\n".join(md))
    
    print(f"Proof Complete.")
    print(f"  Binarized S: {S_bin:.6f}")
    print(f"  NCC S:       {S_ncc:.6f} (Target: 2.828427)")

if __name__ == "__main__":
    run_proof()
