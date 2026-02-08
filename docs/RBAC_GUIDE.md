# Guia do RBAC - Sistema de Controle de Acesso

## O que é RBAC?

RBAC (Role-Based Access Control) é um sistema que controla quem pode acessar quais recursos baseado em **roles** (funções/papéis).

## Roles Disponíveis

```python
class UserRole:
    ADMIN = "admin"        # Acesso total ao sistema
    MODERATOR = "moderator"  # Pode moderar mas não alterar config
    USER = "user"          # Usuário comum
    BANNED = "banned"      # Usuário banido (sem acesso)
```

## Como Usar

### 1. Proteger uma Rota (Decorator)

```python
from new_dashboard.app import require_role, UserRole

@app.route("/admin/painel")
@require_role(UserRole.ADMIN)  # Apenas admins
def painel_admin():
    return "Bem-vindo, admin!"

@app.route("/moderar")
@require_role(UserRole.ADMIN, UserRole.MODERATOR)  # Admins OU moderators
def moderar():
    return "Área de moderação"
```

### 2. Verificar Role Manualmente

```python
from new_dashboard.app import get_user_role, UserRole

def minha_funcao():
    user_id = session.get("discord_user_id")
    role = get_user_role(user_id)

    if role == UserRole.ADMIN:
        # Fazer algo especial para admins
        pass
    elif role == UserRole.MODERATOR:
        # Algo para moderators
        pass
```

## Como Funciona a Verificação?

O sistema verifica roles nesta ordem de prioridade:

1. **Dev Bypass** - `FLASK_ENV=development` + user_id = "test_user_123"
2. **Master Admin Email** - Email `5.wellyton@gmail.com` na sessão
3. **ADMIN_DISCORD_IDS** - IDs listados no `.env`
4. **Banco de Dados** - Coluna `role` na tabela `users`
5. **Padrão** - Retorna `UserRole.USER` se nada se aplicar

## Configuração

### Adicionar Admin via .env

Edite o arquivo `.env`:

```bash
ADMIN_DISCORD_IDS=322846467389259776,987654321123456,111222333444555
```

*Separe múltiplos IDs com vírgula*

### Adicionar Moderador via Banco

```sql
UPDATE users
SET role = 'moderator'
WHERE discord_id = '123456789';
```

### Banir Usuário

```sql
UPDATE users
SET role = 'banned'
WHERE discord_id = '999888777';
```

OU use a coluna `is_banned`:

```sql
UPDATE users
SET is_banned = 1
WHERE discord_id = '999888777';
```

## Respostas de Erro

Quando um usuário tenta acessar algo sem permissão:

```json
{
  "error": "Access denied: Insufficient permissions"
}
```
**Status:** `403 Forbidden`

Para usuários banidos:

```json
{
  "error": "Access denied: User is banned"
}
```
**Status:** `403 Forbidden`

## Exemplos Práticos

### Upload de Imagem (Admin/Moderator)

```python
@app.route("/api/shop/upload", methods=["POST"])
@require_role(UserRole.ADMIN, UserRole.MODERATOR)
def api_shop_upload_image():
    """Apenas admins e moderadores podem fazer upload"""
    # ... código de upload
```

### Ban de Usuário (Apenas Admin)

```python
@app.route("/api/admin/ban", methods=["POST"])
@require_role(UserRole.ADMIN)
def ban_user():
    """Apenas admins podem banir"""
    # ... código de ban
```

### Ver Estatísticas (Todos)

```python
@app.route("/api/stats")
def public_stats():
    """Sem decorator = todos podem acessar"""
    # Não precisa de RBAC
```

## Debugging

Para ver qual role um usuário tem:

```python
user_id = session.get("discord_user_id")
role = get_user_role(user_id)
print(f"Usuario {user_id} tem role: {role}")
```

## Segurança

✅ **Boas Práticas:**
- Sempre use `@require_role()` em rotas administrativas
- Nunca confie apenas em verificações client-side
- Mantenha `ADMIN_DISCORD_IDS` atualizado
- Use `MODERATOR` para delegar tarefas sem dar acesso total

❌ **Evite:**
- Comentar decorators de segurança "temporariamente"
- Hardcodar IDs de admin no código
- Dar role `ADMIN` para moderação simples

## Troubleshooting

**Problema:** "Não consigo acessar painel admin"

1. Verifique se seu Discord ID está em `ADMIN_DISCORD_IDS`
2. Confirme que fez login via Discord OAuth
3. Verifique se `session["discord_user_id"]` está definido
4. Em dev, use `/dev_login` para testar

**Problema:** "Decorator não está funcionando"

- Certifique-se que importou corretamente:
  ```python
  from new_dashboard.app import require_role, UserRole
  ```
- Verifique que o decorator está ANTES da função:
  ```python
  @app.route("/rota")
  @require_role(UserRole.ADMIN)  # <- Decorator aqui
  def minha_rota():
      pass
  ```

---

*Última atualização: 2026-02-07*
