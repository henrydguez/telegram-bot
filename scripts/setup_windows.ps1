$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "=== Telegram Bot - instalacion local Windows ===" -ForegroundColor Cyan

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $python) {
    throw "Python no esta instalado. Instala Python 3.11 o 3.12 y vuelve a ejecutar este script."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    if ((Get-Command py -ErrorAction SilentlyContinue)) { py -3 -m venv .venv } else { python -m venv .venv }
}

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
Write-Host "Actualizando pip..." -ForegroundColor Yellow
& $VenvPython -m pip install --upgrade pip
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
& $VenvPython -m pip install -r backend\requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Se creo .env desde .env.example." -ForegroundColor Green
    Write-Host "IMPORTANTE: abre .env y coloca BOT_TOKEN y NVIDIA_API_KEY." -ForegroundColor Yellow
}

Write-Host ""; Write-Host "Instalacion preparada correctamente." -ForegroundColor Green
Write-Host "Siguiente paso: ejecutar .\scripts\start_windows.ps1" -ForegroundColor Cyan
