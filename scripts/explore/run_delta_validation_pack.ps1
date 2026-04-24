param(
    [string]$Hdf5Path = "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5",
    [string]$OutDir = "artifacts/public_validation_pack",
    [string]$PolicyJson = "configs/delta_closure_policy.json",
    [int]$BootstrapMain = 3000,
    [int]$BootstrapAlt = 2000,
    [int]$Seed = 20260422,
    [switch]$SkipCondaActivation
)

$ErrorActionPreference = "Stop"

function Run-Step {
    param(
        [string]$Title,
        [scriptblock]$Action
    )
    Write-Host ""
    Write-Host "==> $Title" -ForegroundColor Cyan
    & $Action
}

function New-ClosureChecklist {
    param(
        [string]$TargetPath,
        [string]$Hdf5,
        [int]$SeedValue
    )

    $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $runId = Get-Date -Format "yyyyMMdd_HHmmss"
    $hash = "N/A"
    if (Test-Path $Hdf5) {
        try {
            $hash = (Get-FileHash -Algorithm SHA256 -Path $Hdf5).Hash
        } catch {
            $hash = "HASH_ERROR"
        }
    }

    $content = @"
# DELTA Closure Checklist

- Generated at: `$now`
- Run ID: `$runId`
- Data path: `$Hdf5`
- Data SHA256: `$hash`
- Seed: `$SeedValue`

| Run ID | Mapping | Definition Closure | Dimensional Closure | Process Closure | Statistical Closure | Failure Triggered | Notes |
|---|---|---|---|---|---|---|---|
| `$runId` | half_split | TBD | TBD | TBD | TBD | TBD | Fill after reading generated reports |
| `$runId` | parity | TBD | TBD | TBD | TBD | TBD | Fill after reading generated reports |
| `$runId` | quadrant_split | TBD | TBD | TBD | TBD | TBD | Fill after reading generated reports |

## Referenced Outputs

- `NIST_E_DELTA_RIGOR_REPORT.md` (half_split)
- `NIST_E_DELTA_VALIDATION_SANITY.md` (half_split)
- `NIST_E_DELTA_RIGOR_REPORT_parity.md`
- `NIST_E_DELTA_RIGOR_REPORT_quadrant.md`

## Failure Log Shortcut

If any closure item is `Fail`, add a sibling file:

- `FAILURE_LOG_$runId.md`
"@

    Set-Content -Path $TargetPath -Value $content -Encoding UTF8
}

function Update-ClosureChecklistFromSummary {
    param(
        [string]$TargetPath,
        [string]$SummaryJsonPath
    )

    if (-not (Test-Path $SummaryJsonPath)) {
        throw "Summary json not found: $SummaryJsonPath"
    }

    $summary = Get-Content -Path $SummaryJsonPath -Raw | ConvertFrom-Json
    $flags = $summary.closure_flags_draft
    $diag = $summary.diagnostics
    $generatedAt = $summary.generated_at
    $runId = Get-Date -Format "yyyyMMdd_HHmmss"

    $failureTriggered = if ($diag.has_fail) { "YES" } else { "NO" }
    $provisional = if ($diag.provisional_evidence) { "TRUE" } else { "FALSE" }
    $failedItems = if ($diag.failed_items.Count -gt 0) { ($diag.failed_items -join ", ") } else { "none" }

    $rigorMappings = @()
    if ($summary.rigor_reports) {
        foreach ($item in $summary.rigor_reports) {
            if ($item.mapping) {
                $rigorMappings += [string]$item.mapping
            }
        }
    }
    if ($rigorMappings.Count -eq 0) {
        $rigorMappings = @("half_split")
    }

    $rows = @()
    foreach ($mapping in $rigorMappings) {
        $definition = "$($flags.definition_closure)"
        $dimensional = "$($flags.dimensional_closure)"
        $process = "$($flags.process_closure)"
        $statistical = "$($flags.statistical_closure)"
        if ($diag.per_mapping_closure -and $diag.per_mapping_closure.PSObject.Properties.Name -contains $mapping) {
            $pm = $diag.per_mapping_closure.$mapping
            if ($pm.definition_closure) { $definition = "$($pm.definition_closure)" }
            if ($pm.dimensional_closure) { $dimensional = "$($pm.dimensional_closure)" }
            if ($pm.process_closure) { $process = "$($pm.process_closure)" }
            if ($pm.statistical_closure) { $statistical = "$($pm.statistical_closure)" }
        }
        $lowBetter = "N/A"
        $permSig = "N/A"
        if ($diag.low_beats_bell_by_mapping -and $diag.low_beats_bell_by_mapping.PSObject.Properties.Name -contains $mapping) {
            $lowBetter = if ($diag.low_beats_bell_by_mapping.$mapping) { "true" } else { "false" }
        }
        if ($diag.perm_significant_by_mapping -and $diag.perm_significant_by_mapping.PSObject.Properties.Name -contains $mapping) {
            $permSig = if ($diag.perm_significant_by_mapping.$mapping) { "true" } else { "false" }
        }
        $note = "low_beats_bell=$lowBetter; perm_sig=$permSig"
        $rows += "| $runId | $mapping | $definition | $dimensional | $process | $statistical | $failureTriggered | $note |"
    }

    $content = @"
# DELTA Closure Checklist

- Generated at (summary UTC): `$generatedAt`
- Checklist updated at: `$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")`
- Run ID: `$runId`
- Provisional evidence: `$provisional`
- Failed items: `$failedItems`

| Run ID | Mapping | Definition Closure | Dimensional Closure | Process Closure | Statistical Closure | Failure Triggered | Notes |
|---|---|---|---|---|---|---|---|
$($rows -join "`n")

## Referenced Outputs

- `DELTA_CLOSURE_SUMMARY.md`
- `DELTA_CLOSURE_SUMMARY.json`
- `NIST_E_DELTA_RIGOR_REPORT*.md`
- `NIST_E_DELTA_VALIDATION_SANITY.md`

## Failure Log Shortcut

If `Failure Triggered = YES`, add:

- `FAILURE_LOG_<run_id>.md` (from `docs/DELTA_FAILURE_LOG_TEMPLATE.md`)
"@

    Set-Content -Path $TargetPath -Value $content -Encoding UTF8
}

