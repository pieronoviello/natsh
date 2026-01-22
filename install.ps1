# natsh - Natural Shell
# Installation script for PowerShell
#
# INSTALL:
#   irm https://raw.githubusercontent.com/pieronoviello/natsh/main/install.ps1 | iex

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = "Stop"

$INSTALL_DIR = "$env:USERPROFILE\.natsh"
$BIN_DIR = "$env:USERPROFILE\.local\bin"
$RAW = "https://raw.githubusercontent.com/pieronoviello/natsh/main"

Write-Host ""
Write-Host "  natsh - Natural Shell" -ForegroundColor Cyan
Write-Host "  Talk to your terminal in plain English" -ForegroundColor DarkGray
Write-Host ""

# Check Python
$py = $null
@("python", "python3", "py") | ForEach-Object {
    if (-not $py) {
        try { if ((& $_ --version 2>&1) -match "Python 3") { $py = $_ } } catch {}
    }
}
if (-not $py) {
    Write-Host "[X] Python 3 required - https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python: $py" -ForegroundColor Green

# Download files
Write-Host "[..] Downloading..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
Invoke-WebRequest "$RAW/natsh.py" -OutFile "$INSTALL_DIR\natsh.py" -UseBasicParsing
Invoke-WebRequest "$RAW/requirements.txt" -OutFile "$INSTALL_DIR\requirements.txt" -UseBasicParsing
Write-Host "[OK] Downloaded" -ForegroundColor Green

# Setup venv
Write-Host "[..] Installing dependencies..." -ForegroundColor Yellow
Push-Location $INSTALL_DIR
if (Test-Path venv) { Remove-Item -Recurse -Force venv }
& $py -m venv venv 2>$null
& .\venv\Scripts\python.exe -m pip install -q --upgrade pip 2>$null
& .\venv\Scripts\pip.exe install -q -r requirements.txt 2>$null
Pop-Location
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Create wrappers
New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null
'@echo off' + "`r`n" + '"%USERPROFILE%\.natsh\venv\Scripts\python.exe" "%USERPROFILE%\.natsh\natsh.py" %*' | Set-Content "$BIN_DIR\natsh.bat" -Encoding ASCII
'& "$env:USERPROFILE\.natsh\venv\Scripts\python.exe" "$env:USERPROFILE\.natsh\natsh.py" @args' | Set-Content "$BIN_DIR\natsh.ps1" -Encoding UTF8

# Add to PATH
$p = [Environment]::GetEnvironmentVariable("Path", "User")
if ($p -notlike "*$BIN_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$BIN_DIR;$p", "User")
    $env:Path = "$BIN_DIR;$env:Path"
}

Write-Host ""
Write-Host "  [OK] natsh installed!" -ForegroundColor Green
Write-Host ""
Write-Host "  Next: Open NEW terminal and run 'natsh'" -ForegroundColor Cyan
Write-Host "  API key: https://aistudio.google.com/apikey" -ForegroundColor DarkGray
Write-Host ""
