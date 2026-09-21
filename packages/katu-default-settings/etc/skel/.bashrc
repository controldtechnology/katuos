# ~/.bashrc — Katu OS default shell configuration

# Não executar se não for shell interativo
[[ $- != *i* ]] && return

# Histórico
HISTSIZE=5000
HISTFILESIZE=10000
HISTCONTROL=ignoreboth
shopt -s histappend

# Janela atualiza tamanho
shopt -s checkwinsize

# Prompt colorido com identidade Katu
RESET='\[\e[0m\]'
GREEN='\[\e[38;2;0;200;83m\]'
AMBER='\[\e[38;2;255;171;0m\]'
BLUE='\[\e[38;2;88;166;255m\]'
MUTED='\[\e[38;2;139;148;158m\]'

PS1="${GREEN}\u${MUTED}@${BLUE}\h${RESET} ${MUTED}in${RESET} ${AMBER}\w${RESET}\n${GREEN}❯${RESET} "

# Aliases úteis
alias ls='ls --color=auto'
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias grep='grep --color=auto'
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias ..='cd ..'
alias ...='cd ../..'
alias update='sudo apt update && sudo apt upgrade'
alias instalar='sudo apt install'
alias remover='sudo apt remove'
alias buscar='apt search'

# Mostrar info do sistema no login (apenas em terminal interativo)
if command -v fastfetch &>/dev/null; then
    fastfetch --config /etc/fastfetch/config.jsonc 2>/dev/null || true
elif command -v neofetch &>/dev/null; then
    neofetch 2>/dev/null || true
fi
