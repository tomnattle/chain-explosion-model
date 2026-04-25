# Bell No-Smuggling Audit v1

**Fixing:** ROUND2_NO_SMUGGLING_CHECKLIST.md (all boxes were [ ])

Overall: **INCOMPLETE**

| Status | Count |
|---|---|
| PASS | 7 |
| FAIL | 0 |
| WARN | 1 |
| MANUAL-REQUIRED | 1 |

## Results

### [OK] C1: PASS

No global/nonlocal keywords found in pairing/scoring functions. pair_events() and compute_E_S() take only local arguments.

### [OK] C2: PASS

Event pairing (pair_events) uses only time-window criterion. Outcome multiplication oa*ob in compute_E_S is post-pairing correlation computation, not inclusion filter. No joint-outcome-based exclusion found. Outcome ops at lines: [117]

### [OK] C3: PASS

No threading, IPC, or synchronization primitives found. Alice and Bob events are processed sequentially in a single process.

### [MR] C4: MANUAL-REQUIRED

The pairing algorithm reads B-side events to find time-matches, which is causally allowed (Alice knows when B fired, not what B measured). However, manual verification needed to confirm: (1) Alice outcome is determined before pairing, (2) B's setting is never used to determine A's outcome. Cross-side references in source: ['B[j]', 'setB', 'outB', 'sb']

### [OK] C5: PASS

Two independent runs with window=0 produced identical results: S=2.3362758582, pairs=136632. Deterministic confirmed.

### [OK] C6: PASS

chsh() function defined at lines [26] matches preregistered formula 'S = Eab + Eabp + Eapb - Eapbp'. No alternative formula found.

### [??] M1: WARN

simulate_events() uses lam independent of settings (rho(lambda) = uniform, NOT rho(lambda|a,b)). For the real NIST CSV path, no explicit lambda model exists — outcomes are empirical. Measurement dependence claim cannot be evaluated on real data path. MANUAL-REQUIRED: Document which path is used for the Bell claim.

### [OK] M2: PASS

B-side settings (setB, sb) only appear in compute_E_S for post-pairing statistics. Not found in outcome generation. Setting references at lines: [64, 66, 75, 102, 103, 114, 124, 125, 126, 127]. Outcome generation at lines: {'outA =': [69], 'outB =': [70], 'oa =': [115], 'ob =': [102, 116]}

### [OK] M3: PASS

Real NIST data path: outcomes are pre-recorded events, trivially local (no computation needed). Simulation fallback: outA = f(lam, setA), outB = f(lam, setB) — each side's outcome depends only on its own setting.

## What MANUAL-REQUIRED means

These items cannot be verified by automated code inspection alone.
They require a human to read the code and attest to each property.
Until they are attested, the checklist is INCOMPLETE and Bell-interpretation
claims under Round 2 remain procedurally unverified.