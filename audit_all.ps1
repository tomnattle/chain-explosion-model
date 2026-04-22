param(
    [string]$PolicyPath = "docs/claim_audit_policy.json",
    [string]$BatchConfig = "docs/claim_audit_batch_cases.json",
    [int]$FailThreshold = 50
)

Write-Host "Running claim audit all outputs..." -ForegroundColor Cyan

./activate_conda.ps1

python "scripts/explore/claim_audit.py" `
  --out-json "docs/claim_audit_report.json" `
  --out-csv "docs/claim_audit_report.csv" `
  --out-markdown "docs/claim_audit_report.md" `
  --out-html "docs/claim_audit_report.html" `
  --policy-json $PolicyPath

python "scripts/explore/claim_audit.py" `
  --batch-json $BatchConfig `
  --out-json "docs/claim_audit_batch_report.json" `
  --out-csv "docs/claim_audit_batch_report.csv" `
  --out-markdown "docs/claim_audit_batch_report.md" `
  --out-html "docs/claim_audit_batch_report.html" `
  --policy-json $PolicyPath `
  --fail-on-risk-threshold $FailThreshold

