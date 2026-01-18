# API Documentation - BigodeBot

## REST API Endpoints

### Authentication

#### POST `/auth/discord`

Inicia o fluxo de autenticação Discord OAuth2.

**Response:**

```json
{
  "redirect_url": "https://discord.com/api/oauth2/authorize?..."
}
```

#### GET `/callback`

Callback do Discord OAuth2.

**Query Parameters:**

- `code` - Authorization code do Discord

**Response:**
Redireciona para `/dashboard` com sessão autenticada.

---

### Player API

#### GET `/api/player/profile`

Retorna o perfil do jogador autenticado.

**Headers:**

- `Authorization: Bearer <token>` (ou sessão)

**Response:**

```json
{
  "discord_id": "123456789",
  "nitrado_gamertag": "PlayerName",
  "balance": 15000,
  "kills": 42,
  "deaths": 10,
  "kd": 4.2,
  "best_killstreak": 8,
  "total_playtime": 36000,
  "nitrado_verified": true,
  "clan": {
    "id": 1,
    "name": "MyClan",
    "role": "member"
  }
}
```

#### GET `/api/player/stats`

Retorna estatísticas detalhadas do jogador.

**Response:**

```json
{
  "combat": {
    "kills": 42,
    "deaths": 10,
    "kd": 4.2,
    "best_killstreak": 8,
    "current_streak": 3
  },
  "economy": {
    "balance": 15000,
    "total_earned": 50000,
    "total_spent": 35000
  },
  "playtime": {
    "total_seconds": 36000,
    "formatted": "10h 00m"
  },
  "achievements": {
    "unlocked": 5,
    "total": 15,
    "list": ["first_kill", "rich_player", ...]
  }
}
```

#### GET `/api/player/inventory`

Retorna o inventário virtual do jogador.

**Response:**

```json
{
  "items": [
    {
      "item_key": "ak74",
      "name": "AK-74",
      "quantity": 1,
      "added_at": "2024-01-15T10:30:00"
    }
  ]
}
```

#### GET `/api/player/transactions`

Retorna histórico de transações.

**Query Parameters:**

- `limit` - Número de transações (default: 10, max: 100)

**Response:**

