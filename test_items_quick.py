import sys

sys.path.insert(0, ".")

from repositories.item_repository import ItemRepository

ir = ItemRepository()
items = ir.get_all_shop_items()
print(f"Total: {len(items)} itens carregados")
if items:
    print(f"Exemplo: {items[0]['name']} - ${items[0]['price']}")
    print(f"Categorias: {ir.get_all_categories()}")
