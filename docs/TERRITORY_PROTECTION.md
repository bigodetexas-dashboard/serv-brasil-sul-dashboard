# 🏰 Sistema de Proteção de Território - BigodeTexas

## Visão Geral

Sistema que protege bases registradas contra invasões. Qualquer tentativa de construir em território alheio resulta em **BANIMENTO IMEDIATO via XUID**.

---

## 🔐 Como Funciona

### 1️⃣ Registro de Base

Quando um jogador registra uma base:
- Define um **ponto central** (coordenadas X, Z)
- Define um **raio de proteção** (ex: 100m)
- Área fica **exclusiva** para o dono

### 2️⃣ Permissões Automáticas

**QUEM PODE CONSTRUIR:**

✅ **Dono da Base**
- Jogador que registrou a base
- Acesso total e irrestrito

✅ **Membros do Clan**
- Se a base tem um clan associado
- Todos os membros podem construir
- Automático ao entrar no clan

✅ **Usuários Autorizados**
- Permissões concedidas pelo dono
- Registradas em `base_permissions`

**QUEM NÃO PODE:**

❌ **Jogadores sem Discord**
- Não têm conta vinculada
- Considerados invasores

❌ **Jogadores de Outros Clans**
- Membros de clans rivais
- Tentativa de construir = BAN

❌ **Jogadores Não Autorizados**
- Sem permissão explícita
- Sem vínculo com o clan da base

### 3️⃣ Detecção de Invasão

Quando alguém tenta colocar um item:

```
1. Sistema verifica coordenadas (X, Z)
2. Calcula distância até todas as bases
3. Se dentro do raio de proteção:
   ├─ Verifica se é o dono → ✅ PERMITIDO
   ├─ Verifica permissões → ✅ PERMITIDO
   ├─ Verifica se é do clan → ✅ PERMITIDO
   └─ Caso contrário → 🚫 INVASÃO DETECTADA!

4. BAN IMEDIATO via XUID
5. Notificação Discord
6. Muro da Vergonha
```

### 4️⃣ Itens Protegidos

O sistema detecta construção de:

- 🏗️ **Construções**: Cercas, muros, torres
- 🛢️ **Tambores**: Barrels (armazenamento)
- ⛺ **Barracas**: Tents
- 🌱 **Jardins**: GardenPlot
- 🔥 **Fogueiras**: Fireplace
- 🚪 **Portas**: Gates
- 📦 **Qualquer item colocável**

### 5️⃣ Itens BANIDOS Automaticamente

Mesmo o DONO da base não pode usar:

🚫 **Pneus** (TireRepairKit)
- Exploits conhecidos
- Ban instantâneo

🚫 **Shelter** (ImprovisedShelter)
- Glitch de visão através de paredes
- Ban instantâneo

---

## 📊 Estrutura do Banco de Dados

### Tabela: `bases_v2`

```sql
CREATE TABLE bases_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id TEXT NOT NULL,        -- Discord ID do dono
    name TEXT NOT NULL,            -- Nome da base
    location TEXT,                 -- Descrição da localização
    x REAL,                        -- Coordenada X
    z REAL,                        -- Coordenada Z
    radius REAL DEFAULT 100,       -- Raio de proteção (metros)
    clan_id INTEGER,               -- Clan associado (opcional)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: `base_permissions`

```sql
CREATE TABLE base_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_id INTEGER NOT NULL,      -- ID da base
    discord_id TEXT NOT NULL,      -- Discord ID autorizado
    level TEXT NOT NULL,           -- Nível de permissão
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_id) REFERENCES bases_v2(id)
);
```

### Tabela: `clan_members_v2`

```sql
CREATE TABLE clan_members_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clan_id INTEGER NOT NULL,      -- ID do clan
    discord_id TEXT NOT NULL,      -- Discord ID do membro
    role TEXT DEFAULT 'member',    -- Role no clan
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clan_id) REFERENCES clans(id)
);
```

---

## 🎯 Exemplos de Uso

### Exemplo 1: Jogador Tenta Construir na Base de Outro

**Cenário**:
- Base "Fortaleza Norte" pertence a "Jogador A"
- "Jogador B" tenta colocar uma cerca

**Resultado**:
```
🚨 [TERRITÓRIO] INVASÃO DETECTADA!
   Invasor: Jogador B
   Base: Fortaleza Norte
   Dono: Jogador A
   Item: FenceKit

✅ [TERRITÓRIO] Jogador B BANIDO automaticamente!

BAN APLICADO:
- XUID: 1234567890123456
- Motivo: Invasão de território - Tentou construir 'FenceKit' na base 'Fortaleza Norte'
- Evidência: Coordenadas X=5000, Z=3000, Distância: 45m
- Notificação Discord: Enviada
- Muro da Vergonha: Adicionado
```

### Exemplo 2: Membro do Clan Constrói (Permitido)

**Cenário**:
- Base "Fortaleza Norte" pertence ao clan "TXS"
- "Jogador C" é membro do clan "TXS"
- Tenta colocar uma torre de vigia

**Resultado**:
```
✅ [TERRITÓRIO] Construção permitida
   Jogador: Jogador C
   Base: Fortaleza Norte
   Motivo: Membro do clan TXS
   Item: WatchTower
