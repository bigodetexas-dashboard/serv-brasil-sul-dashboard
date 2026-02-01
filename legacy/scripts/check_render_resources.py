# -*- coding: utf-8 -*-
"""
Listar TODOS os recursos do Render (web services, databases, etc)
"""
import requests
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

RENDER_API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"

headers = {"Authorization": f"Bearer {RENDER_API_KEY}", "Accept": "application/json"}

print("=" * 80)
print("LISTANDO TODOS OS RECURSOS DO RENDER")
print("=" * 80)
print()

# Listar web services
print("[1] Web Services:")
response = requests.get(f"{BASE_URL}/services", headers=headers)
if response.status_code == 200:
    services = response.json()
    print(f"    Total: {len(services)}")
    for s in services:
        service = s.get("service", s)
        print(f"    - {service.get('name')} ({service.get('type')})")
else:
    print(f"    Erro: {response.status_code}")

print()

# Listar databases
print("[2] Databases:")
response = requests.get(f"{BASE_URL}/postgres", headers=headers)
if response.status_code == 200:
    dbs = response.json()
    print(f"    Total: {len(dbs)}")
    for db in dbs:
        print(f"    - {db.get('name', 'N/A')}")
else:
    print(f"    Erro: {response.status_code}")

print()

# Listar redis
print("[3] Redis:")
response = requests.get(f"{BASE_URL}/redis", headers=headers)
if response.status_code == 200:
    redis = response.json()
    print(f"    Total: {len(redis)}")
else:
    print(f"    Erro: {response.status_code}")

print()

# Verificar owner/account
print("[4] Verificando conta:")
response = requests.get(f"{BASE_URL}/owners", headers=headers)
if response.status_code == 200:
    owners = response.json()
    print(f"    Total de owners: {len(owners)}")
    for owner in owners:
        o = owner.get("owner", owner)
        print(f"    - {o.get('name', 'N/A')} (ID: {o.get('id', 'N/A')})")
        print(f"      Email: {o.get('email', 'N/A')}")
        print(f"      Type: {o.get('type', 'N/A')}")
else:
    print(f"    Erro: {response.status_code}")

print()
print("=" * 80)
print("CONCLUSAO:")
print("=" * 80)
print()
print("Se voce tem 0 web services mas ainda pede cartao,")
print("pode ser que:")
print("1. O Render mudou a politica de plano Free")
print("2. Sua conta tem alguma restricao")
print("3. Voce tem outros recursos (databases, redis) que contam no limite")
print()
print("SOLUCAO:")
print("Infelizmente, se o Render esta pedindo cartao mesmo sem servicos,")
print("voce tem 3 opcoes:")
print("A) Adicionar um cartao (nao sera cobrado no plano Free)")
print("B) Usar o servico antigo que ja existe")
print("C) Usar outra plataforma (Railway, Fly.io, etc)")
print("=" * 80)
