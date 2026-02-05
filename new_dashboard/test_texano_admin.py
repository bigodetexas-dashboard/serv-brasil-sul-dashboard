"""
Script de teste para verificar se a IA Texano estÃ¡ funcionando corretamente
"""

import sys
import os

# Adicionar o diretÃ³rio pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("TESTE DA IA TEXANO - PAINEL ADMIN")
print("=" * 60)

# Teste 1: Importar mÃ³dulos
print("\n[1/4] Testando importaÃ§Ãµes...")
try:
    from admin_routes import get_system_diagnostics, admin_bp

    print("    OK - admin_routes importado")
except Exception as e:
    print(f"    ERRO - admin_routes: {e}")
    sys.exit(1)

try:
    from ai_integration import ask_ai_admin_sync

    print("    OK - ai_integration importado")
except Exception as e:
    print(f"    ERRO - ai_integration: {e}")
    sys.exit(1)

# Teste 2: Verificar diagnÃ³stico do sistema
print("\n[2/4] Testando coleta de diagnÃ³stico...")
try:
    diagnostics = get_system_diagnostics()
    print(f"    OK - Status: {diagnostics.get('status')}")
    print(f"    OK - DB Status: {diagnostics.get('db_status')}")
    print(f"    OK - Alertas: {len(diagnostics.get('alerts', []))}")
except Exception as e:
    print(f"    ERRO - get_system_diagnostics: {e}")

# Teste 3: Verificar API Keys
print("\n[3/4] Verificando API Keys...")
import os
from dotenv import load_dotenv

env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
load_dotenv(env_path)

GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GROQ_KEY:
    print(f"    OK - GROQ_API_KEY: {GROQ_KEY[:20]}...")
else:
    print("    AVISO - GROQ_API_KEY nÃ£o encontrada")

if GEMINI_KEY:
    print(f"    OK - GEMINI_API_KEY: {GEMINI_KEY[:20]}...")
else:
    print("    AVISO - GEMINI_API_KEY nÃ£o encontrada")

# Teste 4: Testar IA Texano
print("\n[4/4] Testando resposta da IA Texano...")
try:
    diagnostics = get_system_diagnostics()
    context_str = f"""
    [SYSTEM TELEMETRY]
    - Status DB: {diagnostics.get("db_status")}
    - Usuarios Registrados: {diagnostics.get("db_users")}
    - Nivel de Seguranca: {diagnostics.get("security_level")}
    - Entregas Pendentes: {diagnostics.get("pending_deliveries", 0)}
    - Alertas Ativos: {", ".join(diagnostics.get("alerts", []))}
    """

    prompt = "Status do sistema?"
    print(f"    Enviando prompt: '{prompt}'")

    response = ask_ai_admin_sync(prompt, context_str)

    print(f"\n    RESPOSTA DO TEXANO:")
    print(f"    {'-' * 56}")
    print(f"    {response}")
    print(f"    {'-' * 56}")
    print("\n    OK - IA Texano respondeu com sucesso!")

except Exception as e:
    print(f"    ERRO - ask_ai_admin_sync: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTE CONCLUIDO")
print("=" * 60)
