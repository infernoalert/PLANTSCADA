param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Building portable distribution with PyInstaller..."

& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name PLANTSCADA `
    --add-data "controllers/Readme;controllers/Readme" `
    main.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

$DistRoot = Join-Path $ProjectRoot "dist\PLANTSCADA"
$InputDir = Join-Path $DistRoot "input"
$OutputDir = Join-Path $DistRoot "output"

New-Item -ItemType Directory -Force -Path $InputDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host "Portable build ready at: $DistRoot"
