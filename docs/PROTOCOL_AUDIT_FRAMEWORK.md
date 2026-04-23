# Protocol-Layer Audit Framework

## Why

Metric comparison alone is not enough.  
For Bell-style claims, ambiguity can enter at multiple layers:

1. raw event construction
2. binarization/filtering
3. correlation definition
4. claim mapping

This framework adds a second audit axis: **protocol consistency**.

---

## Layered checklist

### A. Raw Event Layer
- dataset source is explicit
- pairing rule is explicit
- time window is explicit

### B. Binarization/Filter Layer
- outcome space is explicit (binary or continuous)
- threshold/postselection rule is explicit

### C. Correlation Layer
- E definition is explicit (`E_binary` / `E_raw` / `E_ncc`)
- normalization rule is explicit

### D. Claim Layer
- final statement is explicit
- scope label is explicit (`chsh_binary` / `continuous_metric` / `audit_only`)
- non-claims are explicit

---

## Tooling

- Script: `scripts/explore/protocol_audit.py`
- Template: `docs/protocol_template.json`

Run:

```powershell
./activate_conda.ps1
python "scripts/explore/protocol_audit.py" `
  --protocol-json "docs/protocol_template.json" `
  --out-json "docs/protocol_audit_report.json"
```

---

## Output semantics

The tool does not decide physics truth.  
It audits whether the claim package is protocol-complete and object-consistent.

- score < 50: high protocol risk
- 50-79: medium protocol risk
- >= 80: low protocol risk

