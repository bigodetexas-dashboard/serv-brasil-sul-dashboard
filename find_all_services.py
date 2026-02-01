# -*- coding: utf-8 -*-
"""
Buscar TODOS os serviços incluindo suspensos e inativos
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
print("BUSCANDO TODOS OS SERVICOS (INCLUINDO SUSPENSOS)")
print("=" * 80)
print()

# Tentar diferentes endpoints
endpoints = [
    "/services",
    "/services?suspended=true",
    "/services?suspended=false",
]

for endpoint in endpoints:
    print(f"[*] Testando endpoint: {endpoint}")
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list):
            services = data
        elif isinstance(data, dict) and 'services' in data:
            services = data['services']
        else:
            services = [data]
        
        print(f"    Encontrados: {len(services)} servico(s)")
        
        for item in services:
            service = item.get('service', item)
            name = service.get('name', 'N/A')
            url = service.get('serviceDetails', {}).get('url', 'N/A')
            suspended = service.get('suspended', 'N/A')
            print(f"    - {name}: {url} (suspended: {suspended})")
    else:
        print(f"    Erro: {response.status_code}")
    print()

# Tentar buscar diretamente por nome
print("[*] Tentando buscar servico especifico...")
print()

# Tentar acessar diretamente a URL que deveria existir
test_url = "https://serv-brasil-sul-dashboard.onrender.com/"
print(f"[*] Testando acesso direto a: {test_url}")

try:
    import requests
    r = requests.get(test_url, timeout=30)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Content-Length: {len(r.text)}")
        print(f"    Primeiros 200 chars: {r.text[:200]}")
        print()
        print("[OK] SITE EXISTE E ESTA ONLINE!")
    else:
        print(f"    [ERRO] Site retornou: {r.status_code}")
except Exception as e:
    print(f"    [ERRO] Nao foi possivel acessar: {e}")

print()
print("=" * 80)
