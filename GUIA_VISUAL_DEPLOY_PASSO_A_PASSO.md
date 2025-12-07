# 🚀 GUIA VISUAL PASSO A PASSO - DEPLOY DO SITE CORRETO

**Para:** Próximo Assistente  
**Data:** 07/12/2025  
**Objetivo:** Colocar o site correto online (localhost:5001 → Render)

---

## 🎯 **SITE QUE DEVE ESTAR ONLINE**

### **Site Correto (Local):**

```text
URL Local: http://localhost:5001
```text

### Características:

- ✅ Achievements (Conquistas) - `/achievements`
- ✅ History (Histórico) - `/history`
- ✅ Settings (Configurações) - `/settings`
- ✅ Tema Horror Apocalypse
- ✅ APIs funcionando
- ✅ Código de 06/12 + 07/12/2025

### **Onde deve ficar online:**

```text
URL Online: https://bigodetexas-dashboard.onrender.com
OU
URL Online: https://serv-brasil-sul-dashboard.onrender.com
```text

---

## 📋 **PASSO A PASSO VISUAL**

### **PASSO 1: ACESSAR RENDER**

```text

1. Abrir navegador
2. Ir para: https://dashboard.render.com
3. Fazer login (se necessário)
4. Ver lista de serviços

```text

### O que você vai ver:

- Lista de Web Services
- Procurar: `bigodetexas-dashboard`

---

### **PASSO 2: ABRIR CONFIGURAÇÕES**

```text

1. Clicar no serviço: bigodetexas-dashboard
2. No menu lateral, clicar em: Settings
3. Rolar até encontrar: "Build & Deploy"

```text

### O que procurar:

- Seção "Build & Deploy"
- Campo "Start Command"
- Valor atual: `python bot_main.py` (ERRADO!)

---

### **PASSO 3: CORRIGIR START COMMAND**

```text

1. Clicar no campo "Start Command"
2. APAGAR o texto atual
3. DIGITAR: cd new_dashboard && gunicorn app:app
4. Clicar em "Save Changes" (Salvar)

```text

### Antes:

```bash
Start Command: python bot_main.py
```text

### Depois:

```bash
Start Command: cd new_dashboard && gunicorn app:app
```text

**IMPORTANTE:** Copie exatamente como está acima!

---

### **PASSO 4: FAZER DEPLOY**

```text

1. Voltar para a página principal do serviço
2. No canto superior direito, clicar: "Manual Deploy"
3. Selecionar: "Deploy latest commit"
4. Aguardar o build começar

```text

### O que você vai ver:

```text
==> Cloning from https://github.com/...
==> Installing dependencies...
==> Running build command...
==> Uploading build...
==> Build successful 🎉
==> Deploying...
```text

---

### **PASSO 5: ACOMPANHAR LOGS**

```text

1. Clicar na aba "Logs"
2. Acompanhar o progresso em tempo real
3. Aguardar aparecer: "Your service is live 🎉"

```text

### Logs corretos (o que você DEVE ver):

```bash
==> Running 'cd new_dashboard && gunicorn app:app'
[INFO] Starting gunicorn...
[INFO] Listening at: http://0.0.0.0:10000
==> Your service is live 🎉
```text

### Logs ERRADOS (se aparecer isso, algo está errado):

```bash
==> Running 'python bot_main.py'

* Serving Flask app 'bot_main'

```text

---

### **PASSO 6: VERIFICAR SITE ONLINE**

```text

1. Aguardar status mudar para: "Live" (verde)
2. Abrir em nova aba: https://bigodetexas-dashboard.onrender.com
3. Verificar se carrega a homepage

```text

### Teste rápido:

```text
https://bigodetexas-dashboard.onrender.com/
https://bigodetexas-dashboard.onrender.com/achievements
https://bigodetexas-dashboard.onrender.com/history
https://bigodetexas-dashboard.onrender.com/settings
```text

**Se `/achievements` carregar:** ✅ SUCESSO!
**Se `/achievements` der 404:** ❌ Algo errado, verificar logs

