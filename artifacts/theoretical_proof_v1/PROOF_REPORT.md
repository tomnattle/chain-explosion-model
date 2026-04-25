# Theoretical Proof: The Normalization Loophole

This experiment demonstrates that the violation of Bell inequalities is not necessarily a sign of non-locality, 
but can be a mathematical consequence of using Normalized Cross-Correlation (NCC) on continuous wave amplitudes.

## Results Summary

| Metric | Binarized (¡À1) | NCC (Normalized Waves) |
|---|---|---|
| **CHSH S Value** | **2.000000** | **2.828427** |
| Theoretical Limit | 2.0 | 2.828427 (2¡Ì2) |
| Bell Violation? | No | **YES** |

## Analysis

1. **Binarization** (Standard Bell Test) forces the continuous cosine wave into a square/triangle correlation. 
   This 'crushing' of information ensures the S value cannot exceed 2.
2. **NCC** (Normalized Cross-Correlation) preserves the full curvature of the wave interaction. 
   Mathematically, `<cos(L-a)cos(L-b)> / <cos^2>` simplifies exactly to `cos(a-b)`. 
   Substituting `cos(delta)` into CHSH yields the Tsirelson bound of **2.828**.

## Conclusion

If nature is composed of discrete wave propagations, and our measurement protocols (like coincidences or normalization) 
effectively perform an NCC-like calculation, we will observe $S = 2.828$ even in a strictly local, classical-wave universe.

**This is the foundational logic for the GHZ audit.**