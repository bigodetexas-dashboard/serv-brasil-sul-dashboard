// ==================== DASHBOARD.JS ====================
// Dashboard do usuário

document.addEventListener('DOMContentLoaded', function () {
    loadUserProfile();
    loadUserStats();
    loadPurchaseHistory();
    loadAchievements();
    setupLogout();
});

async function loadUserProfile() {
    try {
        const response = await fetch('/api/user/profile');
        const data = await response.json();

        document.getElementById('user-name').textContent = data.username || 'Usuário';
        document.getElementById('user-gamertag').textContent = data.gamertag ? `Xbox: ${data.gamertag}` : 'Xbox: Não vinculado';
        document.getElementById('user-balance').textContent = formatNumber(data.balance || 0);

        // Avatar
        if (data.avatar) {
            document.getElementById('user-avatar').style.backgroundImage = `url(${data.avatar})`;
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
    }
}

async function loadUserStats() {
    try {
        const response = await fetch('/api/user/stats');
        const data = await response.json();

        // Combate
        document.getElementById('stat-kills').textContent = data.kills || 0;
        document.getElementById('stat-deaths').textContent = data.deaths || 0;
        document.getElementById('stat-kd').textContent = calculateKD(data.kills, data.deaths);
        document.getElementById('stat-zombies').textContent = data.zombie_kills || 0;

        // Sobrevivência
        document.getElementById('stat-lifetime').textContent = formatTime(data.lifetime || 0);
        document.getElementById('stat-distance').textContent = formatDistance(data.distance_walked || 0);
        document.getElementById('stat-vehicle').textContent = formatDistance(data.vehicle_distance || 0);
        document.getElementById('stat-reconnects').textContent = data.reconnects || 0;

        // Construção
        document.getElementById('stat-buildings').textContent = data.buildings_built || 0;
        document.getElementById('stat-locks').textContent = data.locks_picked || 0;
        document.getElementById('stat-base').textContent = data.has_base ? 'Sim' : 'Não';

        // Preferências
        document.getElementById('stat-weapon').textContent = data.favorite_weapon || '-';
        document.getElementById('stat-city').textContent = data.favorite_city || '-';
        document.getElementById('stat-playtime').textContent = formatTime(data.total_playtime || 0);
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

async function loadPurchaseHistory() {
    try {
        const response = await fetch('/api/user/purchases');
        const data = await response.json();

        const container = document.getElementById('purchases-list');

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🛒</div>
                    <p>Nenhuma compra realizada ainda</p>
                </div>
            `;
            return;
        }

        container.innerHTML = data.map(purchase => `
            <div class="purchase-item">
                <div class="purchase-info">
                    <div class="purchase-date">${formatDate(purchase.date)}</div>
                    <div class="purchase-items">${purchase.items_count} itens - ${formatNumber(purchase.total)} 💰</div>
                </div>
                <div class="purchase-status ${purchase.status}">
                    ${purchase.status === 'delivered' ? '✅ Entregue' : '⏳ Pendente'}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar compras:', error);
    }
}

async function loadAchievements() {
    try {
        const response = await fetch('/api/user/achievements');
        const data = await response.json();

        const container = document.getElementById('achievements-grid');

        const achievements = [
            { id: 'first_kill', icon: '🎯', name: 'Primeira Morte', desc: 'Mate seu primeiro jogador', unlocked: data.first_kill },
            { id: 'survivor', icon: '🏃', name: 'Sobrevivente', desc: 'Sobreviva por 24h', unlocked: data.survivor },
            { id: 'rich', icon: '💰', name: 'Milionário', desc: 'Acumule 10.000 DZCoins', unlocked: data.rich },
            { id: 'builder', icon: '🏗️', name: 'Construtor', desc: 'Construa 10 bases', unlocked: data.builder },
            { id: 'hunter', icon: '🧟', name: 'Caçador', desc: 'Mate 1000 zumbis', unlocked: data.hunter },
            { id: 'explorer', icon: '🗺️', name: 'Explorador', desc: 'Ande 100km', unlocked: data.explorer }
        ];

        container.innerHTML = achievements.map(ach => `
            <div class="achievement-card ${ach.unlocked ? 'unlocked' : 'locked'}">
                <div class="achievement-icon">${ach.icon}</div>
                <div class="achievement-name">${ach.name}</div>
                <div class="achievement-desc">${ach.desc}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar conquistas:', error);
    }
}

function setupLogout() {
    document.getElementById('logout-btn').addEventListener('click', function () {
        if (confirm('Deseja realmente sair?')) {
            window.location.href = '/logout';
        }
    });
}

// Utility functions
function calculateKD(kills, deaths) {
    if (deaths === 0) return kills.toFixed(2);
    return (kills / deaths).toFixed(2);
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    return `${hours}h`;
}

function formatDistance(meters) {
    if (meters >= 1000) {
        return `${(meters / 1000).toFixed(1)}km`;
    }
    return `${meters}m`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
