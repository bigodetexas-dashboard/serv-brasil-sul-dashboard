# -*- coding: utf-8 -*-
"""
Listar TODOS os serviços do Render
"""
import requests
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

print("=" * 80)
print("LISTANDO TODOS OS SERVICOS DO RENDER")
print("=" * 80)
print()

# Listar TODOS os serviços (com paginação)
all_services = []
cursor = None

while True:
    url = f"{BASE_URL}/services"
    if cursor:
        url += f"?cursor={cursor}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list):
            all_services.extend(data)
            # Verificar se há mais páginas
            if len(data) > 0 and 'cursor' in data[-1]:
                cursor = data[-1]['cursor']
            else:
                break
        else:
            break
    else:
        print(f"[ERRO] Status: {response.status_code}")
        print(response.text)
        break

print(f"[OK] Total de servicos encontrados: {len(all_services)}")
print()

for idx, item in enumerate(all_services):
    service = item.get('service', item)
    
    print(f"--- SERVICO {idx + 1} ---")
    print(f"Nome: {service.get('name', 'N/A')}")
    print(f"ID: {service.get('id', 'N/A')}")
    print(f"Slug: {service.get('slug', 'N/A')}")
    print(f"URL: {service.get('serviceDetails', {}).get('url', 'N/A')}")
    print(f"Status: {service.get('suspended', 'N/A')}")
    print(f"Tipo: {service.get('type', 'N/A')}")
    print(f"Root Dir: {service.get('rootDir', 'N/A')}")
    print(f"Branch: {service.get('branch', 'N/A')}")
    print(f"Repo: {service.get('repo', 'N/A')}")
    print()

print("=" * 80)
