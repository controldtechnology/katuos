# Implementações futuras

> Implementações comuns futuras devem ser entregues pelo Katu Update e não exigir reconstrução da ISO.

- [ ] identificar componente
- [ ] implementar
- [ ] testar
- [ ] incrementar versão
- [ ] atualizar changelog
- [ ] gerar pacote
- [ ] testar upgrade
- [ ] publicar beta
- [ ] validar
- [ ] promover stable
- [ ] validar no Katu Update

Uma ideia nova não implica ISO nova. A entrega é versão → pacote → beta → validação
→ stable → repo.katuos.com.br → Katu Update → apenas componentes necessários.

ISO é snapshot periódico para instalação inicial, Live, recuperação, grandes
mudanças de base/boot/instalador ou nova arquitetura. Mesmo nesses casos avaliar
primeiro upgrade suportado para instalações existentes. Documentar qualquer
bootstrap indispensável; nunca exigir reinstalação por conveniência de release.
