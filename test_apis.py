#!/usr/bin/env python3
"""
Script de Teste Completo - Sistema de Achievements, History e Settings
Testa todas as APIs e verifica se tudo está funcionando
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_api(endpoint, method="GET", data=None):
    """Testa um endpoint da API"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n{'='*60}")
        print(f"Testando: {method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"❌ ERRO: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERRO NA REQUISIÇÃO: {e}")
        return False

def main():
    print("="*60)
    print("🧪 TESTE COMPLETO DO SISTEMA")
    print("="*60)
    
    results = {}
    
    # Teste 1: Achievements
    print("\n\n📊 TESTANDO ACHIEVEMENTS API")
    results['achievements_all'] = test_api("/api/achievements/all")
    results['achievements_stats'] = test_api("/api/achievements/stats")
    
    # Teste 2: History
    print("\n\n📜 TESTANDO HISTORY API")
    results['history_events'] = test_api("/api/history/events")
    results['history_stats'] = test_api("/api/history/stats")
    
    # Teste 3: Settings
    print("\n\n⚙️ TESTANDO SETTINGS API")
    results['settings_get'] = test_api("/api/settings/get")
    
    # Teste 4: Testar POST (adicionar evento ao histórico)
    print("\n\n📝 TESTANDO POST - Adicionar Evento")
    test_event = {
        "event_type": "test",
        "icon": "🧪",
        "title": "Teste Automático",
        "description": "Evento de teste criado automaticamente",
        "details": {"test": "true"}
    }
    results['history_add'] = test_api("/api/history/add", "POST", test_event)
    
    # Resumo
    print("\n\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test:30} {status}")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} testes passaram")
    print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente!")
    elif passed > 0:
        print(f"\n⚠️ {total-passed} teste(s) falharam. Verifique os erros acima.")
    else:
        print("\n❌ TODOS OS TESTES FALHARAM!")
        print("Possíveis causas:")
        print("1. Servidor não está rodando (execute: python app.py)")
        print("2. Schema não foi aplicado no banco (execute: psql $DATABASE_URL -f schema_achievements_history.sql)")
        print("3. Problemas de conexão com o banco de dados")

if __name__ == "__main__":
    main()
