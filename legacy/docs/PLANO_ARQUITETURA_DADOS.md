# 🏗️ PLANO DE ARQUITETURA: Integridade de Dados Avançada (Repository Pattern)

**Objetivo:** Eliminar a dependência de arquivos JSON para dados transacionais (Economia/Inventário) e transformar o PostgreSQL em "Single Source of Truth", garantindo consistência total entre Bot e Site.

---

## 🧩 O Conceito: Repository Pattern

Em vez de acessar dados espalhados (`load_json` aqui, `cursor.execute` ali), criaremos uma Camada de Acesso a Dados (DAL) unificada.

### Componentes

1. **`repositories/base_repository.py`**: Classe abstrata com lógica de conexão e retries.
2. **`repositories/player_repository.py`**:
    * Métodos: `get_balance(user_id)`, `add_transaction(user_id, amount, reason)`, `get_inventory(user_id)`.
    * **Inovação:** Este repositório gerencia o Cache (memória) e a persistência no Banco de forma transparente para quem chama.

### Fluxo de Dados Proposto

1. **Leitura:**
    * O Bot pede saldo -> `PlayerRepository` verifica Cache.
    * Se não tiver no Cache -> Busca no PostgreSQL -> Salva no Cache -> Retorna.
    * *Resultado:* Resposta instantânea, zero delay.

2. **Escrita (Write-Through):**
    * O Bot adiciona dinheiro -> `PlayerRepository` atualiza Cache imediatamente.
    * `PlayerRepository` envia UPDATE para PostgreSQL.
    * *Resultado:* O Site (que lê do PostgreSQL) vê a mudança na hora.

3. **Segurança (Falha de Banco):**
    * Se o PostgreSQL cair, o Repositório armazena a transação numa fila em memória.
    * O Bot continua funcionando "offline".
    * Assim que o Banco voltar, a fila é processada (Reconciliação).

---

## 🗺️ Roteiro de Implementação (Próxima Sessão)

Este plano deve ser executado **em conjunto** com a migração para Cogs, para não reescrever código duas vezes.

1. **Criar `repositories/`**: Estrutura inicial.
2. **Migrar `database.py`**: Transformar as funções soltas atuais em métodos da classe `PlayerRepository`.
3. **Refatorar `cogs/economy.py`**: Ao migrar os comandos de economia, fazê-los usar `self.repository.metodo()` em vez de manipular JSONs.
4. **Limpeza Final**: Remover `economy.json` e `players_db.json` do fluxo de transação (mantendo apenas como backup frio).

---

**Impacto no Site (`dashboard_with_oauth.py` / `new_dashboard/app.py`):**

* **Positivo:** O site já lê do Banco. Com o Bot garantindo que tudo vai pro Banco na hora, o site ficará mais preciso.
* **Ação:** Nenhuma alteração de código necessária no site, apenas no Bot.

---
*Plano aprovado pelo usuário em 27/12/2025.*
