# 📋 TAREFAS PENDENTES - PRÓXIMA SESSÃO

## ✅ O QUE JÁ ESTÁ PRONTO (NESTA SESSÃO)

1. ✅ Banco de dados completo (8 tabelas SQL)
2. ✅ Página BASE com mapa interativo
3. ✅ Página CLAN para criar clãs
4. ✅ Página BANCO SUL com design terminal
5. ✅ APIs backend funcionais
6. ✅ Sistema de backup automático
7. ✅ Documentação completa

---

## 🔴 TAREFAS PRIORITÁRIAS (PRÓXIMA SESSÃO)

### 1. ATUALIZAR MENUS DE NAVEGAÇÃO

**Tempo estimado**: 15 minutos

Adicionar links para BASE, CLAN e BANCO em TODAS as páginas:

- [ ] `index.html`
- [ ] `shop.html`
- [ ] `leaderboard.html`
- [ ] `heatmap.html`
- [ ] `dashboard.html`
- [ ] `agradecimentos.html`

**Código para adicionar após o link do Heatmap**:

```html
<li><a href="/base" class="navbar-link"><i class="ri-map-pin-line"></i> Base</a></li>
<li><a href="/clan" class="navbar-link"><i class="ri-team-line"></i> Clã</a></li>
<li><a href="/banco" class="navbar-link"><i class="ri-bank-line"></i> Banco Sul</a></li>
```

---

### 2. APLICAR SCHEMA SQL NO BANCO

**Tempo estimado**: 10 minutos

```bash
# Conectar ao Supabase e executar:
psql -h [host] -U postgres -d postgres -f database_schema.sql

# Ou copiar o conteúdo de database_schema.sql e executar no Supabase Dashboard
```

---

### 3. PÁGINA DE VINCULAÇÃO NITRADO

**Tempo estimado**: 30 minutos

Criar `nitrado_config.html`:

- [ ] Campo para inserir Gamertag do Xbox
- [ ] Botão "Verificar nos logs"
- [ ] API `/api/nitrado/verify` que busca nos logs FTP
- [ ] Salvar `nitrado_gamertag` no banco
- [ ] Marcar como verificado

---

### 4. MELHORAR PÁGINA CLAN

**Tempo estimado**: 45 minutos

Adicionar funcionalidades:

- [ ] Listar membros do clã
- [ ] Adicionar membro (por Discord ID)
- [ ] Remover membro (só líder)
- [ ] Promover a moderador
- [ ] Visualizar estatísticas do clã
- [ ] API `/api/clan/add_member`
- [ ] API `/api/clan/remove_member`
- [ ] API `/api/clan/members`

---

### 5. COMPLETAR EXTRATO BANCÁRIO

**Tempo estimado**: 30 minutos

Na página BANCO SUL:

- [ ] API `/api/banco/transactions`
- [ ] Carregar últimas 20 transações
- [ ] Formatar com estilo imersivo:

  ```
  [12:44] Depósito automático pela missão "Caçador" ... +$250
  [09:21] Transferência enviada a "Texas Brasil" ... -$500
  ```

- [ ] Filtro por data (opcional)

---

### 6. VISUALIZAR BASE REGISTRADA

**Tempo estimado**: 20 minutos

Na página BASE:

- [ ] Verificar se usuário já tem base
- [ ] Se sim: mostrar base no mapa
- [ ] Mostrar coordenadas
- [ ] Mostrar nome
- [ ] Botão "Editar nome" (opcional)
- [ ] Listar membros do clã com acesso

---

### 7. ESTATÍSTICAS SEMANAIS (OPCIONAL)

**Tempo estimado**: 1 hora

Na página principal:

- [ ] Criar seção "Raid Semanal"
- [ ] Mostrar clã com mais kills
- [ ] Mostrar último raid
- [ ] Clã mais rico
- [ ] API `/api/weekly/stats`
- [ ] Sistema de reset semanal (cron job)

---

## 🟡 TAREFAS SECUNDÁRIAS

### 8. PERMISSÕES DE BASE

- [ ] Lógica de verificação de zona
- [ ] Logs de construção
- [ ] Alertas de invasão

### 9. SÍMBOLOS DE CLÃS

- [ ] Biblioteca de ícones
- [ ] Preview do símbolo
- [ ] Geração de imagem

### 10. MELHORIAS VISUAIS

- [ ] Animações
- [ ] Gráficos
- [ ] Responsividade mobile

---

## 📝 ORDEM RECOMENDADA DE EXECUÇÃO

1. **Atualizar menus** (15 min) - Rápido e importante
2. **Aplicar SQL** (10 min) - Necessário para tudo funcionar
3. **Testar páginas** (15 min) - Validar o que já existe
4. **Vinculação Nitrado** (30 min) - Crítico para o sistema
5. **Melhorar CLAN** (45 min) - Funcionalidade core
6. **Extrato bancário** (30 min) - Completar BANCO
7. **Visualizar base** (20 min) - Melhorar UX

**Total estimado**: ~2h45min

---

## 🚀 COMANDOS ÚTEIS

```bash
# Backup antes de começar
python auto_backup.py create "Inicio da proxima sessao"

# Iniciar servidor
cd new_dashboard
python app.py

# Testar páginas
http://localhost:5001/base
http://localhost:5001/clan
http://localhost:5001/banco

# Backup ao finalizar
python auto_backup.py create "Fim da sessao - [descricao]"

# Commit Git
git add -A
git commit -m "feat: [descricao das mudancas]"
```

---

## 📊 PROGRESSO ATUAL

- **Implementado**: 60%
- **Testado**: 20%
- **Documentado**: 90%
- **Pronto para produção**: 40%

---

**Próxima sessão deve focar em**: Completar funcionalidades e testar tudo!

**Desenvolvido por**: Claude (Antigravity AI)  
**Data**: 2025-12-04  
**Versão**: v1.0-base-clan-banco
