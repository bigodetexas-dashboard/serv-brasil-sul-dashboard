# Melhorias Futuras - BigodeTexas

## Estatísticas Adicionais do Leaderboard

**Status**: Planejado (aguardando implementação)

### Colunas Propostas

As seguintes estatísticas podem ser adicionadas futuramente à tabela `users` ou criar uma nova tabela `player_stats`:

1. **zombie_kills** (INTEGER) - Total de zombies mortos
2. **distance_traveled** (REAL) - Distância total percorrida (km)
3. **vehicle_distance** (REAL) - Distância em veículos (km)
4. **reconnects** (INTEGER) - Número de reconexões
5. **buildings_placed** (INTEGER) - Total de construções colocadas
6. **raids_completed** (INTEGER) - Raids completados

### Implementação Recomendada

```sql
-- Opção 1: Adicionar à tabela users
ALTER TABLE users ADD COLUMN zombie_kills INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN distance_traveled REAL DEFAULT 0.0;
ALTER TABLE users ADD COLUMN vehicle_distance REAL DEFAULT 0.0;
ALTER TABLE users ADD COLUMN reconnects INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN buildings_placed INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN raids_completed INTEGER DEFAULT 0;

-- Opção 2: Criar tabela separada (recomendado)
CREATE TABLE player_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT UNIQUE NOT NULL,
    zombie_kills INTEGER DEFAULT 0,
    distance_traveled REAL DEFAULT 0.0,
    vehicle_distance REAL DEFAULT 0.0,
    reconnects INTEGER DEFAULT 0,
    buildings_placed INTEGER DEFAULT 0,
    raids_completed INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discord_id) REFERENCES users(discord_id)
);
```

### Dependências

- Requer parsing adicional dos logs do servidor Nitrado
- Necessita atualização do log parser para capturar essas métricas
- Dashboard precisa ser atualizado para exibir novas estatísticas

### Prioridade

**Baixa** - Funcionalidade opcional, não impacta operação principal do sistema.

---

*Documentado em: 2026-02-07*
