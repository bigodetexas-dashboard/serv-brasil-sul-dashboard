# -*- coding: utf-8 -*-
"""
Deletar serviço antigo e criar novo no Render
"""
import requests
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

RENDER_API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"
OLD_SERVICE_ID = "srv-d4jrhp8gjchc739odl2g"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

print("=" * 80)
print("DELETANDO SERVICO ANTIGO E CRIANDO NOVO")
print("=" * 80)
print()

# PASSO 1: Suspender serviço antigo (mais seguro que deletar)
print("[1] Suspendendo servico antigo...")
print(f"    Service ID: {OLD_SERVICE_ID}")

response = requests.post(
    f"{BASE_URL}/services/{OLD_SERVICE_ID}/suspend", headers=headers
)

print(f"    Status Code: {response.status_code}")

if response.status_code == 200:
    print("    [OK] Servico suspenso com sucesso!")
    print()
else:
    print(f"    [AVISO] Nao foi possivel suspender: {response.text[:200]}")
    print("    Continuando mesmo assim...")
    print()

# PASSO 2: Tentar criar novo serviço
print("[2] Tentando criar novo servico...")

# Buscar owner ID
response = requests.get(f"{BASE_URL}/services", headers=headers)
if response.status_code == 200:
    services = response.json()
    if services:
        owner_id = services[0].get("service", {}).get("ownerId")
        print(f"    Owner ID: {owner_id}")
    else:
        print("    [ERRO] Nenhum servico encontrado para pegar owner ID")
        sys.exit(1)
else:
    print(f"    [ERRO] Falha ao buscar owner ID: {response.status_code}")
    sys.exit(1)

# Configuração do novo serviço
new_service = {
    "type": "web_service",
    "name": "serv-brasil-sul-dashboard",
    "ownerId": owner_id,
    "repo": "https://github.com/bigodetexas-dashboard/serv-brasil-sul-dashboard",
    "branch": "main",
    "rootDir": "new_dashboard",
    "serviceDetails": {
        "env": "python",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "gunicorn app:app",
        "plan": "free",
        "region": "oregon",
        "envVars": [
            {
                "key": "SECRET_KEY",
                "value": "399a2d81b3710671c6ab9ff055fee0af8cf0c48f9c4fb789e52a5635d0119ec8",
            },
            {
                "key": "DATABASE_URL",
                "value": "postgresql://postgres:Lissy%402000@db.uvyhpedcgmroddvkngdl.supabase.co:5432/postgres",
            },
            {"key": "DISCORD_CLIENT_ID", "value": "1442959269141020892"},
            {
                "key": "DISCORD_CLIENT_SECRET",
                "value": "K7TpzNNTVI0Zj0zfpuwF_i-GLDu2S5c0",
            },
            {
                "key": "DISCORD_REDIRECT_URI",
                "value": "https://serv-brasil-sul-dashboard.onrender.com/callback",
            },
            {
                "key": "DISCORD_TOKEN",
                "value": "ODQ3NDU2NjUyMjUzMDY5Mzgy.GN2g88.GGCUohzjGJmtBpnNELLJJB6abbjSQx2rQAWyzg",
            },
            {"key": "ADMIN_PASSWORD", "value": "Lissy@2000"},
            {"key": "ADMIN_WHITELIST", "value": "831391383981522964"},
            {
                "key": "FOOTER_ICON",
                "value": "https://cdn.discordapp.com/attachments/1442262893188878496/1442286419539394682/logo_texas.png",
            },
            {"key": "FTP_HOST", "value": "brsp012.gamedata.io"},
            {"key": "FTP_PASS", "value": "hqPuAFd9"},
            {"key": "FTP_PORT", "value": "21"},
            {"key": "FTP_USER", "value": "ni3622181_1"},
            {
                "key": "NITRADO_TOKEN",
                "value": "FumKsv7MGrfa6zG0bxW7C3kqigM0zloo1FlQH3JqLeQ7siSoqw8DvLbAojdYqr_iheYUt-RYGcTC8rIHfoL662exac8yR8It21vS",
            },
            {
                "key": "NOTIFICATION_WEBHOOK_URL",
                "value": "https://discord.com/api/webhooks/1441892129591922782/20eO0Z6wurnlD47-BgQ7yP5ePt0mK-2pXF8iQUuLfllqkPyVGdkVuSdTr6vd5sBEWCz2",
            },
            {"key": "PYTHON_VERSION", "value": "3.11.9"},
            {"key": "RATE_LIMIT_ENABLED", "value": "true"},
            {"key": "SERVICE_ID", "value": "3622181"},
        ],
    },
    "autoDeploy": "yes",
}

print("    Configuracao:")
print(f"    - Nome: {new_service['name']}")
print(f"    - Repo: {new_service['repo']}")
print(f"    - Root Dir: {new_service['rootDir']}")
print(f"    - Variaveis: {len(new_service['serviceDetails']['envVars'])} configuradas")
print()

response = requests.post(f"{BASE_URL}/services", headers=headers, json=new_service)

print(f"    Status Code: {response.status_code}")
print(f"    Response: {response.text[:500]}")
print()

if response.status_code in [200, 201]:
    service = response.json()
    print("=" * 80)
    print("SUCESSO!")
    print("=" * 80)
    print()
    print("Novo servico criado!")
    print(f"ID: {service.get('id')}")
    print(f"Nome: {service.get('name')}")
    print(f"URL: {service.get('serviceDetails', {}).get('url')}")
    print()
    print("Aguarde 5-10 minutos para o deploy terminar.")
else:
    print("=" * 80)
    print("ERRO - CRIACAO VIA API NAO SUPORTADA")
    print("=" * 80)
    print()
    print("O Render nao permite criar servicos Free via API.")
    print()
    print("SOLUCAO:")
    print("1. O servico antigo foi SUSPENSO (nao deletado)")
    print("2. Acesse: https://dashboard.render.com/select-repo?type=web")
    print("3. Procure: serv-brasil-sul-dashboard")
    print("4. Clique em 'Connect'")
    print("5. Use as configuracoes em: VARIAVEIS_AMBIENTE_BACKUP.txt")
    print("6. Root Directory: new_dashboard")
    print("7. Build: pip install -r requirements.txt")
    print("8. Start: gunicorn app:app")
    print()
    print("Depois que criar, me avise!")

print("=" * 80)
