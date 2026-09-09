$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    throw "No se encontro cloudflared. Instala cloudflared antes de continuar."
}

$ConfigDir = Join-Path $env:USERPROFILE '.cloudflared'
$ConfigFile = Join-Path $ConfigDir 'config.yml'
$TunnelName = 'telegram-nemotron'

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null

Write-Host "1/4 - Autenticando Cloudflare. Se abrira el navegador..." -ForegroundColor Cyan
& cloudflared tunnel login
if ($LASTEXITCODE -ne 0) { throw "No se pudo completar la autenticacion de Cloudflare." }

Write-Host "2/4 - Creando o recuperando el Tunnel '$TunnelName'..." -ForegroundColor Cyan
$existing = @()
try { $existing = & cloudflared tunnel list --output json 2>$null | ConvertFrom-Json } catch {}
$tunnel = $existing | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1
if (-not $tunnel) {
    & cloudflared tunnel create $TunnelName
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el Tunnel '$TunnelName'." }
    $existing = & cloudflared tunnel list --output json 2>$null | ConvertFrom-Json
    $tunnel = $existing | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1
}
if (-not $tunnel) { throw "No se encontro el Tunnel '$TunnelName'." }

$hostname = Read-Host "3/4 - Escribe el dominio publico de la API (ejemplo: api.tudominio.com)"
if ([string]::IsNullOrWhiteSpace($hostname)) { throw "Debes indicar un hostname publico." }

$credentialFile = Join-Path $ConfigDir ($tunnel.id + '.json')
if (-not (Test-Path $credentialFile)) { throw "No se encontro el archivo de credenciales: $credentialFile" }

@"
tunnel: $($tunnel.id)
credentials-file: $credentialFile
ingress:
  - hostname: $hostname
    service: http://127.0.0.1:8000
  - service: http_status:404
"@ | Set-Content -Path $ConfigFile -Encoding UTF8

Write-Host "4/4 - Creando la ruta DNS..." -ForegroundColor Cyan
& cloudflared tunnel route dns $TunnelName $hostname
if ($LASTEXITCODE -ne 0) { throw "No se pudo crear la ruta DNS para $hostname. Comprueba que el dominio esta gestionado por Cloudflare." }

Write-Host "Validando configuracion..." -ForegroundColor Cyan
& cloudflared tunnel --config $ConfigFile ingress validate
if ($LASTEXITCODE -ne 0) { throw "La configuracion del Tunnel no es valida." }

Write-Host "" 
Write-Host "CLOUDFLARE TUNNEL ESTABLE CONFIGURADO CORRECTAMENTE" -ForegroundColor Green
Write-Host "URL de la API: https://$hostname" -ForegroundColor Green
Write-Host "Configuracion: $ConfigFile" -ForegroundColor Green
Write-Host "" 
Write-Host "IMPORTANTE: dime la URL que aparece arriba para fijarla en la Mini App de GitHub Pages." -ForegroundColor Yellow
Write-Host "Despues podremos activar el arranque automatico definitivo." -ForegroundColor Yellow
