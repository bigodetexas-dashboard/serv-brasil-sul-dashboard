# 📋 PENDÊNCIAS CONSOLIDADAS - BigodeBot

**Última Atualização:** 22/12/2025 23:15
**Status:** Atualizado após correção do sistema de login e conquistas.

---

## 🔴 ALTA PRIORIDADE (FAZER PRIMEIRO)

### 1. 🎯 Implementar Sistema de Guerra Entre Clãs

**Status:** PENDENTE (TODO linha ~770 de bot_main.py)
**Tempo:** 2-4 horas
**Descrição:** Sistema de guerra entre clãs não está implementado no banco de dados.
**Funcionalidades Necessárias:**

- [ ] Criar tabela `clan_wars` no PostgreSQL.
- [ ] Comando para declarar guerra (`!guerra clã`).
- [ ] Lógica de pontuação automática em kills entre clãs em guerra.
- [ ] Painel de score no dashboard.

### 2. ⚠️ Integridade de Dados Híbrida (JSON/DB)

**Status:** CRÍTICO
**Descrição:** Algumas funções salvam no JSON e depois no DB (ou vice-versa) de forma isolada.
**Exemplo:** Se o bot cair entre o save do JSON e do DB, os dados perdem sincronia.
**Ação:** Envolver operações críticas em funções que garantam a atomicidade ou priorizar o DB como "Single Source of Truth" de forma mais rigorosa.

---

## 🟡 MÉDIA PRIORIDADE

### 3. Melhorar Exception Handling (Mais de 60 ocorrências)

**Status:** CODE SMELL
**Problema:** Uso de `except Exception:` genérico.
**Ação:** Substituir por exceções específicas (`discord.NotFound`, `aiohttp.ClientError`, `json.JSONDecodeError`, etc.).

### 4. Busca de Posição Real nos Logs

**Status:** TODO (linha ~3130 de bot_main.py)
**Descrição:** Implementar a busca exata das coordenadas XYZ nos logs do servidor para o Heatmap ser 100% preciso.

### 5. Modularização do bot_main.py

**Status:** MANUTENÇÃO
**Descrição:** Arquivo com mais de 3800 linhas. Precisa ser dividido em:

- `commands/economy.py`
- `commands/clans.py`
- `systems/killfeed.py`
- `utils/helpers.py`

---

## 🟢 BAIXA PRIORIDADE (MELHORIAS FUTURAS)

### 6. Documentação (Docstrings)

**Status:** DOCUMENTAÇÃO
**Descrição:** Adicionar docstrings em todas as funções (existem mais de 40 sem documentação).

### 7. Ajustar Linhas Longas (Style guide)

**Status:** ESTILO
**Descrição:** Mais de 40 linhas ultrapassam 100 caracteres.

### 8. Implementar Testes Automatizados

**Status:** QUALIDADE
**Ação:** Criar suíte de testes unitários com `pytest` para as funções de economia e clãs.

---

## ✅ CONCLUÍDO NESTA SESSÃO (22/12/2025)

- [x] Migração de `google-generativeai` para `google-genai` (ai_integration.py).
- [x] Lógica de Bônus Diário (Daily Bonus) via Database.
- [x] Persistência de sessões ativas (`active_sessions.json`).
- [x] Cálculo de Horas Jogadas para Conquista Veterano.
- [x] Verificação de Líder de Clã para Conquista Fundador.
- [x] Correção de ordem de funções (`load_json`/`save_json`).
- [x] Limpeza de variáveis não usadas em `check_alarms`.

---

**Gerado em:** 22/12/2025 23:15
**Agente:** Antigravity
