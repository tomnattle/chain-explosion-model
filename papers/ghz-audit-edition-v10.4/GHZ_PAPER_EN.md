# The Geometric Origin of GHZ Violation: A Post-Selection Audit of the "Smoking Gun"

**Author**: Tom Nattle (Audit Assistant: Antigravity AI)  
**Date**: April 2026  
**Project**: Chain-Explosion Model / Audit Series  
**Version**: 1.1.0 (Audit Edition)

---

## Abstract
The Greenberger-Horne-Zeilinger (GHZ) state is historically regarded as the "smoking gun" of quantum non-locality, ostensibly providing a perfect correlation ($F=4.0$) without statistical inequalities. This paper presents a definitive post-selection audit of the GHZ violation. We demonstrate that the apparent violation is not a sign of non-local entanglement but a statistical artifact driven by amplitude-gating rules and detection thresholds. Using the `V10.4` real cost curve, we show that high $F$ values are strictly coupled to low retention rates, while matched-retention random controls fail to reproduce the effect. We propose that "entanglement" may be a geometric mathematical illusion, suggesting that the foundations of quantum computing may rest on solving geometric problems rather than physical non-locality.

## 1. Introduction: The Audit of the Accounting Rules
For decades, the Bell and GHZ violations have been misinterpreted as evidence for non-locality. Our audit reveals that this misinterpretation stems from "accounting fraud" in data processing: the failure to report the sensitivity of results to the data being discarded. We propose that "photons" are not discrete particles but threshold-triggered events in a continuous field. The "success" of quantum experiments often relies on throwing away 90% or more of "bad data"—a practice that works for small-scale experiments but collapses under the scale required for practical quantum computing.

## 2. Methodology: Post-Selection and Selection Tax
We model the GHZ setup using a medium-wave propagation model (`medium-v10`) with three local phase-locked sources. Instead of forcing a "perfect success," we sweep the gate strength ($gate\_k$) of a soft detector.
- **Selection Rule**: Events are only recorded if the interference amplitude exceeds a threshold.
- **Random Control**: For every gated result, we generate a random subsample with the same retention ratio to distinguish between mechanism-driven gains and statistical noise.

## 3. Results: The Real Cost of "Entanglement"
The `V10.4` results reveal a direct trade-off between correlation strength and data retention.

![GHZ Real Cost Curve](figures/V10_4_REAL_COST_CURVE.png)
*Figure 1: The GHZ Real Cost Curve. The blue line (F_gated) shows that high F values are only achieved by discarding the majority of data. The green line (F_random) shows the statistical baseline. The gap between them identifies the specific "Selection Rules" used to generate the illusion of violation.*

## 4. Discussion: The "30cm Truth" and the Geometric Illusion
In Bell experiments, a 1-nanosecond shift in the timing window—the distance light travels in just 30 cm—can transform "classical" results into "quantum" ones. This "30cm Truth" reveals that experimentalists hold a "remote control" over the results through their choice of coincidence windows and amplitude gates.

### 4.1 Implications for Quantum Computing
The failure of large-scale quantum computing after decades of investment may be explained by the "hollow foundation" revealed here. AI succeeds because it consumes all real data; quantum computing "succeeds" in labs by discarding the data that doesn't fit the model. If entanglement is a geometric illusion, then quantum computers are not harnessing non-local power—they are inadvertently solving complex geometric problems through brute-force filtering.

## 5. Conclusion: An Anti-Counterfeiting Guide
We do not claim that quantum mechanics is "wrong" in its mathematical predictions, but we assert that its foundational experiments are "unbalanced accounts." We have documented and archived the methods used to "balance the books"—pairing windows, amplitude gating, and binarization. We invite the physics community to provide the "discarded 90%" of their raw data for audit.

---
**Data Availability**: All simulation code, raw CSV data, and audit logs are included in the Zenodo package.
**Primary Verification Script**: `v10_4_real_cost_curve.py`
