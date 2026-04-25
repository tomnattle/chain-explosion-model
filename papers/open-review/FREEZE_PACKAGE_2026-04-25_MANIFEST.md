# Freeze Package Manifest (2026-04-25)

Package: `papers/open-review/FREEZE_PACKAGE_2026-04-25.zip`  
Freeze ID: `bell-freeze-2026-04-25`

## What this package is

This package is a read-only snapshot of the Bell audit candidate version used for external technical outreach.  
It includes manuscript drafts, key statistical evidence, reproducibility outputs, and outreach-ready materials.

## Included files and purpose

1. `papers/bell-audit-paper/draft.en.md`  
   - English full draft (main narrative and boundaries).
2. `papers/bell-audit-paper/draft.zh.md`  
   - Chinese full draft (same claim scope).
3. `papers/bell-audit-paper/ABSTRACT_FINAL.en.md`  
   - External English abstract.
4. `papers/bell-audit-paper/ABSTRACT_FINAL.zh.md`  
   - External Chinese abstract.
5. `papers/bell-audit-paper/tables/table2_key_results.md`  
   - Key result table with S values and CI.
6. `papers/READY_FOR_REVIEW.md`  
   - Review readiness status.
7. `artifacts/reports/chsh_bootstrap_ci_standard15.json`  
   - Bootstrap CI for standard window CHSH.
8. `artifacts/reports/chsh_bootstrap_ci_strict0.json`  
   - Bootstrap CI for strict window CHSH.
9. `artifacts/reports/ncc_singles_bridge_real.json`  
   - NCC denominator observability bridge (real events).
10. `artifacts/reports/ncc_singles_bridge_real.png`  
    - Visual summary for the NCC bridge.
11. `artifacts/reports/cnorm_e_delta_bridge_real.md`  
    - `C_norm/C_signed_norm -> E(Δ)` bridge report.
12. `artifacts/reports/cnorm_e_delta_bridge_real.png`  
    - `E(Δ)` bridge figure.
13. `papers/open-review/outreach_quantum_pack/EMAILS_TOP3_QUANTUM_LEADS.en.md`  
    - Outreach drafts for three target experts.
14. `papers/open-review/outreach_quantum_pack/SEND_CHECKLIST_FINAL.zh.md`  
    - Final send checklist (Chinese).

## Frozen claim boundary (important)

- Same event stream, binary CHSH:
  - strict window `0.0`: `S=2.336276`
  - standard window `15.0`: `S=2.839387`
  - delta: `+0.503111` (analysis-rule sensitivity evidence)
- Bootstrap (`n=2000`):
  - strict CI95: `[2.295151, 2.378669]`
  - standard CI95: `[2.820420, 2.857413]`
- `2sqrt(2)=2.828427` lies within standard CI95:  
  **No Tsirelson-violation claim is made.**

## Integrity

- File hashes are recorded in `papers/open-review/FREEZE_PACKAGE_2026-04-25.sha256`.
