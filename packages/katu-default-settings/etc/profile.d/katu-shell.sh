# Katu OS shell customizations (applies to all users)

# History settings
HISTSIZE=5000
HISTFILESIZE=10000
HISTCONTROL=ignoreboth

# Colorized prompt with Katu identity
if [ "$PS1" ]; then
    RESET='\[\e[0m\]'
    GREEN='\[\e[38;2;0;200;83m\]'
    AMBER='\[\e[38;2;255;171;0m\]'
    BLUE='\[\e[38;2;88;166;255m\]'
    MUTED='\[\e[38;2;139;148;158m\]'
    PS1="${GREEN}\u${MUTED}@${BLUE}\h${RESET} ${MUTED}in${RESET} ${AMBER}\w${RESET}\n${GREEN}> ${RESET}"
fi

# Useful aliases
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

# Show system info on login (interactive terminal only)
if [ -n "$PS1" ] && [ -z "$SHLVL" ] || [ "$SHLVL" = "1" ]; then
    if command -v fastfetch >/dev/null 2>&1; then
        fastfetch --config /etc/fastfetch/config.jsonc 2>/dev/null || true
    fi
fi
