param(
    [string]$PythonExe = "python",
    [string]$InnoCompilerPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BuildScript = Join-Path $ProjectRoot "scripts\build.ps1"
$InstallerScript = Join-Path $ProjectRoot "installer\PLANTSCADA.iss"

if (-not (Test-Path $InnoCompilerPath)) {
    throw "Inno Setup compiler not found at: $InnoCompilerPath"
}

& $BuildScript -PythonExe $PythonExe
if ($LASTEXITCODE -ne 0) {
    throw "Portable build step failed with exit code $LASTEXITCODE"
}

Write-Host "Building installer with Inno Setup..."
& $InnoCompilerPath $InstallerScript
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup build failed with exit code $LASTEXITCODE"
}

Write-Host "Installer build completed. Check: $ProjectRoot\installer-dist"
