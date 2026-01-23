# 🚀 Guia de Deploy - BigodeTexas Dashboard

Este guia explica como colocar o novo dashboard online usando o Render.com.

## 1. Preparação no GitHub

1. Certifique-se de que todo o código está no seu repositório GitHub.
2. Os arquivos importantes que criamos (`requirements.txt`, `Procfile`, `runtime.txt`) devem estar na pasta `new_dashboard`.

## 2. Criando o Serviço no Render

1. Acesse [dashboard.render.com](https://dashboard.render.com/).
2. Clique em **New +** e selecione **Web Service**.
3. Conecte seu repositório do GitHub.
4. Dê um nome ao serviço (ex: `bigodetexas-dashboard`).

## 3. Configurações do Serviço

Preencha os campos da seguinte forma:

* **Root Directory:** `new_dashboard` (MUITO IMPORTANTE! Isso diz ao Render para olhar apenas essa pasta)
* **Runtime:** `Python 3`
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn app:app`

## 4. Variáveis de Ambiente (Environment Variables)

Clique na aba **Environment** e adicione as seguintes variáveis (copie do seu arquivo `.env` local):

| Key | Value |
| --- | --- |
| `SECRET_KEY` | (Sua chave secreta aleatória) |
| `DATABASE_URL` | (Sua URL de conexão do Supabase) |
| `DISCORD_CLIENT_ID` | (Seu ID de cliente do Discord Developer Portal) |
| `DISCORD_CLIENT_SECRET` | (Seu segredo do Discord Developer Portal) |
| `DISCORD_REDIRECT_URI` | `https://bigodetexas-dashboard.onrender.com/callback` (Ajuste a URL após o deploy) |

## 5. Finalizando

1. Clique em **Create Web Service**.
2. Aguarde o deploy finalizar.
3. Acesse a URL gerada pelo Render para testar!

---

### Nota sobre o Redirect URI:

Lembre-se de ir no [Discord Developer Portal](https://discord.com/developers/applications), selecionar sua aplicação, ir em **OAuth2** e adicionar a nova URL de callback do Render (ex: `https://seu-app.onrender.com/callback`) na lista de Redirects.
