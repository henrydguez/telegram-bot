$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "cloudflared no esta instalado. Intentando instalarlo con winget..." -ForegroundColor Yellow
        winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
        $cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
    }
}
if (-not $cloudflared) {
    throw "No se encontro cloudflared. Instala Cloudflare Tunnel y vuelve a ejecutar este script."
}

Write-Host "Abriendo tunel HTTPS hacia http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Write-Host "Copia la URL https://*.trycloudflare.com que aparezca y configuraremos la Mini App con ella." -ForegroundColor Yellow
& cloudflared tunnel --url http://127.0.0.1:8000
