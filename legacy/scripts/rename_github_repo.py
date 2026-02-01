# -*- coding: utf-8 -*-
"""
Renomear repositório GitHub via API
"""
import requests
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Configurações
GITHUB_TOKEN = "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"
OWNER = "bigodetexas-dashboard"
OLD_REPO_NAME = "bigodetexas-dashboard"
NEW_REPO_NAME = "serv-brasil-sul-dashboard"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

print("=" * 80)
print("RENOMEANDO REPOSITORIO GITHUB")
print("=" * 80)
print()

# 1. Verificar repositório atual
print(f"[1] Verificando repositorio atual: {OWNER}/{OLD_REPO_NAME}")
response = requests.get(
    f"https://api.github.com/repos/{OWNER}/{OLD_REPO_NAME}", headers=headers
)

if response.status_code == 200:
    repo = response.json()
    print("    [OK] Repositorio encontrado")
    print(f"    Nome atual: {repo['name']}")
    print(f"    URL atual: {repo['html_url']}")
    print()
else:
    print(f"    [ERRO] Repositorio nao encontrado: {response.status_code}")
    print(f"    Response: {response.text}")
    sys.exit(1)

# 2. Renomear repositório
print(f"[2] Renomeando para: {NEW_REPO_NAME}")

data = {"name": NEW_REPO_NAME}

response = requests.patch(
    f"https://api.github.com/repos/{OWNER}/{OLD_REPO_NAME}", headers=headers, json=data
)

print(f"    Status Code: {response.status_code}")

if response.status_code == 200:
    repo = response.json()
    print("    [OK] Repositorio renomeado com sucesso!")
    print()
    print("=" * 80)
    print("SUCESSO!")
    print("=" * 80)
    print()
    print(f"Nome antigo: {OLD_REPO_NAME}")
    print(f"Nome novo: {repo['name']}")
    print(f"URL nova: {repo['html_url']}")
    print()
    print("IMPORTANTE:")
    print("1. O GitHub vai redirecionar automaticamente a URL antiga para a nova")
    print("2. Voce precisa atualizar o remote do Git local:")
    print(f"   git remote set-url origin {repo['clone_url']}")
    print()
else:
    print(f"    [ERRO] Falha ao renomear: {response.status_code}")
    print(f"    Response: {response.text}")

    if response.status_code == 403:
        print()
        print("    Possivel causa: Token sem permissoes suficientes")
    elif response.status_code == 422:
        print()
        print("    Possivel causa: Nome ja esta em uso")

print("=" * 80)
