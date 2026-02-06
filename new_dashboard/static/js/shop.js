// ==================== SHOP.JS ====================
// Sistema completo de loja com carrinho

let allItems = [];
let cart = [];
let currentCategory = 'all';
let userBalance = 0;

// Ícones para cada categoria (RemixIcon)
const categoryIcons = {
    armas: '<i class="ri-crosshair-2-line"></i>',
    municao: '<i class="ri-disc-line"></i>',
    carregadores: '<i class="ri-archive-line"></i>',
    acessorios: '<i class="ri-settings-4-line"></i>',
    armadilhas: '<i class="ri-alert-line"></i>',
    medico: '<i class="ri-first-aid-kit-line"></i>',
    comidas: '<i class="ri-restaurant-line"></i>',
    roupas: '<i class="ri-shirt-line"></i>',
    mochilas: '<i class="ri-shopping-bag-3-line"></i>',
    construcao: '<i class="ri-hammer-line"></i>',
    ferramentas: '<i class="ri-tools-line"></i>',
    veiculos: '<i class="ri-roadster-line"></i>',
    cacador: '<i class="ri-compass-3-line"></i>'
};

// Inicialização
document.addEventListener('DOMContentLoaded', function () {
    loadItems();
    loadUserBalance();
    loadCart();
    setupEventListeners();
});

// Carregar itens da API
async function loadItems() {
    try {
        const response = await fetch('/api/shop/items');
        const data = await response.json();
        allItems = data;
        renderItems();
    } catch (error) {
        console.error('Erro ao carregar itens:', error);
    }
}

// Carregar saldo do usuário
async function loadUserBalance() {
    try {
        const response = await fetch('/api/user/balance');
        const data = await response.json();
        userBalance = data.balance || 0;
        document.getElementById('user-balance').textContent = formatNumber(userBalance);
        // Atualiza também o flutuante se existir
        const floatBalance = document.getElementById('user-balance-float');
        if (floatBalance) {
            floatBalance.textContent = formatNumber(userBalance);
        }
    } catch (error) {
        console.error('Erro ao carregar saldo:', error);
        document.getElementById('user-balance').textContent = '0';
        const floatBalance = document.getElementById('user-balance-float');
        if (floatBalance) {
            floatBalance.textContent = '0';
        }
    }
}

// Carregar carrinho do localStorage
function loadCart() {
    const saved = localStorage.getItem('cart');
    if (saved) {
        cart = JSON.parse(saved);
        updateCartCount();
    }
}

// Salvar carrinho no localStorage
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

// Event Listeners
function setupEventListeners() {
    // Categorias
    document.querySelectorAll('.category-filter').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.category-filter').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentCategory = this.dataset.category;
            renderItems();
        });
    });

    // Busca
    document.getElementById('search-input').addEventListener('input', function (e) {
        renderItems(e.target.value);
    });

    // Ordenação
    document.getElementById('sort-select').addEventListener('change', function () {
        renderItems();
    });

    // Carrinho - usando botão flutuante
    document.getElementById('cart-float-btn').addEventListener('click', openCart);
    document.getElementById('close-cart').addEventListener('click', closeCart);
    document.getElementById('clear-cart').addEventListener('click', clearCart);
    document.getElementById('checkout-btn').addEventListener('click', checkout);

    // Fechar modal ao clicar fora
    document.getElementById('cart-modal').addEventListener('click', function (e) {
        if (e.target === this) {
            closeCart();
        }
    });
}

// Renderizar itens
function renderItems(searchTerm = '') {
    const grid = document.getElementById('items-grid');
    const sortBy = document.getElementById('sort-select').value;

    // Filtrar
    let filtered = allItems.filter(item => {
        const matchCategory = currentCategory === 'all' || item.category === currentCategory;
        const matchSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.description.toLowerCase().includes(searchTerm.toLowerCase());
        return matchCategory && matchSearch;
    });

    // Ordenar
    filtered.sort((a, b) => {
        if (sortBy === 'name') {
            return a.name.localeCompare(b.name);
        } else if (sortBy === 'price-asc') {
            return a.price - b.price;
        } else if (sortBy === 'price-desc') {
            return b.price - a.price;
        }
        return 0;
    });

    // Renderizar
    grid.innerHTML = filtered.map(item => `
        <div class="item-card" data-item-code="${item.code}">
            <div class="item-image" style="position: relative;">
                ${item.image_url && item.image_url.includes('.') ? `<img src="${item.image_url}" style="width:100%; height:100%; object-fit:contain;">` : (categoryIcons[item.category] || '📦')}
                <button onclick="openUploadModal('${item.id}', '${item.name}')" style="position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.6); color: white; border: none; border-radius: 50%; width: 25px; height: 25px; cursor: pointer; display: flex; align-items: center; justify-content: center;">
                    <i class="ri-pencil-line" style="font-size: 0.9rem;"></i>
                </button>
            </div>
            <div class="item-name">${item.name}</div>
            <div class="item-description">${item.description}</div>
            <div class="item-footer">
                <div class="item-price">${formatNumber(item.price)} 💰</div>
                <button class="add-to-cart-btn" onclick="addToCart('${item.code}')">
                    ${window.shopTranslations.adicionarCarrinho}
                </button>
            </div>
        </div>
    `).join('');
}

