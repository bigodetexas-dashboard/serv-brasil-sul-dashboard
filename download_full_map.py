import requests
import os

# URLs para testar no repositório oficial da Bohemia
URLS = [
    "https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Central-Economy/master/DayZ/ChernarusPlus/map.png",
    "https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Central-Economy/master/DayZ/ChernarusPlus/map_sat.png",
    "https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Central-Economy/master/DayZ/ChernarusPlus/map_top.png",
    # URL alternativa de comunidade
    "https://raw.githubusercontent.com/schana/dayz-server-map/master/map.png"
]

def download_map_image():
    print("Tentando baixar imagem do mapa Chernarus...")
    
    for url in URLS:
        print(f"Testando: {url}")
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                size_mb = int(response.headers.get('content-length', 0)) / (1024 * 1024)
                print(f"[SUCESSO] Imagem encontrada! Tamanho: {size_mb:.2f} MB")
                
                filename = "chernarus_map_full.png"
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"Imagem salva como '{filename}'")
                
                # Verificar dimensões (requer Pillow)
                try:
                    from PIL import Image
                    img = Image.open(filename)
                    print(f"Dimensoes: {img.width}x{img.height} pixels")
                    return True
                except ImportError:
                    print("Pillow nao instalado para verificar dimensoes, mas o arquivo foi baixado.")
                    return True
            else:
                print(f"[FALHA] Status {response.status_code}")
        except Exception as e:
            print(f"[ERRO] {e}")
            
    return False

if __name__ == "__main__":
    if download_map_image():
        print("\n[OK] Mapa baixado com sucesso! Agora podemos gerar os tiles.")
    else:
        print("\n[FALHA] Nenhuma imagem encontrada.")
