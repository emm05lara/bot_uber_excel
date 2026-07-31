@echo off
setlocal
title Extractor de ganancias Uber
cd /d "%~dp0"

echo ==========================================
echo   EXTRACTOR DE GANANCIAS DE UBER
echo ==========================================
echo.

rem Usar el entorno virtual del proyecto si existe.
if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
    goto :ejecutar
)

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
    goto :ejecutar
)

rem Si no hay entorno virtual, intentar con Python instalado en Windows.
where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py"
    goto :ejecutar
)

where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :ejecutar
)

echo ERROR: No se encontro Python ni un entorno virtual.
echo.
echo Instala Python o crea el entorno con:
echo     py -m venv venv
echo     venv\Scripts\python.exe -m pip install -r requirements.txt
echo     venv\Scripts\python.exe -m playwright install chromium
echo.
pause
exit /b 1

:ejecutar
if not exist "extraer_uber.py" (
    echo ERROR: No se encontro extraer_uber.py en:
    echo %CD%
    echo.
    echo Coloca este archivo .bat en la misma carpeta del script.
    pause
    exit /b 1
)

echo Ejecutando con: %PYTHON_CMD%
echo.
"%PYTHON_CMD%" "extraer_uber.py"
set "CODIGO_SALIDA=%ERRORLEVEL%"

echo.
if not "%CODIGO_SALIDA%"=="0" (
    echo El programa termino con un error. Codigo: %CODIGO_SALIDA%
) else (
    echo El programa termino correctamente.
)

echo.
pause
exit /b %CODIGO_SALIDA%
