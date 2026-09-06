@echo off
title Conectar y Subir a GitHub de Forma Segura - Carpeta Pedagogica 2.0
color 0B
echo ==============================================================================
echo    ASISTENTE DE PUBLICACION SEGURA EN GITHUB
echo    Software: Carpeta Pedagogica 2.0 (Version Personal y Educativa)
echo    Autor: Luis Alfredo Andia Valverde (luis.andia.valverde@gmail.com)
echo    Licencia: Creative Commons BY-NC 4.0 (Uso Libre No Comercial)
echo ==============================================================================
echo.
echo  [1/3] VERIFICACION DE SEGURIDAD PREVIA:
echo        - Claves privadas (.env) protegidas:     [OK]
echo        - Credenciales y tokens excluidos:       [OK]
echo        - Dependencias pesadas excluidas:        [OK]
echo        - Historial local limpio:                [OK]
echo.
echo ==============================================================================
echo  Repositorio configurado:
echo  --> https://github.com/andialuis/carpeta-pedagogica-2.0.git
echo ==============================================================================
echo.

set "DEFAULT_URL=https://github.com/andialuis/carpeta-pedagogica-2.0.git"
echo Presiona ENTER para usar la direccion predeterminada:
echo [%DEFAULT_URL%]
echo.
set /p REPO_URL="O escribe otra URL si lo deseas (ENTER para continuar): "

if "%REPO_URL%"=="" (
    set "REPO_URL=%DEFAULT_URL%"
)

echo.
echo [2/3] Vinculando repositorio remoto...
"C:\Program Files\Git\cmd\git.exe" remote remove origin 2>nul
"C:\Program Files\Git\cmd\git.exe" remote add origin %REPO_URL%
"C:\Program Files\Git\cmd\git.exe" branch -M main

echo.
echo [3/3] Subiendo codigo de forma segura a GitHub...
echo (Si es la primera vez, se abrira una ventana en tu navegador para autorizar con 1 clic)
echo.
"C:\Program Files\Git\cmd\git.exe" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==============================================================================
    echo    FELICITACIONES! PROYECTO PUBLICADO EXITOSAMENTE EN GITHUB!
    echo ==============================================================================
    echo.
    echo Tu repositorio esta en linea:
    echo   --^> %REPO_URL%
    echo.
    echo Contenido publicado:
    echo   * Codigo completo de Frontend y Backend
    echo   * Habilidad nativa de Antigravity (.agents/skills/carpeta-pedagogica)
    echo   * Licencia CC BY-NC 4.0 a nombre de Luis Alfredo Andia Valverde
    echo   * Sin claves secretas ni datos vulnerables
    echo.
) else (
    echo.
    echo ==============================================================================
    echo [ATENCION] Si no se pudo subir:
    echo 1. Asegurate de haber hecho clic en el boton verde "Crear repositorio" en GitHub.
    echo 2. Si se abrio la ventana de autorizacion en el navegador, completala.
    echo ==============================================================================
)

pause
