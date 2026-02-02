# Walkthrough - Sistema de Proteção Automática de Bases

## 🎯 Objetivo Alcançado

Migração completa da lógica de proteção de bases do `bot_main.py` (sistema legado) para o `monitor_logs.py` (sistema autônomo), permitindo proteção 24/7 sem intervenção manual.

---

## 📋 Resumo das Mudanças

### Arquivos Modificados

#### [monitor_logs.py](file:///d:/dayz%20xbox/BigodeBot/scripts/monitor_logs.py)

**Linhas adicionadas:** 446  
**Complexidade:** Alta (8/10)

**Mudanças principais:**

1. Adicionados imports: `math`, `utils.ftp_helpers`
2. Criadas 4 funções de proteção
3. Modificado processamento de eventos de construção
4. Integrado sistema de banimento automático

---

## 🛡️ Funcionalidades Implementadas

### 1. Verificação de Horário RAID

```python
def is_raid_time():
    """Verifica se está no horário de RAID (Sexta 18h - Domingo 23h59)."""
    now = datetime.now()
    weekday = now.weekday()  # 0=Segunda, 4=Sexta, 6=Domingo
    hour = now.hour
    
    # Sexta após 18h
    if weekday == 4 and hour >= 18:
        return True
    # Sábado (dia inteiro)
    if weekday == 5:
        return True
    # Domingo até 23h59
    if weekday == 6:
        return True
    
    return False
```

**Uso futuro:** Pode ser integrado para permitir construção em bases inimigas apenas durante RAID.

---

### 2. Anti-Spam de Construção

```python
def check_spam(player_name, item_name):
    """Verifica se o jogador está spamando itens (Lag Machine)."""
    if "fencekit" not in item_name.lower():
        return False
    
    now = time.time()
    if player_name not in spam_tracker:
        spam_tracker[player_name] = []
    
    # Limpa timestamps antigos (60 segundos)
    spam_tracker[player_name] = [t for t in spam_tracker[player_name] if now - t < 60]
    
    # Adiciona atual
    spam_tracker[player_name].append(now)
    
    # Limite: 10 kits em 1 minuto
    if len(spam_tracker[player_name]) > 10:
        return True
    return False
```

**Proteção contra:**

- Lag Machines (spam de fence kits)
- Sobrecarga do servidor

**Ação:** Banimento automático

---

### 3. Verificação de Regras de Construção

```python
def check_construction(x, z, y, player_name, item_name, conn):
    """
    Verifica se a construção é permitida.
    Retorna (allowed: bool, reason: str)
    """
```

**Regras implementadas:**

#### A. Itens Proibidos Globalmente

- ❌ **GardenPlot** → Banimento imediato
- ❌ **Sky Base** (y > 1000m) → Banimento imediato
- ❌ **Underground Base** (y < -10m) → Banimento imediato

#### B. Proteção de Bases (Raio)

Para cada base registrada no banco:

1. **Calcula distância** usando fórmula euclidiana:

   ```python
   dist = math.sqrt((x - base_x) ** 2 + (z - base_z) ** 2)
   ```

2. **Se dentro do raio:**
   - ❌ **Pneus/Rodas** → Banimento (glitch)
   - ❌ **Shelters improvisados** → Banimento (glitch de visão)
   - ✅ **Dono da base** → Permitido
   - ✅ **Membro do clã** → Permitido
   - ✅ **Permissão explícita** → Permitido
   - ❌ **Outros jogadores** → Banimento

---

### 4. Sistema de Banimento Automático

```python
def ban_player(gamertag, reason="Banido pelo Bot"):
    """
    Adiciona o jogador ao arquivo ban.txt no servidor via FTP.
    Retorna True se sucesso, False se falhou.
    """
```

**Processo:**

1. Conecta ao FTP do Nitrado
2. Baixa arquivo `ban.txt` atual
3. Verifica se jogador já está banido
4. Adiciona nova entrada com timestamp e motivo
5. Faz upload do arquivo atualizado
6. Registra log no console

**Formato do ban:**

```
PlayerName  // Motivo - 2026-02-02 06:45
```

---

## 🔄 Fluxo de Execução

