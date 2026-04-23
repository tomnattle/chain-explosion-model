# Audit Suite

`audit_suite.py` is a unified runner that combines:

1. claim-level metric audit (`claim_audit`)
2. protocol-layer audit (`protocol_audit`)

and computes a weighted suite score.

## Run

```powershell
./activate_conda.ps1
python "scripts/explore/audit_suite.py" `
  --protocol-json "docs/protocol_template.json" `
  --policy-json "docs/claim_audit_policy.json" `
  --out-json "docs/audit_suite_report.json"
```

## Optional gate

```powershell
python "scripts/explore/audit_suite.py" `
  --protocol-json "docs/protocol_template.json" `
  --fail-on-suite-threshold 60
```

If suite score is below threshold, exits with code `2`.

## Output

- `suite_risk.score_0_to_100`
- `claim_audit` full report
- `protocol_audit` full report

