# -*- coding: utf-8 -*-
"""
Alterar slug do serviço Render para serv-brasil-sul-dashboard
"""
import requests
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"
SERVICE_ID = "srv-d4jrhp8gjchc739odl2g"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("=" * 80)
print("ALTERANDO SLUG DO SERVICO RENDER")
print("=" * 80)
print()

# Dados para atualização
update_data = {
    "slug": "serv-brasil-sul-dashboard"
}

print(f"[*] Alterando slug para: serv-brasil-sul-dashboard")
print(f"[*] Service ID: {SERVICE_ID}")
print()

response = requests.patch(
    f"{BASE_URL}/services/{SERVICE_ID}",
    headers=headers,
    json=update_data
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
print()

if response.status_code == 200:
    print("[OK] Slug alterado com sucesso!")
    print()
    print("Nova URL do site:")
    print("https://serv-brasil-sul-dashboard.onrender.com")
    print()
    print("[IMPORTANTE] O Render vai fazer redeploy automaticamente.")
    print("Aguarde 5-10 minutos para o site ficar acessivel na nova URL.")
else:
    print("[ERRO] Nao foi possivel alterar o slug.")
    print()
    print("Possivel causa: Slug ja esta em uso ou nao pode ser alterado via API.")
    print()
    print("SOLUCAO MANUAL:")
    print("1. Acesse: https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g")
    print("2. Va em Settings")
    print("3. Procure por 'Name' ou 'Slug'")
    print("4. Altere para: serv-brasil-sul-dashboard")
    print("5. Salve as mudancas")

print("=" * 80)
