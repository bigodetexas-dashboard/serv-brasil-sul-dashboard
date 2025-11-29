// ==================== CHECKOUT.JS ====================
// Sistema de checkout com mapa iZurvive

let cart = [];
let selectedCoords = null;

document.addEventListener('DOMContentLoaded', function () {
    loadCheckoutCart();
    setupEventListeners();
});

function loadCheckoutCart() {
    const saved = localStorage.getItem('checkout-cart');
    if (!saved) {
        window.location.href = '/shop';
        return;
    }

    cart = JSON.parse(saved);
    renderOrderSummary();
}

function renderOrderSummary() {
    const container = document.getElementById('order-items');
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    container.innerHTML = cart.map(item => `
        <div class="order-item">
            <div class="order-item-info">
                <div class="order-item-name">${item.name}</div>
                <div class="order-item-qty">Quantidade: ${item.quantity}</div>
            </div>
            <div class="order-item-price">${formatNumber(item.price * item.quantity)} 💰</div>
        </div>
    `).join('');

    document.getElementById('order-total').textContent = `${formatNumber(total)} 💰`;
}

function setupEventListeners() {
    // Botão de validar coordenadas
    document.getElementById('validate-coords').addEventListener('click', validateCoordinates);

    // Confirmar pedido
    document.getElementById('confirm-order').addEventListener('click', confirmOrder);
}

function validateCoordinates() {
    const xInput = document.getElementById('coord-x');
    const yInput = document.getElementById('coord-y');

    const x = parseInt(xInput.value);
    const y = parseInt(yInput.value);

    if (isNaN(x) || isNaN(y)) {
        alert('Por favor, insira coordenadas válidas (números).');
        return;
    }

    if (x < 0 || x > 16000 || y < 0 || y > 16000) {
        alert('Coordenadas fora do mapa! (Use valores entre 0 e 16000)');
        return;
    }

    selectedCoords = { x, y };

    document.getElementById('selected-coords').textContent = `X: ${x}, Y: ${y}`;
    document.getElementById('selected-coords').style.color = 'var(--success)';
    document.getElementById('confirm-order').disabled = false;

    // Feedback visual
    const btn = document.getElementById('validate-coords');
    const originalText = btn.textContent;
    btn.textContent = '✅ Validado!';
    btn.classList.add('btn-success');
    setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove('btn-success');
    }, 2000);
}

async function confirmOrder() {
    if (!selectedCoords) {
        alert('Por favor, defina e valide o local de entrega!');
        return;
    }

    const orderTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    const orderData = {
        items: cart.map(item => ({
            code: item.code,
            name: item.name,
            quantity: item.quantity,
            price: item.price
        })),
        coordinates: selectedCoords,
        total: orderTotal
    };

    try {
        const response = await fetch('/api/shop/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });

        const data = await response.json();

        if (data.success) {
            // Limpar carrinho
            localStorage.removeItem('cart');
            localStorage.removeItem('checkout-cart');

            // Redirecionar para confirmação
            localStorage.setItem('order-confirmation', JSON.stringify(data));
            window.location.href = '/order-confirmation';
        } else {
            alert('Erro ao processar pedido: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao confirmar pedido:', error);
        alert('Erro ao processar pedido. Tente novamente.');
    }
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
