// ==================== CONFIRMATION.JS ====================

let deliveryTime = 300; // 5 minutos em segundos

document.addEventListener('DOMContentLoaded', function () {
    loadOrderDetails();
    startCountdown();
});

function loadOrderDetails() {
    const orderData = localStorage.getItem('order-confirmation');
    if (!orderData) {
        window.location.href = '/shop';
        return;
    }

    const order = JSON.parse(orderData);
    const container = document.getElementById('order-details');

    container.innerHTML = `
        <div class="detail-row">
            <span>Coordenadas:</span>
            <span>X: ${order.coordinates.x}, Y: ${order.coordinates.y}</span>
        </div>
        <div class="detail-row">
            <span>Total Pago:</span>
            <span class="text-primary">${formatNumber(order.total)} 💰</span>
        </div>
        <div class="detail-row">
            <span>Tempo de Entrega:</span>
            <span>${order.deliveryTime}</span>
        </div>
    `;
}

function startCountdown() {
    const timerElement = document.getElementById('countdown');

    const interval = setInterval(() => {
        deliveryTime--;

        const minutes = Math.floor(deliveryTime / 60);
        const seconds = deliveryTime % 60;

        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (deliveryTime <= 0) {
            clearInterval(interval);
            timerElement.textContent = 'Entregue!';
            timerElement.style.color = 'var(--success)';
        }
    }, 1000);
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
