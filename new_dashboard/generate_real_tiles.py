"""
Map tile generator for DayZ Chernarus map.
Generates zoom-level tiles from a source satellite image for Leaflet map display.
"""

import os
from PIL import Image

# ConfiguraÃ§Ãµes
# Imagem fonte fornecida pelo usuario
SOURCE_IMAGE = r"C:\Users\Wellyton\Desktop\DayZ_1.25.0_chernarus_map_16x16_sat.jpg"
OUTPUT_DIR = r"d:\dayz xbox\BigodeBot\new_dashboard\static\tiles"
TILE_SIZE = 256
MAX_ZOOM = 6  # Aumentando para 6 para permitir mais detalhe no heatmap


def generate_real_tiles():
    """
    Generate map tiles from source image for all zoom levels.
    Creates tiles in Leaflet-compatible format: {z}/{x}/{y}.png
    """
    if not os.path.exists(SOURCE_IMAGE):
        print(f"Erro: Imagem fonte nÃ£o encontrada em {SOURCE_IMAGE}")
        return

    # Aumentar limite de pixels para evitar DoS attack warning
    Image.MAX_IMAGE_PIXELS = None

    print(f"Abrindo imagem: {SOURCE_IMAGE}")
    try:
        img_full = Image.open(SOURCE_IMAGE)
    except (IOError, OSError) as e:
        print(f"Erro ao abrir imagem: {e}")
        return

    # Garantir que Ã© quadrada
    width, height = img_full.size
    print(f"Tamanho original: {width}x{height}")

    if width != height:
        size = max(width, height)
        print(f"Ajustando para quadrado: {size}x{size}")
        bg = Image.new("RGB", (size, size), (0, 0, 0))  # Fundo preto
        bg.paste(img_full, (0, 0))
        img_full = bg

    for z in range(MAX_ZOOM + 1):
        try:
            tiles_per_side = 2**z
            target_total_size = tiles_per_side * TILE_SIZE
            print(
                f"Zoom {z}: Gerando {tiles_per_side}x{tiles_per_side} "
                f"tiles ({target_total_size}px total)..."
            )

            # Redimensionar a imagem original para o tamanho total deste nÃ­vel de zoom
            z_img = img_full.resize(
                (target_total_size, target_total_size), Image.Resampling.LANCZOS
            )

            count = 0
            for x in range(tiles_per_side):
                for y in range(tiles_per_side):
                    tile_dir = os.path.join(OUTPUT_DIR, str(z), str(x))
                    os.makedirs(tile_dir, exist_ok=True)

                    # Cortar o tile
                    left = x * TILE_SIZE
                    top = y * TILE_SIZE
                    right = left + TILE_SIZE
                    bottom = top + TILE_SIZE

                    tile = z_img.crop((left, top, right, bottom))

                    # Salvar (Leaflet espera {z}/{x}/{y}.png)
                    tile_path = os.path.join(tile_dir, f"{y}.png")
                    tile.save(tile_path, "PNG", optimize=True)
                    count += 1

            print(f"  [OK] Zoom {z}: {count} tiles salvos.")

        except (IOError, OSError, MemoryError) as e:
            print(f"Erro no Zoom {z}: {e}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_real_tiles()
    print("\nProcesso concluÃ­do! Tiles gerados com sucesso.")
