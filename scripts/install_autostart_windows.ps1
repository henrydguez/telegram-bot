$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$StartScript = Join-Path $Root "scripts\start_windows.ps1"
$TunnelScript = Join-Path $Root "scripts\start_tunnel_windows.ps1"
if (-not (Test-Path $StartScript)) { throw "No existe $StartScript" }
if (-not (Test-Path $TunnelScript)) { throw "No existe $TunnelScript" }

$TaskName = "TelegramNemotronLocalServer"
$TunnelTaskName = "TelegramNemotronCloudflareTunnel"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$StartScript`""
$TunnelAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$TunnelScript`""

$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Inicia el backend local y el bot de Telegram al iniciar sesion." -Force
Register-ScheduledTask -TaskName $TunnelTaskName -Action $TunnelAction -Trigger $Trigger -Settings $Settings -Description "Inicia Cloudflare Tunnel para exponer la API local de la Mini App." -Force

Write-Host "Autoinicio instalado correctamente:" -ForegroundColor Green
Write-Host "  - $TaskName"
Write-Host "  - $TunnelTaskName"
Write-Host "Ambos se reiniciaran automaticamente si se detienen." -ForegroundColor Green
Write-Host "IMPORTANTE: Quick Tunnel genera una URL temporal nueva cuando se reinicia. Para una URL estable necesitaremos un Cloudflare Tunnel con dominio propio." -ForegroundColor Yellow
Write-Host "Para eliminarlo: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false; Unregister-ScheduledTask -TaskName '$TunnelTaskName' -Confirm:`$false" -ForegroundColor Yellow
