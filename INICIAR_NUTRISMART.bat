@echo off
title NutriSmart - Iniciando...
color 0A

echo.
echo  ========================================
echo        NutriSmart - Iniciando App
echo  ========================================
echo.

REM ---- BACKEND ----
echo  [1/2] Iniciando Backend na porta 8000...
start "NutriSmart BACKEND" cmd /k "cd /d "%~dp0backend" && venv\Scripts\activate && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo  Aguardando backend iniciar (pode levar alguns segundos)...
echo.

REM Fica tentando por ate 40 segundos
set TRIES=0
:AGUARDA
set /a TRIES+=1
if %TRIES% gtr 40 (
    echo  [AVISO] Backend demorou muito. Continuando mesmo assim...
    goto INICIA_FRONTEND
)
timeout /t 1 /nobreak > nul
curl -s --max-time 2 http://127.0.0.1:8000/docs > nul 2>&1
if errorlevel 1 (
    echo  . tentativa %TRIES%/40...
    goto AGUARDA
)

echo  [OK] Backend respondendo!

:INICIA_FRONTEND
echo.
echo  [2/2] Iniciando Frontend na porta 3000...
start "NutriSmart FRONTEND" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo  Aguardando frontend compilar (pode levar 10-15s na primeira vez)...
timeout /t 12 /nobreak > nul

echo  [OK] Abrindo navegador...
start "" "http://localhost:3000"

echo.
echo  ========================================
echo   App rodando! Acesse:
echo   http://localhost:3000
echo  ========================================
echo.
echo  Nao feche as janelas BACKEND e FRONTEND!
echo  Para parar: use PARAR_NUTRISMART.bat
echo.
pause