```

### Exemplo 3: Usuário Autorizado Constrói (Permitido)

**Cenário**:
- Base "Fortaleza Norte" pertence a "Jogador A"
- "Jogador D" tem permissão explícita
- Tenta colocar um tambor

**Resultado**:
```
✅ [TERRITÓRIO] Construção permitida
   Jogador: Jogador D
   Base: Fortaleza Norte
   Motivo: Permissão concedida
   Item: Barrel
```

---

## ⚙️ Configuração

### Como Registrar uma Base

**Via Dashboard** (Recomendado):
```
1. Login no dashboard
2. Ir para "Minhas Bases"
3. Clicar em "Registrar Nova Base"
4. Preencher:
   - Nome da base
   - Coordenadas (X, Z)
   - Raio de proteção
   - Clan associado (opcional)
5. Salvar
```

**Via SQL** (Avançado):
```sql
INSERT INTO bases_v2 (owner_id, name, x, z, radius, clan_id)
VALUES ('DISCORD_ID', 'Minha Base', 5000.0, 3000.0, 100.0, NULL);
```

### Como Adicionar Permissões

**Via Dashboard**:
```
1. Acessar "Minhas Bases"
2. Selecionar base
3. Clicar em "Gerenciar Permissões"
4. Adicionar Discord ID do usuário
5. Selecionar nível: "build" ou "admin"
```

**Via SQL**:
```sql
INSERT INTO base_permissions (base_id, discord_id, level)
VALUES (1, 'DISCORD_ID_AMIGO', 'build');
```

### Como Associar Base a Clan

**Via Dashboard**:
```
1. Editar base
2. Selecionar clan no dropdown
3. Salvar
```

**Via SQL**:
```sql
UPDATE bases_v2
SET clan_id = CLAN_ID
WHERE id = BASE_ID;
```

---

## 🔍 Consultas Úteis

### Ver Todas as Bases

```sql
SELECT b.id, b.name, b.owner_id, b.x, b.z, b.radius, c.name as clan_name
FROM bases_v2 b
LEFT JOIN clans c ON b.clan_id = c.id
ORDER BY b.created_at DESC;
```

### Ver Permissões de uma Base

```sql
SELECT bp.discord_id, bp.level, bp.granted_at
FROM base_permissions bp
WHERE bp.base_id = BASE_ID;
```

### Ver Membros do Clan da Base

```sql
SELECT cm.discord_id, cm.role, cm.joined_at
FROM clan_members_v2 cm
WHERE cm.clan_id = (
    SELECT clan_id FROM bases_v2 WHERE id = BASE_ID
);
```

### Ver Invasões Detectadas

```sql
SELECT gamertag, description, detected_at, evidence
FROM infractions
WHERE infraction_type = 'territory_invasion'
ORDER BY detected_at DESC;
```

---

## 🛡️ Proteções Especiais

### 1. Itens Banidos Universalmente

Mesmo o dono não pode usar:
- Pneus (exploit)
- Shelter (glitch de visão)

### 2. Usuários Sem Discord

Jogadores sem conta vinculada:
- Não podem construir em NENHUMA base
- Considerados sempre como invasores
- Incentiva vinculação de conta

### 3. Raio de Proteção Configurável

Cada base pode ter raio diferente:
- Mínimo: 50m
- Padrão: 100m
- Máximo: 200m

### 4. Múltiplas Bases por Jogador

Um jogador pode ter várias bases:
- Sem limite
- Cada uma com proteção independente
- Pode ser em clans diferentes

---

## 🚨 Troubleshooting

### Base Não Protege

**Problema**: Outros constroem na minha base

**Soluções**:
1. Verificar se base está registrada:
   ```sql
   SELECT * FROM bases_v2 WHERE owner_id = 'SEU_DISCORD_ID';
   ```
2. Verificar coordenadas corretas
3. Verificar raio de proteção adequado

### Membro do Clan Não Consegue Construir

**Problema**: Membro autorizado recebe ban

**Soluções**:
1. Verificar se está no clan certo:
   ```sql
   SELECT * FROM clan_members_v2 WHERE discord_id = 'DISCORD_ID';
   ```
2. Verificar se base tem clan_id associado:
   ```sql
   SELECT clan_id FROM bases_v2 WHERE id = BASE_ID;
   ```
3. Verificar se clan_id coincide

### Não Consigo Construir na Minha Base

**Problema**: Próprio dono recebe ban

**Soluções**:
1. Verificar se owner_id está correto
2. Verificar vinculação Discord ↔ Gamertag:
   ```sql
   SELECT discord_id, gamertag FROM player_identities
   WHERE LOWER(gamertag) = LOWER('SEU_GAMERTAG');
   ```

---

## 📈 Estatísticas

### Dashboard (Futuro)

- Total de bases registradas
- Invasões detectadas (hoje/semana/mês)
- Bases mais atacadas
- Clans mais ativos

---

**Documentação Atualizada**: 2026-02-07
**Versão do Sistema**: v2.4.0
**Sistema**: 100% Funcional ✅
