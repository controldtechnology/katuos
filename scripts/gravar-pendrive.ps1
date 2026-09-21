# gravar-pendrive.ps1 — Grava a ISO do Katu OS em um pendrive
# Execute como Administrador: powershell -ExecutionPolicy Bypass -File scripts\gravar-pendrive.ps1

param(
    [string]$IsoPath = ""
)

$Host.UI.RawUI.WindowTitle = "Katu OS — Gravador de Pendrive"

function Write-Cor {
    param([string]$Texto, [string]$Cor = "White")
    Write-Host $Texto -ForegroundColor $Cor
}

Write-Cor ""
Write-Cor "  ██╗  ██╗ █████╗ ████████╗██╗   ██╗     ██████╗ ███████╗" "Green"
Write-Cor "  ██║ ██╔╝██╔══██╗╚══██╔══╝██║   ██║    ██╔═══██╗██╔════╝" "Green"
Write-Cor "  █████╔╝ ███████║   ██║   ██║   ██║    ██║   ██║███████╗" "Green"
Write-Cor "  ██╔═██╗ ██╔══██║   ██║   ██║   ██║    ██║   ██║╚════██║" "Green"
Write-Cor "  ██║  ██╗██║  ██║   ██║   ╚██████╔╝    ╚██████╔╝███████║" "Green"
Write-Cor "  ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝" "Green"
Write-Cor ""
Write-Cor "  Gravador de Pendrive de Instalação" "Cyan"
Write-Cor "  ════════════════════════════════════" "DarkGray"
Write-Cor ""

# Verificar permissões de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Cor "  ERRO: Execute este script como Administrador!" "Red"
    Write-Cor "  Clique com botão direito no PowerShell → 'Executar como administrador'" "Yellow"
    Write-Host ""; Read-Host "Pressione Enter para sair"
    exit 1
}

# Localizar ISO
if (-not $IsoPath) {
    # Procurar na pasta output/
    $isoFiles = Get-ChildItem -Path "C:\katuos\output\", ".\output\", ".\" -Filter "katu-os*.iso" -ErrorAction SilentlyContinue
    if ($isoFiles) {
        $IsoPath = $isoFiles[0].FullName
        Write-Cor "  ISO encontrada: $IsoPath" "Green"
    } else {
        Write-Cor "  ISO não encontrada automaticamente." "Yellow"
        Write-Cor "  Informe o caminho da ISO:" "White"
        $IsoPath = Read-Host "  Caminho"
    }
}

if (-not (Test-Path $IsoPath)) {
    Write-Cor "  ERRO: Arquivo não encontrado: $IsoPath" "Red"
    exit 1
}

$isoSize = (Get-Item $IsoPath).Length
$isoSizeMB = [math]::Round($isoSize / 1MB)
Write-Cor "  ISO: $(Split-Path $IsoPath -Leaf) ($isoSizeMB MB)" "White"
Write-Cor ""

# Listar pendrives disponíveis
Write-Cor "  Detectando pendrives e discos removíveis..." "Cyan"
Write-Cor ""

$discos = Get-Disk | Where-Object { $_.BusType -in @('USB', 'SD') -and $_.Size -gt 0 }

