@echo off
title NutriSmart - Reparando Ambiente Local
color 0E

echo.
echo ========================================
echo   NutriSmart - Reparando Ambiente
echo ========================================
echo.

echo [1/3] Removendo venv antiga...
if exist "%~dp0backend\venv" (
    rmdir /s /q "%~dp0backend\venv"
)

echo [2/3] Criando nova venv...
cd /d "%~dp0backend"
python -m venv venv

echo [3/3] Instalando dependencias...
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt

echo.
echo ========================================
echo   [OK] Ambiente reparado com sucesso!
echo   Tente rodar o START.bat na raiz agora.
echo ========================================
echo.
pause
