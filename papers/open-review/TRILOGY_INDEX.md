# Audit Trilogy Index

## Overview

This index summarizes the **three current Zenodo deposits** for the Bell / GHZ audit line (`papers_final` bilingual PDFs). Use these DOIs for citation and reproducibility; older Zenodo record IDs are **not** the canonical references for this edition.

## Paper I — Bell / CHSH (NIST denominator audit)

- Title: *Denominator-Audit Analysis of Bell/CHSH Statistics: Identifying Accounting Fraud in Pairing Rules* / 贝尔不等式的分母审计：识别配对规则中的会计造假  
- **Zenodo:** https://zenodo.org/records/19784937  
- **DOI:** https://doi.org/10.5281/zenodo.19784937  
- Core finding: On the same NIST complete-blind stream, pairing tolerance **0.0** vs **15.0** (grid-index units) shifts `S_strict=2.336276` → `S_standard=2.839387` (Δ ≈ **+0.503111**); bootstrap stresses **protocol sensitivity**, not Tsirelson violation of a device.  
- Role: Public-data CHSH **denominator / pairing-window** audit.

## Paper II — GHZ (medium-v10, V10.4 in-silico)

- Title: *The Geometric Origin of GHZ Violation: An In-Silico Post-Selection Audit (medium-v10)* / GHZ 违背的几何起源（`medium-v10` 仿真后选择审计，非硬件复刻）  
- **Zenodo:** https://zenodo.org/records/19785022  
- **DOI:** https://doi.org/10.5281/zenodo.19785022  
- Core finding: In **`medium-v10`**, high Mermin-style `F_gated` tracks **amplitude gating** and **low retention**; matched-retention random controls fail to reproduce the gated lift — **selection mechanics in silico**, not a hardware replay claim.  
- Role: **V10.4** computed cost curve (`v10_4_real_cost_curve.py`); not `ghz_loop_explosion_v19.py`.

## Paper III — Audit trilogy (synthesis)

- Title: *The Audit Trilogy (V10.4)* — bilingual bundle covering Bell leg + GHZ V10.4 leg.  
- **Zenodo:** https://zenodo.org/records/19785083  
- **DOI:** https://doi.org/10.5281/zenodo.19785083  
- Core finding: Single document tying **NIST CHSH pairing audit** to **GHZ V10.4 `computed_curve`** with explicit **interpretation boundary** and reproducibility commands.  
- Role: One-stop **methodological** index for both frozen workflows.

## Shared method principles

1. Metric registry first (what enters the average).  
2. Protocol parallelism (same rows / same phase sample; change inclusion rules).  
3. Claim–artifact traceability (paths in repo).  
4. Bootstrap / controls where applicable (Bell: Tsirelson-in-CI; GHZ: matched-retention random).  

## Repository

- **Code / data:** https://github.com/tomnattle/chain-explosion-model  
- **Paper sources:** `papers_final/01_Bell_Audit`, `papers_final/02_GHZ_Audit`, `papers_final/03_Audit_Trilogy`  
- Session notes: `SESSION_ARCHIVE_2026-04-25.md`, `SESSION_ARCHIVE_2026-04-26.md` (if present)