// Adicionar ao carrinho
function addToCart(itemCode) {
    const item = allItems.find(i => i.code === itemCode);
    if (!item) return;

    const existingItem = cart.find(i => i.code === itemCode);
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({
            ...item,
            quantity: 1
        });
    }

    saveCart();
    showNotification(window.shopTranslations.itemAdicionado || `Item ${item.name} adicionado ao carrinho!`);
}

// Abrir carrinho
function openCart() {
    renderCart();
    document.getElementById('cart-modal').classList.add('open');
}

// Fechar carrinho
function closeCart() {
    document.getElementById('cart-modal').classList.remove('open');
}

// Renderizar carrinho
function renderCart() {
    const container = document.getElementById('cart-items');

    if (cart.length === 0) {
        container.innerHTML = `
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <p>${window.shopTranslations.carrinhoVazio}</p>
            </div>
        `;
        document.getElementById('cart-total').textContent = '0';
        return;
    }

    container.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${formatNumber(item.price)} 💰 ${window.shopTranslations.item || 'item'}</div>
            </div>
            <div class="cart-item-quantity">
                <button class="qty-btn" onclick="updateQuantity('${item.code}', -1)">-</button>
                <span>${item.quantity}</span>
                <button class="qty-btn" onclick="updateQuantity('${item.code}', 1)">+</button>
            </div>
            <button class="remove-btn" onclick="removeFromCart('${item.code}')">🗑️</button>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.getElementById('cart-total').textContent = formatNumber(total);
}

// Atualizar quantidade
function updateQuantity(itemCode, change) {
    const item = cart.find(i => i.code === itemCode);
    if (!item) return;

    item.quantity += change;
    if (item.quantity <= 0) {
        removeFromCart(itemCode);
    } else {
        saveCart();
        renderCart();
    }
}

// Remover do carrinho
function removeFromCart(itemCode) {
    cart = cart.filter(i => i.code !== itemCode);
    saveCart();
    renderCart();
}

// Limpar carrinho
function clearCart() {
    if (confirm(window.shopTranslations.confirmarLimpar || 'Deseja limpar todo o carrinho?')) {
        cart = [];
        saveCart();
        renderCart();
    }
}

// Atualizar contador do carrinho
function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCountEl = document.getElementById('cart-count');
    if (cartCountEl) {
        cartCountEl.textContent = count;
    }
}

// Finalizar compra
function checkout() {
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    if (cart.length === 0) {
        alert(window.shopTranslations.carrinhoVazioAlerta);
        return;
    }

    if (total > userBalance) {
        alert(window.shopTranslations.saldoInsuficiente || 'Saldo insuficiente!');
        return;
    }

    // Redirecionar para página de checkout (com mapa)
    localStorage.setItem('checkout-cart', JSON.stringify(cart));
    window.location.href = '/checkout';
}

// Notificação
function showNotification(message) {
    // TODO: Implementar sistema de notificações toast
    console.log(message);
}

// Formatar número
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// ==================== IMAGE UPLOAD LOGIC ====================

function openUploadModal(itemId, itemName) {
    document.getElementById('upload-modal').style.display = 'flex';
    document.getElementById('upload-item-name').textContent = itemName;
    document.getElementById('upload-item-id').value = itemId;
}

function closeUploadModal() {
    document.getElementById('upload-modal').style.display = 'none';
}

async function submitImageUpload() {
    const itemId = document.getElementById('upload-item-id').value;
    const fileInput = document.getElementById('upload-file');

    if (fileInput.files.length === 0) {
        alert("Selecione uma imagem!");
        return;
    }

    const formData = new FormData();
    formData.append('item_id', itemId);
    formData.append('image', fileInput.files[0]);

    try {
        const response = await fetch('/api/shop/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.success) {
            alert("Imagem atualizada com sucesso!");
            closeUploadModal();
            loadItems(); // Reload grid to show new image
        } else {
            alert("Erro: " + (data.error || "Desconhecido"));
        }
    } catch (error) {
        console.error(error);
        alert("Erro na conexão");
    }
}
