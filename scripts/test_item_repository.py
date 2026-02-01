"""
Teste do ItemRepository após sincronização.
"""

from repositories.item_repository import ItemRepository


def test_item_repository():
    print("Testando ItemRepository...")

    try:
        ir = ItemRepository()

        # Teste 1: Carregar todos os itens
        print("\n[Teste 1] Carregando todos os itens...")
        items = ir.get_all_shop_items()
        print(f"   Sucesso! {len(items)} itens carregados")

        if items:
            print(f"   Primeiro item: {items[0]['name']} - ${items[0]['price']}")

        # Teste 2: Carregar por categoria
        print("\n[Teste 2] Carregando itens da categoria 'armas'...")
        armas = ir.get_items_by_category("armas")
        print(f"   Sucesso! {len(armas)} armas encontradas")

        # Teste 3: Buscar item específico
        print("\n[Teste 3] Buscando item 'm4a1'...")
        m4 = ir.get_item_by_key("m4a1")
        if m4:
            print(f"   Encontrado: {m4['name']} - ${m4['price']}")
        else:
            print("   Item não encontrado!")

        # Teste 4: Listar categorias
        print("\n[Teste 4] Listando categorias...")
        categories = ir.get_all_categories()
        print(f"   {len(categories)} categorias: {', '.join(categories)}")

        print("\n✅ Todos os testes passaram! ItemRepository está funcionando.")
        return True

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_item_repository()
