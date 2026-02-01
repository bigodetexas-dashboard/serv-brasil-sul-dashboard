# 🚀 PLANO: CRIAR NOVO SERVIÇO COM URL CORRETA

**Data:** 11/12/2025 20:52  
**Decisão:** OPÇÃO 2 - Criar novo serviço do zero

---

## 📋 **PLANO DE AÇÃO**

### PASSO 1: Criar Novo Serviço no Render (MANUAL)

Você precisa fazer isso manualmente no painel do Render:

1. Acesse: <https://dashboard.render.com>
2. Clique em **"New +"** → **"Web Service"**
3. Selecione o repositório: `bigodetexas-dashboard`
4. Configure:

```
Name: serv-brasil-sul-dashboard-v2
Region: Oregon (US West)
Branch: main
Root Directory: new_dashboard
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Plan: Free
```

**IMPORTANTE:** Use o nome `serv-brasil-sul-dashboard-v2` para que o Render gere o slug correto.

### PASSO 2: Adicionar Variáveis de Ambiente

Copie as variáveis do serviço antigo:

1. Abra em outra aba: <https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g>
2. Vá em **Environment**
3. Copie TODAS as variáveis:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `DISCORD_CLIENT_ID`
   - `DISCORD_CLIENT_SECRET`
   - `DISCORD_REDIRECT_URI` (ALTERE para: `https://serv-brasil-sul-dashboard-v2.onrender.com/callback`)

### PASSO 3: Criar o Serviço

1. Revise todas as configurações
2. Clique em **"Create Web Service"**
3. Aguarde 5-10 minutos (deploy)

### PASSO 4: Verificar URL Gerada

Após o deploy terminar, verifique qual URL foi gerada:

- Se for `https://serv-brasil-sul-dashboard-v2.onrender.com` ✅
- Se for outra, me avise

### PASSO 5: Atualizar Código

Depois que o novo serviço estiver funcionando, vou:

1. Atualizar todas as URLs no código
2. Fazer commit e push
3. O Render vai fazer redeploy automático

### PASSO 6: Deletar Serviço Antigo

Quando tudo estiver funcionando:

1. Acessar: <https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g>
2. Settings → Delete Service

---

## ⚠️ **PROBLEMA POTENCIAL**

O Render pode gerar o slug baseado no repositório, não no nome do serviço.

**Se isso acontecer:**

- O serviço terá nome: `serv-brasil-sul-dashboard-v2`
- Mas a URL será: `https://bigodetexas-dashboard-XXXX.onrender.com`

**Solução alternativa:**

1. Renomear o repositório GitHub para `serv-brasil-sul-dashboard`
2. Criar o serviço novamente
3. O slug será gerado corretamente

---

## 🎯 **VOCÊ ESTÁ PRONTO PARA CRIAR?**

Siga o guia em: `PASSO_A_PASSO_RENDER.md`

Ou me avise se quer que eu explique cada passo novamente!

---

**Tempo estimado:** 20-30 minutos (incluindo deploy)
