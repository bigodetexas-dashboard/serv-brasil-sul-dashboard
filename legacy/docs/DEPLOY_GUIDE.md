# Guia de Implantação - BigodeTexas Bot & Dashboard

Este guia descreve os passos necessários para configurar e rodar o BigodeTexas Bot e seu Dashboard Web.

## Pré-requisitos

1. **Python 3.8+** instalado.
2. **Conta no Discord Developer Portal** para criar o bot e obter as credenciais.
3. **Servidor Nitrado** com acesso aos logs (opcional, para killfeed automático).
4. **Dependências Python**: Instaladas via `pip install -r requirements.txt`.

## Configuração do Ambiente

1. Clone o repositório.
2. Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base).
3. Preencha as seguintes variáveis:
   - `DISCORD_TOKEN`: Token do seu bot.
   - `GUILD_ID`: ID do seu servidor Discord.
   - `SECRET_KEY`: Chave aleatória para sessões do Flask.
   - `DISCORD_CLIENT_ID`: ID da aplicação no Discord.
   - `DISCORD_CLIENT_SECRET`: Secret da aplicação no Discord.
   - `DISCORD_REDIRECT_URI`: URL de callback (ex: `http://localhost:5000/callback`).
   - `ADMIN_PASSWORD`: Senha para acesso administrativo no bot.

## Inicialização do Banco de Dados

O projeto utiliza um banco de dados SQLite unificado (`bigode_unified.db`).
Para inicializá-lo pela primeira vez:

```bash
python init_sqlite_db.py
```

## Executando o Bot

Para rodar o bot do Discord:

```bash
python bot_main.py
```

## Executando o Dashboard

Para rodar o servidor Flask do dashboard:

```bash
cd new_dashboard
python app.py
```

O dashboard estará disponível em `http://localhost:5000`.

## Estrutura de Arquivos Importante

- `/repositories`: Contém a lógica de acesso ao banco de dados (Repository Pattern).
- `/cogs`: Módulos de comandos para o Discord (Economy, Clans, Tools, etc).
- `/new_dashboard`: Código do site (Flask, Templates, Static).
- `bigode_unified.db`: Banco de dados SQLite central.

## Comandos Principais (Discord)

- `!perfil`: Ver seu perfil e saldo.
- `!daily`: Coletar recompensa diária.
- `!loja`: Ver itens disponíveis.
- `!guerra declarar <clã_inimigo>`: Iniciar uma guerra.
- `!procurado <gamertag> <recompensa>`: Colocar um bumba (bounty) em alguém.

## Manutenção

- **Guerra de Clãs**: As guerras expiram automaticamente após 7 dias. O bot/dashboard verifica a data de expiração.
- **Logs**: Verifique as mensagens no console para erros de banco de dados ou autenticação.

---
*Criado por BigodeTexas Team - 2025*
