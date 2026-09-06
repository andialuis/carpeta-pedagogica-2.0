@echo off
title Instalar Habilidad Carpeta Pedagogica en Antigravity
color 0F
echo ================================================================
echo   INSTALADOR DE HABILIDAD PARA GOOGLE ANTIGRAVITY (AGY)
echo   Software: Carpeta Pedagogica 2.0
echo   Autor: Luis Alfredo Andia Valverde (luis.andia.valverde@gmail.com)
echo   Licencia: Creative Commons BY-NC 4.0 (Uso Libre No Comercial)
echo ================================================================
echo.

set "SOURCE=%~dp0.agents\skills\carpeta-pedagogica"
set "DEST=%USERPROFILE%\.gemini\config\skills\carpeta-pedagogica"

if not exist "%SOURCE%" (
    echo [ERROR] No se encontro la carpeta de la habilidad en:
    echo %SOURCE%
    pause
    exit /b 1
)

echo [1/2] Creando directorio global de habilidades en Antigravity...
if not exist "%DEST%" mkdir "%DEST%"

echo [2/2] Copiando manifiesto SKILL.md, scripts y referencias...
xcopy /E /I /Y "%SOURCE%" "%DEST%" >nul

echo.
echo ================================================================
echo   HABILIDAD INSTALADA EXITOSAMENTE EN TU SISTEMA!
echo ================================================================
echo.
echo Ubicacion global:
echo   --^> %DEST%
echo.
echo A partir de ahora, cuando abras Antigravity en CUALQUIER proyecto
echo de tu computadora, tu agente de IA podra:
echo   - Iniciar y administrar Carpeta Pedagogica 2.0
echo   - Ejecutar el pipeline de 4 agentes de analitica
echo   - Exportar feedback formativo para Moodle, Classroom y Teams
echo   - Compilar el Dossier Oficial y guias de triangulacion socratica
echo.
pause
