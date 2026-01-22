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

# Step 1: Check for existing Python installation
Write-Host "[1/5] Checking for Python..." -ForegroundColor Yellow
$py = $null
@("python", "python3", "py") | ForEach-Object {
    if (-not $py) {
        try { if ((& $_ --version 2>&1) -match "Python 3") { $py = $_ } } catch {}
    }
}
if (-not $py) {
    Write-Host "  [X] Python 3 not found on your system" -ForegroundColor Red
    Write-Host "      Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "  [OK] Found: $py (your existing installation)" -ForegroundColor Green

# Step 2: Download natsh files
Write-Host "[2/5] Downloading natsh.py from GitHub..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
Invoke-WebRequest "$RAW/natsh.py" -OutFile "$INSTALL_DIR\natsh.py" -UseBasicParsing
Invoke-WebRequest "$RAW/requirements.txt" -OutFile "$INSTALL_DIR\requirements.txt" -UseBasicParsing
Write-Host "  [OK] Files saved to $INSTALL_DIR" -ForegroundColor Green

# Step 3: Create isolated virtual environment
Write-Host "[3/5] Creating isolated Python environment (venv)..." -ForegroundColor Yellow
Write-Host "      This keeps natsh dependencies separate from your system" -ForegroundColor DarkGray
Push-Location $INSTALL_DIR
if (Test-Path venv) {
    # Use cmd's rmdir for better handling of long paths on Windows
    cmd /c "rmdir /s /q venv" 2>$null
    Start-Sleep -Milliseconds 500
}
& $py -m venv venv 2>$null
Write-Host "  [OK] Virtual environment created at $INSTALL_DIR\venv" -ForegroundColor Green

# Step 4: Install dependencies inside venv
Write-Host "[4/5] Installing AI libraries inside venv..." -ForegroundColor Yellow
Write-Host "      (google-genai, openai, anthropic, pyreadline3)" -ForegroundColor DarkGray
& .\venv\Scripts\python.exe -m pip install -q --upgrade pip 2>$null
& .\venv\Scripts\pip.exe install -q -r requirements.txt 2>$null
Pop-Location
Write-Host "  [OK] Dependencies installed (only in venv, not system-wide)" -ForegroundColor Green

# Step 5: Create command wrappers and add to PATH
Write-Host "[5/5] Creating 'natsh' command..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null
'@echo off' + "`r`n" + '"%USERPROFILE%\.natsh\venv\Scripts\python.exe" "%USERPROFILE%\.natsh\natsh.py" %*' | Set-Content "$BIN_DIR\natsh.bat" -Encoding ASCII
'& "$env:USERPROFILE\.natsh\venv\Scripts\python.exe" "$env:USERPROFILE\.natsh\natsh.py" @args' | Set-Content "$BIN_DIR\natsh.ps1" -Encoding UTF8

$p = [Environment]::GetEnvironmentVariable("Path", "User")
if ($p -notlike "*$BIN_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$BIN_DIR;$p", "User")
    $env:Path = "$BIN_DIR;$env:Path"
    Write-Host "  [OK] Added $BIN_DIR to PATH" -ForegroundColor Green
} else {
    Write-Host "  [OK] PATH already configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "  ======================================" -ForegroundColor Green
Write-Host "  natsh installed successfully!" -ForegroundColor Green
Write-Host "  ======================================" -ForegroundColor Green
Write-Host ""
Write-Host "  What was installed:" -ForegroundColor Cyan
Write-Host "    - $INSTALL_DIR (natsh + isolated venv)"
Write-Host "    - $BIN_DIR\natsh.bat (command wrapper)"
Write-Host ""
Write-Host "  Your system Python was NOT modified." -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. Open a NEW terminal"
Write-Host "    2. Run: natsh"
Write-Host "    3. Get free API key: https://aistudio.google.com/apikey"
Write-Host ""
