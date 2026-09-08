$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "No existe el entorno virtual. Ejecuta primero .\scripts\setup_windows.ps1"
}
if (-not (Test-Path ".env")) {
    throw "No existe .env. Ejecuta primero .\scripts\setup_windows.ps1 y configura las claves."
}

$env:PYTHONUNBUFFERED = "1"
$hostAddr = if ($env:LOCAL_API_HOST) { $env:LOCAL_API_HOST } else { "127.0.0.1" }
$port = if ($env:LOCAL_API_PORT) { $env:LOCAL_API_PORT } else { "8000" }

Write-Host "=== Iniciando servidor local ===" -ForegroundColor Cyan
Write-Host "API: http://$hostAddr`:$port/health"
Write-Host "Telegram: polling directo (sin Render y sin abrir puertos del router)"

$api = Start-Process -FilePath $VenvPython -ArgumentList @("-m","uvicorn","backend.main:app","--host",$hostAddr,"--port",$port) -WorkingDirectory $Root -PassThru
Start-Sleep -Seconds 2

$bot = Start-Process -FilePath $VenvPython -ArgumentList @("bot.py") -WorkingDirectory $Root -PassThru

Write-Host "API PID: $($api.Id) | Bot PID: $($bot.Id)" -ForegroundColor Green
Write-Host "Cierra esta ventana para detener ambos procesos." -ForegroundColor Yellow

try {
    while ($true) {
        if ($api.HasExited) { throw "El backend API se detuvo con codigo $($api.ExitCode)." }
        if ($bot.HasExited) { throw "El bot de Telegram se detuvo con codigo $($bot.ExitCode)." }
        Start-Sleep -Seconds 5
    }
}
finally {
    if (-not $api.HasExited) { Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue }
    if (-not $bot.HasExited) { Stop-Process -Id $bot.Id -Force -ErrorAction SilentlyContinue }
}
