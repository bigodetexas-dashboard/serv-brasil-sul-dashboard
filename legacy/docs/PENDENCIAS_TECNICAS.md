# 📋 LISTA DE PENDÊNCIAS TÉCNICAS (Backlog)

Este documento lista tarefas que precisam ser concluídas assim que o acesso ao banco de dados for restabelecido.

## 🔴 Prioridade Alta (Bloqueantes)

1. **Restabelecer Conexão com Banco de Dados (Supabase)**
    * **Erro atual:** `FATAL: Tenant or user not found`.
    * **Ação:** Verificar no painel da Supabase se o projeto está pausado e reativá-lo.
    * **Teste:** Executar `python try_connect.py` (ou criar um script simples de conexão) para validar.

2. **Validar Testes de API**
    * **Status:** Interrompido devido à falha do banco.
    * **Ação:** Executar `python test_apis.py`. O `app.py` já foi preparado com o modo de teste (`@app.before_request`) para facilitar isso.

3. **Concluir Lógica de Migração (`migrate_to_postgres.py`)**
    * **Status:** Lógica de `migrate_players` está incompleta/placeholder.
    * **Problema:** O arquivo `players_db.json` usa a **Gamertag** como chave, mas a tabela `users` no banco usa o **Discord ID**.
    * **Solução Necessária:** O script precisa primeiro carregar o `links.json` (que mapeia Discord ID <-> Gamertag) para saber qual Discord ID pertence a qual Gamertag antes de inserir os dados do player na tabela `users`.

## 🟡 Prioridade Média (Qualidade de Código)

4. **Refatoração de "Bare Excepts"**
    * **Status:** O linter (Ruff) apontou muitos usos de `try: ... except: pass`.
    * **Ação:** Substituir por `except Exception:` ou tratar erros específicos para evitar silenciar falhas críticas sem log.

5. **Limpeza de Código Morto**
    * **Status:** 195 avisos do linter restantes.
    * **Ação:** Remover imports não utilizados e variáveis declaradas mas não usadas em arquivos periféricos (`test_*.py`).

## 🟢 Prioridade Baixa (Melhorias)

6. **Segurança em Arquivos de Backup**
    * **Status:** A ferramenta Bandit apontou `debug=True` e senhas hardcoded em arquivos antigos na pasta `backups/`.
    * **Ação:** Considerar excluir backups muito antigos ou sanitizá-los para evitar confusão futura.

---
**Última atualização:** 14/12/2025
