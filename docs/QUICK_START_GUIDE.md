# 🚀 Guia Rápido - BigodeTexas v2.3

## 1️⃣ Sistema RBAC (Controle de Acesso)

### Atribuir Roles a Usuários

**Via Dashboard (Administrador)**:
```
1. Acesse: http://127.0.0.1:5001/admin/users
2. Clique no usuário desejado
3. Selecione a role: ADMIN, MODERATOR, USER ou BANNED
4. Salvar alterações
```

**Via Banco de Dados Direto**:
```sql
-- Tornar usuário ADMIN
UPDATE users SET role = 'admin' WHERE discord_id = 'SEU_DISCORD_ID';

-- Tornar usuário MODERATOR
UPDATE users SET role = 'moderator' WHERE discord_id = 'SEU_DISCORD_ID';

-- Banir usuário
UPDATE users SET role = 'banned', is_banned = 1 WHERE discord_id = 'SEU_DISCORD_ID';
```

**Roles Disponíveis**:
- `admin` - Acesso total ao sistema
- `moderator` - Pode gerenciar usuários e conteúdo
- `user` - Acesso padrão (default)
- `banned` - Bloqueado do sistema

### Rotas Protegidas
```python
# Exemplo de uso no código
@app.route("/api/admin/action", methods=["POST"])
@require_role(UserRole.ADMIN)
def admin_action():
    # Apenas admins podem acessar
    pass

@app.route("/api/moderator/action", methods=["POST"])
@require_role(UserRole.ADMIN, UserRole.MODERATOR)
def moderator_action():
    # Admins e moderadores podem acessar
    pass
```

---

## 2️⃣ Sistema de Guerra entre Clãs

### Comandos Discord

**Iniciar Guerra**:
```
/war start [TAG_CLAN1] [TAG_CLAN2]
Exemplo: /war start TXS INIMIGOS
```

**Ver Placar de Guerra**:
```
/war status [TAG_CLAN1] [TAG_CLAN2]
Exemplo: /war status TXS INIMIGOS
```

**Finalizar Guerra**:
```
/war end [TAG_CLAN1] [TAG_CLAN2]
Exemplo: /war end TXS INIMIGOS
```

**Listar Guerras Ativas**:
```
/war list
```

### Via Banco de Dados

**Iniciar guerra manualmente**:
```sql
INSERT INTO clan_wars (clan1_tag, clan2_tag, clan1_kills, clan2_kills, is_active)
VALUES ('TXS', 'INIMIGOS', 0, 0, 1);
```

**Ver guerras ativas**:
```sql
SELECT * FROM clan_wars WHERE is_active = 1;
```

**Finalizar guerra**:
```sql
UPDATE clan_wars
SET is_active = 0, ended_at = CURRENT_TIMESTAMP
WHERE clan1_tag = 'TXS' AND clan2_tag = 'INIMIGOS';
```

### Como Funciona

1. **Guerra Criada**: Duas tags de clãs são registradas
2. **Kill Automático**: Quando um membro do Clan A mata um do Clan B, o placar atualiza automaticamente
3. **Notificação Discord**: Bot envia mensagem com o placar atualizado
4. **Leaderboard**: Dashboard exibe guerras ativas em tempo real

---

## 3️⃣ Sistema Anti-Cheat

### Verificar Usuários Banidos

**Via Python**:
```bash
cd "d:\dayz xbox\BigodeBot"
python tests/test_anti_cheat.py
```

**Via SQL**:
```sql
-- Listar banidos
SELECT gamertag, discord_id, ban_reason, banned_at
FROM users
WHERE is_banned = 1;

-- Banir usuário por gamertag
UPDATE users
SET is_banned = 1, ban_reason = 'Cheat detectado'
WHERE gamertag = 'CHEATER123';

-- Desbanir usuário
UPDATE users
SET is_banned = 0, ban_reason = NULL
WHERE gamertag = 'USUARIO_LIMPO';
```

### Logs de Conexão

**Ver últimas conexões**:
```sql
SELECT * FROM connection_logs
ORDER BY connected_at DESC
LIMIT 50;
```

**Detectar alts (mesmo IP)**:
```sql
SELECT ip_address, COUNT(*) as total_contas
FROM connection_logs
GROUP BY ip_address
HAVING total_contas > 1;
```

---

## 4️⃣ Health Check do Sistema

**Executar verificação completa**:
```bash
cd "d:\dayz xbox\BigodeBot"
python scripts/health_check_complete.py
```

**Agendar verificação automática (Windows)**:
```batch
# Criar tarefa agendada para rodar a cada 6 horas
schtasks /create /tn "BigodeBot Health Check" /tr "python \"d:\dayz xbox\BigodeBot\scripts\health_check_complete.py\"" /sc hourly /mo 6
```

**Interpretar Resultados**:
- `Exit Code 0`: Sistema 100% saudável ✅
- `Exit Code 1`: Sistema parcialmente funcional ⚠️
- `Exit Code 2`: Problemas críticos detectados ❌

---

## 5️⃣ Leaderboard - Estatísticas Adicionais

### Preparar Migração

**Quando estiver pronto para adicionar novas colunas**:
```bash
cd "d:\dayz xbox\BigodeBot"
python migrations/add_leaderboard_columns.py
```

**Novas estatísticas que serão adicionadas**:
- `zombie_kills` - Total de zombies mortos
- `distance_traveled` - Distância total percorrida (km)
- `vehicle_distance` - Distância em veículos (km)
- `reconnects` - Número de reconexões
- `buildings_placed` - Total de construções colocadas
- `raids_completed` - Raids completados

⚠️ **Nota**: Essas colunas requerem parsing adicional dos logs Nitrado (ainda não implementado)

---

## 🔧 Comandos Úteis

### Iniciar Dashboard
```bash
cd "d:\dayz xbox\BigodeBot\new_dashboard"
python app.py
```

### Iniciar Bot Discord
```bash
cd "d:\dayz xbox\BigodeBot"
python bot_main.py
```

### Rodar Testes
```bash
# War System
python tests/test_war_system.py

# Anti-Cheat
python tests/test_anti_cheat.py

# Health Check
python scripts/health_check_complete.py
```

### Backup do Banco de Dados
```bash
# Fazer backup
copy "bigode_unified.db" "backup_bigode_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db"

# Restaurar backup
copy "backup_bigode_YYYYMMDD.db" "bigode_unified.db"
```

---

## 📚 Documentação Adicional

- **RBAC Completo**: [docs/RBAC_GUIDE.md](RBAC_GUIDE.md)
- **Análise do Código**: [CODE_ANALYSIS.md](../CODE_ANALYSIS.md)
- **Registro de Mudanças**: [CHANGELOG.md](../CHANGELOG.md)
- **Melhorias Futuras**: [FUTURE_ENHANCEMENTS.md](../FUTURE_ENHANCEMENTS.md)

---

**Última Atualização**: 2026-02-07
**Versão do Sistema**: v2.3.0
