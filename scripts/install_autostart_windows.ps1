$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$StartScript = Join-Path $Root "scripts\start_windows.ps1"
$TunnelScript = Join-Path $Root "scripts\start_tunnel_windows.ps1"
if (-not (Test-Path $StartScript)) { throw "No existe $StartScript" }
if (-not (Test-Path $TunnelScript)) { throw "No existe $TunnelScript" }

# No requiere permisos de administrador: usamos la carpeta de inicio del usuario.
$Startup = [Environment]::GetFolderPath('Startup')
if (-not $Startup) { throw "No se pudo localizar la carpeta de inicio de Windows." }

$WshShell = New-Object -ComObject WScript.Shell

function New-StartupShortcut {
    param(
        [string]$Name,
        [string]$ScriptPath
    )

    $ShortcutPath = Join-Path $Startup "$Name.lnk"
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
    $Shortcut.WorkingDirectory = $Root
    $Shortcut.WindowStyle = 1
    $Shortcut.Description = "Telegram Nemotron - $Name"
    $Shortcut.Save()
}

New-StartupShortcut -Name "Telegram Nemotron Bot" -ScriptPath $StartScript
New-StartupShortcut -Name "Telegram Nemotron Cloudflare Tunnel" -ScriptPath $TunnelScript

Write-Host "Autoinicio instalado correctamente para el usuario actual:" -ForegroundColor Green
Write-Host "  - Bot/backend: Telegram Nemotron Bot"
Write-Host "  - Tunnel: Telegram Nemotron Cloudflare Tunnel"
Write-Host "Carpeta de inicio: $Startup"
Write-Host "No se necesitan permisos de administrador." -ForegroundColor Green
Write-Host "IMPORTANTE: Quick Tunnel genera una URL temporal nueva cuando se reinicia. Para una URL estable necesitaremos un Cloudflare Tunnel con dominio propio." -ForegroundColor Yellow
Write-Host "Para eliminarlo: Remove-Item (Join-Path ([Environment]::GetFolderPath('Startup')) 'Telegram Nemotron Bot.lnk'), (Join-Path ([Environment]::GetFolderPath('Startup')) 'Telegram Nemotron Cloudflare Tunnel.lnk') -Force" -ForegroundColor Yellow
