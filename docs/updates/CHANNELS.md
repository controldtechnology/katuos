# Canais

Stable é padrão; beta exige escolha administrativa explícita no bootstrap.
Uma única suite fica ativa em katu.sources. Pin negativo bloqueia a suite oposta.
O backend também rejeita candidatos Katu beta quando a configuração indica stable.

Trocar para beta: executar configure-client.py com --channel beta e a mesma chave
pública verificada. Refresh e revisar o plano antes de instalar. Voltar a stable
não faz downgrade automático: versões beta instaladas podem permanecer até stable
alcançá-las. Downgrade exige revisão de compatibilidade de dados e plano separado.

Não há canal dev configurado. Metadados e pool são publicados juntos, e o cliente
nunca usa a versão da ISO como critério de atualização.
