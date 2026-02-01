# 🏗️ PLANO DE REFATORAÇÃO: BigodeBot Modular

O arquivo `bot_main.py` atingiu o "ponto crítico" de manutenção. Com quase 4.000 linhas, qualquer pequena alteração pode causar efeitos colaterais em sistemas não relacionados.

Aqui estão as 3 melhores opções para melhorar a arquitetura:

---

## 🚀 Opção 1: Implementação de Cogs (Recomendado)

O `discord.py` possui um sistema nativo chamado **Cogs**. Ele permite agrupar comandos, eventos e lógica em classes separadas.

### Estrutura Sugerida

```text
BigodeBot/
├── bot_main.py          # Arquivo central (apenas inicialização)
├── cogs/
│   ├── economy.py       # Comandos: !saldo, !pay, !daily
│   ├── shop.py          # Comandos: !loja, !comprar
│   ├── clans.py         # Comandos: !clã, !guerra
│   ├── killfeed.py      # Lógica de parsing de logs e eventos PvP
│   ├── admin.py         # Comandos: !ban, !limpar, !restart
│   └── ai.py            # Comandos: !ia, !analisarlogs
├── utils/
│   ├── decorators.py    # @rate_limit, @require_admin
│   └── helpers.py       # load_json, format_time, etc.
└── web/
    └── server.py        # Configuração do Flask e Dashboard
```

**Vantagens:**

- Você pode recarregar um sistema (ex: Loja) sem desligar o bot (`!reload shop`).
- Código muito mais limpo e fácil de encontrar funções.
- Múltiplas pessoas podem trabalhar em arquivos diferentes sem conflitos.

---

## 🛠️ Opção 2: Refatoração do Parser de Logs (Strategy Pattern)

Atualmente, o `parse_log_line` é uma sequência enorme de `if/elif`.

**A Melhoria:**
Criar um dicionário de "Handlers". Para cada tipo de linha de log, chamamos uma função específica.

```python
LOG_HANDLERS = {
    "killed by Player": handle_kill_event,
    "is connected": handle_login_event,
    "has been disconnected": handle_logout_event,
    "placed": handle_placement_event,
}
```

Isso reduz o `parse_log_line` de 500 linhas para apenas 20 linhas de código.

---

## 🌐 Opção 3: Desacoplamento Total do Banco de Dados

Mover TODA a lógica de negócios (quem ganha bônus, como calcula XP, etc) para o `database.py`.

O `bot_main.py` deve apenas receber o comando do Discord e chamar:
`database.process_player_login(player_name)`

**Vantagem:**
Se um dia você quiser mudar de Discord para Telegram, ou criar um App Mobile, a lógica do jogo está protegida no arquivo de banco de dados, independente da interface.

---

## 📉 Comparativo de Esforço

| Opção | Complexidade | Impacto na Performance | Facilidade de Manutenção |
| :--- | :--- | :--- | :--- |
| **Cogs** | Alta | Neutro | ⭐⭐⭐⭐⭐ |
| **Handlers** | Média | Melhor (O(1)) | ⭐⭐⭐⭐ |
| **Database** | Baixa | Neutro | ⭐⭐⭐ |

---

### 🎯 Minha Recomendação

Devemos começar pela **Opção 1 (Cogs)**. É a mudança que trará mais alívio imediato para o seu desenvolvimento.

**Gostaria que eu demonstrasse como transformar o sistema de Economia em um Cog para você ver como funciona?**
