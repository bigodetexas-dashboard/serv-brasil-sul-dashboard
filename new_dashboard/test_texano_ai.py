# -*- coding: utf-8 -*-
"""
Test script for Texano AI (Bigodudo)
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add paths
sys.path.insert(0, r"d:\dayz xbox\BigodeBot\new_dashboard")
os.chdir(r"d:\dayz xbox\BigodeBot\new_dashboard")

from google import genai
from dotenv import load_dotenv

# Load .env
load_dotenv(r"d:\dayz xbox\.env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "models/gemini-flash-latest"

print("=" * 60)
print("TESTE DO TEXANO AI (BIGODUDO)")
print("=" * 60)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print(f"Modelo: {MODEL}")
print()

# Test 1: Simple question
print("Teste 1: Pergunta simples")
print("-" * 60)

client = genai.Client(api_key=API_KEY)

prompt = """Você é o Bigodudo, um sobrevivente veterano de DayZ.
Responda de forma amigável e descontraída.

Pergunta: Olá Bigodudo, você está funcionando?

Responda em português brasileiro, de forma curta."""

response = client.models.generate_content(model=MODEL, contents=prompt)

if response and response.text:
    print(f"Resposta: {response.text}")
else:
    print(f"Erro: Resposta vazia")
    print(f"Response object: {response}")

print()
print("=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
