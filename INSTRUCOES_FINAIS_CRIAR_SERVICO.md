# 🚀 CRIAR NOVO SERVIÇO - INSTRUÇÕES FINAIS

## ✅ PROGRESSO ATÉ AGORA

1. ✅ Repositório GitHub renomeado: `serv-brasil-sul-dashboard`
2. ✅ Serviço antigo SUSPENSO (não está mais rodando)
3. ✅ Todas as variáveis de ambiente salvas em: `VARIAVEIS_AMBIENTE_BACKUP.txt`
4. ⏳ Aguardando criação manual do novo serviço

---

## 📋 CRIAR SERVIÇO AGORA

O navegador deve abrir em: <https://dashboard.render.com/select-repo?type=web>

### PASSO 1: Selecionar Repositório

- Procure: **serv-brasil-sul-dashboard**
- Clique em: **"Connect"**

### PASSO 2: Configurar Básico

```
Name: serv-brasil-sul-dashboard
Region: Oregon (US West)
Branch: main
Root Directory: new_dashboard
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Instance Type: Free
```

### PASSO 3: Adicionar Variáveis de Ambiente

**OPÇÃO FÁCIL:** Clique em "Add from .env" e cole todo o conteúdo de `VARIAVEIS_AMBIENTE_BACKUP.txt`

**OU adicione uma por uma:**

```
SECRET_KEY=399a2d81b3710671c6ab9ff055fee0af8cf0c48f9c4fb789e52a5635d0119ec8
DATABASE_URL=postgresql://postgres:Lissy%402000@db.uvyhpedcgmroddvkngdl.supabase.co:5432/postgres
DISCORD_CLIENT_ID=1442959269141020892
DISCORD_CLIENT_SECRET=K7TpzNNTVI0Zj0zfpuwF_i-GLDu2S5c0
DISCORD_REDIRECT_URI=https://serv-brasil-sul-dashboard.onrender.com/callback
DISCORD_TOKEN=ODQ3NDU2NjUyMjUzMDY5Mzgy.GN2g88.GGCUohzjGJmtBpnNELLJJB6abbjSQx2rQAWyzg
ADMIN_PASSWORD=Lissy@2000
ADMIN_WHITELIST=831391383981522964
FOOTER_ICON=https://cdn.discordapp.com/attachments/1442262893188878496/1442286419539394682/logo_texas.png
FTP_HOST=brsp012.gamedata.io
FTP_PASS=hqPuAFd9
FTP_PORT=21
FTP_USER=ni3622181_1
NITRADO_TOKEN=FumKsv7MGrfa6zG0bxW7C3kqigM0zloo1FlQH3JqLeQ7siSoqw8DvLbAojdYqr_iheYUt-RYGcTC8rIHfoL662exac8yR8It21vS
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/1441892129591922782/20eO0Z6wurnlD47-BgQ7yP5ePt0mK-2pXF8iQUuLfllqkPyVGdkVuSdTr6vd5sBEWCz2
PYTHON_VERSION=3.11.9
RATE_LIMIT_ENABLED=true
SERVICE_ID=3622181
```

### PASSO 4: Criar

- Clique em: **"Deploy web service"**
- Aguarde: 5-10 minutos

---

## 🎯 URL ESPERADA

Com o repositório renomeado, a URL deve ser:

```
https://serv-brasil-sul-dashboard.onrender.com
```

---

## ✅ DEPOIS QUE CRIAR

Me avise quando:

1. Serviço criado
2. Status "Live"
3. Qual URL foi gerada

Então vou:

1. Atualizar código
2. Atualizar Discord OAuth
3. Fazer deploy final
4. Deletar serviço antigo permanentemente

---

**Tempo estimado:** 15-20 minutos total
