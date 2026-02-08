# 🤖 Configuração de Comandos Discord - BigodeTexas

## Como Adicionar Comandos de Guerra ao Bot

### Passo 1: Verificar Estrutura de Pastas

Certifique-se de que a pasta `commands/` existe:
```
BigodeBot/
├── bot_main.py
├── commands/
│   └── war_commands.py  ✅ (já criado)
├── war_system.py
└── ...
```

### Passo 2: Modificar bot_main.py

Adicione o seguinte código ao `bot_main.py`:

```python
# No início do arquivo, após os imports
import os

# Após a criação do bot (linha ~50)
@bot.event
async def on_ready():
    print(f'[BOT] Logado como {bot.user}')

    # Carregar comandos de guerra
    try:
        await bot.load_extension('commands.war_commands')
        print('[BOT] Comandos de guerra carregados com sucesso')
    except Exception as e:
        print(f'[BOT] Erro ao carregar comandos de guerra: {e}')

    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        print(f'[BOT] {len(synced)} comandos slash sincronizados')
    except Exception as e:
        print(f'[BOT] Erro ao sincronizar comandos: {e}')
```

### Passo 3: Reiniciar o Bot

```bash
# Parar o bot (se estiver rodando)
# Iniciar novamente
cd "d:\dayz xbox\BigodeBot"
python bot_main.py
```

---

## Comandos Discord Disponíveis

### ⚔️ Comandos de Guerra

#### `/war_start <clan1> <clan2>`
**Descrição**: Inicia uma guerra entre dois clãs
**Permissão**: Apenas Administradores
**Exemplo**:
```
/war_start TXS INIMIGOS
```

**Resposta**:
```
⚔️ GUERRA DECLARADA!
Uma guerra foi iniciada entre os clãs!

🔴 Clã 1: TXS
🔵 Clã 2: INIMIGOS
📊 Placar: 0 x 0
```

---

#### `/war_status <clan1> <clan2>`
**Descrição**: Exibe o placar atual de uma guerra
**Permissão**: Todos
**Exemplo**:
```
/war_status TXS INIMIGOS
```

**Resposta**:
```
⚔️ STATUS DA GUERRA
Guerra entre TXS e INIMIGOS

🔴 TXS: 15 kills
🔵 INIMIGOS: 12 kills
📊 Placar: 15 x 12

🏆 TXS está na liderança!
📅 Iniciada em: 2026-02-07
```

---

#### `/war_end <clan1> <clan2>`
**Descrição**: Finaliza uma guerra entre clãs
**Permissão**: Apenas Administradores
**Exemplo**:
```
/war_end TXS INIMIGOS
```

**Resposta**:
```
🏁 GUERRA FINALIZADA!
A guerra entre TXS e INIMIGOS foi encerrada!

📊 Placar Final: 15 x 12
🏆 Vencedor: TXS com 15 kills!
```

---

#### `/war_list`
**Descrição**: Lista todas as guerras ativas
**Permissão**: Todos
**Exemplo**:
```
/war_list
```

**Resposta**:
```
⚔️ GUERRAS ATIVAS
Total de guerras em andamento: 2

⚔️ TXS vs INIMIGOS
Placar: 15 x 12
🏆 TXS
📅 Desde: 2026-02-07

⚔️ ALFA vs BETA
Placar: 8 x 8
⚖️ Empate
📅 Desde: 2026-02-07
```

---

## 📝 Scripts de Gerenciamento

### Gerenciar Roles (RBAC)

```bash
# Listar todos os usuários e roles
python scripts/manage_roles.py list

# Atribuir role de admin
python scripts/manage_roles.py set 123456789 admin

# Atribuir role de moderator
python scripts/manage_roles.py set 123456789 moderator

# Banir usuário
python scripts/manage_roles.py ban 123456789 "Uso de cheats"

# Desbanir usuário
python scripts/manage_roles.py unban 123456789

# Ver ajuda
python scripts/manage_roles.py help
```

**Saída Exemplo**:
```
============================================================
LISTA DE USUARIOS E ROLES
============================================================

Total de usuários: 15

Estatísticas:
  🔴 Admins:      2
  🟡 Moderators:  3
  🟢 Users:       9
  ⚫ Banned:      1

🔴 ADMIN:
  - BigodeTexas (123456789)
  - Admin2 (987654321)

🟡 MODERATOR:
  - Moderador1 (111222333)
  - Moderador2 (444555666)
  - Moderador3 (777888999)

🟢 USER:
  - Jogador1 (100200300)
  - Jogador2 (400500600)
  ...

⚫ BANNED:
  - Cheater123 (999888777) [BANIDO]
```

---

## 🔧 Troubleshooting

### Comandos não aparecem no Discord

1. Verifique se o bot tem a permissão `applications.commands`
2. Certifique-se de que os comandos foram sincronizados:
```python
await bot.tree.sync()
```
3. Aguarde até 1 hora para os comandos aparecerem globalmente
4. Para testar imediatamente, use guild-specific sync:
```python
await bot.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))
```

### Erro "Module not found: commands.war_commands"

Certifique-se de que:
1. A pasta `commands/` existe
2. Há um arquivo `__init__.py` dentro de `commands/`
3. O arquivo `war_commands.py` está dentro de `commands/`

### Comandos não executam

Verifique:
1. Se o bot está online
2. Se há erros no console ao executar o comando
3. Se o usuário tem as permissões necessárias (Admin para /war_start e /war_end)

---

## 🎯 Próximos Passos

1. ✅ Adicionar comandos ao bot
2. ✅ Testar comandos no servidor Discord
3. ✅ Configurar roles de usuários
4. ✅ Iniciar primeira guerra de teste
5. ✅ Monitorar logs e ajustar conforme necessário

---

**Documentação atualizada**: 2026-02-07
**Versão do Sistema**: v2.3.0
