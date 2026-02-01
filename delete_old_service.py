# -*- coding: utf-8 -*-
"""
Deletar serviço antigo permanentemente
"""
import requests
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

RENDER_API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"
OLD_SERVICE_ID = "srv-d4jrhp8gjchc739odl2g"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json"
}

print("=" * 80)
print("DELETANDO SERVICO ANTIGO PERMANENTEMENTE")
print("=" * 80)
print()

print(f"[*] Deletando servico: {OLD_SERVICE_ID}")
print()

response = requests.delete(
    f"{BASE_URL}/services/{OLD_SERVICE_ID}",
    headers=headers
)

print(f"Status Code: {response.status_code}")

if response.status_code == 204:
    print("[OK] Servico deletado com sucesso!")
    print()
    print("Agora voce pode criar o novo servico sem precisar de cartao.")
    print()
    print("PROXIMO PASSO:")
    print("1. Volte para: https://dashboard.render.com/select-repo?type=web")
    print("2. Procure: serv-brasil-sul-dashboard")
    print("3. Clique em 'Connect'")
    print("4. Configure e adicione variaveis")
    print("5. Clique em 'Deploy web service'")
elif response.status_code == 200:
    print("[OK] Servico deletado!")
    print()
    print("Agora pode criar o novo servico.")
else:
    print(f"[ERRO] Falha ao deletar: {response.status_code}")
    print(f"Response: {response.text}")
    print()
    print("SOLUCAO MANUAL:")
    print("1. Acesse: https://dashboard.render.com")
    print("2. Encontre o servico: serv-brasil-sul-dashboard")
    print("3. Clique nele")
    print("4. Settings > Delete Service")
    print("5. Confirme a delecao")

print("=" * 80)