---

### **PASSO 7: APLICAR SCHEMA NO BANCO**

```text

1. Abrir terminal/PowerShell
2. Navegar até: cd "d:/dayz xbox/BigodeBot"
3. Executar: python apply_schema_production.py
4. Quando perguntar, digitar: sim
5. Aguardar conclusão

```text

### Comandos:

```bash
cd "d:/dayz xbox/BigodeBot"
python apply_schema_production.py
```text

### O que vai acontecer:

```text
APLICANDO SCHEMA NO BANCO DE PRODUCAO
[OK] Conectando ao banco de producao...
[OK] SQL lido (3080 caracteres)

ATENCAO: Isto vai criar tabelas no banco de PRODUCAO!

Tabelas que serao criadas:

  - activity_history
  - user_settings

Deseja continuar? (sim/nao): sim

[SUCESSO] SCHEMA APLICADO NO BANCO DE PRODUCAO!
```text

---

### **PASSO 8: TESTAR TUDO**

```text

1. Abrir site online
2. Fazer login com Discord
3. Testar cada página nova:
   - Achievements
   - History
   - Settings
1. Verificar se APIs funcionam

```text

### Checklist de testes:

- [ ] Homepage carrega
- [ ] Login Discord funciona
- [ ] `/achievements` mostra conquistas
- [ ] `/history` mostra histórico (vazio no início)
- [ ] `/settings` mostra configurações
- [ ] Sem erros 500 nos logs

---

## 🔧 **TROUBLESHOOTING**

### **Problema 1: Build Failed**

### Sintoma:

```text
==> Build failed ❌
Error: ...
```text

### Solução:

1. Ver logs completos
2. Verificar se requirements.txt existe
3. Tentar "Clear build cache & deploy"

---

### **Problema 2: Site não carrega**

### Sintoma:

- Site mostra erro 503
- Ou "Application Error"

### Solução:

1. Ver logs do Render
2. Verificar se Start Command está correto
3. Verificar variáveis de ambiente

---

### **Problema 3: Páginas novas dão 404**

### Sintoma:

- `/achievements` retorna 404
- `/history` retorna 404
- `/settings` retorna 404

### Solução:

- Schema não foi aplicado no banco
- Executar: `python apply_schema_production.py`

---

### **Problema 4: Ainda roda bot_main.py**

### Sintoma:

```bash
==> Running 'python bot_main.py'
```text

### Solução:

1. Verificar se salvou o Start Command
2. Fazer novo deploy
3. Limpar cache e tentar novamente

---

## 📊 **CHECKLIST COMPLETO**

### **Antes de começar:**

- [ ] Código está no GitHub (commit: f1d9c784)
- [ ] Servidor local funciona (localhost:5001)
- [ ] Tem acesso ao painel do Render

### **Durante o deploy:**

- [ ] Start Command corrigido
- [ ] Deploy iniciado
- [ ] Build bem-sucedido
- [ ] Logs mostram gunicorn (não bot_main.py)
- [ ] Status "Live" apareceu

### **Após o deploy:**

- [ ] Site online carrega
- [ ] Schema aplicado no banco
- [ ] Páginas novas funcionam
- [ ] Login Discord funciona
- [ ] Sem erros nos logs

---

## 🎯 **COMANDOS RÁPIDOS**

### **Aplicar Schema:**

```bash
cd "d:/dayz xbox/BigodeBot"
python apply_schema_production.py
```text

### **Verificar Banco:**

```bash
python check_database.py
```text

### **Testar APIs Localmente:**

```bash
cd "d:/dayz xbox/BigodeBot/new_dashboard"
python app.py
```text

### **Ver Logs do Git:**

```bash
git log --oneline -5
```text

---

## 📁 **ARQUIVOS IMPORTANTES**

### **Leia antes de começar:**

1. `RELATORIO_PROBLEMA_DEPLOY.md` - Diagnóstico completo
2. `RELATORIO_SESSAO_2025-12-07_FINAL.md` - O que foi feito
3. Este arquivo - Guia passo a passo

