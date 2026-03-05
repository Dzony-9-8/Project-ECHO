@echo off
setlocal
title Project ECHO - Master Controller

echo ========================================================
echo   PROJECT ECHO - Master Startup Control (AI OS)
echo ========================================================

echo.
echo [1/4] Terminating existing ECHO processes...

rem Killing Backend (Port 8000)
netstat -aon | findstr :8000 | findstr LISTENING > "%TEMP%\echo_pids.txt"
for /f "usebackq tokens=5" %%a in ("%TEMP%\echo_pids.txt") do taskkill /F /PID %%a >nul 2>&1

rem Killing Frontend (Port 5173)
netstat -aon | findstr :5173 | findstr LISTENING > "%TEMP%\echo_pids.txt"
for /f "usebackq tokens=5" %%a in ("%TEMP%\echo_pids.txt") do taskkill /F /PID %%a >nul 2>&1

del "%TEMP%\echo_pids.txt" >nul 2>&1

echo.
echo [2/4] Validating Environments...

if not exist ai-orchestrator\venv (
    echo [!] Missing ai-orchestrator environment.
    echo Please run setup_all.bat first.
    pause
    exit /b
)

if not exist ai-ui\node_modules (
    echo [!] Missing ai-ui dependencies.
    echo Please run setup_all.bat first.
    pause
    exit /b
)

echo.
echo [3/4] Launching AI Backend (api/server.py)...
start "ECHO Backend" cmd /k "cd ai-orchestrator && venv\Scripts\activate && python ..\api\server.py"

echo.
echo [4/4] Launching Web Interface (vite)...
start "ECHO UI" cmd /k "cd ai-ui && npm run dev"

echo.
echo ========================================================
echo   ECHO IS INITIALIZING...
echo   - Frontend will be available at http://localhost:5173
echo.
echo   Waiting for servers to start before opening browser...
echo ========================================================

timeout /t 5 >nul
start http://localhost:5173

echo.
echo [DONE] System hand-off complete.
timeout /t 3 >nul
exit
