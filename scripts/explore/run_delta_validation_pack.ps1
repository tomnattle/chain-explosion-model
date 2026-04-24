param(
    [string]$Hdf5Path = "data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5",
    [string]$OutDir = "artifacts/public_validation_pack",
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
      --out-md (Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.md") `
      --out-json (Join-Path $OutDir "DELTA_CLOSURE_SUMMARY.json")
}

Write-Host ""
Write-Host "Delta validation pack complete." -ForegroundColor Green
Write-Host "Output directory: $OutDir" -ForegroundColor Green
