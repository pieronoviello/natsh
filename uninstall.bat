@echo off
setlocal enabledelayedexpansion

:: natsh - Uninstaller (CMD)
:: Removes natsh and all associated files
::
:: Run: uninstall.bat

set "INSTALL_DIR=%USERPROFILE%\.natsh"
set "BIN_DIR=%USERPROFILE%\.local\bin"

echo.
echo   natsh - Uninstaller
echo.

:: Confirm uninstallation
set /p "confirm=Remove natsh and all data? [y/N] "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    exit /b 0
)

echo.

:: Remove installation directory
if exist "%INSTALL_DIR%" (
    echo [..] Removing %INSTALL_DIR%...
    rmdir /s /q "%INSTALL_DIR%"
    echo [OK] Installation directory removed
) else (
    echo [--] Installation directory not found
)

:: Remove natsh.bat wrapper
if exist "%BIN_DIR%\natsh.bat" (
    echo [..] Removing natsh.bat...
    del /f /q "%BIN_DIR%\natsh.bat"
    echo [OK] natsh.bat removed
) else (
    echo [--] natsh.bat not found
)

:: Remove natsh.ps1 wrapper
if exist "%BIN_DIR%\natsh.ps1" (
    echo [..] Removing natsh.ps1...
    del /f /q "%BIN_DIR%\natsh.ps1"
    echo [OK] natsh.ps1 removed
) else (
    echo [--] natsh.ps1 not found
)

echo.
echo ========================================
echo   natsh uninstalled successfully!
echo ========================================
echo.
echo Removed:
echo   - %INSTALL_DIR% (config, history, venv)
echo   - %BIN_DIR%\natsh.bat
echo   - %BIN_DIR%\natsh.ps1
echo.
echo Note: You may need to manually remove %BIN_DIR% from your PATH
echo       if no other programs use it.
echo.

endlocal
