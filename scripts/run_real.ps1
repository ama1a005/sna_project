# Download SNAP datasets and execute full quarterly pipeline
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Running Temporal Echo Chamber Pipeline (SNAP Mode)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if (Test-Path "$projectRoot\.venv\Scripts\python.exe") {
    $pythonExe = "$projectRoot\.venv\Scripts\python.exe"
} else {
    $pythonExe = "python"
}

Write-Host "Step 1: Downloading Stanford SNAP datasets (if not present)..." -ForegroundColor Yellow
try {
    & $pythonExe -m echochamber download --raw-dir data/raw
} catch {
    Write-Warning "Direct network download failed (network restricted or offline). If already downloaded, proceed."
}

Write-Host "Step 2: Executing SNAP quarterly pipeline..." -ForegroundColor Yellow
& $pythonExe -m echochamber run --config configs/snap.yaml

Write-Host "`nSNAP Pipeline completed. Launch dashboard with: streamlit run app/Home.py" -ForegroundColor Green
