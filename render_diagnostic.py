# -*- coding: utf-8 -*-
"""
Script de Diagnóstico do Render
Verifica status do serviço e identifica problemas
"""
import requests
import json
import sys

# Configurar encoding UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# API Key do Render
API_KEY = "rnd_h14PM98BoJsf0EP5Q8eXUmE3Kc4Y"
BASE_URL = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

print("=" * 80)
print("DIAGNOSTICO DO RENDER - SERV. BRASIL SUL DASHBOARD")
print("=" * 80)
print()

# 1. Listar todos os serviços
print("[1] BUSCANDO SERVICOS...")
response = requests.get(f"{BASE_URL}/services", headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")
print()

if response.status_code == 200:
    try:
        data = response.json()
        
        # A resposta pode ser uma lista ou um objeto com chave 'services'
        if isinstance(data, list):
            services = data
        elif isinstance(data, dict) and 'services' in data:
            services = data['services']
        else:
            services = [data]
        
        print(f"[OK] Encontrados {len(services)} servico(s)")
        print()
        
        for idx, service in enumerate(services):
            print(f"--- SERVICO {idx + 1} ---")
            print(json.dumps(service, indent=2))
            print()
            
            service_id = service.get('service', {}).get('id') or service.get('id')
            service_name = service.get('service', {}).get('name') or service.get('name')
            
            if service_id:
                print(f"[2] BUSCANDO DETALHES DO SERVICO: {service_name}")
                detail_response = requests.get(f"{BASE_URL}/services/{service_id}", headers=headers)
                
                if detail_response.status_code == 200:
                    details = detail_response.json()
                    print("[OK] Detalhes obtidos:")
                    print(json.dumps(details, indent=2))
                    print()
                    
                    # Buscar deploys
                    print(f"[3] BUSCANDO DEPLOYS...")
                    deploys_response = requests.get(f"{BASE_URL}/services/{service_id}/deploys", headers=headers)
                    
                    if deploys_response.status_code == 200:
                        deploys_data = deploys_response.json()
                        print("[OK] Deploys obtidos:")
                        print(json.dumps(deploys_data, indent=2)[:1000])
                        print()
                    else:
                        print(f"[ERRO] Deploys: {deploys_response.status_code}")
                        print(deploys_response.text[:500])
                else:
                    print(f"[ERRO] Detalhes: {detail_response.status_code}")
                    print(detail_response.text[:500])
            
    except Exception as e:
        print(f"[ERRO] Excecao: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[ERRO] Status: {response.status_code}")
    print(f"Response: {response.text}")

print("=" * 80)
print("[FIM] DIAGNOSTICO COMPLETO")
print("=" * 80)
