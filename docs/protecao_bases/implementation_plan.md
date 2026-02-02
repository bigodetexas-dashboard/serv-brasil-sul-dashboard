# Migração da Proteção de Bases - BigodeTexas

## Objetivo

Migrar a inteligência de proteção de bases do `bot_main.py` (sistema legado) para o `monitor_logs.py` (novo sistema autônomo), permitindo que o robô detecte e puna automaticamente construções ilegais em áreas protegidas.

## Contexto

O sistema antigo (`bot_main.py`) já possuía uma lógica robusta de proteção que:

- ✅ Calculava distância entre construções e bases registradas
- ✅ Verificava permissões (dono, clã, amigos)
- ✅ Aplicava banimento automático com mensagens específicas
- ✅ Bloqueava itens específicos (GardenPlot, Pneus, Shelters)
- ✅ Detectava Sky Bases e Underground Bases

O novo sistema (`monitor_logs.py`) atualmente apenas:

- ✅ Lê logs do Nitrado
- ✅ Registra eventos de construção no banco
- ❌ **NÃO aplica nenhuma punição**

## Funcionalidades a Migrar

### 1. Verificação de Horário RAID

**Localização Original:** `bot_main.py` (não encontrada explicitamente, mas mencionada pelo usuário)

**Implementação:**

```python
def is_raid_time():
    """Verifica se está no horário de RAID (Sexta 18h - Domingo 23h59)"""
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

### 2. Cálculo de Distância e Proteção de Bases

**Localização Original:** [`bot_main.py:553-620`](file:///d:/dayz%20xbox/BigodeBot/bot_main.py#L553-L620)

**Lógica Atual:**

```python
def check_construction(x, z, y, player_name, item_name):
    """Verifica se a construção é permitida."""
    
    # 1. Banimento de GardenPlot
    if "gardenplot" in item_name.lower():
        return False, "GardenPlot"
    
    # 2. Sky Base (y > 1000m)
    if y > 1000:
        return False, "SkyBase"
    
    # 3. Underground Base (y < -10m)
    if y < -10:
        return False, "UndergroundBase"
    
    # 4. Proteção de Base (Raio)
    active_bases = database.get_active_bases()
    for base in active_bases:
        dist = math.sqrt((x - base["x"]) ** 2 + (z - base["z"]) ** 2)
        if dist <= base["radius"]:
            # A. Itens Banidos em Base
            if "wheel" in item_name.lower() or "tire" in item_name.lower():
                return False, f"BannedItemBase:{item_name}"
            if "improvisedshelter" in item_name.lower():
                return False, f"BannedItemBase:{item_name}"
            
            # B. Verificação de Permissão
            builder_id = get_discord_id_by_gamertag(player_name)
            if not builder_id:
                return False, f"UnauthorizedBase:{base.get('name', 'Base')}"
            
            # É o dono?
            if str(base["owner_id"]) == str(builder_id):
                return True, "Owner"
            
            # Tem permissão explícita?
            if database.check_base_permission(base["id"], builder_id):
                return True, "PermittedUser"
            
            # É do mesmo clã?
            builder_clan_tag, builder_clan_data = database.get_user_clan(builder_id)
            if base.get("clan_id") and builder_clan_data:
                if builder_clan_data.get("id") == base["clan_id"]:
                    return True, "ClanBaseMember"
            
            # Fallback: Compara TAGs (legado)
            owner_clan_tag, _ = database.get_user_clan(base["owner_id"])
            if owner_clan_tag and builder_clan_tag == owner_clan_tag:
                return True, "ClanMemberLegacy"
            
            return False, f"UnauthorizedBase:{base.get('name', 'Base')}"
    
    return True, "OK"
```

### 3. Sistema de Banimento

**Localização Original:** [`bot_main.py:1162-1203`](file:///d:/dayz%20xbox/BigodeBot/bot_main.py#L1162-L1203)

**Integração Necessária:**

- Conectar ao FTP do Nitrado
- Adicionar gamertag ao arquivo `ban.txt`
- Registrar no banco de dados local
- Enviar notificação ao Discord (opcional, mas recomendado)

### 4. Anti-Spam de Construção

**Localização Original:** [`bot_main.py:532-550`](file:///d:/dayz%20xbox/BigodeBot/bot_main.py#L532-L550)

**Lógica:**

```python
spam_tracker = {}  # {player_name: [timestamps]}

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

