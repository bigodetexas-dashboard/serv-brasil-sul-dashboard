# 🚀 GUIA COMPLETO - DEPLOY DO NOVO DASHBOARD

**Data:** 07/12/2025  
**Objetivo:** Substituir site antigo pelo novo dashboard com Achievements, History e Settings

---

## 📋 **SITUAÇÃO ATUAL**

### Site Antigo (Online)

- **URL:** <https://bigodetexas-dashboard.onrender.com>
- **Serviço:** srv-d4jrhp8gjchc739odl2g
- **Status:** RODANDO (versão antiga)

### Novo Dashboard (Local)

- **Pasta:** `d:/dayz xbox/BigodeBot/new_dashboard/`
- **Status:** 100% COMPLETO
- **Novidades:**
  - Sistema de Conquistas
  - Histórico de Atividades
  - Configurações de Usuário
  - APIs completas
  - Frontend conectado

---

## 🎯 **PLANO DE DEPLOY**

### **Opção 1: Atualizar Serviço Existente (RECOMENDADO)**

Vantagens:

- ✅ Mantém a mesma URL
- ✅ Mantém variáveis de ambiente
- ✅ Mais rápido
- ✅ Sem necessidade de reconfigurar Discord OAuth

### **Opção 2: Criar Novo Serviço**

Vantagens:

- ✅ Pode testar antes de substituir
- ✅ Rollback fácil se der problema
- ❌ Precisa reconfigurar tudo

---

## 🚀 **PASSO A PASSO - OPÇÃO 1 (ATUALIZAR)**

### **1. Preparar Código para Deploy**

#### A. Verificar arquivos essenciais

```bash
cd "d:/dayz xbox/BigodeBot/new_dashboard"
```

Arquivos necessários:

- ✅ `app.py` - Aplicação principal
- ✅ `requirements.txt` - Dependências
- ✅ `Procfile` - Comando de start
- ✅ `runtime.txt` - Versão Python
- ✅ `templates/` - Todos os HTMLs
- ✅ `static/` - CSS, JS, imagens

#### B. Verificar Procfile

```bash
# Deve conter:
web: gunicorn app:app
```

#### C. Verificar runtime.txt

```bash
# Deve conter:
python-3.10.12
```

#### D. Verificar requirements.txt

Deve incluir:

```
Flask==2.3.3
gunicorn==21.2.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
requests==2.31.0
```

### **2. Fazer Commit e Push**

```bash
cd "d:/dayz xbox/BigodeBot"

# Adicionar tudo
git add -A

# Commit
git commit -m "feat: Deploy novo dashboard v10.0 com Achievements, History e Settings

- Sistema de conquistas completo
- Histórico de atividades
- Configurações de usuário
- APIs adaptadas para estrutura existente
- Frontend 100% conectado
- Pronto para produção"

# Push
git push origin main
```

### **3. Aplicar Schema no Banco de Produção**

**IMPORTANTE:** Antes de fazer deploy, aplicar schema no banco de produção!

```bash
# Conectar ao banco de produção
python apply_partial.py
```

Ou manualmente via Supabase/Render Dashboard:

1. Acessar painel do PostgreSQL
2. Executar SQL de `schema_partial.sql`

### **4. Atualizar Serviço no Render**

#### Via Dashboard Render

1. Acessar: <https://dashboard.render.com>
2. Encontrar serviço: `srv-d4jrhp8gjchc739odl2g`
3. Clicar em "Manual Deploy" → "Deploy latest commit"
4. Aguardar build (5-10 minutos)

#### Via Render CLI (Alternativa)

```bash
# Instalar Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy --service srv-d4jrhp8gjchc739odl2g
```

### **5. Verificar Variáveis de Ambiente**

No painel do Render, verificar se estão configuradas:

```env
SECRET_KEY=<sua_chave_secreta>
DATABASE_URL=<url_postgresql_supabase>
DISCORD_CLIENT_ID=<discord_app_id>
DISCORD_CLIENT_SECRET=<discord_app_secret>
DISCORD_REDIRECT_URI=https://bigodetexas-dashboard.onrender.com/callback
```

### **6. Aguardar Deploy**

O Render vai:

1. ✅ Fazer pull do código
2. ✅ Instalar dependências
3. ✅ Executar build
4. ✅ Iniciar aplicação
5. ✅ Site ficará online automaticamente

---

## 🧪 **TESTES PÓS-DEPLOY**

### **1. Verificar Homepage**

```
https://bigodetexas-dashboard.onrender.com/
```

- [ ] Página carrega
- [ ] Estatísticas aparecem
- [ ] Tema Horror Apocalypse aplicado

