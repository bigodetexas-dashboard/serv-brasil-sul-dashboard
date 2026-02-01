# -*- coding: utf-8 -*-
"""
Verificar se slug foi alterado e tentar método alternativo
"""
import requests
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
print("VERIFICANDO STATUS ATUAL E TENTANDO ALTERAR SLUG")
print("=" * 80)
print()

# 1. Verificar status atual
print("[1] Verificando status atual...")
response = requests.get(f"{BASE_URL}/services/{SERVICE_ID}", headers=headers)

if response.status_code == 200:
    service = response.json()
    current_slug = service.get('slug')
    current_url = service.get('serviceDetails', {}).get('url')
    
    print(f"Slug atual: {current_slug}")
    print(f"URL atual: {current_url}")
    print()
    
    if current_slug == "serv-brasil-sul-dashboard":
        print("[OK] Slug ja esta correto!")
        print("URL do site: https://serv-brasil-sul-dashboard.onrender.com")
    else:
        print("[*] Slug ainda nao foi alterado.")
        print()
        print("=" * 80)
        print("CONCLUSAO:")
        print("=" * 80)
        print()
        print("O Render NAO permite alterar o slug via API.")
        print("O slug e definido automaticamente baseado no nome do repositorio.")
        print()
        print("OPCOES:")
        print()
        print("OPCAO 1: Usar a URL atual (RECOMENDADO)")
        print("  URL: https://bigodetexas-dashboard.onrender.com")
        print("  Vantagem: Ja esta funcionando, nao precisa mudar nada")
        print()
        print("OPCAO 2: Criar novo servico com slug correto")
        print("  1. Criar novo servico no Render")
        print("  2. Nome: serv-brasil-sul-dashboard")
        print("  3. Configurar para gerar slug: serv-brasil-sul-dashboard")
        print("  4. Deletar servico antigo")
        print("  Desvantagem: Precisa reconfigurar tudo")
        print()
        print("OPCAO 3: Alterar manualmente no painel (se possivel)")
        print("  1. Acessar: https://dashboard.render.com/web/srv-d4jrhp8gjchc739odl2g")
        print("  2. Settings > Name")
        print("  3. Tentar alterar (pode nao funcionar)")
        print()
        print("=" * 80)
        print("RECOMENDACAO:")
        print("=" * 80)
        print()
        print("Use a URL atual: https://bigodetexas-dashboard.onrender.com")
        print()
        print("Vou atualizar todos os arquivos do projeto para usar a URL correta.")
        print()
else:
    print(f"[ERRO] Status: {response.status_code}")
    print(response.text)
