import sys

sys.path.insert(0, ".")

from repositories.item_repository import ItemRepository

ir = ItemRepository()
print(f"Banco usado pelo ItemRepository: {ir.db_file}")
print(f"Tipo de banco: {ir.db_type}")

items = ir.get_all_shop_items()
print(f"\nTotal de itens carregados: {len(items)}")

# Testar diretamente o banco correto
import sqlite3

conn = sqlite3.connect("new_dashboard/bigode_unified.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM shop_items")
print(f"Total no banco new_dashboard: {cur.fetchone()[0]}")
conn.close()

# Testar banco raiz
try:
    conn2 = sqlite3.connect("bigode_unified.db")
    cur2 = conn2.cursor()
    cur2.execute("SELECT COUNT(*) FROM shop_items")
    print(f"Total no banco raiz: {cur2.fetchone()[0]}")
    conn2.close()
except Exception as e:
    print(f"Banco raiz: {e}")
