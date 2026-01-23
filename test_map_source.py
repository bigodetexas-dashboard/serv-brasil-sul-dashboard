import requests
import os

# Baseado na estrutura comum de servidores de tiles do iZurvive/DayZ Community
# Tenta baixar um tile central do Chernarus (Zoom 2, tile 1,1 ou similar)
# URL padrão do iZurvive: https://maps.izurvive.com/maps/chernarusplus-sat/1.0.0/tiles/{z}/{x}/{y}.png
# Ou variações encontradas em projetos como DayZ-Map-DL

URLS_TO_TEST = [
    "https://maps.izurvive.com/maps/chernarusplus-top/1.0.0/tiles/{z}/{x}/{y}.png",
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png", 
    "https://dayz.ginfo.gg/tiles/chernarusplus/{z}/{x}/{y}.png"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.izurvive.com/"
}

def test_download():
    # Testar Zoom 0, X=0, Y=0 (Mapa Inteiro)
    z, x, y = 0, 0, 0
    
    print(f"Testando download de tile BASE (Z={z}, X={x}, Y={y})...")
    
    for base_url in URLS_TO_TEST:
        url = base_url.format(z=z, x=x, y=y)
        print(f"Tentando: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                print(f"[SUCESSO] Tile encontrado em: {base_url}")
                print(f"Tamanho: {len(response.content)} bytes")
                
                # Salvar para verificar
                with open("test_tile_real.png", "wb") as f:
                    f.write(response.content)
                print("Tile salvo como 'test_tile_real.png'")
                return base_url
            else:
                print(f"[FALHA] Status {response.status_code}")
        except Exception as e:
            print(f"[ERRO] {e}")
            
    return None

if __name__ == "__main__":
    found_url = test_download()
    if found_url:
        print(f"\nURL CONFIRMADA: {found_url}")
        print("Podemos usar esta URL para baixar o mapa completo.")
    else:
        print("\nNenhuma URL funcionou. Precisamos investigar mais o DayZ-Map-DL.")
