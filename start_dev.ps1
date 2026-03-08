#!/usr/bin/env pwsh

# SkillForge L4 开发环境启动脚本

Write-Host "正在启动 SkillForge L4 开发环境..." -ForegroundColor Green

# 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host "错误: 未找到虚拟环境 .venv" -ForegroundColor Red
    Write-Host "请先运行: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# 安装后端依赖
Write-Host "检查后端依赖..." -ForegroundColor Yellow
pip install fastapi uvicorn python-multipart

# 启动后端服务器 (后台)
Write-Host "启动后端服务器 (端口 8000)..." -ForegroundColor Yellow
Start-Process -FilePath "uvicorn" -ArgumentList "skillforge.src.api.l4_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WindowStyle Hidden

# 等待后端启动
Start-Sleep -Seconds 3

# 检查后端是否启动成功
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ 后端服务器启动成功" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ 后端服务器可能未正常启动" -ForegroundColor Yellow
}

# 启动前端服务器
Write-Host "启动前端服务器 (端口 5173)..." -ForegroundColor Yellow
Set-Location "ui/app"

# 安装前端依赖
if (-not (Test-Path "node_modules")) {
    Write-Host "安装前端依赖..." -ForegroundColor Yellow
    npm install
}

# 启动前端
Write-Host "启动前端开发服务器..." -ForegroundColor Green
Write-Host "前端地址: http://localhost:5173" -ForegroundColor Cyan
Write-Host "后端地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API健康检查: http://localhost:8000/api/v1/health" -ForegroundColor Cyan

npm run dev