### **2. Testar Login Discord**

```
https://bigodetexas-dashboard.onrender.com/login
```

- [ ] Redireciona para Discord
- [ ] Callback funciona
- [ ] Retorna para dashboard

### **3. Testar Novas Páginas**

```
https://bigodetexas-dashboard.onrender.com/achievements
https://bigodetexas-dashboard.onrender.com/history
https://bigodetexas-dashboard.onrender.com/settings
```

- [ ] Achievements carrega conquistas do banco
- [ ] History carrega eventos
- [ ] Settings carrega configurações

### **4. Testar APIs**

```bash
# Achievements
curl https://bigodetexas-dashboard.onrender.com/api/achievements/all

# History
curl https://bigodetexas-dashboard.onrender.com/api/history/events

# Settings
curl https://bigodetexas-dashboard.onrender.com/api/settings/get
```

Deve retornar `401 Not authenticated` (correto!)

### **5. Verificar Logs**

No painel do Render:

- Clicar em "Logs"
- Verificar se não há erros
- Confirmar que Flask iniciou

---

## 🔧 **TROUBLESHOOTING**

### **Erro: "Application failed to start"**

**Causa:** Erro no código ou dependências

**Solução:**

1. Verificar logs no Render
2. Testar localmente: `python app.py`
3. Verificar `requirements.txt`

### **Erro: "Database connection failed"**

**Causa:** DATABASE_URL incorreto ou banco inacessível

**Solução:**

1. Verificar variável DATABASE_URL no Render
2. Testar conexão localmente
3. Verificar se IP do Render está permitido no Supabase

### **Erro: "Discord OAuth failed"**

**Causa:** Redirect URI não configurado

**Solução:**

1. Acessar Discord Developer Portal
2. Adicionar: `https://bigodetexas-dashboard.onrender.com/callback`
3. Salvar mudanças

### **Erro: "Static files not found"**

**Causa:** Caminho incorreto

**Solução:**

1. Verificar estrutura de pastas
2. Confirmar que `static/` está no root do `new_dashboard/`
3. Verificar `url_for('static', ...)` nos templates

### **Erro: "Schema not applied"**

**Causa:** Tabelas não existem no banco de produção

**Solução:**

1. Executar `apply_partial.py` apontando para DATABASE_URL de produção
2. Ou executar SQL manualmente no painel do banco

---

## 📊 **CHECKLIST FINAL**

### Pré-Deploy

- [ ] Código commitado e pushed
- [ ] Schema aplicado no banco de produção
- [ ] Variáveis de ambiente configuradas
- [ ] Discord OAuth configurado

### Deploy

- [ ] Manual Deploy executado no Render
- [ ] Build concluído sem erros
- [ ] Aplicação iniciou com sucesso

### Pós-Deploy

- [ ] Homepage carrega
- [ ] Login Discord funciona
- [ ] Achievements funciona
- [ ] History funciona
- [ ] Settings funciona
- [ ] APIs retornam respostas corretas
- [ ] Sem erros nos logs

---

## 🎉 **COMANDOS RÁPIDOS**

### Deploy Completo (Copiar e Colar)

```bash
# 1. Commit e Push
cd "d:/dayz xbox/BigodeBot"
git add -A
git commit -m "feat: Deploy novo dashboard v10.0"
git push origin main

# 2. Aplicar Schema (se ainda não fez)
python apply_partial.py

# 3. Acessar Render e fazer Manual Deploy
# https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g

# 4. Aguardar build (5-10 min)

# 5. Testar
# https://bigodetexas-dashboard.onrender.com/
```

---

## 📝 **NOTAS IMPORTANTES**

1. **Backup:** O site antigo será substituído. Se quiser manter backup, criar novo serviço.

2. **Downtime:** Haverá ~5-10 minutos de downtime durante o deploy.

3. **Rollback:** Se der problema, pode fazer rollback no Render para commit anterior.

4. **Schema:** CRÍTICO aplicar schema antes do deploy, senão APIs vão falhar.

5. **Testes:** Testar tudo localmente antes de fazer deploy.

---

## 🚀 **PRÓXIMOS PASSOS APÓS DEPLOY**

1. **Monitorar Logs** - Primeiras 24h
2. **Coletar Feedback** - Usuários testando
3. **Otimizar Performance** - Se necessário
4. **Adicionar Mais Conquistas** - Conforme uso
5. **Implementar Triggers** - Para conquistas automáticas

---

**Desenvolvido por:** Antigravity AI  
**Para:** SERV. BRASIL SUL - XBOX DayZ Community  
**Versão:** v10.0-achievements-system  
**Status:** ✅ PRONTO PARA DEPLOY!
