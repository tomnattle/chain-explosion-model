# Top-3 Quantum Lead Emails (Ready to Send)

Use these as copy-paste drafts.  
Each email asks exactly one technical question and keeps the scope on reproducible data analysis.

---

## 1) Scott Aaronson (theory / complexity boundary)

Subject: Bell S-value sensitivity to analysis rules (same public dataset)

Dear Prof. Aaronson,

I found a reproducible sensitivity in public NIST Bell data: changing only the pairing window shifts binary CHSH S from 2.336 to 2.839 on the same event stream.
I would value one technical check before external submission.

Single question:  
Does the usual Tsirelson-bound interpretation implicitly assume a fixed event-pairing rule, and if so, should pairing-window choice be treated as an explicit hypothesis variable rather than a hidden implementation detail?

Reproducible snapshot (public data pipeline):
- same dataset, binary CHSH:
  - strict pairing window `0.0` -> `S = 2.336276` (95% CI `[2.295151, 2.378669]`)
  - wide pairing window `15.0` -> `S = 2.839387` (95% CI `[2.820420, 2.857413]`)
- delta from pairing rule alone: `+0.503111`

We do not claim a Tsirelson violation. Our point is sensitivity: the same raw dataset spans a wide S-range under different declared analysis rules.
We also do not claim that this result alone establishes a replacement ontology for quantum theory.

Repository: <https://github.com/tomnattle/chain-explosion-model>  
Key figure: `artifacts/reports/ncc_singles_bridge_real.png`  
Bridge report: `artifacts/reports/ncc_singles_bridge_real.json`
E(Δ) bridge figure/report: `artifacts/reports/cnorm_e_delta_bridge_real.png`, `artifacts/reports/cnorm_e_delta_bridge_real.md`

If useful, I can send a 2-line command block for exact rerun.

Best regards,  
[Your Name]

---

## 2) John Martinis (hardware / decoherence engineering)

Subject: Engineering question: pairing-window sensitivity in Bell metrics

Dear Prof. Martinis,

I found a reproducible sensitivity in public NIST Bell data: changing only the pairing window shifts binary CHSH S from 2.336 to 2.839 on the same event stream.
I am preparing an engineering-focused analysis note on detector/pairing effects and would highly value one practical check.

Single question:  
In superconducting/photonic entanglement benchmarking workflows, should coincidence pairing-window selection be reported as a first-class parameter, since it can materially shift reported correlation metrics on the same event stream?

Reproducible snapshot (public data pipeline):
- same dataset, binary CHSH:
  - strict pairing window `0.0` -> `S = 2.336276` (95% CI `[2.295151, 2.378669]`)
  - wide pairing window `15.0` -> `S = 2.839387` (95% CI `[2.820420, 2.857413]`)
- delta from pairing rule alone: `+0.503111`

`C_norm = coincidences / sqrt(singles_A * singles_B)` is the experimental counterpart of the NCC denominator; it is not a CHSH-equivalence proof, but an observable bridge quantity.
We do not claim a Tsirelson violation.
We also do not claim that this result alone establishes a replacement ontology for quantum theory.

Repository: <https://github.com/tomnattle/chain-explosion-model>  
Key figure: `artifacts/reports/ncc_singles_bridge_real.png`  
Bridge report: `artifacts/reports/ncc_singles_bridge_real.json`
E(Δ) bridge figure/report: `artifacts/reports/cnorm_e_delta_bridge_real.png`, `artifacts/reports/cnorm_e_delta_bridge_real.md`

I can share a minimal rerun command immediately if convenient.

Best regards,  
[Your Name]

---

## 3) Stephanie Wehner (network / operational foundations)

Subject: Operational question: analysis-rule sensitivity in Bell statistics

Dear Prof. Wehner,

I found a reproducible sensitivity in public NIST Bell data: changing only the pairing window shifts binary CHSH S from 2.336 to 2.839 on the same event stream.
I am trying to keep a strict boundary between operational statistics and ontology claims, and would value one protocol-focused check.

Single question:  
For protocol-level comparability (e.g., network/QKD contexts), should pairing-window choice be explicitly standardized in addition to statistic definition, given that different windows on the same data can shift CHSH S by about 0.5?

Reproducible snapshot (public data pipeline):
- same dataset, binary CHSH:
  - strict pairing window `0.0` -> `S = 2.336276` (95% CI `[2.295151, 2.378669]`)
  - wide pairing window `15.0` -> `S = 2.839387` (95% CI `[2.820420, 2.857413]`)
- delta from pairing rule alone: `+0.503111`

`C_norm = coincidences / sqrt(singles_A * singles_B)` is the experimental counterpart of the NCC denominator; it is not a CHSH-equivalence proof, but an observable bridge quantity.
We do not claim a Tsirelson violation.
We also do not claim that this result alone establishes a replacement ontology for quantum theory.

Repository: <https://github.com/tomnattle/chain-explosion-model>  
Key figure: `artifacts/reports/ncc_singles_bridge_real.png`  
Bridge report: `artifacts/reports/ncc_singles_bridge_real.json`
E(Δ) bridge figure/report: `artifacts/reports/cnorm_e_delta_bridge_real.png`, `artifacts/reports/cnorm_e_delta_bridge_real.md`

If helpful, I can also provide a concise methods note (1 page max).

Best regards,  
[Your Name]
