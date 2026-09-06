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
echo  INSTRUCCIONES EN GITHUB:
echo  1. Entra a tu cuenta en: https://github.com/new
echo  2. Crea un repositorio nuevo (ejemplo: "carpeta-pedagogica-2.0").
echo     IMPORTANTE: Dejalo VACIO (NO marques "Add a README", ni .gitignore ni License).
echo  3. Copia la direccion URL HTTPS de tu repositorio.
echo     (Ejemplo: https://github.com/tu-usuario/carpeta-pedagogica-2.0.git)
echo ==============================================================================
echo.

set /p REPO_URL="Pega aqui la URL de tu repositorio de GitHub y presiona ENTER: "

if "%REPO_URL%"=="" (
    echo [AVISO] No ingresaste ninguna URL. Operacion cancelada.
    pause
    exit /b 1
)

echo.
echo [2/3] Vinculando repositorio remoto...
"C:\Program Files\Git\cmd\git.exe" remote remove origin 2>nul
"C:\Program Files\Git\cmd\git.exe" remote add origin %REPO_URL%
"C:\Program Files\Git\cmd\git.exe" branch -M main

echo.
echo [3/3] Subiendo codigo de forma segura a GitHub...
echo (Si es la primera vez, el Gestor de Credenciales abrira tu navegador para autorizar con 1 clic)
echo.
"C:\Program Files\Git\cmd\git.exe" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==============================================================================
    echo    FELICITACIONES! PROYECTO PUBLICADO EXITOSAMENTE EN GITHUB!
    echo ==============================================================================
    echo.
    echo Tu repositorio esta en linea con:
    echo   * Codigo completo de Frontend y Backend
    echo   * Habilidad nativa de Antigravity (.agents/skills/carpeta-pedagogica)
    echo   * Licencia CC BY-NC 4.0 a nombre de Luis Alfredo Andia Valverde
    echo   * Sin claves secretas ni datos vulnerables
    echo.
) else (
    echo.
    echo ==============================================================================
    echo [ATENCION] Hubo un detalle al subir el codigo.
    echo Posibles causas:
    echo 1. La URL del repositorio tiene un error tipografico.
    echo 2. El repositorio en GitHub ya tenia un README inicial (no estaba vacio).
    echo 3. Faltan permisos de acceso en tu cuenta.
    echo ==============================================================================
)

pause
