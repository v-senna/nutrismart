@echo off
title NutriSmart - Limpar Cache e Iniciar
color 0B

echo.
echo  ========================================
echo    NutriSmart - Limpeza de Cache
echo  ========================================
echo.

echo  [1/2] Parando processos existentes...
taskkill /F /IM node.exe /T > nul 2>&1
taskkill /F /IM python.exe /T > nul 2>&1

echo  [2/2] Removendo pastas de cache e build...
if exist ..\frontend\.next (
    echo  Removendo ..\frontend\.next...
    rmdir /s /q ..\frontend\.next
)
if exist ..\frontend\node_modules\.cache (
    echo  Removendo cache do ..\frontend\node_modules...
    rmdir /s /q ..\frontend\node_modules\.cache
)

echo.
echo  [OK] Limpeza concluida!
echo  Iniciando normalmente em 3 segundos...
timeout /t 3 /nobreak > nul

call INICIAR_NUTRISMART.bat
