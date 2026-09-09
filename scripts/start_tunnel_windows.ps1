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

$ConfigDir = Join-Path $env:USERPROFILE '.cloudflared'
$ConfigFile = Join-Path $ConfigDir 'config.yml'
$TunnelName = 'telegram-nemotron'

if (-not (Test-Path $ConfigFile)) {
    Write-Host "No existe una configuracion de Cloudflare Tunnel estable." -ForegroundColor Yellow
    Write-Host "IMPORTANTE: Quick Tunnels (*.trycloudflare.com) son temporales y no son compatibles con el streaming SSE usado por la Mini App." -ForegroundColor Yellow
    Write-Host "Para dejar el sistema estable necesitamos crear UNA VEZ un Tunnel con nombre y un dominio administrado por Cloudflare." -ForegroundColor Yellow
    Write-Host "Abriendo el proceso de autenticacion de Cloudflare..." -ForegroundColor Cyan
    & cloudflared tunnel login
    if ($LASTEXITCODE -ne 0) { throw "No se pudo completar cloudflared tunnel login." }

    Write-Host "Creando/recuperando el Tunnel '$TunnelName'..." -ForegroundColor Cyan
    $existing = & cloudflared tunnel list --output json 2>$null | ConvertFrom-Json
    $tunnel = $existing | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1
    if (-not $tunnel) {
        & cloudflared tunnel create $TunnelName
        if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el Tunnel '$TunnelName'." }
        $existing = & cloudflared tunnel list --output json 2>$null | ConvertFrom-Json
        $tunnel = $existing | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1
    }
    if (-not $tunnel) { throw "No se encontro el Tunnel '$TunnelName' despues de crearlo." }

    $hostname = Read-Host "Escribe el dominio publico para la API (ejemplo: api.tudominio.com)"
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

    & cloudflared tunnel route dns $TunnelName $hostname
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear la ruta DNS para $hostname." }

    $envFile = Join-Path $Root '.env'
    if (Test-Path $envFile) {
        $lines = Get-Content $envFile
        $filtered = $lines | Where-Object { $_ -notmatch '^MINI_APP_API_URL=' }
        ($filtered + "MINI_APP_API_URL=https://$hostname") | Set-Content $envFile -Encoding UTF8
    }

    Write-Host "Tunnel estable configurado: https://$hostname" -ForegroundColor Green
    Write-Host "Ahora actualiza la Mini App para usar esa URL y reinicia el bot/backend." -ForegroundColor Yellow
}

Write-Host "Iniciando Cloudflare Tunnel estable hacia http://127.0.0.1:8000 ..." -ForegroundColor Cyan
& cloudflared tunnel --config $ConfigFile run
