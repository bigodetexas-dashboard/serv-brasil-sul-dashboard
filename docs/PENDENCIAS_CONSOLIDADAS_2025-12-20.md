# 📋 PENDÊNCIAS CONSOLIDADAS - BigodeBot

**Última Atualização:** 2025-12-20 19:35
**Status:** Atualizado com análise completa do código

---

## 🔴 ALTA PRIORIDADE (FAZER PRIMEIRO)

### 1. ✅ Configurar Interpretador Python no VS Code

**Status:** PENDENTE
**Tempo:** 2 minutos
**Arquivo:** Configuração do VS Code
**Descrição:** IDE mostra 5-7 erros de import (falsos positivos)
**Solução:** `Ctrl+Shift+P` → `Python: Select Interpreter` → Escolher Python 3.12.3
**Guia:** Ver `COMO_RESOLVER_ERROS_IMPORT.md`

### 2. 🎯 Implementar Sistema de Guerra Entre Clãs

**Status:** TODO (linha 767 de bot_main.py)
**Tempo:** 2-4 horas
**Arquivo:** `bot_main.py`
**Descrição:** Sistema de guerra entre clãs não está implementado
**Impacto:** Feature importante para gameplay e engajamento

**Funcionalidades Necessárias:**

- [ ] Declarar guerra entre clãs
- [ ] Sistema de pontuação de guerra
- [ ] Histórico de guerras
- [ ] Recompensas para vencedores
- [ ] Tabela no banco de dados

### 3. ⚠️ Migrar para google.genai

**Status:** DEPRECAÇÃO ATIVA
**Tempo:** 30 minutos
**Arquivo:** `ai_integration.py`, `requirements.txt`
**Descrição:** `google.generativeai` está deprecado e será descontinuado
**Urgência:** Médio prazo (ainda funciona, mas deve ser migrado)

**Passos:**

```bash
# 1. Desinstalar antiga
pip uninstall google-generativeai

# 2. Instalar nova
pip install google-genai

# 3. Atualizar requirements.txt
# google-generativeai → google-genai

# 4. Atualizar ai_integration.py
# import google.generativeai → import google.genai
```

---

## 🟡 MÉDIA PRIORIDADE

### 4. Implementar TODOs Pendentes

#### TODO #1: Calcular Horas Jogadas (linha 696)

**Arquivo:** `bot_main.py`
**Função:** `check_achievements()`
**Código Atual:**

```python
"hours_played": 0,  # TODO: calcular do players_db
```

**Impacto:** Conquista "Veterano" não funciona
**Solução:** Calcular tempo total de jogo do players_db

#### TODO #2: Verificar Líder de Clã (linha 697)

**Arquivo:** `bot_main.py`
**Função:** `check_achievements()`
**Código Atual:**

```python
"clan_created": False,  # TODO: verificar se é líder de clã
```

**Impacto:** Conquista "Fundador de Clã" não funciona
**Solução:** Verificar se user é líder em algum clã

#### TODO #3: Busca de Posição Real nos Logs (linha 3128)

**Arquivo:** `bot_main.py`
**Descrição:** Posições no mapa podem não ser precisas
**Solução:** Implementar parser de logs para extrair coordenadas reais

### 5. Melhorar Exception Handling (70+ ocorrências)

**Status:** CODE SMELL
**Tempo:** 4-6 horas
**Impacto:** Melhor debugging e manutenção

**Problema:** Uso excessivo de `except Exception:` genérico

**Exemplo de Melhoria:**

```python
# ❌ Evitar
try:
    await msg.delete()
except Exception:
    pass

# ✅ Preferir
try:
    await msg.delete()
except discord.errors.NotFound:
    pass  # Mensagem já foi deletada
except discord.errors.Forbidden:
    logger.warning("Sem permissão para deletar mensagem")
```

**Principais Localizações:**

- bot_main.py: linhas 138, 150, 183, 322, 426, 434, 466, 500, 536, 614, 683, 741, 794, 859, 873, 879, 897, 910, 1100, 1121, 1175, 1245, 1272, 1376, 1403, 1445, 1494, 1516, 1540, 1629, 1640, 1759, 1764, 1998, 2002, 2009, 2514, 2593, 3039, 3370, 3374, 3630, 3809, 3832

### 6. Limpar Variáveis Não Utilizadas (8)

**Status:** CODE CLEANUP
**Tempo:** 30 minutos

