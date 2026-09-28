# Testes

Teste local: `python -m unittest discover -s scripts/tests -p test_continuous_update.py -v`.
Teste Linux: workflow Katu component packages, Debian trixie, ferramentas APT reais.
`integration_updates.py` recusa execução fora de contêiner Docker explicitamente
marcado com KATU_DISPOSABLE_TEST=1. Ele altera as fontes APT desse contêiner.

Cobertura inicial executada: nenhum update, um pacote, dependência core, novo app
por meta, ícones, assinatura inválida, payload corrompido, servidor indisponível,
gates de promoção. Testes adicionais exercitam helper real na autoatualização,
dependência ausente, alteração de plano, tema e holds. Testes locais cobrem espaço,
estado instalado, dpkg incompleto, falha Flatpak e migração idempotente.

Qt offscreen verifica estados de lista, falha e atualizado, além de screenshot.
Não equivale a teste do Plasma/Polkit real. Autoatualização no contêiner exercita
helper em execução e substituição de seus arquivos, mas systemd PID 1 e encerramento
da GUI devem ser testados na instalação real.

## Homologação em Katu instalado (obrigatória antes de stable)

- Guardar baseline de dpkg-query, fontes APT, configurações e checksums do /home.
- Provisionar chave pública verificada/canal beta, instalar bootstrap/updater.
- Publicar apenas katu-ai 1.1.0 sobre 1.0.0; central deve continuar em 1.0.0.
- Publicar apenas ícones; confirmar download e versão somente desse pacote.
- Oferecer katu-example por Recommends; não restaurar app removido sem autorização.
- Atualizar updater com janela aberta e validar serviço/histórico após substituição.
- Validar notificação KDE/VER, Polkit, timer, progresso, cancelamento no download.
- Simular rede interrompida, pacote incompleto, assinatura errada, pouco espaço,
  bateria baixa, dependências quebradas e interrupção em VM com snapshot.
- Confirmar reboot requerido, MAIS TARDE e reinício autorizado.
- Reiniciar e validar boot/GRUB/Plymouth/login/Plasma/rede/áudio/hardware.
- Conferir configurações pessoais e arquivos intactos; testar remoção aplicável.

Não marcar esses itens como concluídos com base somente em mocks ou contêiner.
