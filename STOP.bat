@echo off
title NutriSmart - Parando...
color 0C

echo.
echo ========================================
echo    NutriSmart - Encerrando Servidores
echo ========================================
echo.

taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo [OK] Todos os servicos foram interrompidos.
echo.
timeout /t 3 /nobreak > nul
exit