| Linha | Arquivo | Variável | Ação |
|-------|---------|----------|------|
| 927 | bot_main.py | `item_name` | Remover parâmetro ou usar |
| 2024 | bot_main.py | `k` | Substituir por `_` |
| 2045 | bot_main.py | `i` | Substituir por `_` |
| 2579 | bot_main.py | `found_alarm` | Remover ou usar |
| 2655 | bot_main.py | `timestamp`, `x`, `z` | Remover parâmetros ou usar |
| 3302 | bot_main.py | `event_name` | Remover |
| 3717 | bot_main.py | `wid` | Remover |

### 7. Adicionar Encoding em Opens

**Status:** BUG POTENCIAL (Windows)
**Tempo:** 15 minutos
**Localização:** bot_main.py linha 1990

**Problema:**

```python
with open(filename) as f:  # ❌ Sem encoding
```

**Solução:**

```python
with open(filename, encoding='utf-8') as f:  # ✅ Com encoding
```

### 8. Renomear Variável `set`

**Status:** REDEFINE BUILT-IN
**Tempo:** 5 minutos
**Localização:** bot_main.py linha 2695

**Problema:**

```python
set = some_value  # ❌ Redefine built-in
```

**Solução:**

```python
param_set = some_value  # ✅ Nome específico
```

---

## 🟢 BAIXA PRIORIDADE (MELHORIAS FUTURAS)

### 9. Refatorar bot_main.py em Módulos

**Status:** MANUTENÇÃO DE LONGO PRAZO
**Tempo:** 8-12 horas
**Problema:** Arquivo muito grande (3836 linhas vs recomendado 1000)

**Estrutura Proposta:**

```
bot_main.py (core - 500 linhas)
├── commands/
│   ├── __init__.py
│   ├── economy.py      # Comandos de economia
│   ├── shop.py         # Comandos de loja
│   ├── clans.py        # Comandos de clãs
│   ├── admin.py        # Comandos administrativos
│   └── ai.py           # Comandos de IA
├── systems/
│   ├── __init__.py
│   ├── achievements.py # Sistema de conquistas
│   ├── killfeed.py     # Sistema de killfeed
│   └── stats.py        # Sistema de estatísticas
└── utils/
    ├── __init__.py
    ├── decorators.py   # Decoradores (rate_limit, admin)
    └── helpers.py      # Funções auxiliares
```

**Benefícios:**

- Mais fácil de navegar
- Mais fácil de testar
- Mais fácil de manter
- Melhor organização

### 10. Adicionar Docstrings

**Status:** DOCUMENTAÇÃO
**Tempo:** 3-4 horas
**Impacto:** Melhor compreensão do código

**Funções sem docstring:** 30+

**Exemplo:**

```python
# ❌ Sem docstring
def get_balance(user_id):
    eco = database.get_economy(user_id)
    return eco.get("balance", 0) if eco else 0

# ✅ Com docstring
def get_balance(user_id):
    """
    Retorna o saldo de DZ Coins de um usuário.

    Args:
        user_id (str): ID do Discord do usuário

    Returns:
        int: Saldo em DZ Coins, 0 se usuário não existir
    """
    eco = database.get_economy(user_id)
    return eco.get("balance", 0) if eco else 0
```

### 11. Ajustar Linhas Longas (40+ ocorrências)

**Status:** ESTILO
**Tempo:** 1-2 horas
**Problema:** Linhas com mais de 100 caracteres

**Principais localizações:**

- Linhas 104, 379, 455, 1094, 1110, 1142, 1166, 1218, 1225, 1295, 1310, 1321, 1330, 1343, 1361, 1370, 1399, 1442, 1472, 1482, 1708, 1735, 1837, 1932, 1951, 1962, 1966, 1986, 2060, 2447, 2490, 2717, 2735, 2754, 3132, 3670, 3741, 3779

### 12. Criar Testes Automatizados

**Status:** QUALIDADE
**Tempo:** 8-16 horas

**Tipos de Teste:**

- [ ] Testes unitários (funções individuais)
- [ ] Testes de integração (banco de dados)
- [ ] Testes E2E (comandos do bot)
- [ ] Testes de performance

**Framework Recomendado:** pytest

---

## 📱 PENDÊNCIAS DO DASHBOARD (new_dashboard/)

### Alta Prioridade

#### 1. Página de Configurações (Settings)

**Status:** Template criado, conteúdo incompleto
**Arquivo:** `new_dashboard/templates/settings.html`

**Funcionalidades Necessárias:**

- [ ] Preferências de notificação
- [ ] Configurações de privacidade
- [ ] Preferências de idioma
- [ ] Tema (claro/escuro)
- [ ] Configurações de som
- [ ] Backend para salvar preferências

#### 2. Sistema de Conquistas (Achievements)

**Status:** Interface criada, dados mockados

**Pendências:**

