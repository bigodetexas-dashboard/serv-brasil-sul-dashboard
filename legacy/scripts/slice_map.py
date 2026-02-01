import os
from PIL import Image

# Configurações
# Caminho da imagem fonte (ajuste conforme sua escolha: _sat.jpg ou _top.jpg)
SOURCE_IMAGE = "static/img/DayZ_1.25.0_chernarus_map_16x16_sat.jpg"
OUTPUT_DIR = "new_dashboard/static/tiles"
TILE_SIZE = 256


def generate_tiles_from_image():
    print(f"Iniciando processamento da imagem: {SOURCE_IMAGE}")

    if not os.path.exists(SOURCE_IMAGE):
        print(f"[ERRO] Imagem nao encontrada: {SOURCE_IMAGE}")
        return

    # Abrir imagem
    # Aumentar limite de pixels para imagens gigantes
    Image.MAX_IMAGE_PIXELS = None

    try:
        img = Image.open(SOURCE_IMAGE)
        print(f"[INFO] Imagem carregada. Dimensoes: {img.width}x{img.height}")
    except Exception as e:
        print(f"[ERRO] Falha ao abrir imagem: {e}")
        return

    # O DayZ Chernarus é quadrado (15360x15360m).
    # Vamos assumir que a imagem cobre todo o mapa.
    # O nível de zoom máximo depende do tamanho da imagem.
    # Zoom 0 = 1 tile (256x256)
    # Zoom 1 = 2x2 tiles (512x512)
    # ...
    # Zoom Z = 2^Z x 2^Z tiles = (2^Z * 256) pixels

    # Calcular qual seria o zoom máximo nativo da imagem
    # Ex: se imagem tem 16384px (16x16 tiles de 1024?), vamos calcular.

    # Gerar tiles completos (Zoom 0 a 6)
    MAX_ZOOM = 6

    print(f"Iniciando loop de geracao (Zoom 0 a {MAX_ZOOM})...")
    print(f"Imagem original: {img.width}x{img.height} pixels")

    for z in range(MAX_ZOOM + 1):
        num_tiles = 2**z
        total_pixels = num_tiles * TILE_SIZE

        print(
            f"\n[Z{z}] Gerando {num_tiles}x{num_tiles} tiles ({total_pixels}x{total_pixels} pixels)..."
        )

        # Redimensionar imagem original para o tamanho deste nível de zoom
        # Usamos LANCZOS para melhor qualidade na redução
        current_img = img.resize((total_pixels, total_pixels), Image.Resampling.LANCZOS)

        for x in range(num_tiles):
            for y in range(num_tiles):
                # Coordenadas de corte
                left = x * TILE_SIZE
                upper = y * TILE_SIZE
                right = left + TILE_SIZE
                lower = upper + TILE_SIZE

                # Cortar tile
                tile = current_img.crop((left, upper, right, lower))

                # Criar diretório
                tile_dir = os.path.join(OUTPUT_DIR, str(z), str(x))
                os.makedirs(tile_dir, exist_ok=True)

                # Salvar tile
                tile_path = os.path.join(tile_dir, f"{y}.png")
                tile.save(tile_path, "PNG", optimize=True)

        print(f"   [OK] Zoom {z} concluido.")

    print("\n[SUCESSO] Todos os tiles gerados!")


if __name__ == "__main__":
    generate_tiles_from_image()
