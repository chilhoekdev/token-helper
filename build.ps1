# BoostCypher Token Helper Build Script
# This script compiles the Python application to an executable using PyInstaller

param(
    [switch]$OpenOutput = $false
)

# Set error handling
$ErrorActionPreference = "Stop"

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

try {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "BoostCypher Token Helper - Build Script" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Change to project directory
    Set-Location $scriptDir
    Write-Host "Working directory: $(Get-Location)" -ForegroundColor Yellow

    # Check if .venv exists
    if (-not (Test-Path ".venv")) {
        Write-Host "Error: Virtual environment not found at .venv" -ForegroundColor Red
        exit 1
    }

    Write-Host "Virtual environment found" -ForegroundColor Green
    Write-Host ""

    # Run PyInstaller
    Write-Host "Building executable..." -ForegroundColor Yellow
    Write-Host "Running PyInstaller with icon and UI bundling" -ForegroundColor Gray
    Write-Host ""

    & .\.\.venv\Scripts\pyinstaller --onefile --windowed --icon=boostcypher.ico --add-data "ui;ui" --hidden-import=windowfix --name "BoostCypher Token Helper" main.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Build Successful!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Output: .\dist\BoostCypher Token Helper.exe" -ForegroundColor Green
        Write-Host ""

        if ($OpenOutput) {
            Write-Host "Opening output directory..." -ForegroundColor Yellow
            Invoke-Item ".\dist"
        }
        else {
            Write-Host "Tip: Use -OpenOutput flag to automatically open the output folder" -ForegroundColor Gray
            Write-Host "Example: .\build.ps1 -OpenOutput" -ForegroundColor Gray
        }
    }
    else {
        Write-Host ""
        Write-Host "Build failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
