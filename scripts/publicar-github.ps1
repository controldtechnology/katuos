# publicar-github.ps1
# Publica o repositório Katu OS no GitHub e dispara o build da ISO automaticamente
# Uso: powershell -ExecutionPolicy Bypass -File scripts\publicar-github.ps1

param(
    [string]$GithubUser = "",
    [string]$RepoName = "katuos"
)

$env:PATH += ";C:\Program Files\Git\bin;C:\Program Files\GitHub CLI\bin"

function Write-Cor {
    param([string]$Texto, [string]$Cor = "White")
    Write-Host $Texto -ForegroundColor $Cor
}

Write-Cor ""
Write-Cor "  Katu OS — Publicar no GitHub e iniciar build da ISO" "Green"
Write-Cor "  ════════════════════════════════════════════════════" "DarkGray"
Write-Cor ""

# Verificar git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Cor "  ERRO: Git não encontrado. Instale em: https://git-scm.com/" "Red"
    exit 1
}

# Verificar gh CLI
$ghDisponivel = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghDisponivel) {
    Write-Cor "  GitHub CLI (gh) não encontrado." "Yellow"
    Write-Cor "  Instale com: winget install GitHub.cli" "Cyan"
    Write-Cor "  Depois rode: gh auth login" "Cyan"
    Write-Cor ""
    Write-Cor "  OU crie o repositório manualmente:" "White"
    Write-Cor "  1. Acesse https://github.com/new" "White"
    Write-Cor "  2. Nome: $RepoName" "White"
    Write-Cor "  3. Visibilidade: Public" "White"
    Write-Cor "  4. Não inicializar com README" "White"
    Write-Cor "  5. Copie a URL do repositório e execute:" "White"
    Write-Cor ""
    Write-Cor "     cd C:\katuos" "Cyan"
    Write-Cor "     git remote add origin https://github.com/SEU_USUARIO/$RepoName.git" "Cyan"
    Write-Cor "     git push -u origin master" "Cyan"
    Write-Cor ""
    Write-Cor "  O build da ISO inicia automaticamente após o push!" "Green"
    Read-Host "Pressione Enter para sair"
    exit 0
}

# Verificar autenticação GitHub
Write-Cor "  Verificando autenticação GitHub..." "Cyan"
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Cor "  Não autenticado. Iniciando login..." "Yellow"
    gh auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Cor "  Falha no login. Tente: gh auth login" "Red"
        exit 1
    }
}

# Obter usuário atual
if (-not $GithubUser) {
    $GithubUser = gh api user --jq '.login' 2>$null
    if (-not $GithubUser) {
        $GithubUser = Read-Host "  Seu usuário do GitHub"
    }
}

Write-Cor "  Usuário: $GithubUser" "White"
Write-Cor "  Repositório: $RepoName" "White"
Write-Cor ""

Set-Location C:\katuos

# Criar repositório no GitHub
$existente = gh repo view "$GithubUser/$RepoName" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Cor "  Repositório já existe: github.com/$GithubUser/$RepoName" "Yellow"
} else {
    Write-Cor "  Criando repositório no GitHub..." "Cyan"
    gh repo create "$GithubUser/$RepoName" `
        --public `
        --description "Katu OS 1.0 — Distribuição Linux brasileira (Debian Trixie + KDE Plasma)" `
        --homepage "https://katuos.com.br"

    if ($LASTEXITCODE -ne 0) {
        Write-Cor "  Falha ao criar repositório." "Red"
        exit 1
    }
    Write-Cor "  ✓ Repositório criado!" "Green"
}

# Configurar remote
$remoteUrl = "https://github.com/$GithubUser/$RepoName.git"
$existeRemote = git remote get-url origin 2>$null
if ($existeRemote) {
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}

Write-Cor "  Remote configurado: $remoteUrl" "White"

# Push
Write-Cor ""
Write-Cor "  Enviando código para o GitHub..." "Cyan"
Write-Cor "  (Pode demorar alguns minutos — tem imagens e assets)" "DarkGray"

git push -u origin master --force

if ($LASTEXITCODE -ne 0) {
    Write-Cor "  Falha no push. Verifique suas credenciais." "Red"
    exit 1
}

Write-Cor ""
Write-Cor "  ✓ CÓDIGO ENVIADO COM SUCESSO!" "Green"
Write-Cor ""
Write-Cor "  O build da ISO INICIOU AUTOMATICAMENTE no GitHub!" "Green"
Write-Cor ""
Write-Cor "  Acompanhe o progresso em:" "Cyan"
Write-Cor "  https://github.com/$GithubUser/$RepoName/actions" "White"
Write-Cor ""
Write-Cor "  Quando concluído (45-90 min), baixe a ISO em:" "Cyan"
Write-Cor "  https://github.com/$GithubUser/$RepoName/actions" "White"
Write-Cor "  → Clique no build mais recente → Artifacts → katu-os-1.0-amd64-iso" "White"
Write-Cor ""

# Abrir Actions no navegador
$abrirBrowser = Read-Host "  Abrir GitHub Actions no navegador agora? (s/n)"
if ($abrirBrowser -eq 's' -or $abrirBrowser -eq 'S') {
    Start-Process "https://github.com/$GithubUser/$RepoName/actions"
}

Write-Cor ""
Write-Cor "  Depois de baixar a ISO, grave no pendrive com:" "White"
Write-Cor "  powershell -ExecutionPolicy Bypass -File scripts\gravar-pendrive.ps1" "Cyan"
Write-Cor ""
