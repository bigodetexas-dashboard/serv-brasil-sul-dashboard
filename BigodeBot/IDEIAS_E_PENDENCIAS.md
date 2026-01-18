# 🚀 Ideias e Pendências Futuras do BigodeBot

Este documento centraliza as ideias de melhorias, análises técnicas e pendências identificadas durante a sessão de desenvolvimento de 17/01/2026.

---

## 🛠️ Migração para PostgreSQL (Análise Técnica)

**Status Atual:** O projeto utiliza SQLite de forma fortemente acoplada (`sqlite3` driver, sintaxe específica).
**Veredito (17/01/2026):** Migração imediata **NÃO RECOMENDADA** devido ao alto risco de quebra e necessidade de refatoração estrutural.

### ⚠️ Riscos e Desafios

1. **Acoplamento de Código:** A classe `BaseRepository` e vários scripts dependem diretamente de objetos `sqlite3.Row` e conexões diretas.
2. **Sintaxe SQL:** Incompatibilidades leves em sintaxe SQL (ex: `AUTOINCREMENT` vs `SERIAL`, tratamento de datas).
3. **Infraestrutura:** Necessidade de configurar e manter um servidor PostgreSQL (Docker ou Local Service) no ambiente Windows do usuário.

### 📅 Plano de Migração (Sugerido para Futuro)

Para migrar com segurança, recomenda-se a seguinte ordem:

1. **Fase 1 (Abstração):** Refatorar `BaseRepository` para usar um padrão de interface (Adapter Pattern), isolando o código do bot da implementação específica do banco.
2. **Fase 2 (Paralelismo):** Subir um container PostgreSQL e replicar dados do SQLite para ele via script de ETL.
3. **Fase 3 (Virada):** Alterar a configuração para apontar para o Postgres apenas quando a fase de testes estiver 100%.

---

## 💡 Novas Funcionalidades (Conceitos "AAA")

Ideias para elevar o nível do dashboard e engajamento do servidor.

### 1. 🗺️ Centro de Inteligência (Heatmap Tático)

Transformar o mapa estático em uma ferramenta de inteligência de combate.

* **Conceito:** Usar coordenadas do `killfeed` para plotar "Zonas de Perigo" em tempo real.
* **Funcionalidades:**
  * Manchas vermelhas no mapa indicando onde ocorreram mortes nas últimas 1h, 6h, 24h.
  * Ícones de "Sniper Spotted" (onde ocorreram tiros de longa distância).
* **Engajamento:** Jogadores consultam o site antes de sair da base para saber onde está o PVP.

### 2. 📜 Sistema de Missões e Battle Pass

Gamificação diária para reter jogadores.

* **Conceito:** Dashboard oferece 3 contratos diários aleatórios.
* **Exemplos:**
  * *"Caçador de Cabeças":* Mate 2 jogadores acima de 500m.
  * *"Nômade":* Percorra 10km a pé.
  * *"Logística":* Venda 5 itens no Trader.
* **Recompensas:** XP para um "Passe de Batalha" do site (níveis desbloqueiam cores no chat, descontos na loja, ou kits in-game).

### 3. 📉 Mercado Negro (Economia Dinâmica)

Uma bolsa de valores para itens do DayZ.

* **Conceito:** Preços da loja flutuam automaticamente baseados na Oferta e Procura.
* **Lógica:**
  * Se muitos jogadores compram **M4A1**, o estoque virtual cai e o preço **SOBE**.
  * Se ninguém compra **SKS**, o preço **CAI** para incentivar a compra.
* **Engajamento:** Cria uma classe de jogadores "Traders" que compram na baixa e vendem na alta.

---

## 📝 Próximos Passos (Backlog Sugerido)

* [ ] **Prioridade 1:** Desenhar o layout da tela "Centro de Inteligência".
* [ ] **Prioridade 2:** Criar tabela no banco para registrar histórico de preços (para o Mercado Negro).
* [ ] **Prioridade 3:** Estudar biblioteca `SQLAlchemy` ou `Peewee` para abstração de banco de dados (preparação Postgres).
