# BigodeBot - DayZ Xbox Server Management System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Sistema completo de gerenciamento para servidor DayZ Xbox com bot Discord e painel web administrativo.

## 🎯 Funcionalidades

### Discord Bot

- **Killfeed em Tempo Real** - Monitora logs do servidor via FTP
- **Sistema de Economia** - DZ Coins, loja virtual, transações
- **Sistema de Clãs** - Criação, membros, guerras entre clãs
- **Recompensas (Bounties)** - Sistema de caça-recompensas
- **Conquistas** - Sistema de achievements desbloqueáveis
- **Leaderboards** - Rankings de kills, K/D, coins, playtime
- **Proteção de Bases** - Alarmes automáticos e anti-raid
- **IA Integrada** - Perguntas e análises via Google Gemini
- **Heatmap PvP** - Visualização de zonas quentes

### Painel Web (Dashboard)

- **Autenticação Discord/Xbox** - Login integrado
- **Perfil de Jogador** - Stats, inventário, transações
- **Loja Virtual** - Compra de itens com entrega via drone
- **Mapa Interativo** - Visualização de bases e eventos
- **Admin Panel** - Controle de servidor, spawns, configurações
- **Estatísticas em Tempo Real** - Players online, eventos

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.10 ou superior
- Conta Discord com bot criado
- Servidor DayZ com acesso FTP (Nitrado)
- Conta Google Cloud (para IA - opcional)

### Passo a Passo

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/BigodeBot.git
cd BigodeBot
```

1. **Instale as dependências**

```bash
pip install -r requirements.txt
```

1. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
# Discord
DISCORD_TOKEN=seu_token_discord
DISCORD_CLIENT_ID=seu_client_id
DISCORD_CLIENT_SECRET=seu_client_secret
DISCORD_REDIRECT_URI=http://localhost:5000/callback

# Microsoft/Xbox (opcional)
MICROSOFT_CLIENT_ID=seu_microsoft_client_id
MICROSOFT_CLIENT_SECRET=seu_microsoft_client_secret
MICROSOFT_REDIRECT_URI=http://localhost:5000/callback/xbox

# Google Gemini (opcional)
GEMINI_API_KEY=sua_api_key_gemini

# FTP Nitrado
FTP_HOST=seu_servidor_ftp
FTP_USER=seu_usuario_ftp
FTP_PASS=sua_senha_ftp

# Outros
FOOTER_ICON=url_do_icone
ADMIN_PASSWORD=senha_admin
```

1. **Inicialize o banco de dados**

```bash
python -c "from repositories.base_repository import BaseRepository; BaseRepository().init_database()"
```

1. **Execute o bot**

```bash
python bot_main.py
```

1. **Execute o dashboard** (em outro terminal)

```bash
python new_dashboard/app.py
```

## 📁 Estrutura do Projeto

```
BigodeBot/
├── bot_main.py              # Ponto de entrada do bot Discord
├── cogs/                    # Comandos do bot (modular)
│   ├── admin.py            # Comandos administrativos
│   ├── ai.py               # Integração com IA
│   ├── clans.py            # Sistema de clãs
│   ├── economy.py          # Sistema econômico
│   ├── killfeed.py         # Monitoramento de logs
│   ├── leaderboard.py      # Rankings
│   └── tools.py            # Utilidades
├── repositories/            # Camada de dados (Repository Pattern)
│   ├── base_repository.py  # Classe base com connection pool
│   ├── player_repository.py
│   ├── clan_repository.py
│   ├── bounty_repository.py
│   ├── item_repository.py
│   └── connection_pool.py  # Pool de conexões SQLite
├── new_dashboard/           # Painel web Flask
│   ├── app.py              # Aplicação Flask
│   ├── static/             # CSS, JS, imagens
│   └── templates/          # Templates HTML
├── utils/                   # Utilitários
│   ├── cache.py            # Sistema de cache LRU
│   ├── nitrado.py          # API Nitrado
│   ├── ftp_helpers.py      # Helpers FTP
│   ├── decorators.py       # Decoradores customizados
│   └── helpers.py          # Funções auxiliares
├── tests/                   # Testes automatizados
├── database_schema_sqlite.sql  # Schema do banco
├── database_indexes.sql     # Índices de performance
└── requirements.txt         # Dependências Python
```

