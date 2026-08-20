# SwachhAI Gujarat — Complete Startup
# Run this from swachhai-gujarat/ root

Write-Host "=== SwachhAI Gujarat ===" -ForegroundColor Green
Write-Host ""

# Load env
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]*)=(.*)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}

Write-Host "[1] Starting Backend (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep 3

Write-Host "[2] Starting Frontend (http://localhost:5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "SwachhAI Gujarat is starting up!" -ForegroundColor Green
Write-Host "Citizen Portal:    http://localhost:5173" -ForegroundColor White
Write-Host "Municipal Portal:  http://localhost:5173/municipal" -ForegroundColor White
Write-Host "API Docs:          http://localhost:8000/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "Demo Login:" -ForegroundColor Yellow
Write-Host "  Admin:   admin@swachhai.demo / admin123" -ForegroundColor White
Write-Host "  Officer: officer@swachhai.demo / officer123" -ForegroundColor White
Write-Host "  Citizen: citizen1@demo.swachhai / citizen123" -ForegroundColor White
