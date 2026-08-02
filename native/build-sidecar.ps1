# Build the PyInstaller backend exe and copy into Tauri resources.
# See mcp-central-docs/standards/rules/tauri_nsis_building.md
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RepoName = Split-Path -Leaf $Root
$Triple = "x86_64-pc-windows-msvc"
$ResourceDir = "$PSScriptRoot\resources"
$DevDir = "$PSScriptRoot\binaries"
New-Item -ItemType Directory -Force -Path $ResourceDir, $DevDir | Out-Null

Push-Location $Root
$pyi = "$Root\.venv\Scripts\pyinstaller.exe"
if (-not (Test-Path $pyi)) { uv add --dev pyinstaller }
& $pyi "$Root\demo_app-backend.spec" --clean --noconfirm
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
Pop-Location

$src = "$Root\dist\demo_app-backend.exe"
if (-not (Test-Path $src)) { throw "Backend exe not found at $src" }
Copy-Item $src "$ResourceDir\demo_app-backend.exe" -Force
Copy-Item $src "$DevDir\demo_app-backend-$Triple.exe" -Force
if (Test-Path "$Root\.env.example") { Copy-Item "$Root\.env.example" "$ResourceDir\.env.example" -Force }
Write-Host "Backend exe staged into Tauri resources." -ForegroundColor Green