## 🎮 Comandos do Bot

### Economia

- `!saldo` - Ver seu saldo de DZ Coins
- `!daily` - Resgatar bônus diário
- `!loja [categoria]` - Ver itens da loja
- `!comprar <item>` - Comprar item
- `!transferir @user <valor>` - Transferir coins
- `!extrato` - Ver histórico de transações

### Clãs

- `!criar_clã <nome>` - Criar novo clã
- `!clã [tag]` - Ver informações do clã
- `!clãs` - Ranking de clãs
- `!depositar_clã <valor>` - Depositar no banco do clã
- `!convidar_clã @user` - Convidar membro
- `!guerra declarar <tag>` - Declarar guerra
- `!guerra placar` - Ver placar da guerra

### Rankings

- `!top kills` - Top matadores
- `!top kd` - Melhor K/D
- `!top streak` - Maiores killstreaks
- `!top coins` - Mais ricos
- `!top playtime` - Mais tempo jogado
- `!heatmap` - Gerar mapa de calor PvP

### Utilidades

- `!perfil [@user]` - Ver perfil de jogador
- `!registrar <gamertag>` - Vincular gamertag
- `!alarme set <nome> <X> <Z> <raio>` - Configurar alarme de base
- `!procurado <gamertag> <valor>` - Colocar recompensa
- `!ia <pergunta>` - Perguntar para a IA

### Admin (Requer senha)

- `!restart` - Reiniciar servidor
- `!spawn <item> <qtd> <gamertag>` - Spawnar item
- `!desvincular <gamertag>` - Desvincular conta
- `!gerarevento` - Gerar ideia de evento (IA)
- `!analisarlogs <linhas>` - Analisar logs (IA)

## ⚙️ Configuração Avançada

### Connection Pool

O sistema usa connection pooling para melhor performance:

```python
# repositories/connection_pool.py
pool = ConnectionPool(
    db_path="bigodebot.db",
    pool_size=5,  # Número de conexões
    timeout=30    # Timeout em segundos
)
```

### Cache

Cache LRU para dados frequentes:

```python
from utils.cache import cached

@cached(ttl=300)  # Cache por 5 minutos
def get_expensive_data():
    return expensive_query()
```

### Índices de Banco

Execute para criar índices de performance:

```bash
sqlite3 bigodebot.db < database_indexes.sql
```

## 🧪 Testes

Execute os testes automatizados:

```bash
pytest tests/ -v
```

Com cobertura:

```bash
pytest tests/ --cov=repositories --cov-report=html
```

## 📊 Performance

### Otimizações Implementadas

- ✅ Connection pooling SQLite
- ✅ Cache LRU em memória
- ✅ Índices de banco otimizados
- ✅ WAL mode para melhor concorrência
- ✅ Queries otimizadas com LIMIT

### Benchmarks

- Consultas de leaderboard: ~5ms (com cache)
- Inserção de kill: ~10ms
- Atualização de saldo: ~8ms
- Geração de heatmap: ~2s (500 pontos)

## 🔒 Segurança

- Autenticação Discord OAuth2
- Verificação Xbox via Microsoft OAuth
- Rate limiting em comandos sensíveis
- Validação de inputs
- Proteção contra SQL injection (prepared statements)
- Logs de segurança automáticos

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- [Discord.py](https://discordpy.readthedocs.io/) - Framework do bot
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Google Gemini](https://ai.google.dev/) - IA integrada
- [Nitrado](https://nitrado.net/) - Hospedagem de servidor

## 📧 Suporte

- Discord: [Servidor de Suporte](#)
- Email: <suporte@bigodebot.com>
- Issues: [GitHub Issues](https://github.com/seu-usuario/BigodeBot/issues)

---

**Desenvolvido com ❤️ para a comunidade DayZ Xbox**
