# -*- coding: utf-8 -*-
"""
Script de teste de Fallback para o Bigodudo
Simula falha no Groq para validar o Gemini
"""

import sys
import os
import asyncio

# Corrigir encoding no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Adicionar caminhos
sys.path.insert(0, r"d:\dayz xbox\BigodeBot\new_dashboard")
os.chdir(r"d:\dayz xbox\BigodeBot\new_dashboard")

import ai_integration
from dotenv import load_dotenv

# Carregar .env original
load_dotenv(r"d:\dayz xbox\BigodeBot\.env")


async def test_fallback():
    print("=" * 70)
    print("TESTE DE FALLBACK: GROQ -> GEMINI")
    print("=" * 70)

    # 1. Teste com Groq (deve funcionar)
    print("\n[FASE 1] Testando motor primÃ¡rio (Groq)...")
    try:
        resp1 = await ai_integration.ask_ai_hybrid(
            "Oi Bigodudo, teste do Groq.", "test_user"
        )
        print(f"âœ… Groq OK: {resp1[:50]}...")
    except Exception as e:
        print(f"âŒ Erro inesperado no Groq: {e}")

    # 2. Simular falha no Groq (limpando a chave na memÃ³ria do mÃ³dulo)
    print("\n[FASE 2] Simulando falha no Groq...")
    original_key = ai_integration.GROQ_API_KEY
    ai_integration.GROQ_API_KEY = "chave_invalida_teste"

    try:
        print("Enviando pergunta (esperando fallback para Gemini)...")
        resp2 = await ai_integration.ask_ai_hybrid(
            "Oi Bigodudo, teste do Gemini.", "test_user"
        )
        print(f"âœ… Fallback OK (Gemini respondeu): {resp2[:50]}...")
    except Exception as e:
        print(f"âŒ Falha no Fallback: {e}")
    finally:
        # Restaurar a chave
        ai_integration.GROQ_API_KEY = original_key

    print("\n" + "=" * 70)
    print("TESTE DE ROBUSTEZ CONCLUÃDO")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_fallback())
