# 🔨 Sistema de Banimento Automático - BigodeTexas

## Visão Geral

Sistema de **banimento IMEDIATO** que detecta infrações e aplica punições automáticas via XUID (Xbox ID), com notificações Discord e Muro da Vergonha público.

---

## 🚨 Tipos de Infrações Detectadas

### ⚫ CRÍTICAS (Ban Permanente Imediato)

| # | Infração | Descrição | Detecção |
|---|----------|-----------|----------|
| 1 | **Lag Machine** | Spam de construção (>10 itens/min) | Automática |
| 2 | **Fly Hack** | Construção em altura ilegal | Automática |
| 3 | **Sky Base** | Base acima de 1000m | Automática |
| 4 | **Underground Base** | Base abaixo de -10m | Automática |
| 5 | **Banned Item** | Uso de itens proibidos (Pneus, Shelter) | Automática |
| 6 | **Item Duplication** | Duplicação de itens (relog rápido) | Automática |
| 7 | **Speed Hack** | Velocidade anormal de movimento | Automática |
| 8 | **Aimbot** | Taxa de headshot anormal | Automática |
| 9 | **Wallhack** | Kills através de paredes | Automática |

### 🔴 GRAVES (Ban Imediato - Revisável)

| # | Infração | Descrição | Detecção |
|---|----------|-----------|----------|
| 10 | **Alt Account** | Múltiplas contas no mesmo IP | Automática |
| 11 | **Garden Exploit** | Construção em jardim | Automática |
| 12 | **Raid Exploit** | Raid fora do horário permitido | Automática |
| 13 | **Glitch Abuse** | Abuso de bugs do jogo | Manual/Automática |

---

## 🔧 Como Funciona

### 1️⃣ Detecção Automática

O sistema monitora logs do servidor em tempo real:

```
[LOG PARSER] Detectando evento...
    ↓
[ANTI-CHEAT] Analisando comportamento...
    ↓
[INFRAÇÃO DETECTADA!]
    ↓
[AUTO-BAN] Iniciando banimento imediato...
```

### 2️⃣ Banimento Imediato (4 Etapas)

```python
1. Registra infração no banco de dados
   └─ Tabela: infractions
   └─ Dados: gamertag, xuid, tipo, evidências

2. Marca como banido localmente
   └─ Tabela: users
   └─ Campos: is_banned=1, role='banned'

3. Adiciona ao ban.txt do Nitrado via XUID
   └─ FTP: /dayzxb/config/ban.txt
   └─ Formato: XUID // Gamertag - Motivo - Data [AUTO-BAN]

4. Notificação Discord + Muro da Vergonha
   └─ Webhook automático
   └─ Página pública: /hall-of-shame
```

### 3️⃣ Notificação Discord

**Embed Automático**:
```
🔨 BANIMENTO AUTOMÁTICO

👤 Jogador: NomeDoJogador
🆔 XUID: 1234567890123456
⚠️ Severidade: CRÍTICA

🚨 Infração: lag_machine
📋 Motivo: Spam de construção: 15 itens/min

🔍 Evidência:
[2026-02-07 19:45:23] Placed FenceKit at (1234, 5678)
[2026-02-07 19:45:24] Placed FenceKit at (1235, 5679)
...

ID da Infração: 42 | Sistema Anti-Cheat BigodeTexas
```

### 4️⃣ Muro da Vergonha

**Página Pública**: http://127.0.0.1:5001/hall-of-shame

**Exibe**:
- Nome do jogador
- XUID (Xbox ID)
- Tipo de infração
- Severidade (Crítica/Grave)
- Motivo detalhado
- Data do banimento
- Evidências (se disponível)

**Atualização**: Automática a cada 30 segundos

---

## 🎯 Uso do Sistema

### Banimento Manual (CLI)

```bash
python -c "
from auto_ban_system import ban_player_immediate

ban_player_immediate(
    gamertag='Cheater123',
    xuid='1234567890123456',
    reason='Uso de aimbot confirmado',
    infraction_type='aimbot',
    evidence='Headshot rate: 95% (suspeito acima de 60%)'
)
"
```

### Banimento via Bot Discord (Futuro)

```
/ban @Usuario motivo:"Fly hack detectado"
```

### Ver Muro da Vergonha

**Web**: http://127.0.0.1:5001/hall-of-shame

**API**:
```bash
curl http://127.0.0.1:5001/api/bans
```

---

## 📊 Banco de Dados

### Tabela: `infractions`

```sql
CREATE TABLE infractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gamertag TEXT NOT NULL,
    discord_id TEXT,
    xuid TEXT,                      -- Xbox User ID
    ip_address TEXT,
    infraction_type TEXT NOT NULL,  -- Tipo da infração
    severity TEXT NOT NULL,         -- CRÍTICA ou GRAVE
    description TEXT,               -- Descrição detalhada
    evidence TEXT,                  -- Evidências (logs)
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auto_banned BOOLEAN DEFAULT 1,  -- Ban automático?
    ban_lifted BOOLEAN DEFAULT 0,   -- Ban removido?
    admin_notes TEXT                -- Notas do admin
);
```

### Consultas Úteis

