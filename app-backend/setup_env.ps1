Param(
    [switch]$StartServer
)

$ErrorActionPreference = 'Stop'
Write-Host "[setup] Creating virtual environment in .venv..."
python -m venv .venv

$venvPy = Join-Path $PWD '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) {
    Write-Host "[setup] Could not find venv python at $venvPy. Ensure 'python' is on PATH and try again." -ForegroundColor Red
    exit 1
}

Write-Host "[setup] Upgrading pip and installing build tools..."
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install wheel setuptools

if (Test-Path "requirements.txt") {
    Write-Host "[setup] Installing requirements from requirements.txt..."
    & $venvPy -m pip install -r requirements.txt
} else {
    Write-Host "[setup] requirements.txt not found — skipping pip install." -ForegroundColor Yellow
}

Write-Host "[setup] Finished. Activate the venv with: .\\.venv\\Scripts\\Activate.ps1"
Write-Host "[setup] To start the FastAPI server run: .\\.venv\\Scripts\\python -m uvicorn app_back:app --reload --host 127.0.0.1 --port 8000"

if ($StartServer) {
    Write-Host "[setup] Starting uvicorn..."
    & $venvPy -m uvicorn app_back:app --reload --host 127.0.0.1 --port 8000
}