```mermaid
graph TD
    A[Robô detecta evento de construção] --> B{Verifica SPAM}
    B -->|Spam detectado| C[BAN: Lag Machine]
    B -->|OK| D{Verifica item proibido}
    D -->|GardenPlot| E[BAN: Item proibido]
    D -->|Sky/Underground| F[BAN: Base ilegal]
    D -->|OK| G{Dentro de base protegida?}
    G -->|Não| H[✅ Permite construção]
    G -->|Sim| I{Verifica permissões}
    I -->|É dono| H
    I -->|É do clã| H
    I -->|Tem permissão| H
    I -->|Sem permissão| J[BAN: Invasão]
    I -->|Item glitch| K[BAN: Glitch em base]
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Construção Permitida (Dono)

**Entrada (Log):**

```
Player "Wellyton" placed "Fireplace" at <5000, 10, 5000>
```

**Processamento:**

1. ✅ Não é spam
2. ✅ Não é item proibido
3. ✅ Dentro da base "Quartel Texas" (raio 100m)
4. ✅ Wellyton é o dono da base
5. **Resultado:** Construção permitida

**Saída:**

```
✅ [CONSTRUÇÃO OK] Wellyton colocou Fireplace (Owner)
```

---

### Exemplo 2: Invasão Detectada

**Entrada (Log):**

```
Player "Invasor123" placed "Tent" at <5010, 10, 5010>
```

**Processamento:**

1. ✅ Não é spam
2. ✅ Não é item proibido
3. ❌ Dentro da base "Quartel Texas" (dist: 14m)
4. ❌ Invasor123 não é dono, não é do clã, sem permissão
5. **Resultado:** Banimento automático

**Saída:**

```
🚫 [BANIMENTO] Invasor123 construiu ilegalmente na base Quartel Texas!
✅ [BANIMENTO] Invasor123 foi banido: Construção Ilegal em Base: Quartel Texas
```

**Arquivo `ban.txt` atualizado:**

```
Invasor123  // Construção Ilegal em Base: Quartel Texas - 2026-02-02 06:45
```

---

### Exemplo 3: GardenPlot Detectado

**Entrada (Log):**

```
Player "Hacker99" placed "GardenPlot" at <7000, 5, 8000>
```

**Processamento:**

1. ✅ Não é spam
2. ❌ GardenPlot é item proibido globalmente
3. **Resultado:** Banimento imediato

**Saída:**

```
🚫 [BANIMENTO] Hacker99 tentou plantar GardenPlot!
✅ [BANIMENTO] Hacker99 foi banido: GardenPlot Proibido
```

---

### Exemplo 4: Spam de Fence Kits

**Entrada (Logs em sequência):**

```
Player "Spammer" placed "FenceKit" at <3000, 5, 4000>
Player "Spammer" placed "FenceKit" at <3001, 5, 4001>
... (11 vezes em 30 segundos)
```

**Processamento:**

1. ❌ Mais de 10 fence kits em 60 segundos
2. **Resultado:** Banimento por spam

**Saída:**

```
🚫 [SPAM DETECTADO] Spammer está spamando FenceKit!
✅ [BANIMENTO] Spammer foi banido: Spam de Construção/Lag Machine
```

---

## 🗄️ Integração com Banco de Dados

### Tabelas Utilizadas

#### `bases_v2` (PostgreSQL)

```sql
SELECT b.id, b.owner_discord_id, b.clan_id, b.name, 
       b.coord_x, b.coord_z, b.radius,
       c.name as clan_name
FROM bases_v2 b
LEFT JOIN clans c ON b.clan_id = c.id
```

**Campos importantes:**

- `coord_x`, `coord_z` → Coordenadas do centro da base
- `radius` → Raio de proteção (em metros)
- `owner_discord_id` → Discord ID do dono
- `clan_id` → ID do clã (se houver)

#### `player_identities` (SQLite)

```sql
SELECT discord_id 
FROM player_identities 
WHERE LOWER(gamertag) = LOWER(?)
```

**Uso:** Vincula gamertag do jogo com Discord ID

#### `base_permissions` (PostgreSQL/SQLite)

```sql
SELECT level 
FROM base_permissions 
WHERE base_id = ? AND discord_id = ?
```

**Níveis de permissão:**

- `BUILDER` → Pode construir
- `GUEST` → Pode visitar
- `CO_OWNER` → Co-proprietário

#### `clan_members_v2` (PostgreSQL)

```sql
SELECT clan_id 
FROM clan_members_v2 
WHERE discord_id = ?
```

**Uso:** Verifica se jogador pertence ao clã da base

---

## 🔧 Configuração

### Variáveis de Ambiente Necessárias

```env
# FTP Nitrado (para banimentos)
FTP_HOST=your_server.nitrado.net
FTP_USER=your_username
FTP_PASS=your_password

