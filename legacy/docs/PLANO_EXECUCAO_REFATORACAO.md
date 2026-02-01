# 🏗️ PLANO DE EXECUÇÃO: Migração para Cogs (Modularização)

**Status:** APROVADO PARA INÍCIO
**Objetivo:** Reduzir a complexidade do `bot_main.py` sem afetar a estabilidade do Web Dashboard.
**Metodologia:** Migração Gradual ("Piloto").

---

## 🗺️ Roteiro Passo a Passo (Para o Próximo Agente)

O usuário aprovou a refatoração com a condição estrita de **NÃO QUEBRAR O SITE**. Siga este roteiro cirúrgico:

### FASE 1: Preparação da Estrutura (Segura)

1. Criar diretório `cogs/` na raiz do projeto.
2. Criar `cogs/__init__.py` (vazio).
3. No `bot_main.py`, adicionar apenas a lógica de carregamento de extensões no `on_ready` ou `setup_hook`. **Não remova nenhum comando ainda.**

### FASE 2: Teste Piloto (Mover Admin)

1. Criar `cogs/admin.py`.
2. Copiar comandos simples de administração (`kick`, `ban`, `clear`, `restart`) do `bot_main.py` para `cogs/admin.py`.
3. Adaptar o código para usar `self.bot` em vez de `bot` e decoradores de cog (`@commands.command` -> `@commands.command()`).
4. Comentar/Remover os comandos originais no `bot_main.py` **somente após garantir que o código foi copiado**.
5. Testar se o bot inicia e carrega o Cog.

### FASE 3: Migração dos Sistemas Principais (Um por vez)

Uma vez que o Piloto (Admin) funcione, migrar os sistemas na seguinte ordem de menor risco para maior risco:

1. **Economia Básica** (`commands/economy.py`): `!saldo`, `!transferir`, `!daily`.
2. **Clãs** (`commands/clans.py`): `!clan`, `!registrar`.
3. **Logs/Killfeed** (`systems/killfeed.py`): Log de mortes (Cuidado: este é crítico).

### ⚠️ Regras de Ouro

* **Web Dashboard é Sagrado:** O `bot_main.py` continuará iniciando a thread do Flask (`dashboard_bp`). Não mexa na inicialização do Flask.
* **Backup:** Sempre verifique se o backup `BigodeBot_10.1` existe antes de deletar grandes blocos de código.
* **Teste de Regressão:** Após cada migração, valide se o site continua acessível.

---

## Estrutura de Pastas Alvo

```text
BigodeBot/
├── bot_main.py          (Magra: Apenas Loaders, Eventos Globais e Flask)
├── cogs/
│   ├── admin.py         (Done: Fase 2)
│   ├── economy.py       (Todo: Fase 3.1)
│   ├── clans.py         (Todo: Fase 3.2)
│   └── killfeed.py      (Todo: Fase 3.3)
└── ... (outros arqs)
```
