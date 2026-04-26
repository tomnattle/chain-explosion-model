# GHZ Script Evolution Archive (After v10.3)

This file records why multiple GHZ scripts were created after `scripts/explore/ghz_medium_v10/v10_3_selection_tax_audit.py`, what was questioned, how we responded, and what the current stance is.  
The goal is to preserve real context, so future work can understand *why* these versions exist.

---

## 0. Starting Point (Main line around v10.3)

- Earlier work partially targeted whether GHZ-style high `F` (often discussed as 4) could be approached.
- This triggered recurring disputes on gating, selection, and metric definitions: mechanism gain vs selection gain.
- `v10_3_selection_tax_audit.py` was the first structured audit step: under one propagation mechanism, vary only gate strength and jointly track `F_gated`, `R_gated`, `D_gated = F * R`, and `selection_tax`.

---

## 1. v10.3 (Selection-tax audit)

Script: `scripts/explore/ghz_medium_v10/v10_3_selection_tax_audit.py`

### 1.1 Question at that stage

- Does high `F` come with high selection cost (low retention)?
- Under fixed physics/geometry, how does the curve move when only `gate_k` changes?

### 1.2 Method highlights

- Medium-wave three-body geometry and phase constraints;
- `soft_detector` with threshold `gate_k * RMS`, mapping to `{-1, 0, 1}`;
- Four GHZ settings combined into `F_gated`, with retention `R_gated` reported together.

### 1.3 Impact

- Established the "selection-tax" narrative: high score is not free and must disclose cost.

---

## 2. External challenge trigger (illustrative-curve issue)

### 2.1 Who challenged and what was challenged

- Challenge source: discussions around Claude Sonnet 4.6 (web version).
- Core challenge: whether `ghz_cost_benefit_curve_2p2_to_4p0.*` was a preset illustrative anchor, not computed evidence.

### 2.2 Fact-check result

- Legacy script `scripts/explore/ghz_threshold/plot_f_target_cost_curve.py` is indeed a parametric illustrative curve generator;
- Legacy metadata `artifacts/ghz_threshold_experiment/ghz_cost_benefit_curve_2p2_to_4p0.meta.json` explicitly says `illustrative_curve` and `retention_anchor_at_f_max`;
- Conclusion: that legacy curve should no longer be used as primary computed evidence.

---

## 3. v11 (first response to the anchor criticism)

Script: `scripts/explore/ghz_honest_cost_curve_v11.py`

### 3.1 Motivation

- Remove illustrative anchors and enforce "no preset endpoint" style: fixed retention grid, preregistration-like metadata.

### 3.2 What it did

- Three hidden-variable schemes;
- Fixed retention grid `0.05..1.00`;
- Unified CSV/JSON/MD/plot outputs.

### 3.3 Limitation (confirmed in later review)

- `v11` is not the same model as `ghz_medium_v10`; it is not a one-to-one reproduction of the medium-wave geometry pipeline.
- It is better interpreted as an alternate "honest baseline" experiment, not a direct refutation of `v10`.

---

## 4. v19 (extreme trigger exploration)

Script: `scripts/explore/ghz_loop_explosion_v19.py`

### 4.1 Motivation

- Push a high-threshold "chain explosion / burst trigger" idea to an extreme and observe three-body metric behavior.

### 4.2 Characteristics

- Strong burst-trigger narrative in both comments and implementation;
- High-selection-intensity exploratory script.

### 4.3 Role

- Made selection sensitivity explicit, but also intensified the core dispute:  
  is high score from mechanism, or from rule design?

---

## 5. v10.4 (return to medium-v10 computed curve)

Script: `scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`

### 5.1 Goal

- Produce a computed curve inside the original `ghz_medium_v10` model;
- Replace endpoint-anchored illustrative curves.

### 5.2 First release outcome

- Generated `V10_4_REAL_COST_CURVE.*`;
- Metadata marks `type = computed_curve`;
- Curve points are computed from fixed samples across gate sweep.

### 5.3 Second release strengthening (key step)

- Added matched-retention random control:
  - output `F_gated`;
  - output `F_random_mean ± std` at the same retention levels.

### 5.4 How this changed the conclusion

- It clearly separates:
  - not "random dropping gives the same high score";
  - high `F` is strongly tied to the amplitude-gating rule;
  - therefore high values should be interpreted as post-selection amplification, not full-sample mechanism evidence.

---

## 6. Paper narrative repositioning (already applied)

- Replaced legacy illustrative-curve references with `V10_4_REAL_COST_CURVE.*`;
- Shifted narrative from "trying to reproduce F=4" to "auditing detector/selection-rule sensitivity of F";
- Added matched-retention random controls to reduce one-curve misinterpretation.

---

## 7. Current real stance (no avoidance version)

1. **Legacy illustrative-curve issue is real**: that old figure should not be used as primary evidence.  
2. **v10.4 is computed evidence**: reproducible within the medium-v10 main model.  
3. **High F is rule-coupled**: amplitude gating can push high values; matched-retention random controls do not reproduce the same level.  
4. **Most stable claim is not "overturning quantum theory"**: it is that high-correlation metrics are highly sensitive to retention protocols, so dropped samples and selection rules must be first-class reported results.  
5. **Current team working hypothesis (not final verdict)**:  
   - "quantum is likely non-interference" is kept as a directional working hypothesis;  
   - this is not a final theorem, but a driver for subsequent stress tests and counter-challenge tasks.

---

## 8. Why this archive must exist

- Without it, future readers only see filenames and may misread why `v11`, `v19`, and `v10_4` coexist.
- In reality, they correspond to successive dispute responses:  
  **illustrative-curve challenge -> no-anchor response -> extreme-trigger exploration -> return to main-model computed curve + random controls**.

---

## 9. Interface for next tasks

Recommended default context package for all next GHZ tasks:

- Main model script: `scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`
- Evidence artifacts: `artifacts/ghz_medium_v10/V10_4_REAL_COST_CURVE.*`
- Dispute-context scripts: `scripts/explore/ghz_honest_cost_curve_v11.py`, `scripts/explore/ghz_loop_explosion_v19.py`
- This archive: `artifacts/ghz_medium_v10/V10_4_STORY_ARCHIVE.en.md`

> This keeps every new version answerable on three points:  
> (1) which challenge it responds to; (2) relation to the v10 main model; (3) which conclusion boundary it changes.
