$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Project virtual environment not found. Create .venv and install requirements first."
}

Push-Location $root
try {
    & $python tools/create_windows_icon.py
    if ($LASTEXITCODE -ne 0) { throw "Could not generate the Windows icon." }

    & $python -m PyInstaller --noconfirm --clean --windowed --name SmallPunchPuppies --icon assets/hammy.ico --add-data "assets;assets" main.py
    if ($LASTEXITCODE -ne 0) { throw "The game build failed." }

    & $python -m PyInstaller --noconfirm --clean --onefile --windowed --name SmallPunchPuppiesUpdater updater.py
    if ($LASTEXITCODE -ne 0) { throw "The updater build failed." }

    Copy-Item -LiteralPath "dist\SmallPunchPuppiesUpdater.exe" -Destination "dist\SmallPunchPuppies\SmallPunchPuppiesUpdater.exe" -Force
    Copy-Item -LiteralPath "packaging\README_FIRST.txt" -Destination "dist\SmallPunchPuppies\README_FIRST.txt" -Force
    $versionLine = Select-String -Path "core\version.py" -Pattern '^VERSION = "([^"]+)"$'
    if (-not $versionLine) { throw "Could not read VERSION from core\version.py." }
    $version = $versionLine.Matches[0].Groups[1].Value
    $packageName = "SmallPunchPuppies-Windows-v$version.zip"
    $package = Join-Path $root $packageName
    if (Test-Path -LiteralPath $package) { Remove-Item -LiteralPath $package -Force }
    Compress-Archive -Path "dist\SmallPunchPuppies\*" -DestinationPath $package -CompressionLevel Optimal

    Write-Host "Playtest build: dist\SmallPunchPuppies\SmallPunchPuppies.exe"
    Write-Host "Portable package to share: $packageName"
}
finally {
    Pop-Location
}
