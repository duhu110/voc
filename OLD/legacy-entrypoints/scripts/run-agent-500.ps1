$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Python virtual environment not found at $pythonExe"
}

Push-Location $repoRoot
try {
    & $pythonExe -m voc_agent.complaint_taxonomy_validator.live_batch --sample-size 500
}
finally {
    Pop-Location
}
