import os
import requests
from concurrent.futures import ThreadPoolExecutor

# ConfiguraÃ§Ãµes
# URL base do iZurvive (pode precisar de ajustes se mudar)
BASE_URL = "https://maps.izurvive.com/maps/chernarusplus/{z}/{x}/{y}.png"
OUTPUT_DIR = "static/tiles"
ZOOM_LEVELS = range(0, 8)  # 0 a 7
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.izurvive.com/",
}


def download_tile(z, x, y):
    url = BASE_URL.format(z=z, x=x, y=y)
    path = os.path.join(OUTPUT_DIR, str(z), str(x))
    filename = f"{y}.png"
    filepath = os.path.join(path, filename)

    if os.path.exists(filepath):
        return  # JÃ¡ existe

    os.makedirs(path, exist_ok=True)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"Baixado: {z}/{x}/{y}")
        else:
            print(f"Falha {response.status_code}: {url}")
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")


def main():
    print("Iniciando download dos tiles do mapa Chernarus...")

    tasks = []
    for z in ZOOM_LEVELS:
        # Calcular limites para cada zoom (Chernarus Ã© aprox quadrado)
        # Zoom 0: 1x1
        # Zoom 1: 2x2
        # Zoom 2: 4x4
        # etc. 2^z
        max_coord = 2**z

        print(f"Preparando Zoom {z} ({max_coord}x{max_coord} tiles)...")

        for x in range(max_coord):
            for y in range(max_coord):
                tasks.append((z, x, y))

    print(f"Total de tiles a baixar: {len(tasks)}")

    # Usar threads para acelerar
    with ThreadPoolExecutor(max_workers=10) as executor:
        for z, x, y in tasks:
            executor.submit(download_tile, z, x, y)
            # Pequeno delay para nÃ£o sobrecarregar
            # time.sleep(0.01)

    print("Download concluÃ­do!")


if __name__ == "__main__":
    main()
