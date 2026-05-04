param(
    [string]$EnvName = "audit-api",
    [int]$V6MaxIter = 160,
    [int]$V8Rounds = 100,
    [float]$V8EtaProbe = 0.001,
    [int]$V9MaxIter = 120,
    [int]$StressMaxIter = 120,
    [int]$StressRefineMaxIter = 260,
    [string]$V9RealDataDir = "",
    [int]$V9RealMaxIter = 140,
    [switch]$IncludeV10,
    [string]$V10DataDir = "",
    [string]$V10OutDir = "artifacts/ripple_quantum_tests_v10_fail_anatomy_lock"
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

function Read-Json([string]$Path) {
    return Get-Content -Path $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Get-Sha256([string]$Path) {
    if (Test-Path $Path) {
        return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLower()
    }
    return ""
}

Write-Host "Starting locked unified ripple pipeline..." -ForegroundColor Cyan
Set-Location $PSScriptRoot

Invoke-Step "Activate conda environment ($EnvName)" {
    . "$PSScriptRoot/activate_conda.ps1" -EnvName $EnvName
}

Invoke-Step "Verify python" {
    python --version
}

$manifest = [ordered]@{
    started_at = (Get-Date).ToString("o")
    env_name = $EnvName
    workspace = $PSScriptRoot
    python_version = ""
    git_head = ""
    device_fingerprint = [ordered]@{
        os = ""
        cpu_name = ""
        cpu_cores_logical = 0
        cpu_cores_physical = 0
        blas_info = ""
    }
    script_sha256 = [ordered]@{
        v6_joint = ""
        v8_unify = ""
        v9_material_extension = ""
        run_ripple_unified_lock = ""
    }
    runs = @()
}

$pyVer = (python --version 2>&1).Trim()
$manifest.python_version = $pyVer

try {
    $manifest.git_head = (git rev-parse HEAD 2>$null).Trim()
} catch {
    $manifest.git_head = ""
}

try {
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $manifest.device_fingerprint.os = [System.Environment]::OSVersion.VersionString
    $manifest.device_fingerprint.cpu_name = [string]$cpu.Name
    $manifest.device_fingerprint.cpu_cores_logical = [int][Environment]::ProcessorCount
    $manifest.device_fingerprint.cpu_cores_physical = [int]$cpu.NumberOfCores
} catch {
    $manifest.device_fingerprint.os = [System.Environment]::OSVersion.VersionString
    $manifest.device_fingerprint.cpu_cores_logical = [int][Environment]::ProcessorCount
    $manifest.device_fingerprint.cpu_cores_physical = 0
}

$blasJson = python -c "import json, numpy as np; import numpy.__config__ as c; gi=getattr(c,'get_info',None); out={'numpy_version':np.__version__,'blas_opt_info':{},'openblas_info':{},'mkl_info':{}}; 
if callable(gi):
    out['blas_opt_info']=gi('blas_opt_info')
    out['openblas_info']=gi('openblas_info')
    out['mkl_info']=gi('mkl_info')
print(json.dumps(out, ensure_ascii=False))" 2>$null
if ($LASTEXITCODE -eq 0 -and $blasJson) {
    $manifest.device_fingerprint.blas_info = $blasJson
} else {
    $manifest.device_fingerprint.blas_info = "unknown"
}

$v6Out = "artifacts/ripple_quantum_tests_v6_lock"
$v8Out = "artifacts/ripple_quantum_tests_v8_unify"
$v9Out = "artifacts/ripple_quantum_tests_v9_material_lock"
$v9RealOut = "artifacts/ripple_quantum_tests_v9_realdata_lock"
$v6StressOut = "artifacts/ripple_quantum_tests_v6_lock_stress_refine"

$manifest.script_sha256.v6_joint = Get-Sha256 (Join-Path $PSScriptRoot "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py")
$manifest.script_sha256.v8_unify = Get-Sha256 (Join-Path $PSScriptRoot "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v8_unify.py")
$manifest.script_sha256.v9_material_extension = Get-Sha256 (Join-Path $PSScriptRoot "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v9_material_extension.py")
$manifest.script_sha256.v9_realdata_runner = Get-Sha256 (Join-Path $PSScriptRoot "scripts/explore/ripple_quantum_tests/v9_realdata_runner.py")
$manifest.script_sha256.v9_gate_report = Get-Sha256 (Join-Path $PSScriptRoot "scripts/explore/ripple_quantum_tests/v9_gate_report.py")
$manifest.script_sha256.v10_fail_anatomy = Get-Sha256 (Join-Path $PSScriptRoot "scripts/explore/ripple_quantum_tests/v10_fail_anatomy.py")
$manifest.script_sha256.run_ripple_unified_lock = Get-Sha256 (Join-Path $PSScriptRoot "run_ripple_unified_lock.ps1")

Invoke-Step "Run v6 primary" {
    python "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py" `
        --maxiter $V6MaxIter `
        --out-dir $v6Out
}

$v6JsonPath = Join-Path $PSScriptRoot "$v6Out/RIPPLE_QUANTUM_TESTS_V6_RESULTS.json"
$v6 = Read-Json $v6JsonPath
$v6Pass = [bool]$v6.meta.gates.joint_pass_all_shape_and_physics

$manifest.runs += [ordered]@{
    stage = "v6_primary"
    out_dir = $v6Out
    joint_pass = $v6Pass
    loss = [double]$v6.meta.optimization.fun
    optimum = $v6.meta.optimization.x
}

if (-not $v6Pass) {
    Write-Host "v6 primary failed gate -> running stress+refine diagnostic..." -ForegroundColor Yellow
    Invoke-Step "Run v6 stress+refine diagnostic" {
        python "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py" `
            --stress `
            --stress-alpha-min 0.0 `
            --stress-alpha-max 0.4 `
            --stress-alpha-steps 9 `
            --stress-maxiter $StressMaxIter `
            --stress-refine `
            --stress-refine-maxiter $StressRefineMaxIter `
            --out-dir $v6StressOut
    }
    $manifest.runs += [ordered]@{
        stage = "v6_stress_refine"
        out_dir = $v6StressOut
        note = "Diagnostic sweep with refine enabled"
    }

    $stressCsv = Join-Path $PSScriptRoot "$v6StressOut/RIPPLE_V6_STRESS_ALPHA.csv"
    if (Test-Path $stressCsv) {
        $rows = Import-Csv $stressCsv
        $recovered = $rows | Where-Object { [int]$_.joint_pass_final -eq 1 } | Sort-Object {[double]$_.loss_final} | Select-Object -First 1
        if ($null -ne $recovered) {
            $manifest.runs += [ordered]@{
                stage = "v6_recovered_snapshot"
                source = "v6_stress_refine"
                alpha = [double]$recovered.alpha
                loss_final = [double]$recovered.loss_final
                optimum = [ordered]@{
                    mu = [double]$recovered.mu
                    rho = [double]$recovered.rho
                    eta = [double]$recovered.eta
                    bw_ghz = [double]$recovered.bw_ghz
                }
            }
        }
    }
}

Invoke-Step "Run v8 unified" {
    python "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v8_unify.py" `
        --rounds $V8Rounds `
        --eta-probe $V8EtaProbe
}

$v8JsonPath = Join-Path $PSScriptRoot "$v8Out/v8_quantum_grand_unification.json"
$v8 = Read-Json $v8JsonPath
$manifest.runs += [ordered]@{
    stage = "v8_unified"
    out_dir = $v8Out
    joint_pass = [bool]$v8.joint_pass
    joint_loss = [double]$v8.joint_loss
}

Invoke-Step "Run v9 material extension" {
    python "scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v9_material_extension.py" `
        --maxiter $V9MaxIter `
        --out-dir $v9Out
}

$v9JsonPath = Join-Path $PSScriptRoot "$v9Out/RIPPLE_QUANTUM_TESTS_V9_RESULTS.json"
$v9 = Read-Json $v9JsonPath
$manifest.runs += [ordered]@{
    stage = "v9_material_extension"
    out_dir = $v9Out
    optimum = $v9.optimum
}

if ($V9RealDataDir -and (Test-Path $V9RealDataDir)) {
    Invoke-Step "Run v9 realdata runner" {
        python "scripts/explore/ripple_quantum_tests/v9_realdata_runner.py" `
            --data-dir $V9RealDataDir `
            --maxiter $V9RealMaxIter `
            --out-dir $v9RealOut
    }
    Invoke-Step "Run v9 gate report" {
        python "scripts/explore/ripple_quantum_tests/v9_gate_report.py" `
            --in-json "$v9RealOut/RIPPLE_QUANTUM_TESTS_V9_REALDATA_RESULTS.json" `
            --out-md "$v9RealOut/RIPPLE_QUANTUM_TESTS_V9_GATE_REPORT.md"
    }
    $v9r = Read-Json (Join-Path $PSScriptRoot "$v9RealOut/RIPPLE_QUANTUM_TESTS_V9_REALDATA_RESULTS.json")
    $manifest.runs += [ordered]@{
        stage = "v9_realdata"
        out_dir = $v9RealOut
        data_dir = $V9RealDataDir
        final_pass = [bool]$v9r.gates.final_pass
        optimum = $v9r.optimum
    }
} else {
    $manifest.runs += [ordered]@{
        stage = "v9_realdata"
        skipped = $true
        reason = "V9RealDataDir missing or not found"
    }
}

if ($IncludeV10) {
    $v10ResolvedData = ""
    if ($V10DataDir -and (Test-Path $V10DataDir)) {
        $v10ResolvedData = $V10DataDir
    } elseif ($V9RealDataDir -and (Test-Path $V9RealDataDir)) {
        $v10ResolvedData = $V9RealDataDir
    } else {
        $v10ResolvedData = "artifacts/ripple_quantum_tests_v9_realdata_input_template"
    }
    if (-not (Test-Path $v10ResolvedData)) {
        throw "V10 data dir not found: $v10ResolvedData (set -V10DataDir or -V9RealDataDir, or bootstrap template)"
    }
    Invoke-Step "Run v10 failure anatomy" {
        python "scripts/explore/ripple_quantum_tests/v10_fail_anatomy.py" `
            --data-dir $v10ResolvedData `
            --out-dir $V10OutDir
    }
    $manifest.runs += [ordered]@{
        stage = "v10_fail_anatomy"
        out_dir = $V10OutDir
        data_dir = $v10ResolvedData
    }
} else {
    $manifest.runs += [ordered]@{
        stage = "v10_fail_anatomy"
        skipped = $true
        reason = "IncludeV10 not set"
    }
}

$manifest.finished_at = (Get-Date).ToString("o")
$manifestPath = Join-Path $PSScriptRoot "artifacts/ripple_unified_lock/RUN_MANIFEST.json"
New-Item -ItemType Directory -Force -Path (Split-Path $manifestPath -Parent) | Out-Null
$manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host ""
Write-Host "Locked unified pipeline finished." -ForegroundColor Green
Write-Host "Manifest: artifacts/ripple_unified_lock/RUN_MANIFEST.json" -ForegroundColor Yellow
if ($IncludeV10) {
    Write-Host "V10 anatomy: $V10OutDir/V10_FAIL_ANATOMY.md" -ForegroundColor Yellow
}
