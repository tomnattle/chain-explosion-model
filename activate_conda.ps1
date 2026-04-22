# PowerShell Script - Activate Conda Environment
# This script works even if conda init hasn't been run
# Usage: .\activate_conda.ps1 [environment_name]

param(
    [string]$EnvName = "audit-api"
)

Write-Host "Activating Conda environment: $EnvName" -ForegroundColor Cyan

# Try to find conda
$condaPath = $null

# Check common conda installation paths
$possiblePaths = @(
    "$env:USERPROFILE\anaconda3\Scripts\conda.exe",
    "$env:USERPROFILE\miniconda3\Scripts\conda.exe",
    "D:\app\ana\Scripts\conda.exe",
    "C:\ProgramData\Anaconda3\Scripts\conda.exe",
    "C:\ProgramData\Miniconda3\Scripts\conda.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $condaPath = $path
        break
    }
}

# Also try to find conda in PATH
if (-not $condaPath) {
    $condaCmd = Get-Command conda -ErrorAction SilentlyContinue
    if ($condaCmd) {
        $condaPath = $condaCmd.Source
    }
}

if (-not $condaPath) {
    Write-Host "Error: Conda not found. Please install Anaconda or Miniconda." -ForegroundColor Red
    Write-Host "Or run: .\setup_env.ps1 conda" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found conda at: $condaPath" -ForegroundColor Green

# Get conda base directory
$condaBase = Split-Path (Split-Path $condaPath -Parent) -Parent

# Initialize conda for this session
$condaInitScript = Join-Path $condaBase "shell\condabin\conda-hook.ps1"
if (Test-Path $condaInitScript) {
    Write-Host "Initializing conda for this session..." -ForegroundColor Yellow
    & $condaInitScript
}

# Try to activate the environment
Write-Host "Activating environment: $EnvName" -ForegroundColor Yellow

# Method 1: Try using conda activate (if initialized)
try {
    conda activate $EnvName
    Write-Host "Environment activated successfully!" -ForegroundColor Green
    Write-Host "Python version: $(python --version)" -ForegroundColor Cyan
    return
} catch {
    Write-Host "Method 1 failed, trying alternative method..." -ForegroundColor Yellow
}

# Method 2: Use conda run (works without initialization)
try {
    $env:CONDA_DEFAULT_ENV = $EnvName
    $env:CONDA_PREFIX = Join-Path $condaBase "envs\$EnvName"
    
    if (Test-Path $env:CONDA_PREFIX) {
        $env:PATH = "$env:CONDA_PREFIX;$env:CONDA_PREFIX\Scripts;$env:CONDA_PREFIX\Library\bin;$env:PATH"
        Write-Host "Environment activated successfully (alternative method)!" -ForegroundColor Green
        Write-Host "Python version: $(python --version)" -ForegroundColor Cyan
        Write-Host "Environment: $EnvName" -ForegroundColor Cyan
    } else {
        Write-Host "Error: Environment '$EnvName' not found." -ForegroundColor Red
        Write-Host "Available environments:" -ForegroundColor Yellow
        & $condaPath env list
        Write-Host ""
        Write-Host "To create the environment, run: .\setup_env.ps1 conda" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "Error activating environment: $_" -ForegroundColor Red
    exit 1
}

