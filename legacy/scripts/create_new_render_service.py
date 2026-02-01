# -*- coding: utf-8 -*-
"""
Criar novo serviço no Render com slug correto
"""
import requests
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

print("=" * 80)
print("CRIANDO NOVO SERVICO NO RENDER")
print("=" * 80)
print()

# Dados do novo serviço
new_service = {
    "type": "web_service",
    "name": "serv-brasil-sul-dashboard",
    "ownerId": "tea-d4j3d6ur433s7393sag0",  # Mesmo owner do serviço existente
    "repo": "https://github.com/bigodetexas-dashboard/bigodetexas-dashboard",
    "branch": "main",
    "rootDir": "new_dashboard",
    "serviceDetails": {
        "env": "python",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "gunicorn app:app",
        "plan": "free",
        "region": "oregon",
    },
    "autoDeploy": "yes",
}

print("[*] Tentando criar novo servico...")
print(f"Nome: {new_service['name']}")
print(f"Repo: {new_service['repo']}")
print(f"Root Dir: {new_service['rootDir']}")
print()

response = requests.post(f"{BASE_URL}/services", headers=headers, json=new_service)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:1000]}")
print()

if response.status_code in [200, 201]:
    data = response.json()
    service_id = data.get("id")
    service_url = data.get("serviceDetails", {}).get("url")

    print("[OK] Servico criado com sucesso!")
    print(f"ID: {service_id}")
    print(f"URL: {service_url}")
    print()
    print("PROXIMO PASSO:")
    print("1. Configurar variaveis de ambiente no novo servico")
    print("2. Aguardar deploy automatico")
    print("3. Deletar servico antigo (bigodetexas-dashboard)")
else:
    print("[ERRO] Nao foi possivel criar o servico.")
    print()
    if response.status_code == 400:
        print("Possivel causa: Servico com esse nome ja existe")
        print("ou parametros invalidos.")
    elif response.status_code == 401:
        print("Possivel causa: API Key invalida ou sem permissao.")
    elif response.status_code == 403:
        print("Possivel causa: Limite de servicos atingido no plano Free.")

    print()
    print("SOLUCAO MANUAL:")
    print("1. Acesse: https://dashboard.render.com/select-repo?type=web")
    print("2. Selecione o repositorio: bigodetexas-dashboard")
    print("3. Configure:")
    print("   - Name: serv-brasil-sul-dashboard")
    print("   - Root Directory: new_dashboard")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn app:app")
    print("4. Adicione as variaveis de ambiente")
    print("5. Clique em 'Create Web Service'")

print("=" * 80)
