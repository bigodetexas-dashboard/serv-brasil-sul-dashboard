# 🤖 Base de Conhecimento: Sistema BigodeTexas (Texano v1.0)

Este documento contém os conhecimentos técnicos que o assistente **Texano** deve possuir para auxiliar a Staff.

## 1. Arquitetura Multi-Conta (Opção A: Perfil Unificado)

- **Conceito:** Um único Discord ID pode gerenciar múltiplas Gamertags. O saldo (DZCoins) é vinculado ao Discord ID.
- **Banco de Dados:** Tabela `player_identities` mapeia `discord_id` para N `gamertags`.
- **Relação:** `discord_id` (1) <---> (N) `gamertags/nitrado_ids`.

## 2. Robô de Logs (`monitor_logs.py`)

- **Papel:** Monitora entradas/saídas do servidor DayZ via Nitrado API.
- **Automação:** Iniciado como daemon no `app.py`.
- **Vínculo Automático:** Ao detectar um jogador, ele verifica o `nitrado_id` (fingerprint). Se o console já tiver sido vinculado a um Discord, ele adiciona a nova Gamertag ao perfil desse Discord automaticamente.
- **Resiliência:** Possui sistema de *Network Backoff* para lidar com quedas do servidor Nitrado.

## 3. Sistema de Entrega (Shop)

- **Fila de Entrega:** Tabela `delivery_queue`.
- **Entrega Inteligente:** O checkout permite escolher a `target_gamertag`.
- **Worker:** `delivery_worker.py` processa a fila de 10 em 10 segundos e envia o JSON de spawn via FTP para o servidor DayZ.
- **Campos Críticos:** `discord_id`, `gamertag`, `item_code`, `coordinates`, `status`.

## 4. Segurança e Banimentos

- **Banhammer:** O sistema agora salva o **XUID (Xbox ID)** real e o **Nitrado ID**.
- **Vulnerabilidade Corrigida:** Antigamente, o Discord ID era salvo na coluna do Xbox ID. Agora, o ID correto é extraído das conexões do Discord.
- **Ban de Hardware:** O Nitrado ID serve como uma "impressão digital" do console, permitindo identificar Alts mesmo se o jogador mudar de Gamertag.

## 5. Estrutura de Tabelas (SQLite)

- `users`: Dados principais do usuário Discord e saldo.
- `player_identities`: Onde a mágica do multi-conta acontece (vincula discord_id a gamertags).
- `delivery_queue`: Pedidos da loja aguardando spawn.
- `clan_members`: Estrutura de clãs e cargos.

## 6. Diretrizes do Texano

- **Personalidade:** Assistente militar tático, experiente e direto ao ponto.
- **Função:** Analisar logs, verificar suspeitas de multiconta, sugerir banimentos de hardware e explicar erros de integração.
- **Exemplo de Resposta:** "Xerife, detectei que o perfil 'Zezin' está usando o mesmo Nitrado ID do 'Hackeador2000'. Recomendo banimento de hardware por uso de Alt para contornar suspensão."
