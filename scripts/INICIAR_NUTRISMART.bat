@echo off
title NutriSmart - Iniciando...
color 0A

echo.
echo  ========================================
echo        NutriSmart - Iniciando App
echo  ========================================
echo.

REM ---- BACKEND ----
echo  [1/2] Iniciando Backend na porta 8001...
start "NutriSmart BACKEND" cmd /k "cd /d "%~dp0..\backend" && venv\Scripts\python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001"

echo  Aguardando backend iniciar (pode levar alguns segundos)...
echo.

REM Fica tentando por ate 40 segundos, mas permite pular
setlocal EnableDelayedExpansion
echo  Verificando se o backend esta pronto...
set TRIES=0

:AGUARDA
set /a TRIES+=1
if %TRIES% gtr 15 (
    echo.
    echo  [AVISO] Backend esta demorando muito para responder.
    echo  Verifique a janela "NutriSmart BACKEND" para ver se ha erros.
    set /p "SKIP=Deseja abrir o frontend mesmo assim? (S/N): "
    if /i "!SKIP!"=="S" goto INICIA_FRONTEND
    set TRIES=0
)

timeout /t 1 /nobreak > nul
curl -s --max-time 2 http://127.0.0.1:8001/docs > nul 2>&1
if errorlevel 1 (
    if !TRIES!==1 <nul set /p "=  Tentando conectar ao backend..."
    <nul set /p "=."
    goto AGUARDA
)

echo.
echo  [OK] Backend respondendo!

:INICIA_FRONTEND
echo.
echo  [2/2] Iniciando Frontend na porta 3001...
start "NutriSmart FRONTEND" cmd /k "cd /d "%~dp0.." && npm run dev -- -p 3001 -H 0.0.0.0"

echo  Aguardando frontend compilar (pode levar 10-15s na primeira vez)...
timeout /t 12 /nobreak > nul

echo  [OK] Abrindo navegador...
start "" "http://localhost:3001"

echo.
echo  ========================================
echo   App rodando! Acesse:
echo   http://localhost:3001
echo  ========================================
echo.
echo  Nao feche as janelas BACKEND e FRONTEND!
echo  Para parar: use PARAR_NUTRISMART.bat
echo.
pause