### **Scripts úteis:**

- `apply_schema_production.py` - Aplicar schema
- `check_database.py` - Verificar banco
- `test_apis.py` - Testar APIs

### **Configuração:**

- `Procfile` - Comando de start (já corrigido)
- `new_dashboard/Procfile` - Comando alternativo
- `requirements.txt` - Dependências

---

## 🎨 **COMPARAÇÃO VISUAL**

### **Site ERRADO (atual online):**

```text
URL: https://bigodetexas-dashboard.onrender.com

Páginas:
✅ / (homepage)
✅ /shop
✅ /leaderboard
✅ /dashboard
❌ /achievements (404)
❌ /history (404)
❌ /settings (404)

Logs:
==> Running 'python bot_main.py'

* Serving Flask app 'bot_main'

```text

### **Site CORRETO (deve ficar assim):**

```text
URL: https://bigodetexas-dashboard.onrender.com

Páginas:
✅ / (homepage)
✅ /shop
✅ /leaderboard
✅ /dashboard
✅ /achievements (NOVO!)
✅ /history (NOVO!)
✅ /settings (NOVO!)

Logs:
==> Running 'cd new_dashboard && gunicorn app:app'
[INFO] Starting gunicorn...
[INFO] Listening at: http://0.0.0.0:10000
```text

---

## ⏱️ **TEMPO ESTIMADO**

- **Passo 1-3:** 2 minutos (configurar)
- **Passo 4-5:** 5-10 minutos (build)
- **Passo 6:** 1 minuto (verificar)
- **Passo 7:** 2 minutos (schema)
- **Passo 8:** 3 minutos (testar)

**TOTAL:** 15-20 minutos

---

## 🎉 **RESULTADO ESPERADO**

Após seguir todos os passos:

✅ Site online em: `https://bigodetexas-dashboard.onrender.com`
✅ Mesmas funcionalidades do localhost:5001
✅ Achievements, History, Settings funcionando
✅ APIs conectadas ao banco
✅ Login Discord funcionando
✅ Sem erros nos logs

---

## 📞 **SE PRECISAR DE AJUDA**

### **Documentos de referência:**

- `RELATORIO_PROBLEMA_DEPLOY.md` - Diagnóstico
- `GUIA_DEPLOY_NOVO_DASHBOARD.md` - Guia completo
- `IMPLEMENTACAO_COMPLETA_2025-12-07.md` - Detalhes técnicos

### **Comandos de diagnóstico:**

```bash

# Ver status do Git

git status

# Ver últimos commits

git log --oneline -5

# Verificar banco

python check_database.py

# Testar APIs

python test_apis.py
```text

---

## 🔑 **INFORMAÇÕES IMPORTANTES**

### **Repositório GitHub:**

```text
URL: https://github.com/bigodetexas-dashboard/bigodetexas-dashboard
Branch: main
Último commit: f1d9c784
```text

### **Serviço Render:**

```text
Nome: bigodetexas-dashboard
URL: https://bigodetexas-dashboard.onrender.com
Start Command CORRETO: cd new_dashboard && gunicorn app:app
```text

### **Banco de Dados:**

```env
Variável: DATABASE_URL (no Render)
Tabelas novas: activity_history, user_settings
Script: apply_schema_production.py
```text

---

## ✅ **CONFIRMAÇÃO FINAL**

Antes de considerar concluído, verificar:

1. ✅ Site online carrega sem erros
2. ✅ URL `/achievements` funciona
3. ✅ URL `/history` funciona
4. ✅ URL `/settings` funciona
5. ✅ Login Discord funciona
6. ✅ Logs não mostram erros
7. ✅ Schema aplicado no banco
8. ✅ Testes básicos passam

### Se todos os itens acima estiverem ✅, o deploy está COMPLETO!

---

**Desenvolvido por:** Antigravity AI  
**Para:** SERV. BRASIL SUL - XBOX DayZ Community  
**Data:** 07/12/2025 11:12  
**Status:** 📋 Guia Completo - Pronto para Uso
