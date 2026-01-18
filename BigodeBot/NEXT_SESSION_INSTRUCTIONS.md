# 🚨 INSTRUÇÕES CRÍTICAS PARA A PRÓXIMA SESSÃO

**Data:** 11/01/2026
**Autor:** Antigravity (Assistant)
**Status:** Desenvolvimento Concluído / Pendências de Configuração

Este arquivo contém as instruções exatas do que **FALTA** ser feito para o sistema rodar em produção. O código está pronto e testado.

## 🛑 1. Configuração de Variáveis de Ambiente (.env)

O sistema de Login Xbox e Integração Nitrado **NÃO** funcionará até que o usuário forneça as chaves reais.

- **Arquivo Alvo:** `.env` (Na raiz do projeto)
- **Ação Necessária:** Substituir os valores placeholder.

```ini
# NITRADO (Essencial para Ban e Restart)
NITRADO_TOKEN=TOKEN_REAL_AQUI
SERVICE_ID=ID_SERVIDOR_AQUI

# MICROSOFT / XBOX (Essencial para Login e Verificação)
# Obter no Azure Portal: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
MICROSOFT_CLIENT_ID=CLIENT_ID_REAL_AQUI
MICROSOFT_CLIENT_SECRET=SECRET_REAL_AQUI
MICROSOFT_REDIRECT_URI=http://localhost:5000/callback/xbox  # Ou URL de prod
```

## 🔐 2. Definir Administradores

Atualmente, o painel `/admin` bloqueia todos exceto IDs hardcoded ou placeholders.

- **Arquivo Alvo:** `new_dashboard/app.py`
- **Linha Aprox:** ~1390 (Lista `ADMIN_IDS`)
- **Ação:** Pedir ao usuário o **Discord ID** dele e adicionar nesta lista.

```python
# new_dashboard/app.py
ADMIN_IDS = [
    123456789012345678, # <-- Substituir pelo ID do Dono
    987654321098765432  # <-- Adicionar outros Admins
]
```

## 🚀 3. Validar Deploy

O sistema é composto por **dois** processos que devem rodar simultaneamente:

1. **Bot Discord**: `python bot_main.py`
    - *Responsável por Killfeed, proteção de base automática e logs.*
2. **Dashboard Web**: `python new_dashboard/app.py`
    - *Responsável por Login, Heatmap, Painel Admin e Vínculos.*

## 🧪 4. Testes Finais (Checklist)

Se o usuário fornecer as chaves acima, execute:

1. **Vínculo Xbox**: Tente logar com uma conta Microsoft em `/login/xbox`.
2. **Banimento Real**: Use o botão "Banir" no Painel Admin (`/admin`) e verifique se o comando chegou na Nitrado (logs do bot mostrarão).

---

**⚠️ AVISO:** Não inicie novas funcionalidades (ex: Loja V2) antes de garantir que essas configurações básicas de segurança e acesso estejam resolvidas.
