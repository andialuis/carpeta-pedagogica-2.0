@echo off
echo ============================================
echo   Carpeta Pedagogica 2.0 - Iniciar Servidores
echo ============================================
echo.

:: Matar procesos anteriores en los puertos
echo [1/3] Limpiando puertos anteriores...
FOR /F "tokens=5" %%P IN ('netstat -aon ^| findstr :8000') DO TaskKill /PID %%P /F 2>NUL
FOR /F "tokens=5" %%P IN ('netstat -aon ^| findstr :3001') DO TaskKill /PID %%P /F 2>NUL
timeout /t 2 /nobreak >NUL

:: Iniciar Backend FastAPI
echo [2/3] Iniciando Backend FastAPI (puerto 8000)...
start "Backend FastAPI" /min cmd /c "cd /d "%~dp0backend" && venv\Scripts\uvicorn.exe main:app --reload"
timeout /t 3 /nobreak >NUL

:: Iniciar Frontend Next.js
echo [3/3] Iniciando Frontend Next.js (puerto 3001)...
start "Frontend Next.js" /min cmd /c "cd /d "%~dp0frontend" && npm run dev -- -p 3001"
timeout /t 4 /nobreak >NUL

echo.
echo ============================================
echo   Servidores iniciados correctamente!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3001
echo ============================================
echo.
echo Abriendo navegador...
timeout /t 3 /nobreak >NUL
start http://localhost:3001

echo.
echo [OK] Todo listo. Puedes cerrar esta ventana.
echo      Los servidores corren en segundo plano.
pause
