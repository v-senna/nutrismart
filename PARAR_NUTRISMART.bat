@echo off
title NutriSmart - Parando Servidores...
color 0C

echo ============================================
echo       NutriSmart - Parando Servidores
echo ============================================
echo.

echo Encerrando processos nas portas 8001 e 3001...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Encerrando Backend (PID %%a)...
    taskkill /F /PID %%a > nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING"') do (
    echo Encerrando Frontend (PID %%a)...
    taskkill /F /PID %%a > nul 2>&1
)

echo.
echo [OK] Servidores encerrados!
echo.
pause
