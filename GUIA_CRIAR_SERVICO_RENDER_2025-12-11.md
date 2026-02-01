# 🚀 GUIA: CRIAR SERVIÇO CORRETO NO RENDER

**Data:** 11/12/2025 20:46  
**Problema Identificado:** O serviço `serv-brasil-sul-dashboard` nunca foi criado  
**Solução:** Criar manualmente no painel do Render

---

## 🔍 **O QUE ACONTECEU**

### Situação Atual

- ✅ **Existe:** `bigodetexas-dashboard.onrender.com` (site antigo)
- ❌ **NÃO existe:** `serv-brasil-sul-dashboard.onrender.com` (site novo)

### O Que a Assistente Anterior Pensou

Ela PENSOU que tinha criado o serviço `serv-brasil-sul-dashboard`, mas na verdade apenas fez deploy no serviço antigo (`bigodetexas-dashboard`).

### Por Que Isso Aconteceu

O Render não permite criar serviços Free via API. A assistente anterior não conseguiu criar o novo serviço programaticamente.

---

## ✅ **SOLUÇÃO: CRIAR SERVIÇO MANUALMENTE**

### PASSO 1: Acessar Render Dashboard

1. Acesse: **<https://dashboard.render.com>**
2. Faça login (GitHub ou email)
3. Você verá o serviço existente: `bigodetexas-dashboard`

### PASSO 2: Criar Novo Web Service

1. Clique no botão **"New +"** (canto superior direito)
2. Selecione **"Web Service"**
3. Conecte ao repositório GitHub:
   - Se já estiver conectado, selecione: `bigodetexas-dashboard/bigodetexas-dashboard`
   - Se não, clique em "Connect account" e autorize GitHub

### PASSO 3: Configurar o Serviço

**Configurações Básicas:**

```
Name: serv-brasil-sul-dashboard
Region: Oregon (US West)
Branch: main
Root Directory: new_dashboard
Runtime: Python 3
```

**Build & Deploy:**

```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

**Instance Type:**

```
Plan: Free
```

### PASSO 4: Adicionar Variáveis de Ambiente

Clique em "Advanced" e adicione as seguintes variáveis:

```env
SECRET_KEY=4ba0cf9c9cbfe18a82202b546f497c7d4d449d6e73b3fdf45503ebb8d1d5547e
DATABASE_URL=<sua_url_postgresql_supabase>
DISCORD_CLIENT_ID=1442959269141020892
DISCORD_CLIENT_SECRET=iw9RzpjUTvU5R0_cmzBiVzYPnldCNOJS
DISCORD_REDIRECT_URI=https://serv-brasil-sul-dashboard.onrender.com/callback
```

**IMPORTANTE:** Você precisa pegar o `DATABASE_URL` do serviço antigo ou do arquivo `.env` local.

### PASSO 5: Criar o Serviço

1. Revise todas as configurações
2. Clique em **"Create Web Service"**
3. O Render vai começar o build automaticamente
4. Aguarde 5-10 minutos

### PASSO 6: Aguardar Deploy

O Render vai:

1. ✅ Fazer pull do código do GitHub
2. ✅ Instalar dependências (`pip install -r requirements.txt`)
3. ✅ Iniciar aplicação (`gunicorn app:app`)
4. ✅ Gerar URL: `https://serv-brasil-sul-dashboard.onrender.com`

**Status:** Você verá "Building..." → "Live" quando terminar

---

## 🔧 **APÓS O SERVIÇO SER CRIADO**

### 1. Aplicar Schema no Banco de Produção

```bash
cd "d:/dayz xbox/BigodeBot"
python apply_schema_production.py
```

Digite `sim` quando solicitado.

### 2. Atualizar Discord OAuth

No Discord Developer Portal:

1. Acessar: <https://discord.com/developers/applications>
2. Selecionar aplicação: `1442959269141020892`
3. Ir em **OAuth2 → Redirects**
4. **ADICIONAR:** `https://serv-brasil-sul-dashboard.onrender.com/callback`
5. Salvar mudanças

### 3. Testar o Site

Acessar:

```
https://serv-brasil-sul-dashboard.onrender.com/
https://serv-brasil-sul-dashboard.onrender.com/achievements
https://serv-brasil-sul-dashboard.onrender.com/history
https://serv-brasil-sul-dashboard.onrender.com/settings
```

### 4. (Opcional) Deletar Serviço Antigo

Depois de confirmar que tudo funciona:

1. Acessar: <https://dashboard.render.com>
2. Selecionar serviço: `bigodetexas-dashboard`
3. Settings → Delete Service

---

## 📋 **CHECKLIST**

### Criação do Serviço

- [ ] Acessou Render Dashboard
- [ ] Clicou em "New +" → "Web Service"
- [ ] Selecionou repositório correto
- [ ] Configurou Name: `serv-brasil-sul-dashboard`
- [ ] Configurou Root Directory: `new_dashboard`
- [ ] Configurou Build Command: `pip install -r requirements.txt`
- [ ] Configurou Start Command: `gunicorn app:app`
- [ ] Adicionou todas as variáveis de ambiente
- [ ] Clicou em "Create Web Service"

### Pós-Deploy

- [ ] Deploy terminou (status "Live")
- [ ] Executou `apply_schema_production.py`
- [ ] Atualizou Discord OAuth redirect URI
- [ ] Testou site e todas as páginas funcionam
- [ ] (Opcional) Deletou serviço antigo

---

## ⚠️ **IMPORTANTE: DATABASE_URL**

Você precisa do `DATABASE_URL` do Supabase. Para encontrar:

**Opção 1: Pegar do serviço antigo**

1. Acessar: <https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g>
2. Ir em "Environment"
3. Copiar valor de `DATABASE_URL`

**Opção 2: Pegar do Supabase**

1. Acessar: <https://supabase.com/dashboard>
2. Selecionar projeto
3. Settings → Database → Connection String
4. Copiar URL (formato: `postgresql://postgres:...@...pooler.supabase.com:6543/postgres`)

---

## 🎯 **RESULTADO ESPERADO**

Após seguir todos os passos:

✅ **Novo site online:** `https://serv-brasil-sul-dashboard.onrender.com`  
✅ **Todas as páginas funcionando**  
✅ **Discord OAuth configurado**  
✅ **Schema aplicado no banco**  
✅ **Site antigo pode ser deletado**

---

## 💡 **POR QUE FAZER ISSO MANUALMENTE?**

O Render **não permite** criar serviços Free via API. A única forma é:

1. Criar manualmente no painel web
2. Ou usar Render CLI (mas ainda precisa de interação manual)

**Tempo estimado:** 15-20 minutos (incluindo aguardar deploy)

---

**Desenvolvido por:** Antigravity AI  
**Para:** SERV. BRASIL SUL - XBOX DayZ Community  
**Status:** 📝 AGUARDANDO CRIAÇÃO MANUAL DO SERVIÇO
