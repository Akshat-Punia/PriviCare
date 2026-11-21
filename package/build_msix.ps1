<#
.SYNOPSIS
    Packages HealthGuard AI into an official Microsoft MSIX application (.msix)
    for Microsoft Store submission and Windows 10/11 sideloading.

.DESCRIPTION
    1. Copies binary dist/HealthGuard-AI.exe and asset logos to staging folder.
    2. Packages with MakeAppx.exe from Windows 10/11 SDK.
    3. Self-signs with a developer certificate or prepares for Microsoft Store submission.
#>

param(
    [string]$Config = "Release",
    [switch]$CreateCert
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$DistDir = Join-Path $ProjectRoot "dist"
$StagingDir = Join-Path $ProjectRoot "package\staging"
$OutputDir = Join-Path $ProjectRoot "dist\msix"

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  HealthGuard AI — Windows App / MSIX Packaging Utility" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

# 1. Verify executable exists
$ExePath = Join-Path $DistDir "HealthGuard-AI.exe"
if (-not (Test-Path $ExePath)) {
    Write-Error "HealthGuard-AI.exe not found in $DistDir. Run PyInstaller build first."
}

# 2. Prepare staging directory
if (Test-Path $StagingDir) {
    Remove-Item -Recurse -Force $StagingDir
}
New-Item -ItemType Directory -Path $StagingDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $StagingDir "assets") | Out-Null
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

# 3. Copy application files
Write-Host "[1/4] Staging application binaries and assets..." -ForegroundColor Green
Copy-Item $ExePath -Destination (Join-Path $StagingDir "HealthGuard-AI.exe")
Copy-Item (Join-Path $ProjectRoot "assets\*") -Destination (Join-Path $StagingDir "assets") -Recurse
Copy-Item (Join-Path $PSScriptRoot "AppxManifest.xml") -Destination (Join-Path $StagingDir "AppxManifest.xml")

# 4. Find MakeAppx.exe from Windows SDK
Write-Host "[2/4] Locating Windows SDK MakeAppx tool..." -ForegroundColor Green
$SdkPath = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits\10\bin" -Filter "MakeAppx.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1)

$MsixOut = Join-Path $OutputDir "HealthGuard-AI.msix"

if ($SdkPath) {
    Write-Host "Found MakeAppx.exe: $($SdkPath.FullName)" -ForegroundColor Cyan
    Write-Host "[3/4] Creating MSIX Package: $MsixOut..." -ForegroundColor Green
    & $SdkPath.FullName pack /d $StagingDir /p $MsixOut /o
    Write-Host "[4/4] MSIX package built successfully!" -ForegroundColor Green
} else {
    Write-Warning "MakeAppx.exe not found in standard Windows Kits path."
    Write-Host "Staging directory prepared at: $StagingDir" -ForegroundColor Yellow
    Write-Host "You can package it using Visual Studio or by installing the Windows 10/11 App SDK." -ForegroundColor Yellow
}

Write-Host "`nStaging files ready at: $StagingDir" -ForegroundColor Green
if (Test-Path $MsixOut) {
    $SizeMb = [math]::Round((Get-Item $MsixOut).Length / 1MB, 2)
    Write-Host ("MSIX Package: {0} ({1} MB)" -f $MsixOut, $SizeMb) -ForegroundColor Cyan
}
