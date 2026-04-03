@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Cleaning: %cd%
echo.

echo Python caches...
for /d /r %%d in (__pycache__) do if exist "%%d" rd /s /q "%%d" 2>nul
for /r %%f in (*.pyc) do if exist "%%f" del /f /q "%%f" 2>nul
for /r %%f in (*.pyo) do if exist "%%f" del /f /q "%%f" 2>nul

echo Tool caches...
for /d /r %%d in (.pytest_cache) do if exist "%%d" rd /s /q "%%d" 2>nul
for /d /r %%d in (.mypy_cache) do if exist "%%d" rd /s /q "%%d" 2>nul
for /d /r %%d in (.ruff_cache) do if exist "%%d" rd /s /q "%%d" 2>nul
for /d /r %%d in (htmlcov) do if exist "%%d" rd /s /q "%%d" 2>nul
if exist ".coverage" del /f /q ".coverage" 2>nul

echo Frontend build output...
if exist "frontend\dist" rd /s /q "frontend\dist" 2>nul
pushd "%~dp0frontend"
call npm run clean 2>nul
popd

echo.
echo Done. Kept: source, node_modules, .env, credentials, .git
endlocal
