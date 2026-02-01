# 📋 PENDÊNCIAS CONSOLIDADAS - BigodeBot (Revisão 22/12/2025 v2)

**Última Atualização:** 27/12/2025
**Alteração:** Prioridade "Guerras de Clãs" removida a pedido do usuário. Foco total em refatoração e estabilidade ("Enxugar código").

---

## 🔴 ALTA PRIORIDADE (FAZER PRIMEIRO)

### 1. 🎯 Refatoração / Modularização (Cogs)

**Objetivo:** "Enxugar" o código do `bot_main.py` (3000+ linhas) sem quebrar o site.
**O que fazer:**

- Criar pasta `cogs/`.
- Mover comandos de Economia, Clãs, Admin e Logs para arquivos separados.
- Desacoplar lógica do bot da lógica do site para que o site não dependa do bot rodando.

### 2. ⚠️ Integridade de Dados Híbrida (JSON/DB)

**Status:** CRÍTICO
**Descrição:** Algumas funções salvam no JSON e depois no DB de forma isolada, gerando risco de desincronia.
**Ação:** Centralizar o salvamento de dados no DB (`database.py`) e usar o JSON apenas como backup secundário ou cache de leitura rápida.

---

## 🟡 MÉDIA PRIORIDADE

### 3. Melhorar Exception Handling

**Status:** CODE SMELL
**Problema:** Uso excessivo de `except Exception:` genérico (silencia erros reais).
**Ação:** Substituir por exceções específicas (`discord.NotFound`, `aiohttp.ClientError`).

### 4. Busca de Posição Real nos Logs

**Status:** PENDENTE
**Descrição:** Implementar regex para pegar coordenadas exatas (X, Y, Z) dos logs para o Heatmap ser preciso, em vez de depender apenas da "região".

---

## 🟢 BAIXA PRIORIDADE

### 5. Documentação

**Status:** MANUTENÇÃO
**Ação:** Adicionar docstrings explicativas nas funções principais.

---

## ✅ CONCLUÍDO RECENTEMENTE

- [x] Atualização da marca do Dashboard para "BigodeTexas".
- [x] Correção da página "/base" (Mapa iZurvive + Input Manual).
- [x] Backup completo do projeto (`BigodeBot_10.1`).
