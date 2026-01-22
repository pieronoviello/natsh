# natsh - Natural Shell
# Uninstallation script for PowerShell
#
# UNINSTALL:
#   irm https://raw.githubusercontent.com/pieronoviello/natsh/main/uninstall.ps1 | iex

$ErrorActionPreference = "Stop"

$INSTALL_DIR = "$env:USERPROFILE\.natsh"
$BIN_DIR = "$env:USERPROFILE\.local\bin"

Write-Host ""
Write-Host "  natsh - Uninstaller" -ForegroundColor Cyan
Write-Host ""

# Check if natsh is installed
if (-not (Test-Path $INSTALL_DIR)) {
    Write-Host "  [!] natsh is not installed" -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# Remove installation directory
Write-Host "[1/2] Removing natsh files..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction SilentlyContinue
Write-Host "  [OK] Removed $INSTALL_DIR" -ForegroundColor Green

# Remove command wrappers
Write-Host "[2/2] Removing command wrappers..." -ForegroundColor Yellow
Remove-Item -Force "$BIN_DIR\natsh.bat" -ErrorAction SilentlyContinue
Remove-Item -Force "$BIN_DIR\natsh.ps1" -ErrorAction SilentlyContinue
Write-Host "  [OK] Removed natsh commands" -ForegroundColor Green

Write-Host ""
Write-Host "  ======================================" -ForegroundColor Green
Write-Host "  natsh uninstalled successfully!" -ForegroundColor Green
Write-Host "  ======================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Thanks for trying natsh!" -ForegroundColor DarkGray
Write-Host ""
