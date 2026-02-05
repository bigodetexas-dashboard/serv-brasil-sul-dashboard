# -*- coding: utf-8 -*-
"""
Test script for Hybrid AI System (Groq + Gemini)
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add paths
sys.path.insert(0, r"d:\dayz xbox\BigodeBot\new_dashboard")
os.chdir(r"d:\dayz xbox\BigodeBot\new_dashboard")

from ai_integration import ask_ai_sync, get_ai_stats
from dotenv import load_dotenv

# Load .env
load_dotenv(r"d:\dayz xbox\.env")

GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

print("=" * 70)
print("TESTE DO SISTEMA HÃBRIDO DE IA - TEXANO AI (BIGODUDO)")
print("=" * 70)
print(f"Groq API Key: {GROQ_KEY[:15] if GROQ_KEY else 'NÃƒO CONFIGURADA'}...")
print(f"Gemini API Key: {GEMINI_KEY[:15] if GEMINI_KEY else 'NÃƒO CONFIGURADA'}...")
print()

# Test 1: Simple question
print("Teste 1: Pergunta simples ao Bigodudo")
print("-" * 70)

try:
    response = ask_ai_sync("OlÃ¡ Bigodudo, vocÃª estÃ¡ funcionando?", "test_user_123")
    print(f"âœ… Resposta: {response}")
except Exception as e:
    print(f"âŒ Erro: {e}")

print()

# Test 2: Game-related question
print("Teste 2: Pergunta sobre o jogo")
print("-" * 70)

try:
    response = ask_ai_sync("Como ganho coins rÃ¡pido?", "test_user_123")
    print(f"âœ… Resposta: {response}")
except Exception as e:
    print(f"âŒ Erro: {e}")

print()

# Statistics
print("=" * 70)
print("ESTATÃSTICAS DE USO")
print("=" * 70)
stats = get_ai_stats()
print(f"Total de chamadas: {stats['total_calls']}")
print(
    f"Groq (primary): {stats['groq_calls']} chamadas ({stats['groq_success_rate']:.1f}%)"
)
print(
    f"Gemini (fallback): {stats['gemini_calls']} chamadas ({stats['gemini_usage_rate']:.1f}%)"
)
print(f"Erros Groq: {stats['groq_errors']}")
print(f"Erros Gemini: {stats['gemini_errors']}")
print()
print("=" * 70)
print("TESTE CONCLUÃDO")
print("=" * 70)
