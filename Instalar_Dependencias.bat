@echo off
title Carpeta Pedagogica 2.0 - Instalador de Dependencias
color 0F
echo ================================================================
echo   CARPETA PEDAGOGICA 2.0 - INSTALADOR AUTOMATICO
echo   Autor: Luis Alfredo Andia Valverde (luis.andia.valverde@gmail.com)
echo   Licencia: Creative Commons BY-NC 4.0 (Uso Libre No Comercial)
echo ================================================================
echo.

:: 1. Verificar Python
echo [1/4] Verificando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH del sistema.
    echo Por favor instala Python 3.10 o superior desde https://www.python.org
    pause
    exit /b 1
)
python --version

:: 2. Verificar Node.js
echo.
echo [2/4] Verificando instalacion de Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado o no esta en el PATH del sistema.
    echo Por favor instala Node.js 18 o superior desde https://nodejs.org
    pause
    exit /b 1
)
node --version

:: 3. Instalar dependencias del Backend (FastAPI + Python)
echo.
echo [3/4] Configurando entorno virtual e instalando librerias del Backend...
cd /d "%~dp0backend"
if not exist "venv" (
    echo Creando entorno virtual venv...
    python -m venv venv
)
echo Instalando requirements.txt...
call venv\Scripts\python.exe -m pip install --upgrade pip
call venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ALERTA] Hubo advertencias al instalar librerias de Python.
)

:: 4. Instalar dependencias del Frontend (Next.js + React)
echo.
echo [4/4] Instalando dependencias del Frontend (Next.js)...
cd /d "%~dp0frontend"
call npm install
if %errorlevel% neq 0 (
    echo [ALERTA] Hubo advertencias al instalar dependencias de Node.js.
)

echo.
echo ================================================================
echo   INSTALACION COMPLETADA EXITOSAMENTE!
echo ================================================================
echo.
echo Para iniciar la aplicacion, simplemente ejecuta:
echo   --^> Iniciar_Carpeta.bat
echo.
echo Se abrira en tu navegador web en: http://localhost:3001
echo.
pause
