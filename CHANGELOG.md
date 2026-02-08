# Changelog - BigodeTexas Bot

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.3.0] - 2026-02-07

### 🎉 Adicionado
- **War System (Sistema de Guerra entre Clãs)**
  - Tabela `clan_wars` para rastrear guerras ativas
  - Atualização automática de placar quando clãs em guerra se matam
  - Módulo `war_system.py` com funções dedicadas
  - Testes automatizados em `tests/test_war_system.py`

- **Anti-Cheat System (Detecção de Alts/Banidos)**
  - Verificação automática de gamertag banido no login
  - Detecção de IPs em lista de banidos
  - Identificação de contas alternativas (mesmo IP)
  - Alertas em tempo real no console
  - Testes automatizados em `tests/test_anti_cheat.py`

- **RBAC (Role-Based Access Control)**
  - Classe `UserRole` (admin, moderator, user, banned)
  - Decorator `@require_role()` para proteção de rotas
  - Função `get_user_role()` com verificação multi-camada
  - Aplicado em rotas administrativas

- **Sincronização Avançada de Economia**
  - Implementação de sync 'all' com merge PostgreSQL + SQLite
  - Retorna dados completos de todos os usuários
  - Resolve inconsistências entre bancos

### 🐛 Corrigido
- **Favicon 404** - Adicionado favicon.ico ao site
- **Encoding UTF-8** - Logs agora exibem caracteres especiais corretamente no Windows
- **Debug Mode** - Configuração segura apenas para desenvolvimento
  - Avisos de segurança quando debug está ativo com acesso externo
  - `allow_unsafe_werkzeug` apenas em modo debug
- **Rota /deaths duplicada** - Removida duplicação
- **Encoding crash** - Corrigido conflito com StdoutInterceptor

### 📚 Documentação
- Criado `FUTURE_ENHANCEMENTS.md` para melhorias planejadas
- Criado `CHANGELOG.md` (este arquivo)
- Documentadas colunas futuras do leaderboard
- Script de migração preparado em `migrations/add_leaderboard_columns.py`

### 🧪 Testes
- Suite de testes para War System
- Suite de testes para Anti-Cheat
- Cobertura de casos de sucesso e falha

### 🔒 Segurança
- RBAC completo implementado
- WAF mantido e reforçado
- Rate limiting ajustado
- Detecção proativa de contas suspeitas

### ⚡ Performance
- Otimização de queries de sincronização
- Cache de roles de usuários
- Conexões diretas ao SQLite quando apropriado

---

## [2.2.0] - 2026-02-06

### Adicionado
- WebSocket real-time para dashboard
- Sistema de notificações ao vivo
- Integração com IA (Groq + Gemini)

### Melhorado
- Dashboard redesenhado (Gold Elite theme)
- Performance de queries do banco
- Sistema de achievements

---

## [2.1.0] - 2026-01-15

### Adicionado
- Sistema de clãs v2
- Proteção de bases
- Sistema de shop com delivery

---

## [2.0.0] - 2025-12-01

### Adicionado
- Dashboard web completo
- OAuth Discord
- Sistema de economia
- Killfeed automático

---

*Formato baseado em [Keep a Changelog](https://keepachangelog.com/)*
