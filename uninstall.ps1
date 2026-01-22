# natsh - Uninstaller (PowerShell)
# Removes natsh and all associated files
#
# Run: .\uninstall.ps1

$ErrorActionPreference = "Stop"

$INSTALL_DIR = "$env:USERPROFILE\.natsh"
$BIN_DIR = "$env:USERPROFILE\.local\bin"

Write-Host ""
Write-Host "  natsh - Uninstaller" -ForegroundColor Cyan
Write-Host ""

# Confirm uninstallation
$confirm = Read-Host "Remove natsh and all data? [y/N]"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Remove installation directory
if (Test-Path $INSTALL_DIR) {
    Write-Host "[..] Removing $INSTALL_DIR..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $INSTALL_DIR
    Write-Host "[OK] Installation directory removed" -ForegroundColor Green
} else {
    Write-Host "[--] Installation directory not found" -ForegroundColor DarkGray
}

# Remove natsh.bat wrapper
$batPath = "$BIN_DIR\natsh.bat"
if (Test-Path $batPath) {
    Write-Host "[..] Removing natsh.bat..." -ForegroundColor Yellow
    Remove-Item -Force $batPath
    Write-Host "[OK] natsh.bat removed" -ForegroundColor Green
} else {
    Write-Host "[--] natsh.bat not found" -ForegroundColor DarkGray
}

# Remove natsh.ps1 wrapper
$ps1Path = "$BIN_DIR\natsh.ps1"
if (Test-Path $ps1Path) {
    Write-Host "[..] Removing natsh.ps1..." -ForegroundColor Yellow
    Remove-Item -Force $ps1Path
    Write-Host "[OK] natsh.ps1 removed" -ForegroundColor Green
} else {
    Write-Host "[--] natsh.ps1 not found" -ForegroundColor DarkGray
}

# Optional: Remove from PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -like "*$BIN_DIR*") {
    $cleanPath = Read-Host "Remove $BIN_DIR from PATH? [y/N]"
    if ($cleanPath -eq "y" -or $cleanPath -eq "Y") {
        $newPath = ($userPath -split ";" | Where-Object { $_ -ne $BIN_DIR -and $_ -ne "" }) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "[OK] PATH cleaned" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  natsh uninstalled successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Removed:" -ForegroundColor Cyan
Write-Host "  - $INSTALL_DIR (config, history, venv)"
Write-Host "  - $BIN_DIR\natsh.bat"
Write-Host "  - $BIN_DIR\natsh.ps1"
Write-Host ""
