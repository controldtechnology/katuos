# setup-wsl2-build.ps1
# Instala WSL2 + Debian e prepara o ambiente de build do Katu OS
# REQUISITO: VT-x/AMD-V habilitado no BIOS
# Execute como Administrador

$env:PATH += ";C:\Program Files\Git\bin"

function Write-Cor {
    param([string]$Texto, [string]$Cor = "White")
    Write-Host $Texto -ForegroundColor $Cor
}

Write-Cor ""
Write-Cor "  Katu OS — Setup WSL2 e Build" "Green"
Write-Cor "  ═══════════════════════════════" "DarkGray"
Write-Cor ""

# Verificar admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Cor "  ERRO: Execute como Administrador!" "Red"
    exit 1
}

# Verificar VT-x
$cpu = Get-WmiObject -Class Win32_Processor
if (-not $cpu.VirtualizationFirmwareEnabled) {
    Write-Cor "  ATENÇÃO: VT-x NÃO está habilitado no BIOS!" "Red"
    Write-Cor ""
    Write-Cor "  Para habilitar:" "Yellow"
    Write-Cor "  1. Reinicie o computador" "White"
    Write-Cor "  2. Entre no BIOS/UEFI:" "White"
    Write-Cor "     • Dell/Lenovo:  F2 ou F1 durante a inicialização" "White"
    Write-Cor "     • HP:           F10 ou Esc" "White"
    Write-Cor "     • ASUS/Gigabyte: DEL ou F2" "White"
    Write-Cor "  3. Procure por uma das opções:" "White"
    Write-Cor "     • 'Intel Virtualization Technology' → Enable" "White"
    Write-Cor "     • 'Intel VT-x' → Enable" "White"
    Write-Cor "     • 'AMD-V' ou 'SVM Mode' → Enable" "White"
    Write-Cor "  4. Salve (F10) e reinicie" "White"
    Write-Cor "  5. Execute este script novamente" "White"
    Write-Cor ""
    Write-Cor "  CPU detectada: $($cpu.Name)" "DarkGray"
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Cor "  ✓ VT-x habilitado!" "Green"
Write-Cor ""

# Habilitar WSL e Virtual Machine Platform
Write-Cor "  Habilitando recursos WSL2..." "Cyan"
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null

# Instalar WSL2
Write-Cor "  Instalando WSL2 + Debian..." "Cyan"
wsl --install -d Debian --no-launch 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Cor "  Reinicialização necessária para completar a instalação do WSL2." "Yellow"
    Write-Cor "  Após reiniciar, execute este script novamente." "White"
    $reiniciar = Read-Host "  Reiniciar agora? (s/n)"
    if ($reiniciar -eq 's') { Restart-Computer -Force }
    exit 0
}

Write-Cor "  ✓ WSL2 instalado!" "Green"

# Definir WSL2 como padrão
wsl --set-default-version 2 2>&1 | Out-Null

# Criar script de build dentro do WSL2
$buildScript = @'
#!/bin/bash
set -e

echo "=== Katu OS Build ==="
echo "Copiando projeto para o Linux..."
cp -r /mnt/c/katuos ~/katuos
cd ~/katuos

echo "Instalando dependências de build..."
sudo apt-get update -qq
sudo apt-get install -y \
    live-build debootstrap squashfs-tools xorriso \
    isolinux syslinux-common dpkg-dev apt-utils rsync \
    gzip xz-utils wget curl ca-certificates gnupg \
    python3-pyqt5 python3-pip 2>/dev/null

echo "Iniciando build da ISO (45-90 minutos)..."
bash scripts/build.sh

echo ""
echo "=== BUILD CONCLUÍDO ==="
ISO=$(find output/ -name "*.iso" | head -1)
if [ -n "$ISO" ]; then
    echo "ISO: $ISO"
    echo "Copiando para Windows..."
    cp "$ISO" /mnt/c/katuos/output/
    cp "${ISO}.sha256" /mnt/c/katuos/output/ 2>/dev/null || true
    echo "ISO disponível em: C:\katuos\output\"
fi
'@

$buildScript | Out-File -FilePath "C:\katuos\scripts\wsl2-build.sh" -Encoding utf8 -NoNewline

Write-Cor "  ✓ Script de build WSL2 criado!" "Green"
Write-Cor ""
Write-Cor "  Para iniciar o build da ISO, execute:" "Cyan"
Write-Cor ""
Write-Cor "     wsl -d Debian bash /mnt/c/katuos/scripts/wsl2-build.sh" "Yellow"
Write-Cor ""
Write-Cor "  Ou abra o Debian no menu Iniciar e execute:" "White"
Write-Cor "     bash /mnt/c/katuos/scripts/wsl2-build.sh" "Yellow"
Write-Cor ""

$buildAgora = Read-Host "  Iniciar o build agora no WSL2? (s/n)"
if ($buildAgora -eq 's') {
    Write-Cor ""
    Write-Cor "  Iniciando build... (isso vai abrir uma janela WSL2)" "Green"
    Start-Process "wsl" -ArgumentList "-d Debian bash /mnt/c/katuos/scripts/wsl2-build.sh"
    Write-Cor "  Build iniciado! Acompanhe na janela WSL2." "Green"
    Write-Cor "  A ISO ficará em: C:\katuos\output\ quando pronto." "White"
}

Write-Cor ""
