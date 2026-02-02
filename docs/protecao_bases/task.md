# Tarefas - Migração de Proteção de Bases

## Planejamento

- [x] Localizar lógica de proteção no `bot_main.py`
- [x] Analisar função `check_construction`
- [x] Analisar função `check_spam`
- [x] Analisar função `ban_player`
- [x] Criar plano de implementação

## Implementação

### Funções Auxiliares

- [x] Implementar `is_raid_time()` no `monitor_logs.py`
- [x] Implementar `check_spam()` no `monitor_logs.py`
- [x] Implementar `check_construction()` no `monitor_logs.py`
- [x] Implementar `ban_player()` no `monitor_logs.py`

### Integração com Banco de Dados

- [ ] Verificar se `database.get_active_bases()` existe
- [ ] Verificar se `database.get_user_clan()` existe
- [ ] Verificar se `database.check_base_permission()` existe
- [ ] Criar funções faltantes se necessário

### Modificação do Loop Principal

- [x] Adicionar imports necessários (`math`, `ftp_helpers`)
- [x] Adicionar variável global `spam_tracker`
- [x] Modificar processamento de eventos `build_action`
- [x] Modificar processamento de eventos `placement`
- [x] Adicionar chamadas para `check_spam()`
- [x] Adicionar chamadas para `check_construction()`
- [x] Implementar lógica de banimento baseada nos resultados

## Verificação

### Testes Unitários

- [ ] Testar `is_raid_time()` com diferentes datas
- [ ] Testar `check_spam()` com múltiplas construções
- [ ] Testar `check_construction()` com diferentes cenários:
  - [ ] GardenPlot → Banir
  - [ ] Sky Base (y > 1000) → Banir
  - [ ] Underground (y < -10) → Banir
  - [ ] Construção dentro do raio por dono → Permitir
  - [ ] Construção dentro do raio por membro do clã → Permitir
  - [ ] Construção dentro do raio por estranho → Banir
  - [ ] Construção fora do raio → Permitir

### Testes de Integração

- [ ] Simular evento de construção ilegal nos logs
- [ ] Verificar se o robô detecta corretamente
- [ ] Verificar se o banimento é executado
- [ ] Verificar se o arquivo `ban.txt` é atualizado no FTP
- [ ] Verificar logs de console do robô

### Testes em Produção (Monitorado)

- [ ] Ativar robô com logs detalhados
- [ ] Monitorar primeiras 24h para falsos positivos
- [ ] Ajustar parâmetros se necessário

## Documentação

- [ ] Criar walkthrough mostrando o sistema funcionando
- [ ] Documentar casos de uso comuns
- [ ] Documentar como desbanir jogadores (processo manual)
