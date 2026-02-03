# -*- coding: utf-8 -*-
"""
Script para adicionar link 'Tiro na Lata' em todas as navbars
"""

import os
import re

# Arquivos a serem atualizados
files_to_update = [
    "heatmap.html",
    "clan.html",
    "banco.html",
    "dashboard.html",
    "checkout.html",
    "agradecimentos.html",
    "leaderboard.html",
    "shop.html",
]

# Caminho base
templates_dir = os.path.join(os.path.dirname(__file__), "new_dashboard", "templates")

# Link a ser adicionado
new_link = '                <li><a href="/deaths" class="navbar-link"><i class="ri-crosshair-line"></i> Tiro na Lata</a></li>\r\n'

# Padrão para encontrar (após Mapa de Calor)
pattern = r"(.*Mapa de Calor</a></li>\r?\n)"

for filename in files_to_update:
    filepath = os.path.join(templates_dir, filename)

    if not os.path.exists(filepath):
        print(f"[SKIP] {filename} não encontrado")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar se já tem o link
    if "Tiro na Lata" in content:
        print(f"[OK] {filename} já tem o link")
        continue

    # Adicionar link após Mapa de Calor
    new_content = re.sub(pattern, r"\1" + new_link, content)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[UPDATED] {filename}")
    else:
        print(f"[SKIP] {filename} - padrão não encontrado")

print("\n[DONE] Atualização concluída!")
