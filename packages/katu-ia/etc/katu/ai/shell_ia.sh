#!/bin/bash
# Katu IA — Shell Environment
# Funções e aliases de IA para o terminal

# Carregar config
KATU_AI_CONF="${HOME}/.config/katu/ai/config.json"

_katu_ai_provider() {
    python3 -c "
import json, os
cfg = {}
f = os.path.expanduser('~/.config/katu/ai/config.json')
if os.path.exists(f):
    cfg = json.load(open(f))
print(cfg.get('provider','claude'))
" 2>/dev/null || echo "claude"
}

_katu_ia_query() {
    local prompt="$1"
    local provider
    provider="$(_katu_ai_provider)"

    python3 -c "
import sys, os, json
sys.path.insert(0, '/usr/lib/katu-ia')

cfg_file = os.path.expanduser('~/.config/katu/ai/config.json')
cfg = {}
if os.path.exists(cfg_file):
    cfg = json.load(open(cfg_file))

provider = cfg.get('provider', 'claude')
prompt = sys.argv[1]

try:
    if provider == 'claude':
        import anthropic
        key = cfg.get('claude_key') or os.environ.get('ANTHROPIC_API_KEY','')
        c = anthropic.Anthropic(api_key=key)
        with c.messages.stream(
            model=cfg.get('modelo',{}).get('claude','claude-sonnet-4-6'),
            max_tokens=2048,
            system='Você é um assistente de terminal Linux. Responda em português do Brasil. Seja conciso e direto.',
            messages=[{'role':'user','content':prompt}]
        ) as s:
            for t in s.text_stream:
                print(t, end='', flush=True)
        print()
    elif provider == 'openai':
        from openai import OpenAI
        key = cfg.get('openai_key') or os.environ.get('OPENAI_API_KEY','')
        c = OpenAI(api_key=key)
        s = c.chat.completions.create(
            model=cfg.get('modelo',{}).get('openai','gpt-4o'),
            messages=[{'role':'system','content':'Responda em português do Brasil. Seja conciso.'},
                      {'role':'user','content':prompt}],
            stream=True, max_tokens=2048
        )
        for chunk in s:
            d = chunk.choices[0].delta.content
            if d: print(d, end='', flush=True)
        print()
    elif provider == 'ollama':
        import urllib.request, json as js
        url = cfg.get('ollama_url','http://localhost:11434') + '/api/generate'
        data = js.dumps({'model': cfg.get('modelo',{}).get('ollama','llama3'),
                         'prompt': prompt, 'stream': True}).encode()
        req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req, timeout=120) as r:
            for line in r:
                obj = js.loads(line.decode())
                if obj.get('response'):
                    print(obj['response'], end='', flush=True)
        print()
except Exception as e:
    print(f'Erro: {e}', file=sys.stderr)
    sys.exit(1)
" "$prompt"
}

# ── Aliases principais ────────────────────────────────────────────────────────

# ai 'pergunta' — pergunta geral
ai() {
    if [ -z "$1" ]; then
        echo "Uso: ai 'sua pergunta'"
        return 1
    fi
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA\033[0m\n"
    _katu_ia_query "$*"
    echo ""
}

# ai-fix — analisa o último erro
ai-fix() {
    local ultimo_cmd
    ultimo_cmd=$(fc -ln -1 2>/dev/null || history 1 | awk '{$1=""; print}')
    local prompt="O comando '$ultimo_cmd' produziu um erro. Explique o que significa e mostre como corrigir. Responda em português."
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA — Analisando erro\033[0m\n"
    _katu_ia_query "$prompt"
    echo ""
}

# ai-explain <comando> — explica um comando
ai-explain() {
    local prompt="Explique em português o que faz este comando Linux: $*\nMostre exemplos práticos."
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA — Explicando: $*\033[0m\n"
    _katu_ia_query "$prompt"
    echo ""
}

# ai-code 'descrição' — gera código
ai-code() {
    local prompt="Escreva código para: $*\nUse boas práticas, adicione comentários em português e trate erros."
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA — Gerando código\033[0m\n"
    _katu_ia_query "$prompt"
    echo ""
}

# ai-review <arquivo> — revisa código
ai-review() {
    if [ -z "$1" ] || [ ! -f "$1" ]; then
        echo "Uso: ai-review <arquivo>"
        return 1
    fi
    local conteudo
    conteudo=$(cat "$1")
    local prompt="Revise o seguinte código em português. Aponte problemas, sugira melhorias e identifique bugs:\n\`\`\`\n${conteudo}\n\`\`\`"
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA — Revisando: $1\033[0m\n"
    _katu_ia_query "$prompt"
    echo ""
}

# ai-commit — gera mensagem de commit
ai-commit() {
    local diff
    diff=$(git diff --cached 2>/dev/null || git diff HEAD 2>/dev/null || echo "sem mudanças staged")
    local prompt="Baseado neste diff do git, gere uma mensagem de commit concisa e descritiva em inglês (convenção conventional commits):\n\n${diff}\n\nFormato: tipo(escopo): descrição"
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA — Gerando mensagem de commit\033[0m\n"
    _katu_ia_query "$prompt"
    echo ""
}

# ai-sql 'descrição'
ai-sql() {
    local prompt="Escreva uma query SQL para: $*\nExplique cada parte da query em português e otimize se necessário."
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA — Gerando SQL\033[0m\n"
    _katu_ia_query "$prompt"
    echo ""
}

# ai-doc <arquivo>
ai-doc() {
    if [ -z "$1" ] || [ ! -f "$1" ]; then
        echo "Uso: ai-doc <arquivo>"
        return 1
    fi
    local conteudo
    conteudo=$(cat "$1")
    local prompt="Adicione documentação completa em português ao código abaixo (docstrings, comentários, parâmetros, retornos):\n\`\`\`\n${conteudo}\n\`\`\`"
    echo ""
    printf "\033[38;2;0;200;83m▶ Katu IA — Documentando: $1\033[0m\n"
    _katu_ia_query "$prompt"
    echo ""
}

# Prompt especial para bash
PS1_AI='\[\e[38;2;0;200;83m\][\[\e[38;2;255;171;0m\]IA:\[\e[38;2;0;200;83m\]$(_katu_ai_provider)]\[\e[0m\] '"$PS1"

echo ""
printf "\033[38;2;0;200;83m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n"
printf "\033[38;2;0;200;83m  Katu IA — Shell Ambiente Ativo\033[0m\n"
printf "\033[38;2;139;148;158m  Provider: \033[0m\033[38;2;0;200;83m$(_katu_ai_provider)\033[0m\n"
printf "\033[38;2;139;148;158m  Comandos: ai, ai-fix, ai-explain, ai-code,\033[0m\n"
printf "\033[38;2;139;148;158m            ai-review, ai-commit, ai-sql, ai-doc\033[0m\n"
printf "\033[38;2;0;200;83m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n"
echo ""
