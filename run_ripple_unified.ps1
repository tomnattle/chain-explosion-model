param(
    [string]$EnvName = "audit-api",
    [switch]$SkipV6,
    [switch]$SkipV8,
    [switch]$SkipV9,
    [int]$V6MaxIter = 160,
    [int]$V8Rounds = 100,
    [float]$V8EtaProbe = 0.001,
    [int]$V9MaxIter = 120
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    Write-Host ""
    Write-Host "==== $Name ====" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name (exit code: $LASTEXITCODE)"
    }
    Write-Host "OK: $Name" -ForegroundColor Green
}

Write-Host "Starting unified ripple pipeline..." -ForegroundColor Cyan
Write-Host "Workspace: $PSScriptRoot" -ForegroundColor DarkCyan
Set-Location $PSScriptRoot

# Dot-source is required so activation affects the current PowerShell session.
Invoke-Step "Activate conda environment ($EnvName)" {
    . "$PSScriptRoot/activate_conda.ps1" -EnvName $EnvName
}

Invoke-Step "Verify python environment" {
    python --version
}

if (-not $SkipV6) {
    Invoke-Step "Run v6 joint consistency" {
        python "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py" `
            --maxiter $V6MaxIter `
            --out-dir "artifacts/ripple_quantum_tests_v6"
    }
}

if (-not $SkipV8) {
    Invoke-Step "Run v8 unified audit" {
        python "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v8_unify.py" `
            --rounds $V8Rounds `
            --eta-probe $V8EtaProbe
    }
}

if (-not $SkipV9) {
    Invoke-Step "Run v9 material extension" {
        python "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v9_material_extension.py" `
            --maxiter $V9MaxIter `
            --out-dir "artifacts/ripple_quantum_tests_v9_material"
    }
}

Write-Host ""
Write-Host "Unified ripple pipeline finished." -ForegroundColor Green
Write-Host "Key outputs:" -ForegroundColor Yellow
if (-not $SkipV6) { Write-Host "  - artifacts/ripple_quantum_tests_v6/" }
if (-not $SkipV8) { Write-Host "  - artifacts/ripple_quantum_tests_v8_unify/" }
if (-not $SkipV9) { Write-Host "  - artifacts/ripple_quantum_tests_v9_material/" }