if (-not $SkipCondaActivation) {
    Run-Step "Activate conda environment" {
        . "./activate_conda.ps1"
    }
}

if (-not (Test-Path $Hdf5Path)) {
    throw "Missing HDF5 file: $Hdf5Path"
}

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
}

Run-Step "Snapshot previous summary (if exists)" {
    $summaryJson = Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.json"
    $prevSummaryJson = Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.previous.json"
    if (Test-Path $summaryJson) {
        Copy-Item $summaryJson $prevSummaryJson -Force
        Write-Host "wrote $prevSummaryJson" -ForegroundColor Green
    } else {
        Write-Host "no previous summary found" -ForegroundColor Yellow
    }
}

Run-Step "Run rigor pack (half_split)" {
    python "scripts/explore/explore_nist_e_delta_rigor_pack.py" `
      --hdf5 $Hdf5Path `
      --mapping "half_split" `
      --bootstrap $BootstrapMain `
      --seed $Seed `
      --out-md (Join-Path $OutDir "NIST_E_DELTA_RIGOR_REPORT.md")
}

Run-Step "Run validation sanity (half_split)" {
    python "scripts/explore/explore_nist_e_delta_validation_sanity.py" `
      --hdf5 $Hdf5Path `
      --mapping "half_split" `
      --out-md (Join-Path $OutDir "NIST_E_DELTA_VALIDATION_SANITY.md")
}

Run-Step "Run rigor pack (parity)" {
    python "scripts/explore/explore_nist_e_delta_rigor_pack.py" `
      --hdf5 $Hdf5Path `
      --mapping "parity" `
      --bootstrap $BootstrapAlt `
      --seed $Seed `
      --out-md (Join-Path $OutDir "NIST_E_DELTA_RIGOR_REPORT_parity.md")
}

Run-Step "Run rigor pack (quadrant_split)" {
    python "scripts/explore/explore_nist_e_delta_rigor_pack.py" `
      --hdf5 $Hdf5Path `
      --mapping "quadrant_split" `
      --bootstrap $BootstrapAlt `
      --seed $Seed `
      --out-md (Join-Path $OutDir "NIST_E_DELTA_RIGOR_REPORT_quadrant.md")
}

Run-Step "Generate closure checklist template" {
    $checklistPath = Join-Path $OutDir "DELTA_CLOSURE_CHECKLIST.md"
    New-ClosureChecklist -TargetPath $checklistPath -Hdf5 $Hdf5Path -SeedValue $Seed
    Write-Host "wrote $checklistPath" -ForegroundColor Green
}

Run-Step "Generate closure summary (md + json)" {
    python "scripts/explore/summarize_delta_closure.py" `
      --artifacts-dir $OutDir `
      --policy-json $PolicyJson `
      --out-md (Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.md") `
      --out-json (Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.json")
}

Run-Step "Auto-fill closure checklist from summary" {
    $checklistPath = Join-Path $OutDir "DELTA_CLOSURE_CHECKLIST.md"
    $summaryJson = Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.json"
    Update-ClosureChecklistFromSummary -TargetPath $checklistPath -SummaryJsonPath $summaryJson
    Write-Host "updated $checklistPath" -ForegroundColor Green
}

Run-Step "Compare current summary with previous (if exists)" {
    $summaryJson = Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.json"
    $prevSummaryJson = Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.previous.json"
    if (Test-Path $prevSummaryJson) {
        python "scripts/explore/compare_delta_summaries.py" `
          --current $summaryJson `
          --previous $prevSummaryJson `
          --out-md (Join-Path $OutDir "DELTA_CLOSURE_COMPARISON.md") `
          --out-json (Join-Path $OutDir "DELTA_CLOSURE_COMPARISON.json")
    } else {
        Write-Host "skip comparison: previous summary not found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Delta validation pack complete." -ForegroundColor Green
Write-Host "Output directory: $OutDir" -ForegroundColor Green
