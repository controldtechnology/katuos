param(
    [ValidateSet('Create','Start','Capture','Command','Keys','Console','Interrupt','PowerOff','ForwardSSH','SSH','Sync','SyncSource')][string]$Action,
    [string]$Iso,
    [string]$Command,
    [string]$CommandBase64,
    [string[]]$Keys,
    [string]$Evidence = 'screen'
)
$ErrorActionPreference = 'Stop'
$vbox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$vm = 'Katu-Audit-20260923'
$base = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../output/audit-20260923'))
function Invoke-VBox { & $vbox @args; if ($LASTEXITCODE -ne 0) { throw "VBoxManage failed: $LASTEXITCODE" } }
switch ($Action) {
    'Create' {
        if (-not (Test-Path -LiteralPath $Iso -PathType Leaf)) { throw 'ISO missing' }
        if ([IO.Path]::GetExtension($Iso) -ne '.iso') { throw 'Use the original ISO, never unattended VISO' }
        Invoke-VBox createvm --name $vm --ostype Debian_64 --basefolder $base --register
        Invoke-VBox modifyvm $vm --memory 4096 --cpus 2 --firmware efi --graphicscontroller vmsvga --vram 128 --accelerate-3d off --boot1 dvd --boot2 disk --nic1 nat --uart1 0x3F8 4 --uartmode1 file "$base/serial.log"
        Invoke-VBox storagectl $vm --name SATA --add sata --controller IntelAhci --portcount 2
        Invoke-VBox createmedium disk --filename "$base/$vm/install.vdi" --size 32768 --format VDI
        Invoke-VBox storageattach $vm --storagectl SATA --port 0 --device 0 --type hdd --medium "$base/$vm/install.vdi"
        Invoke-VBox storageattach $vm --storagectl SATA --port 1 --device 0 --type dvddrive --medium $Iso
    }
    'Start' { Invoke-VBox startvm $vm --type headless }
    'Capture' {
        if ($Evidence -notmatch '^[a-zA-Z0-9_-]+$') { throw 'Invalid evidence name' }
        Invoke-VBox controlvm $vm screenshotpng "$base/$Evidence.png"
    }
    'Command' {
        if ($CommandBase64) { $Command = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($CommandBase64)) }
        Invoke-VBox controlvm $vm keyboardputstring $Command
        Invoke-VBox controlvm $vm keyboardputscancode 1c 9c
    }
    'Keys' { Invoke-VBox controlvm $vm keyboardputscancode @Keys }
    'Console' { Invoke-VBox controlvm $vm keyboardputscancode 1d 38 3c bc b8 9d }
    'Interrupt' { Invoke-VBox controlvm $vm keyboardputscancode 1d 2e ae 9d }
    'ForwardSSH' { Invoke-VBox controlvm $vm natpf1 'audit-ssh,tcp,127.0.0.1,2226,,22' }
    'SSH' {
        if ($CommandBase64) { $Command = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($CommandBase64)) }
        & ssh -i "$base/../virtualbox/test-vm-key" -o BatchMode=yes -o "UserKnownHostsFile=$base/known_hosts" -p 2226 katu@127.0.0.1 $Command
        if ($LASTEXITCODE -ne 0) { throw "Guest command failed: $LASTEXITCODE" }
    }
    'Sync' {
        & scp -i "$base/../virtualbox/test-vm-key" -o BatchMode=yes -o "UserKnownHostsFile=$base/known_hosts" -P 2226 -r $PSScriptRoot katu@127.0.0.1:/tmp/katu-scripts-new
        if ($LASTEXITCODE -ne 0) { throw "Guest copy failed: $LASTEXITCODE" }
    }
    'SyncSource' {
        & scp -i "$base/../virtualbox/test-vm-key" -o BatchMode=yes -o "UserKnownHostsFile=$base/known_hosts" -P 2226 "$base/source-check.tar.gz" katu@127.0.0.1:/tmp/source-check.tar.gz
        if ($LASTEXITCODE -ne 0) { throw "Source copy failed: $LASTEXITCODE" }
    }
    'PowerOff' { Invoke-VBox controlvm $vm poweroff }
}
