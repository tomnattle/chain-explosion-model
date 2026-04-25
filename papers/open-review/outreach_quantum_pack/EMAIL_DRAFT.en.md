# Quantum Lead Outreach Draft (EN)

Subject: One reproducible check on Bell data metrics: singles/coincidences normalization

Dear Prof. [Name],

I am running a reproducible reanalysis pipeline on public Bell-test data, and I would value one technical check before external submission.

Core check (single question):
In your data-analysis practice, is the quantity `coincidences / sqrt(singles_A * singles_B)` a defensible normalization bridge for comparing setting-pair dependence?

Current reproducible snapshot:
- NCC source: `events_csv`
- Events CSV: `D:\workspace\chain-explosion-model\data\nist_completeblind_side_streams.csv`
- strict window/pairs: `0.25` / `136632`
- standard window/pairs: `15.0` / `148670`
- CHSH strict S: `2.327428`
- CHSH standard S: `2.836171`

Repository: https://github.com/tomnattle/chain-explosion-model

If useful, I can send a minimal command block and exact artifact paths for direct replication.

Best regards,
[Your Name]

---

Preflight gate: PASS
