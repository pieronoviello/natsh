@echo off
setlocal enabledelayedexpansion

:: natsh - Natural Shell
:: Installation script for CMD
::
:: Run: install.bat

set "INSTALL_DIR=%USERPROFILE%\.natsh"
set "BIN_DIR=%USERPROFILE%\.local\bin"

echo.
echo   natsh - Natural Shell
echo   Say it. Run it.
echo.

:: Check for Python
set "PYTHON="
for %%p in (python python3 py) do (
    %%p --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%v in ('%%p --version 2^>^&1') do (
            echo %%v | findstr /i "Python 3" >nul
            if !errorlevel! equ 0 (
                set "PYTHON=%%p"
                goto :found_python
            )
        )
    )
)

echo [X] Python 3 is required
echo     Download from: https://www.python.org/downloads/
exit /b 1

:found_python
echo [OK] Python found: %PYTHON%

:: Create install directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Check if running from local directory with natsh.py
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%natsh.py" (
    if exist "%SCRIPT_DIR%requirements.txt" (
        echo [..] Installing from local files...
        copy /y "%SCRIPT_DIR%natsh.py" "%INSTALL_DIR%\natsh.py" >nul
        copy /y "%SCRIPT_DIR%requirements.txt" "%INSTALL_DIR%\requirements.txt" >nul
        goto :install_deps
    )
)

echo [X] Local files not found. Please run from the natsh directory.
echo     Or use the PowerShell installer for GitHub download.
exit /b 1

:install_deps
:: Setup Python virtual environment
echo [..] Setting up Python environment...
pushd "%INSTALL_DIR%"

if exist "venv" rmdir /s /q "venv"

%PYTHON% -m venv venv
call venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
call venv\Scripts\deactivate.bat

popd

:: Create bin directory
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

:: Create natsh.bat wrapper
(
echo @echo off
echo "%%USERPROFILE%%\.natsh\venv\Scripts\python.exe" "%%USERPROFILE%%\.natsh\natsh.py" %%*
) > "%BIN_DIR%\natsh.bat"

:: Add to PATH
echo [..] Checking PATH...
echo %PATH% | findstr /i "%BIN_DIR%" >nul
if errorlevel 1 (
    echo [..] Adding natsh to user PATH...
    for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%b"
    if defined USER_PATH (
        setx PATH "%BIN_DIR%;!USER_PATH!" >nul
    ) else (
        setx PATH "%BIN_DIR%" >nul
    )
)

echo.
echo ========================================
echo   natsh installed successfully!
echo ========================================
echo.
echo Next steps:
echo   1. Open a NEW terminal (to refresh PATH)
echo   2. Run: natsh
echo   3. Enter your free Gemini API key
echo      Get it at: https://aistudio.google.com/apikey
echo.

endlocal
