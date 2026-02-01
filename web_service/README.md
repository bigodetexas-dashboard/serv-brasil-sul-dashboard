# Web Service - Dashboard

Serviço independente do painel web para BigodeBot.

## Estrutura

```
web_service/
├── app.py               # Aplicação Flask
├── templates/           # Templates HTML
├── static/              # CSS, JS, imagens
├── config.py            # Configurações
├── requirements.txt     # Dependências específicas
└── README.md           # Esta documentação
```

## Instalação

```bash
cd web_service
pip install -r requirements.txt
```

## Configuração

Crie `.env` na raiz do web_service:

```env
DISCORD_CLIENT_ID=seu_client_id
DISCORD_CLIENT_SECRET=seu_secret
DISCORD_REDIRECT_URI=http://localhost:5000/callback
MICROSOFT_CLIENT_ID=seu_microsoft_id
MICROSOFT_CLIENT_SECRET=seu_microsoft_secret
DATABASE_PATH=../shared/bigodebot.db
SECRET_KEY=chave_secreta_flask
```

## Execução

```bash
python app.py
```

Acesse: <http://localhost:5000>

## Dependências Compartilhadas

O dashboard usa módulos compartilhados em `../shared/`:

- `repositories/` - Acesso ao banco de dados
- `utils/` - Utilitários comuns
- `models/` - Modelos de dados

## Endpoints

Ver `API_DOCUMENTATION.md` na raiz do projeto.
