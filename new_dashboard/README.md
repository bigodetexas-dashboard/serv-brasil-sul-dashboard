# 🧟‍♂️ SERV. BRASIL SUL - XBOX | Dashboard DayZ

## 📋 RESUMO DO PROJETO

Dashboard web completo para servidor DayZ com tema **Horror Apocalíptico**, sistema de loja, rankings, estatísticas e integração Discord OAuth.

---

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### 🎨 **Design & Interface**

- ✅ **Tema Horror Apocalíptico** - Cores sangue, ferrugem e sujeira
- ✅ **Fontes Temáticas** - Creepster (títulos), Special Elite (textos)
- ✅ **Atmosfera Gritty** - Grain/noise overlay, texturas de sujeira
- ✅ **Ícones Remix** - Substituindo emojis por ícones profissionais
- ✅ **Totalmente Responsivo** - Mobile, tablet e desktop

### 🏠 **Homepage (`/`)**

- ✅ Hero section com título dramático
- ✅ Estatísticas em tempo real (Jogadores, Kills, DZCoins)
- ✅ Cards de features com ícones
- ✅ Navegação completa

### 🛒 **Loja (`/shop`)**

- ✅ Grid de itens com 13 categorias
- ✅ Sistema de busca em tempo real
- ✅ Filtros e ordenação
- ✅ Carrinho de compras funcional
- ✅ Modal de carrinho animado
- ✅ LocalStorage para persistência
- ✅ Leitura do `items.json`

### 🏆 **Rankings (`/leaderboard`)**

- ✅ Pódio visual animado (Top 3)
- ✅ 10 rankings completos:
  - 💰 Mais Rico
  - 🔫 Mais Mata Players
  - 💀 Mais Morre
  - 📊 Melhor K/D
  - 🧟 Mais Mata Zumbis
  - 🚶 Mais Anda no Mapa
  - 🚗 Mais Anda de Veículo
  - 🔄 Mais Desloga/Reloga
  - 🏗️ Mais Constrói Bases
  - 🔓 Mais Roda Cadeado
- ✅ Troca de categorias dinâmica

### 👤 **Dashboard (`/dashboard`)**

- ✅ Perfil do usuário com avatar Discord
- ✅ Saldo de DZCoins
- ✅ Estatísticas de combate
- ✅ Estatísticas de sobrevivência
- ✅ Histórico de compras
- ✅ Sistema de conquistas

### 🛍️ **Checkout (`/checkout`)**

- ✅ Resumo do pedido
- ✅ Mapa iZurvive integrado (iframe)
- ✅ Inputs manuais para coordenadas X e Y
- ✅ Validação de coordenadas (0-16000)
- ✅ Confirmação de pedido

### ✅ **Confirmação (`/order-confirmation`)**

- ✅ Página de sucesso
- ✅ Detalhes do pedido
- ✅ Timer de 5 minutos (countdown)
- ✅ Coordenadas de entrega

### 🔐 **Autenticação**

- ✅ Discord OAuth implementado
- ✅ Login funcional
- ✅ Callback configurado
- ✅ Sessões de usuário
- ✅ Logout

---

## 🗂️ ESTRUTURA DE ARQUIVOS

```text
new_dashboard/
├── app.py                          # Aplicação Flask principal
├── discord_auth.py                 # Módulo de autenticação OAuth
├── requirements.txt                # Dependências Python
├── Procfile                        # Configuração Render
├── runtime.txt                     # Versão Python
├── DEPLOY_GUIDE.md                 # Guia de deploy
├── templates/
│   ├── index.html                  # Homepage
│   ├── shop.html                   # Loja
│   ├── leaderboard.html            # Rankings
│   ├── dashboard.html              # Perfil do usuário
│   ├── checkout.html               # Checkout
│   └── order_confirmation.html     # Confirmação
├── static/
│   ├── css/
│   │   ├── style.css               # Base (tema horror)
│   │   ├── home.css                # Homepage
│   │   ├── shop.css                # Loja
│   │   ├── leaderboard.css         # Rankings
│   │   ├── dashboard.css           # Dashboard
│   │   ├── checkout.css            # Checkout
│   │   └── confirmation.css        # Confirmação
│   ├── js/
│   │   ├── main.js                 # Homepage
│   │   ├── shop.js                 # Loja
│   │   ├── leaderboard.js          # Rankings
│   │   ├── dashboard.js            # Dashboard
│   │   ├── checkout.js             # Checkout
│   │   └── confirmation.js         # Confirmação
│   └── images/
│       └── logo_placa.png          # Logo (a ser adicionado)
```text

