# Execute deterministic synthetic fixture pipeline
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Running Temporal Echo Chamber Pipeline (Fixture Mode)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Use venv python if available, else system python
if (Test-Path "$projectRoot\.venv\Scripts\python.exe") {
    $pythonExe = "$projectRoot\.venv\Scripts\python.exe"
} else {
    $pythonExe = "python"
}

& $pythonExe -m echochamber run --config configs/fixture.yaml

Write-Host "`nPipeline completed. Run 'streamlit run app/Home.py' to launch dashboard." -ForegroundColor Green