**Ver todos os banimentos**:
```sql
SELECT * FROM infractions
WHERE auto_banned = 1 AND ban_lifted = 0
ORDER BY detected_at DESC;
```

**Estatísticas por tipo**:
```sql
SELECT infraction_type, COUNT(*) as total
FROM infractions
GROUP BY infraction_type
ORDER BY total DESC;
```

**Banimentos de hoje**:
```sql
SELECT * FROM infractions
WHERE DATE(detected_at) = DATE('now')
AND auto_banned = 1;
```

---

## ⚙️ Configuração

### 1. Webhook Discord

Edite `.env`:

```env
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI
```

**Como criar webhook**:
1. Discord → Configurações do Canal
2. Integrações → Webhooks
3. Novo Webhook
4. Copiar URL do Webhook

### 2. FTP Nitrado

Já configurado em `.env`:

```env
FTP_HOST=brsp012.gamedata.io
FTP_PORT=21
FTP_USER=ni3622181_1
FTP_PASS=hqPuAFd9
```

### 3. Ativar Sistema

**Automático**: Sistema já está ativo ao iniciar o dashboard

**Manual**:
```bash
python auto_ban_system.py
```

---

## 🛡️ Proteções e Segurança

### Prevenção de Falsos Positivos

1. **Evidências Obrigatórias**: Todo ban registra evidências
2. **Logs Detalhados**: Tudo é registrado com timestamp
3. **Revisão Possível**: Admins podem revisar via dashboard
4. **Banimento por XUID**: Mais preciso que por gamertag

### Sistema de Appeals (Futuro)

- Jogadores poderão abrir ticket
- Admins revisam evidências
- Ban pode ser removido se for falso positivo

### Whitelist de Proteção (Futuro)

Admins e moderadores não podem ser banidos automaticamente:

```python
PROTECTED_XUIDS = [
    "admin_xuid_1",
    "admin_xuid_2"
]
```

---

## 📈 Estatísticas

### Dashboard Admin (Futuro)

- Total de banimentos por dia/semana/mês
- Infrações mais comuns
- Horários de pico de infrações
- Taxa de detecção de cheats

### Relatórios Exportáveis

```bash
# Exportar banimentos para CSV
python -c "
from auto_ban_system import get_hall_of_shame
import csv

bans = get_hall_of_shame(limit=1000)
with open('bans_export.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=bans[0].keys())
    writer.writeheader()
    writer.writerows(bans)
"
```

---

## 🔍 Troubleshooting

### Ban não aplicado no Nitrado

**Problema**: Jogador banido localmente mas continua no servidor

**Solução**:
1. Verificar credenciais FTP no `.env`
2. Verificar caminho do `ban.txt`: `/dayzxb/config/ban.txt`
3. Reiniciar servidor Nitrado para aplicar bans

### Notificação Discord não enviada

**Problema**: Ban aplicado mas sem notificação

**Solução**:
1. Verificar `NOTIFICATION_WEBHOOK_URL` no `.env`
2. Testar webhook manualmente
3. Verificar logs: `[AUTO-BAN] ✓/✗ Notificação enviada ao Discord`

### Muro da Vergonha vazio

**Problema**: Página carrega mas não mostra banimentos

**Solução**:
1. Verificar se tabela `infractions` existe:
   ```bash
   python -c "from auto_ban_system import ensure_infractions_table; ensure_infractions_table()"
   ```
2. Verificar se há registros:
   ```bash
   python -c "from auto_ban_system import get_hall_of_shame; print(get_hall_of_shame())"
   ```

---

## 🚀 Próximas Melhorias

- [ ] Comandos Discord para banir/desbanir
- [ ] Sistema de appeals via website
- [ ] Whitelist de proteção para admins
- [ ] Dashboard de estatísticas avançado
- [ ] Exportação automática de relatórios
- [ ] Detecção de ESP/Radar hack
- [ ] Machine Learning para detecção de padrões suspeitos

---

## 📚 Exemplos de Uso

### Exemplo 1: Ban Manual com Evidências

```python
from auto_ban_system import ban_player_immediate

ban_player_immediate(
    gamertag="HackerXYZ",
    xuid="2535465465465465",
    reason="Fly hack detectado - Construção a 1500m de altura",
    infraction_type="fly_hack",
    evidence="[2026-02-07 20:15:32] Placed WatchTower at height: 1523m"
)
```

### Exemplo 2: Verificar se Jogador está Banido

```python
import database

conn = database.get_connection()
cur = conn.cursor()

cur.execute("""
    SELECT is_banned, ban_reason, banned_at
    FROM users
    WHERE gamertag = ?
""", ("NomeDoJogador",))

result = cur.fetchone()
if result and result[0] == 1:
    print(f"Banido: {result[1]} em {result[2]}")
else:
    print("Não banido")

conn.close()
```

### Exemplo 3: Listar Top 10 Infrações

```python
from auto_ban_system import get_hall_of_shame

bans = get_hall_of_shame(limit=10)

for i, ban in enumerate(bans, 1):
    print(f"{i}. {ban['gamertag']} - {ban['infraction_type']} ({ban['severity']})")
```

---

**Documentação Atualizada**: 2026-02-07
**Versão do Sistema**: v2.4.0
**Autor**: BigodeTexas Team + Claude Sonnet 4.5
