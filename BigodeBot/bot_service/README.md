# Bot Service - Discord Bot

Serviço independente do bot Discord para BigodeBot.

## Estrutura

```
bot_service/
├── main.py              # Ponto de entrada do bot
├── cogs/                # Comandos modulares
│   ├── __init__.py
│   ├── admin.py
│   ├── ai.py
│   ├── clans.py
│   ├── economy.py
│   ├── killfeed.py
│   ├── leaderboard.py
│   └── tools.py
├── config.py            # Configurações do bot
├── requirements.txt     # Dependências específicas
└── README.md           # Esta documentação
```

## Instalação

```bash
cd bot_service
pip install -r requirements.txt
```

## Configuração

Crie `.env` na raiz do bot_service:

```env
DISCORD_TOKEN=seu_token
GEMINI_API_KEY=sua_key
FTP_HOST=servidor_ftp
FTP_USER=usuario
FTP_PASS=senha
DATABASE_PATH=../shared/bigodebot.db
```

## Execução

```bash
python main.py
```

## Dependências Compartilhadas

O bot usa módulos compartilhados em `../shared/`:

- `repositories/` - Acesso ao banco de dados
- `utils/` - Utilitários comuns
- `models/` - Modelos de dados

## Comandos Disponíveis

Ver documentação principal do projeto.
