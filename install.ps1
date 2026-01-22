# natsh - Natural Shell
# Installation script for PowerShell
#
# INSTALL FROM GITHUB:
#   irm https://raw.githubusercontent.com/pieronoviello/natsh/main/install.ps1 | iex
#
# INSTALL LOCALLY:
#   .\install.ps1

$ErrorActionPreference = "Stop"

$INSTALL_DIR = "$env:USERPROFILE\.natsh"
$BIN_DIR = "$env:USERPROFILE\.local\bin"
$RAW_URL = "https://raw.githubusercontent.com/pieronoviello/natsh/main"

Write-Host ""
Write-Host "  natsh - Natural Shell" -ForegroundColor Cyan
Write-Host "  Talk to your terminal in plain English" -ForegroundColor DarkGray
Write-Host ""

# Check for Python
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3") {
            $python = $cmd
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "[X] Python 3 is required" -ForegroundColor Red
    Write-Host "    Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Python found: $python" -ForegroundColor Green

# Create install directory
if (-not (Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
}

# Check if running locally (with local files) or remotely (via irm | iex)
$isLocal = $false
if ($PSScriptRoot -and $PSScriptRoot -ne "") {
    $localNatshPy = Join-Path $PSScriptRoot "natsh.py"
    $localRequirements = Join-Path $PSScriptRoot "requirements.txt"
    if ((Test-Path $localNatshPy) -and (Test-Path $localRequirements)) {
        $isLocal = $true
    }
}

if ($isLocal) {
    Write-Host "[..] Installing from local files..." -ForegroundColor Yellow
    Copy-Item $localNatshPy "$INSTALL_DIR\natsh.py" -Force
    Copy-Item $localRequirements "$INSTALL_DIR\requirements.txt" -Force
} else {
    Write-Host "[..] Downloading from GitHub..." -ForegroundColor Yellow
    try {
        # Ensure TLS 1.2 for older Windows versions
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri "$RAW_URL/natsh.py" -OutFile "$INSTALL_DIR\natsh.py" -UseBasicParsing
        Invoke-WebRequest -Uri "$RAW_URL/requirements.txt" -OutFile "$INSTALL_DIR\requirements.txt" -UseBasicParsing
    } catch {
        Write-Host "[X] Download failed: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[OK] Files ready" -ForegroundColor Green

# Setup Python virtual environment
Write-Host "[..] Setting up Python environment (this may take a minute)..." -ForegroundColor Yellow
Push-Location $INSTALL_DIR

if (Test-Path "venv") {
    Remove-Item -Recurse -Force "venv"
}

& $python -m venv venv
& .\venv\Scripts\python.exe -m pip install --quiet --upgrade pip
& .\venv\Scripts\pip.exe install --quiet -r requirements.txt

Pop-Location

Write-Host "[OK] Python environment ready" -ForegroundColor Green

# Create bin directory
if (-not (Test-Path $BIN_DIR)) {
    New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null
}

# Create natsh.bat wrapper (for CMD)
$batchContent = @"
@echo off
"%USERPROFILE%\.natsh\venv\Scripts\python.exe" "%USERPROFILE%\.natsh\natsh.py" %*
"@
Set-Content -Path "$BIN_DIR\natsh.bat" -Value $batchContent -Encoding ASCII

# Create natsh.ps1 wrapper (for PowerShell)
$ps1Content = @'
& "$env:USERPROFILE\.natsh\venv\Scripts\python.exe" "$env:USERPROFILE\.natsh\natsh.py" @args
'@
Set-Content -Path "$BIN_DIR\natsh.ps1" -Value $ps1Content -Encoding UTF8

Write-Host "[OK] Commands created" -ForegroundColor Green

# Add to PATH if not already present
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
if ($userPath -notlike "*$BIN_DIR*") {
    Write-Host "[..] Adding to PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", "$BIN_DIR;$userPath", "User")
    $env:Path = "$BIN_DIR;$env:Path"
    Write-Host "[OK] Added to PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  natsh installed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open a NEW terminal"
Write-Host "  2. Run: natsh"
Write-Host "  3. Enter your Gemini API key (free)"
Write-Host "     https://aistudio.google.com/apikey"
Write-Host ""
