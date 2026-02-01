# -*- coding: utf-8 -*-
"""
Script para verificar status do deploy no Render
Monitora logs e confirma quando deploy estiver completo
"""
import requests
import time
import sys

RENDER_SERVICE_URL = "https://serv-brasil-sul-dashboard.onrender.com"
HEALTH_ENDPOINT = f"{RENDER_SERVICE_URL}/health"
CHECKOUT_ENDPOINT = f"{RENDER_SERVICE_URL}/checkout"

def check_service_status():
    """Verifica se o serviço está online"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        return response.status_code == 200
    except:
        return False

def check_tiles_deployed():
    """Verifica se os tiles foram deployados"""
    try:
        # Tenta acessar um tile específico
        tile_url = f"{RENDER_SERVICE_URL}/static/tiles/0/0/0.png"
        response = requests.head(tile_url, timeout=10)
        return response.status_code == 200
    except:
        return False

def monitor_deploy(max_wait_minutes=15):
    """Monitora o deploy até completar"""
    print("[MONITOR] Iniciando monitoramento do deploy...")
    print(f"[INFO] URL: {RENDER_SERVICE_URL}")
    print(f"[INFO] Aguardando ate {max_wait_minutes} minutos\n")
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    last_service_status = None
    last_tiles_status = None
    
    while (time.time() - start_time) < max_wait_seconds:
        elapsed = int(time.time() - start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        
        # Verificar serviço
        service_ok = check_service_status()
        if service_ok != last_service_status:
            if service_ok:
                print(f"[{minutes:02d}:{seconds:02d}] [OK] Servico online!")
            else:
                print(f"[{minutes:02d}:{seconds:02d}] [WAIT] Servico reiniciando...")
            last_service_status = service_ok
        
        # Verificar tiles (só se serviço estiver ok)
        if service_ok:
            tiles_ok = check_tiles_deployed()
            if tiles_ok != last_tiles_status:
                if tiles_ok:
                    print(f"[{minutes:02d}:{seconds:02d}] [SUCCESS] Tiles deployados!")
                    print("\n[DONE] Deploy concluido com sucesso!")
                    print(f"[URL] Acesse: {CHECKOUT_ENDPOINT}")
                    return True
                last_tiles_status = tiles_ok
        
        # Aguardar antes de próxima verificação
        time.sleep(10)
    
    print(f"\n[TIMEOUT] Tempo limite atingido ({max_wait_minutes} minutos)")
    print(f"[INFO] Verifique manualmente: {CHECKOUT_ENDPOINT}")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("MONITOR DE DEPLOY - BIGODETEXAS DASHBOARD")
    print("=" * 60)
    print()
    
    # Verificar status inicial
    print("[CHECK] Verificando status atual...")
    if check_service_status():
        print("[STATUS] Servico ja esta online")
        if check_tiles_deployed():
            print("[STATUS] Tiles ja estao deployados!")
            print(f"\n[SUCCESS] Tudo pronto! Acesse: {CHECKOUT_ENDPOINT}")
            sys.exit(0)
        else:
            print("[STATUS] Tiles ainda nao deployados, aguardando...")
    else:
        print("[STATUS] Servico offline, aguardando deploy...")
    
    print()
    
    # Monitorar
    success = monitor_deploy(max_wait_minutes=15)
    
    sys.exit(0 if success else 1)