```json
{
  "transactions": [
    {
      "id": 123,
      "type": "kill",
      "amount": 50,
      "description": "Kill reward",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

### Shop API

#### GET `/api/shop/categories`

Lista todas as categorias da loja.

**Response:**

```json
{
  "categories": [
    "armas",
    "municao",
    "medico",
    "construcao",
    "veiculos"
  ]
}
```

#### GET `/api/shop/items`

Lista itens da loja.

**Query Parameters:**

- `category` - Filtrar por categoria (opcional)
- `active_only` - Apenas itens ativos (default: true)

**Response:**

```json
{
  "items": [
    {
      "item_key": "ak74",
      "name": "AK-74",
      "description": "Rifle de assalto",
      "price": 5000,
      "category": "armas",
      "is_active": true
    }
  ]
}
```

#### POST `/api/shop/purchase`

Compra um item da loja.

**Request Body:**

```json
{
  "item_key": "ak74",
  "coordinates": {
    "x": 4500,
    "z": 10200
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Item purchased successfully",
  "new_balance": 10000,
  "spawn_request_id": "abc123"
}
```

---

### Clan API

#### GET `/api/clans`

Lista todos os clãs.

**Query Parameters:**

- `sort_by` - Campo para ordenar (balance, members, created_at)
- `limit` - Número de clãs (default: 10)

**Response:**

```json
{
  "clans": [
    {
      "id": 1,
      "name": "Elite Squad",
      "leader_discord_id": "123456789",
      "balance": 50000,
      "member_count": 5,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### GET `/api/clans/:id`

Detalhes de um clã específico.

**Response:**

```json
{
  "id": 1,
  "name": "Elite Squad",
  "leader_discord_id": "123456789",
  "balance": 50000,
  "banner_url": "https://...",
  "members": [
    {
      "discord_id": "123456789",
      "role": "leader",
      "joined_at": "2024-01-01T00:00:00"
    }
  ],
  "active_war": {
    "id": 5,
    "opponent_id": 2,
    "opponent_name": "Rivals",
    "clan1_points": 10,
    "clan2_points": 8,
    "expires_at": "2024-01-20T20:00:00"
  }
}
```

#### POST `/api/clans/create`

Cria um novo clã.

**Request Body:**

```json
{
  "name": "New Clan"
}
```

**Response:**

```json
{
  "success": true,
  "clan_id": 10,
  "message": "Clan created successfully"
}
```

#### POST `/api/clans/:id/deposit`

Deposita coins no banco do clã.

**Request Body:**

```json
{
  "amount": 1000
}
```

**Response:**

```json
{
  "success": true,
  "new_clan_balance": 51000,
  "new_player_balance": 9000
}
```

---

### Leaderboard API

#### GET `/api/leaderboard/kills`

Top jogadores por kills.

**Query Parameters:**

- `limit` - Número de jogadores (default: 10, max: 100)

**Response:**

```json
{
  "leaderboard": [
    {
      "rank": 1,
      "nitrado_gamertag": "TopKiller",
      "kills": 150,
      "deaths": 30,
      "kd": 5.0
    }
  ]
}
```

#### GET `/api/leaderboard/kd`

Top jogadores por K/D ratio.

**Query Parameters:**

- `limit` - Número de jogadores
- `min_kills` - Mínimo de kills (default: 5)

**Response:**

```json
{
  "leaderboard": [
    {
      "rank": 1,
      "nitrado_gamertag": "ProPlayer",
      "kills": 100,
      "deaths": 10,
      "kd": 10.0
    }
  ]
}
```

#### GET `/api/leaderboard/coins`

Top jogadores por saldo.

**Response:**

```json
{
  "leaderboard": [
    {
      "rank": 1,
      "nitrado_gamertag": "RichPlayer",
      "balance": 100000
    }
  ]
}
```

---

### Bounty API

#### GET `/api/bounties`

Lista todas as recompensas ativas.

**Response:**

```json
{
  "bounties": [
    {
      "gamertag": "TargetPlayer",
      "amount": 5000,
      "placed_by": "HunterPlayer",
      "created_at": "2024-01-15T10:00:00"
    }
  ]
}
```

#### POST `/api/bounties/place`

Coloca uma recompensa.

**Request Body:**

```json
{
  "gamertag": "TargetPlayer",
  "amount": 5000
}
```

**Response:**

```json
{
  "success": true,
  "total_bounty": 5000,
  "new_balance": 5000
}
```

---

### Admin API

**Nota:** Todos os endpoints admin requerem autenticação de administrador.

#### POST `/api/admin/restart`

Reinicia o servidor DayZ.

**Response:**

```json
{
  "success": true,
  "message": "Server restart initiated"
}
```

#### POST `/api/admin/spawn`

Spawna um item no servidor.

**Request Body:**

```json
{
  "item_name": "AK-74",
  "quantity": 1,
  "coordinates": {
    "x": 4500,
    "z": 10200
  }
}
```

**Response:**

```json
{
  "success": true,
  "spawn_id": "xyz789"
}
```

#### GET `/api/admin/online-players`

Lista jogadores online.

**Response:**

```json
{
  "players": [
    {
      "gamertag": "Player1",
      "playtime_seconds": 3600,
      "connected_at": "2024-01-15T10:00:00"
    }
  ],
  "count": 15
}
```

---

## WebSocket Events

### Connection

```javascript
const socket = io('http://localhost:5000');
```

### Events

#### `killfeed`

Evento de kill em tempo real.

**Payload:**

```json
{
  "killer": "PlayerA",
  "victim": "PlayerB",
  "weapon": "AK-74",
  "distance": 150,
  "location": "Berezino",
  "timestamp": "2024-01-15T10:30:00"
}
```

#### `player_login`

Jogador conectou ao servidor.

**Payload:**

```json
{
  "gamertag": "Player1",
  "timestamp": "2024-01-15T10:00:00"
}
```

#### `player_logout`

Jogador desconectou do servidor.

**Payload:**

```json
{
  "gamertag": "Player1",
  "playtime_seconds": 3600,
  "timestamp": "2024-01-15T11:00:00"
}
```

---

## Error Responses

Todos os endpoints podem retornar os seguintes erros:

### 400 Bad Request

```json
{
  "error": "Invalid request",
  "message": "Missing required field: amount"
}
```

### 401 Unauthorized

```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

- Endpoints públicos: 60 requisições/minuto
- Endpoints autenticados: 120 requisições/minuto
- Endpoints admin: 300 requisições/minuto

**Headers de resposta:**

- `X-RateLimit-Limit` - Limite total
- `X-RateLimit-Remaining` - Requisições restantes
- `X-RateLimit-Reset` - Timestamp de reset