---

## Mudanças Propostas

### [MODIFY] [monitor_logs.py](file:///d:/dayz%20xbox/BigodeBot/scripts/monitor_logs.py)

**Alterações:**

1. **Adicionar Imports:**

   ```python
   import math
   from utils.ftp_helpers import connect_ftp
   ```

2. **Adicionar Funções de Verificação:**
   - `is_raid_time()` - Verifica horário de RAID
   - `check_construction(x, z, y, player_name, item_name)` - Verifica regras de construção
   - `check_spam(player_name, item_name)` - Detecta spam de construção
   - `ban_player(gamertag, reason)` - Executa banimento via FTP

3. **Modificar Processamento de Eventos de Construção:**
   - No bloco `elif e_type in ["build_action", "placement"]:` (linha ~140)
   - **ANTES:** Apenas registrava no banco
   - **DEPOIS:**
     1. Extrair coordenadas (x, y, z)
     2. Chamar `check_spam()` → Se positivo, banir
     3. Chamar `check_construction()` → Se negativo, banir com motivo específico
     4. Registrar no banco (mantido)

4. **Adicionar Tabela de Rastreamento:**

   ```python
   spam_tracker = {}  # {player_name: [timestamps]}
   ```

---

## Verificação

### Testes Automatizados

1. **Teste de Horário RAID:**

   ```python
   # Simular diferentes dias/horários
   assert is_raid_time() == True  # Sexta 20h
   assert is_raid_time() == False # Segunda 14h
   ```

2. **Teste de Distância:**

   ```python
   # Base em (5000, 5000) com raio 100m
   # Construção em (5050, 5050) → dist ~70m → DENTRO
   # Construção em (5200, 5200) → dist ~282m → FORA
   ```

3. **Teste de Permissões:**
   - Dono constrói → ✅ Permitido
   - Membro do clã constrói → ✅ Permitido
   - Jogador sem vínculo constrói → ❌ Banido
   - Jogador de outro clã constrói → ❌ Banido

### Verificação Manual

1. **Simular Construção Ilegal:**
   - Criar base de teste no banco
   - Inserir evento de construção nos logs
   - Verificar se o robô detecta e bane

2. **Verificar Arquivo `ban.txt`:**
   - Conectar ao FTP após teste
   - Confirmar que o gamertag foi adicionado

3. **Verificar Logs do Robô:**
   - Mensagens de "BANINDO {player} por {motivo}"
   - Erros de conexão FTP (se houver)

---

## Riscos e Considerações

> [!WARNING]
> **Banimento Automático é Irreversível**
>
> Uma vez que o jogador é adicionado ao `ban.txt`, ele não consegue mais entrar no servidor até remoção manual. Certifique-se de que a lógica está 100% correta antes de ativar em produção.

> [!IMPORTANT]
> **Dependências Externas**
>
> - **FTP:** Requer credenciais válidas (`FTP_HOST`, `FTP_USER`, `FTP_PASS`)
> - **Banco de Dados:** Tabelas `active_bases`, `player_identities`, `users`, `clans` devem existir
> - **Discord (Opcional):** Para notificações de banimento

> [!CAUTION]
> **Falsos Positivos**
>
> - **Jogadores sem Discord vinculado:** Serão tratados como "inimigos" em áreas protegidas
> - **Bases sem clã:** Apenas o dono poderá construir (sem sistema de amigos implementado)
> - **Lag do servidor:** Coordenadas podem vir incorretas, causando banimentos injustos

---

## Próximos Passos

1. ✅ **Revisar este plano** com o usuário
2. ⏳ **Implementar funções** no `monitor_logs.py`
3. ⏳ **Testar em ambiente de desenvolvimento** (logs simulados)
4. ⏳ **Ativar em produção** com monitoramento intensivo
5. ⏳ **Criar walkthrough** documentando o sistema funcionando
