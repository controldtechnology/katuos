param(
    [ValidateSet('Capture','Diagnose')][string]$Action = 'Capture'
)
$ErrorActionPreference = 'Stop'
$vbox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$audit = Join-Path $PSScriptRoot '../output/audit-20260923'
function Invoke-VBox { & $vbox @args; if ($LASTEXITCODE -ne 0) { throw "VBoxManage failed: $LASTEXITCODE" } }
if ($Action -eq 'Diagnose') {
    Invoke-VBox controlvm katuos keyboardputstring 'mount; ls /scripts/live /lib/live/boot; ls -l /mnt/katu-root/sbin/init /mnt/katu-root/usr/lib/systemd/systemd; cat /conf/param.conf; dmesg | tail -25'
    Invoke-VBox controlvm katuos keyboardputscancode 1c 9c
    Start-Sleep -Seconds 2
}
Invoke-VBox controlvm katuos screenshotpng (Join-Path $audit "$Action.png")
