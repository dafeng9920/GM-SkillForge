#!/usr/bin/env pwsh

# SkillForge L4 Startup Script (Optimized for New Env)

Write-Host "--- SkillForge L4 Startup ---" -ForegroundColor Green

# 1. Check Virtual Environment
if (-not (Test-Path ".venv")) {
    Write-Host "Error: .venv not found. Please recreate it." -ForegroundColor Red
    exit 1
}

# 2. Activate Virtual Environment
Write-Host "Activating venv..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# 3. Start Backend (Hidden Window)
Write-Host "Starting Backend (Port 8000)..." -ForegroundColor Yellow
# Using python -m uvicorn to be safe
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "skillforge.src.api.l4_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WindowStyle Hidden

# 4. Wait for Backend
Start-Sleep -Seconds 3

# 5. Check Frontend
Write-Host "Starting Frontend (Port 5173)..." -ForegroundColor Yellow
Set-Location "ui/app"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing node_modules..." -ForegroundColor Yellow
    npm install
}

Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan

npm run dev