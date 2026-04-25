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

$PayloadZip = Join-Path $ProjectRoot "dist\PLANTSCADA-payload.zip"
if (Test-Path -LiteralPath $PayloadZip) {
    Remove-Item -LiteralPath $PayloadZip -Force
}
Write-Host "Creating payload zip: $PayloadZip"
Compress-Archive -Path (Join-Path $DistRoot "*") -DestinationPath $PayloadZip -CompressionLevel Optimal -Force

if (-not (Test-Path -LiteralPath $PayloadZip)) {
    throw "Failed to create payload zip: $PayloadZip"
}

Write-Host "Building PLANTSCADA-Setup.exe (one-file installer)..."

& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name PLANTSCADA-Setup `
    --add-data "$PayloadZip;." `
    (Join-Path $ProjectRoot "tools\setup_wizard.py")

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller setup build failed with exit code $LASTEXITCODE"
}

$SetupExe = Join-Path $ProjectRoot "dist\PLANTSCADA-Setup.exe"
Write-Host "Setup installer ready at: $SetupExe"
