@echo off
title NutriSmart - Sistema Ativo
color 0A

echo.
echo ========================================
echo    NutriSmart - Iniciando Aplicativo
echo ========================================
echo.

REM Fechar processos antigos para evitar conflitos
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

REM 1. Preparar Backend
echo [1/2] Iniciando Backend (Porta 8000)...
cd /d "%~dp0backend"
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    venv\Scripts\python -m pip install -r ..\requirements.txt
)
start "NutriSmart - API" cmd /k "venv\Scripts\python -m uvicorn main:app --reload --port 8000"

echo Aguardando inicializacao...
timeout /t 5 /nobreak > nul

REM 2. Preparar Frontend
echo [2/2] Iniciando Interface (Porta 3001)...
cd /d "%~dp0"
start "NutriSmart - Web" cmd /k "npm run dev -- -p 3001"

echo.
echo ========================================
echo   App pronto! Acesse: http://localhost:3001
echo   Para desligar: Use o STOP.bat
echo ========================================
echo.
timeout /t 5 /nobreak > nul
start "" "http://localhost:3001"
pause
