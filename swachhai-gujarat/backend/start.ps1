#!/usr/bin/env powershell
# ─────────────────────────────────────────────
# SwachhAI Gujarat — Backend Startup Script
# Run from: swachhai-gujarat/backend/
# ─────────────────────────────────────────────

# Load .env from parent directory
$envFile = Join-Path (Get-Location).Path "..\\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]*)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
    Write-Host "[OK] Loaded .env"
} else {
    Write-Host "[WARN] .env not found — using defaults"
}

Write-Host "Starting SwachhAI Gujarat Backend on http://localhost:8000"
Write-Host "API Docs: http://localhost:8000/api/docs"

.\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