- [ ] Conectar com banco de dados real
- [ ] Implementar lógica de desbloqueio
- [ ] Sistema de notificação de conquistas
- [ ] Adicionar mais conquistas

#### 3. Histórico de Atividades (History)

**Status:** Interface criada, dados mockados

**Pendências:**

- [ ] Conectar com banco de dados real
- [ ] Sistema de logging de atividades
- [ ] Filtros por tipo de atividade
- [ ] Paginação
- [ ] Exportação (CSV/PDF)

### Média Prioridade

#### 4. Sistema de Clãs

- [ ] Sistema de convites
- [ ] Chat interno do clã
- [ ] Sistema de ranks
- [ ] Estatísticas detalhadas
- [ ] Guerra entre clãs
- [ ] Território no mapa

#### 5. Sistema de Bases

- [ ] Melhorar visualização no mapa
- [ ] Adicionar fotos das bases
- [ ] Sistema de defesa
- [ ] Inventário da base
- [ ] Histórico de ataques/defesas
- [ ] Sistema de permissões

#### 6. Banco Sul

- [ ] Sistema de juros
- [ ] Histórico de transações
- [ ] Sistema de empréstimos
- [ ] Investimentos (renda passiva)
- [ ] Transferências entre jogadores
- [ ] Limites de saque/depósito

---

## 🔧 PENDÊNCIAS TÉCNICAS

### Segurança

- [ ] Implementar rate limiting completo
- [ ] Validação de inputs no backend
- [ ] Proteção contra SQL injection (usar prepared statements)
- [ ] Proteção contra XSS
- [ ] HTTPS obrigatório em produção
- [ ] Sistema de logs de segurança

### Performance

- [ ] Implementar cache no backend
- [ ] Otimizar queries do banco de dados
- [ ] Lazy loading de imagens
- [ ] Minificação de CSS/JS
- [ ] CDN para assets estáticos

### Testes

- [ ] Testes unitários (backend)
- [ ] Testes de integração
- [ ] Testes E2E (frontend)
- [ ] Testes de performance
- [ ] Testes de segurança

---

## 📊 RESUMO POR PRIORIDADE

### 🔴 Alta Prioridade (3 itens)

1. Configurar interpretador Python no VS Code (2 min)
2. Implementar Sistema de Guerra (2-4h)
3. Migrar para google.genai (30 min)

**Tempo Total:** ~3-5 horas

### 🟡 Média Prioridade (5 itens)

4. Implementar TODOs pendentes (2-3h)
5. Melhorar exception handling (4-6h)
6. Limpar variáveis não utilizadas (30 min)
7. Adicionar encoding em opens (15 min)
8. Renomear variável `set` (5 min)

**Tempo Total:** ~7-10 horas

### 🟢 Baixa Prioridade (3 itens)

9. Refatorar bot_main.py (8-12h)
10. Adicionar docstrings (3-4h)
11. Ajustar linhas longas (1-2h)

**Tempo Total:** ~12-18 horas

---

## 🎯 PLANO DE AÇÃO SUGERIDO

### Semana 1 (Alta Prioridade)

- [ ] Dia 1: Configurar IDE + Migrar google.genai
- [ ] Dia 2-3: Implementar Sistema de Guerra
- [ ] Dia 4: Testar e documentar

### Semana 2 (Média Prioridade)

- [ ] Dia 1: Implementar TODOs pendentes
- [ ] Dia 2-3: Melhorar exception handling (top 20)
- [ ] Dia 4: Cleanup (variáveis, encoding, renomear)

### Semana 3 (Dashboard)

- [ ] Dia 1-2: Sistema de Conquistas
- [ ] Dia 3-4: Histórico de Atividades

### Semana 4 (Refatoração)

- [ ] Dia 1-3: Refatorar bot_main.py
- [ ] Dia 4: Adicionar docstrings

---

## 📝 NOTAS FINAIS

### ✅ Já Resolvido Hoje

- ✅ Requirements.txt completo
- ✅ migrate_to_postgres.py sem warnings
- ✅ Documentação abrangente criada

### ⚠️ Atenção Especial

- Sistema de Guerra é a feature mais solicitada
- Migração do google.genai deve ser feita em breve
- Erros do IDE são falsos positivos (não afetar produção)

### 💡 Dicas

- Focar em features antes de refatoração
- Testar cada mudança antes de commit
- Manter backups antes de grandes mudanças
- Documentar decisões importantes

---

**Última Revisão:** 2025-12-20 19:35
**Próxima Revisão:** Após implementar Sistema de Guerra
**Responsável:** Equipe de Desenvolvimento BigodeBot
