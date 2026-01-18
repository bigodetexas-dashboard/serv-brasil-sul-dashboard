from repositories.item_repository import ItemRepository

try:
    repo = ItemRepository()
    print("ItemRepository instantiated successfully.")
except Exception as e:
    print(f"Failed to instantiate ItemRepository: {e}")
