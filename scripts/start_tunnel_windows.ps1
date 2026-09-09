$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) { throw "No se encontro cloudflared. Instala Cloudflare Tunnel antes de iniciar el servicio." }

$ConfigFile = Join-Path $env:USERPROFILE '.cloudflared\config.yml'
if (-not (Test-Path $ConfigFile)) {
    Write-Host "Cloudflare Tunnel estable aun no esta configurado. Ejecuta una vez:" -ForegroundColor Yellow
    Write-Host ".\scripts\setup_cloudflare_stable_windows.ps1" -ForegroundColor Cyan
    exit 0
}

Write-Host "Iniciando Cloudflare Tunnel estable hacia http://127.0.0.1:8000 ..." -ForegroundColor Cyan
& cloudflared tunnel --config $ConfigFile run
