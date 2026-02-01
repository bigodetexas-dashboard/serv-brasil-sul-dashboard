import requests
import os

# Tenta baixar tiles reais simulando um navegador
# Fonte: Dayz.GG (Ginfo) - Mencionado no projeto DayZ-Map-DL

BASE_URL = "https://dayz.ginfo.gg/tiles/chernarusplussat/{z}/{x}/{y}.png"
OUTPUT_DIR = "new_dashboard/static/tiles_real"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://dayz.ginfo.gg/",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin"
}

def test_download_real():
    # Testar Zoom 2, X=1, Y=1
    z, x, y = 2, 1, 1
    url = BASE_URL.format(z=z, x=x, y=y)
    
    print(f"Tentando baixar tile real de: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            print(f"[SUCESSO] Tile baixado! Tamanho: {len(response.content)} bytes")
            
            # Salvar
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open("test_real_tile.png", "wb") as f:
                f.write(response.content)
            print("Salvo como 'test_real_tile.png'")
            return True
        else:
            print(f"[FALHA] Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    test_download_real()