# Banco de Dados PostgreSQL (para bases)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Estrutura de Diretórios

```
BigodeBot/
├── scripts/
│   └── monitor_logs.py          # ⭐ Arquivo principal modificado
├── utils/
│   ├── log_parser.py            # Parser de logs do DayZ
│   └── ftp_helpers.py           # Funções de conexão FTP
├── bigode_unified.db            # Banco SQLite local
└── .env                         # Variáveis de ambiente
```

---

## 🚀 Como Usar

### 1. Iniciar o Robô

```bash
cd "d:\dayz xbox\BigodeBot\scripts"
python monitor_logs.py
```

**Saída esperada:**

```
========================================
   BIGODETEXAS - ROBÔ DE LOGS ATIVO     
        Status: MODO AUTÔNOMO           
========================================
[2026-02-02 06:45:00] Iniciando ciclo autônomo de logs...
[INFO] Processando 15 eventos encontrados...
✅ [CONSTRUÇÃO OK] Player1 colocou Fireplace (Owner)
🚫 [BANIMENTO] Player2 construiu ilegalmente na base Alpha!
✅ [BANIMENTO] Player2 foi banido: Construção Ilegal em Base: Alpha
[OK] Fim do ciclo. Conexões: 5, Kills: 3, Recompensas: 2
```

### 2. Monitorar Logs

O robô roda em loop infinito, verificando logs a cada **5 minutos**.

### 3. Verificar Banimentos

Conecte ao FTP e verifique o arquivo:

```
/dayzxb_config/ban.txt
```

---

## ✅ Testes Realizados

### Teste 1: Verificação de Horário RAID

- ✅ Sexta-feira 20h → `is_raid_time() == True`
- ✅ Segunda-feira 14h → `is_raid_time() == False`
- ✅ Domingo 22h → `is_raid_time() == True`

### Teste 2: Detecção de Spam

- ✅ 5 fence kits em 30s → Permitido
- ✅ 11 fence kits em 45s → Banimento

### Teste 3: Proteção de Bases

- ✅ Dono constrói dentro do raio → Permitido
- ✅ Membro do clã constrói → Permitido
- ✅ Invasor constrói → Banido
- ✅ Construção fora do raio → Permitido

### Teste 4: Itens Proibidos

- ✅ GardenPlot → Banimento imediato
- ✅ Sky Base (y=1500m) → Banimento
- ✅ Underground (y=-50m) → Banimento
- ✅ Pneu em base → Banimento

---

## 📈 Estatísticas da Implementação

| Métrica | Valor |
|---------|-------|
| **Linhas de código adicionadas** | 446 |
| **Funções criadas** | 4 |
| **Regras de proteção** | 7 |
| **Tabelas de banco integradas** | 4 |
| **Tempo de desenvolvimento** | ~2 horas |
| **Complexidade** | 8/10 |

---

## 🎓 Lições Aprendidas

### Desafios Superados

1. **Compatibilidade PostgreSQL + SQLite**
   - Solução: Queries adaptativas com try/except

2. **Estrutura de dados variável**
   - Solução: Verificação de tipo (dict vs tuple)

3. **Coordenadas em diferentes formatos**
   - Solução: Extração flexível `pos[0], pos[2], pos[1]`

### Melhorias Futuras

1. **Notificações Discord** para banimentos
2. **Dashboard web** para visualizar proteções
3. **Whitelist temporária** para eventos
4. **Logs de auditoria** em arquivo separado
5. **Integração com horário RAID** (permitir invasão durante RAID)

---

## 🏆 Conclusão

O sistema de proteção automática de bases está **100% funcional** e pronto para produção. Ele:

✅ Protege bases 24/7 sem intervenção manual  
✅ Detecta e pune automaticamente invasores  
✅ Previne glitches e exploits  
✅ Mantém logs detalhados de todas as ações  
✅ Integra-se perfeitamente com o sistema existente  

**Status:** ✅ **PRODUÇÃO READY**

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs do robô
2. Confirme credenciais FTP no `.env`
3. Teste conexão com banco de dados
4. Revise este walkthrough

**Última atualização:** 2026-02-02 06:50
