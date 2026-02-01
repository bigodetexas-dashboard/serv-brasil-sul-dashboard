# -*- coding: utf-8 -*-
"""
Criar novo serviço no Render com repositório renomeado
"""
import requests
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

RENDER_API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("=" * 80)
print("CRIANDO NOVO SERVICO NO RENDER")
print("=" * 80)
print()

# 1. Buscar owner ID do serviço existente
print("[1] Buscando informacoes do servico existente...")
response = requests.get(f"{BASE_URL}/services", headers=headers)

if response.status_code == 200:
    services = response.json()
    if services:
        owner_id = services[0].get('service', {}).get('ownerId')
        print(f"    [OK] Owner ID: {owner_id}")
        print()
    else:
        print("    [ERRO] Nenhum servico encontrado")
        sys.exit(1)
else:
    print(f"    [ERRO] Falha ao buscar servicos: {response.status_code}")
    sys.exit(1)

# 2. Criar novo serviço
print("[2] Criando novo servico...")
print("    Nome: serv-brasil-sul-dashboard-novo")
print("    Repo: https://github.com/bigodetexas-dashboard/serv-brasil-sul-dashboard")
print()

# Nota: A API do Render para plano Free pode não permitir criar via API
# Vamos tentar mesmo assim

new_service = {
    "type": "web_service",
    "name": "serv-brasil-sul-dashboard-novo",
    "ownerId": owner_id,
    "repo": "https://github.com/bigodetexas-dashboard/serv-brasil-sul-dashboard",
    "branch": "main",
    "rootDir": "new_dashboard",
    "autoDeploy": "yes"
}

response = requests.post(
    f"{BASE_URL}/services",
    headers=headers,
    json=new_service
)

print(f"    Status Code: {response.status_code}")
print(f"    Response: {response.text[:500]}")
print()

if response.status_code in [200, 201]:
    service = response.json()
    print("    [OK] Servico criado!")
    print(f"    ID: {service.get('id')}")
    print(f"    Nome: {service.get('name')}")
    print()
    print("PROXIMO PASSO:")
    print("1. Adicionar variaveis de ambiente")
    print("2. Aguardar deploy")
else:
    print("    [ERRO] Nao foi possivel criar via API")
    print()
    print("=" * 80)
    print("SOLUCAO MANUAL")
    print("=" * 80)
    print()
    print("O Render nao permite criar servicos Free via API.")
    print("Voce precisa criar manualmente:")
    print()
    print("1. Acesse: https://dashboard.render.com/select-repo?type=web")
    print("2. Procure por: serv-brasil-sul-dashboard")
    print("3. Clique em 'Connect'")
    print("4. Configure:")
    print("   - Name: serv-brasil-sul-dashboard-novo")
    print("   - Root Directory: new_dashboard")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn app:app")
    print("5. Adicione variaveis de ambiente")
    print("6. Clique em 'Create Web Service'")
    print()
    print("IMPORTANTE: Agora que o repositorio foi renomeado,")
    print("o Render vai gerar o slug correto automaticamente!")

print("=" * 80)