if (-not $discos) {
    Write-Cor "  Nenhum pendrive detectado." "Yellow"
    Write-Cor "  Conecte um pendrive de pelo menos $([math]::Round($isoSizeMB * 1.2 / 1024, 1)) GB e tente novamente." "White"
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Cor "  Pendrives disponíveis:" "White"
Write-Cor "  ┌─────┬────────────────────────────────┬──────────┐" "DarkGray"
Write-Cor "  │ Num │ Nome                           │ Tamanho  │" "DarkGray"
Write-Cor "  ├─────┼────────────────────────────────┼──────────┤" "DarkGray"

$discoLista = @()
foreach ($d in $discos) {
    $tamGB = [math]::Round($d.Size / 1GB, 1)
    $nome = if ($d.FriendlyName) { $d.FriendlyName.PadRight(30).Substring(0, 30) } else { "Disco removível".PadRight(30) }
    Write-Cor "  │  $($discoLista.Count + 1)  │ $nome │ $($tamGB.ToString("0.0").PadLeft(6)) GB │" "White"
    $discoLista += $d
}
Write-Cor "  └─────┴────────────────────────────────┴──────────┘" "DarkGray"
Write-Cor ""

# Selecionar disco
do {
    $escolha = Read-Host "  Qual pendrive usar? (número)"
    $num = 0
    [int]::TryParse($escolha, [ref]$num) | Out-Null
} while ($num -lt 1 -or $num -gt $discoLista.Count)

$disco = $discoLista[$num - 1]
$tamGB = [math]::Round($disco.Size / 1GB, 1)
$isoGB = [math]::Round($isoSize / 1GB, 1)

Write-Cor ""
Write-Cor "  Disco selecionado: $($disco.FriendlyName) ($tamGB GB)" "Yellow"

# Verificar tamanho mínimo
if ($disco.Size -lt $isoSize + 256MB) {
    Write-Cor "  ERRO: Pendrive muito pequeno! Precisa de pelo menos $([math]::Round(($isoSize + 256MB) / 1GB, 1)) GB." "Red"
    Read-Host "Pressione Enter para sair"
    exit 1
}

# AVISO FINAL
Write-Cor ""
Write-Cor "  ╔══════════════════════════════════════════════════════╗" "Red"
Write-Cor "  ║  ATENÇÃO: TODOS OS DADOS DO PENDRIVE SERÃO APAGADOS  ║" "Red"
Write-Cor "  ╚══════════════════════════════════════════════════════╝" "Red"
Write-Cor ""
Write-Cor "  Pendrive: $($disco.FriendlyName) — $tamGB GB" "White"
Write-Cor "  ISO:      $(Split-Path $IsoPath -Leaf) — $isoGB GB" "White"
Write-Cor "  Disco #:  $($disco.Number)" "White"
Write-Cor ""

$confirmar = Read-Host "  Digite CONFIRMAR para continuar"
if ($confirmar -ne "CONFIRMAR") {
    Write-Cor "  Operação cancelada." "Yellow"
    exit 0
}

Write-Cor ""
Write-Cor "  Iniciando gravação..." "Green"

try {
    # Usar dd via PowerShell (método nativo Windows)
    # Alternativa: usar Rufus em modo silencioso se disponível

    # Método 1: Tentar com o comando dd do Git for Windows
    $dd = "C:\Program Files\Git\usr\bin\dd.exe"
    if (Test-Path $dd) {
        Write-Cor "  Usando dd (Git for Windows)..." "Cyan"
        $discoPath = "\\.\PhysicalDrive$($disco.Number)"

        # Desmontar volumes no disco
        $volumes = Get-Partition -DiskNumber $disco.Number -ErrorAction SilentlyContinue
        foreach ($v in $volumes) {
            if ($v.DriveLetter) {
                try { mountvol "$($v.DriveLetter):\" /d 2>$null } catch {}
            }
        }

        Write-Cor "  Gravando ISO → $discoPath" "White"
        Write-Cor "  (Isso pode demorar 5-20 minutos dependendo do pendrive)" "DarkGray"

        $processo = Start-Process -FilePath $dd `
            -ArgumentList "if=`"$IsoPath`" of=`"$discoPath`" bs=4M status=progress" `
            -Wait -PassThru -NoNewWindow

        if ($processo.ExitCode -eq 0) {
            Write-Cor ""
            Write-Cor "  ✓ GRAVAÇÃO CONCLUÍDA COM SUCESSO!" "Green"
        } else {
            throw "dd retornou código $($processo.ExitCode)"
        }
    } else {
        # Método 2: Sugerir Balena Etcher
        Write-Cor ""
        Write-Cor "  dd não encontrado. Use um dos programas abaixo:" "Yellow"
        Write-Cor ""
        Write-Cor "  RECOMENDADO — Balena Etcher (gratuito, simples):" "Cyan"
        Write-Cor "  1. Baixe em: https://etcher.balena.io/" "White"
        Write-Cor "  2. Abra o Etcher" "White"
        Write-Cor "  3. Selecione a ISO: $IsoPath" "White"
        Write-Cor "  4. Selecione o pendrive" "White"
        Write-Cor "  5. Clique em Flash!" "White"
        Write-Cor ""
        Write-Cor "  ALTERNATIVA — Rufus (mais configurável):" "Cyan"
        Write-Cor "  1. Baixe em: https://rufus.ie/" "White"
        Write-Cor "  2. Modo: DD Image (não ISO)" "White"

        # Tentar abrir navegador com Etcher
        $abrirEtcher = Read-Host "  Abrir página do Balena Etcher no navegador? (s/n)"
        if ($abrirEtcher -eq 's' -or $abrirEtcher -eq 'S') {
            Start-Process "https://etcher.balena.io/"
        }
    }
} catch {
    Write-Cor "  ERRO durante a gravação: $_" "Red"
    Write-Cor ""
    Write-Cor "  Use o Balena Etcher como alternativa:" "Yellow"
    Write-Cor "  https://etcher.balena.io/" "White"
}

Write-Cor ""
Write-Cor "  Próximos passos:" "Cyan"
Write-Cor "  1. Reinicie o computador com o pendrive conectado" "White"
Write-Cor "  2. Entre no BIOS (F2/F12/DEL/Esc) e selecione boot pelo pendrive" "White"
Write-Cor "  3. Escolha 'Iniciar Katu OS' ou 'Instalar Katu OS'" "White"
Write-Cor "  4. Siga o instalador visual" "White"
Write-Cor ""
Read-Host "Pressione Enter para sair"
