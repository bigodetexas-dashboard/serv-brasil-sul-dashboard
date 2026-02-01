# 🎯 PASSO A PASSO: CRIAR SERVIÇO NO RENDER

**Siga exatamente estas etapas**

---

## PASSO 1: ACESSAR RENDER

1. Abra seu navegador
2. Acesse: **<https://dashboard.render.com>**
3. Faça login (GitHub ou email)
4. Você verá a dashboard com o serviço existente: `bigodetexas-dashboard`

---

## PASSO 2: INICIAR CRIAÇÃO DO SERVIÇO

1. Clique no botão **"New +"** (canto superior direito da tela)
2. No menu que abrir, clique em **"Web Service"**
3. Você será levado para a página "Create a new Web Service"

---

## PASSO 3: CONECTAR REPOSITÓRIO

1. Você verá uma lista de repositórios GitHub
2. Procure por: **bigodetexas-dashboard** ou **bigodetexas-dashboard/bigodetexas-dashboard**
3. Clique no botão **"Connect"** ao lado deste repositório

**Se não aparecer:**

- Clique em "Configure account" ou "Connect account"
- Autorize o Render a acessar seus repositórios GitHub
- Volte e procure novamente

---

## PASSO 4: CONFIGURAR SERVIÇO (PARTE 1 - BÁSICO)

Na página de configuração, preencha:

### Name (Nome do serviço)

```
serv-brasil-sul-dashboard
```

### Region (Região)

```
Oregon (US West)
```

### Branch (Branch do Git)

```
main
```

### Root Directory (Diretório raiz)

```
new_dashboard
```

**IMPORTANTE:** Digite exatamente `new_dashboard` (sem barra no início ou fim)

### Runtime (Ambiente)

```
Python 3
```

(Deve detectar automaticamente)

---

## PASSO 5: CONFIGURAR SERVIÇO (PARTE 2 - BUILD)

### Build Command (Comando de build)

```
pip install -r requirements.txt
```

### Start Command (Comando de inicialização)

```
gunicorn app:app
```

---

## PASSO 6: CONFIGURAR VARIÁVEIS DE AMBIENTE

1. Role a página até encontrar **"Environment Variables"** ou **"Advanced"**
2. Clique em **"Add Environment Variable"** ou **"Add from .env"**
3. Adicione CADA variável abaixo (uma por vez):

### Variável 1: SECRET_KEY

```
Key: SECRET_KEY
Value: 4ba0cf9c9cbfe18a82202b546f497c7d4d449d6e73b3fdf45503ebb8d1d5547e
```

### Variável 2: DATABASE_URL

```
Key: DATABASE_URL
Value: [COPIE DO SERVIÇO ANTIGO OU DO .env LOCAL]
```

**Como pegar DATABASE_URL:**

- **Opção A:** Abra outra aba → <https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g> → Environment → Copie o valor de DATABASE_URL
- **Opção B:** Abra o arquivo `.env` local e copie o valor

### Variável 3: DISCORD_CLIENT_ID

```
Key: DISCORD_CLIENT_ID
Value: 1442959269141020892
```

### Variável 4: DISCORD_CLIENT_SECRET

```
Key: DISCORD_CLIENT_SECRET
Value: iw9RzpjUTvU5R0_cmzBiVzYPnldCNOJS
```

### Variável 5: DISCORD_REDIRECT_URI

```
Key: DISCORD_REDIRECT_URI
Value: https://serv-brasil-sul-dashboard.onrender.com/callback
```

---

## PASSO 7: ESCOLHER PLANO

1. Role até a seção **"Instance Type"** ou **"Plan"**
2. Selecione: **Free**
3. Confirme que está selecionado (deve mostrar "$0/month")

---

## PASSO 8: REVISAR E CRIAR

1. **REVISE TUDO:**
   - Name: `serv-brasil-sul-dashboard` ✓
   - Root Directory: `new_dashboard` ✓
   - Build Command: `pip install -r requirements.txt` ✓
   - Start Command: `gunicorn app:app` ✓
   - 5 variáveis de ambiente adicionadas ✓
   - Plan: Free ✓

2. **Clique no botão azul:** **"Create Web Service"**

---

## PASSO 9: AGUARDAR DEPLOY

Após clicar em "Create Web Service":

1. Você será levado para a página do serviço
2. Verá o status: **"Building..."** ou **"In Progress"**
3. Logs aparecerão na tela mostrando o progresso
4. **AGUARDE 5-10 MINUTOS**

### O que você verá nos logs

```
==> Cloning from https://github.com/...
==> Running build command: pip install -r requirements.txt
==> Installing dependencies...
==> Build successful
==> Starting service...
==> Your service is live 🎉
```

5. Quando terminar, o status mudará para: **"Live"** (verde)

---

## PASSO 10: VERIFICAR URL

1. Na página do serviço, procure pela URL no topo
2. Deve ser: **<https://serv-brasil-sul-dashboard.onrender.com>**
3. Clique na URL para abrir em nova aba
4. **IMPORTANTE:** Na primeira vez, pode demorar 30-60 segundos para carregar (serviço "acordando")

---

## ✅ SUCESSO

Se você vir a homepage do dashboard, **PARABÉNS!** O serviço foi criado com sucesso!

---

## 🔴 SE DER ERRO

### Erro: "Build failed"

- Verifique os logs
- Procure por linhas em vermelho
- Me envie as últimas 20 linhas dos logs

### Erro: "Application failed to start"

- Verifique se Root Directory = `new_dashboard`
- Verifique se Start Command = `gunicorn app:app`
- Verifique se DATABASE_URL está correto

### Erro: "404 Not Found" ao acessar URL

- Aguarde mais 2-3 minutos (pode estar finalizando)
- Recarregue a página (F5)
- Verifique se status está "Live"

---

## 📞 ME AVISE QUANDO

- [ ] Serviço foi criado (status "Live")
- [ ] URL está acessível
- [ ] Ou se der algum erro

Então continuaremos com os próximos passos:

1. Aplicar schema no banco
2. Atualizar Discord OAuth
3. Testar todas as funcionalidades

---

**Boa sorte! Estou aqui para ajudar se precisar!** 🚀