---

## 🎨 PALETA DE CORES (HORROR APOCALYPSE)

```css

--primary: #3a4a2a;           /* Verde Militar Escuro */
--secondary: #5a1a1a;         /* Vermelho Sangue Seco */
--accent: #7a6a3a;            /* Ferrugem/Latão Oxidado */
--blood: #4a0a0a;             /* Sangue Escuro */
--bg-card: rgba(20,16,14,0.95); /* Concreto Sujo */
--text-primary: #b8b0a8;      /* Branco Sujo/Poeira */

```text

---

## 🔧 API ENDPOINTS

### Estatísticas

- `GET /api/stats` - Estatísticas do servidor

### Loja

- `GET /api/shop/items` - Lista de itens
- `POST /api/shop/purchase` - Processar compra

### Usuário

- `GET /api/user/profile` - Perfil do usuário
- `GET /api/user/stats` - Estatísticas do usuário
- `GET /api/user/purchases` - Histórico de compras
- `GET /api/user/achievements` - Conquistas

### Rankings

- `GET /api/leaderboard?type={tipo}` - Rankings por tipo

---

## 🚀 COMO RODAR LOCALMENTE

1. **Instalar dependências:**

```bash
pip install -r requirements.txt
```text

1. **Configurar variáveis de ambiente (.env):**

```env
SECRET_KEY=sua_chave_secreta
DATABASE_URL=sua_url_postgresql
DISCORD_CLIENT_ID=seu_client_id
DISCORD_CLIENT_SECRET=seu_client_secret
DISCORD_REDIRECT_URI=http://localhost:5001/callback
```text

1. **Rodar o servidor:**

```bash
python app.py
```text

1. **Acessar:**

```text
http://localhost:5001
```text

---

## 📦 DEPLOY NO RENDER

Siga o guia completo em `DEPLOY_GUIDE.md`

### Resumo:

1. Push para GitHub
2. Criar Web Service no Render
3. Configurar Root Directory: `new_dashboard`
4. Adicionar variáveis de ambiente
5. Deploy automático

---

## 🎯 PRÓXIMOS PASSOS

### ⏳ Pendente (Quota de Imagens)

- [ ] Gerar logo da placa final (resetará em ~4h30m)
- [ ] Salvar em `static/images/logo_placa.png`

### 🔮 Melhorias Futuras

- [ ] Imagens reais dos itens da loja
- [ ] Sistema de notificações em tempo real
- [ ] Chat integrado
- [ ] Sistema de clãs
- [ ] Mapa de calor (heatmap)

---

## 📝 NOTAS IMPORTANTES

### Banco de Dados

- Tabela `players` deve ter todas as colunas de estatísticas
- Tabela `purchases` para histórico de compras
- Conexão via Supabase PostgreSQL

### Discord OAuth

- Redirect URI deve ser atualizado para produção
- Scopes: `identify`, `guilds`

### Coordenadas do Mapa

- Range válido: 0 - 16000
- Validação client-side e server-side

---

## 🎨 DESIGN INSPIRADO EM

- DayZ (jogo)
- Zombie Apocalypse WordPress Theme
- Sites de horror/sobrevivência
- Estética pós-apocalíptica realista

---

## 👥 CRÉDITOS

**Desenvolvido para:** SERV. BRASIL SUL - XBOX  
**Tema:** Horror Apocalypse (DayZ Authentic)  
**Fontes:** Creepster, Special Elite, Share Tech Mono  
**Ícones:** Remix Icon  

---

## 📞 SUPORTE

Para dúvidas ou problemas, consulte:

- `DEPLOY_GUIDE.md` - Guia de deploy
- `STATUS.md` - Status do projeto
- Documentação do Flask
- Documentação do Discord OAuth

---

**Última atualização:** 28/11/2025  
**Status:** ✅ Pronto para deploy (aguardando logo final)
