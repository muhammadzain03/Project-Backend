@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo  SENG 533 – starting backend (Flask :5000) and frontend (Vite :3000)
echo  Close each window to stop that process.
echo.

start "SENG533 Backend" cmd /k cd /d "%~dp0backend" ^&^& python app.py

timeout /t 2 /nobreak >nul

start "SENG533 Frontend" cmd /k cd /d "%~dp0frontend" ^&^& npm run dev

echo.
echo  Two windows should open. Backend: http://127.0.0.1:5000  Frontend: http://localhost:3000
echo.
pause
