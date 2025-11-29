// ==================== LEADERBOARD.JS ====================
// Sistema de rankings

let currentRanking = 'richest';
let rankingsData = {};

const rankingConfig = {
    richest: { label: 'DZCoins', icon: '💰', field: 'balance' },
    kills: { label: 'Kills', icon: '🔫', field: 'kills' },
    deaths: { label: 'Deaths', icon: '💀', field: 'deaths' },
    kd: { label: 'K/D', icon: '📊', field: 'kd' },
    zombies: { label: 'Zumbis Mortos', icon: '🧟', field: 'zombie_kills' },
    distance: { label: 'Metros Andados', icon: '🚶', field: 'distance_walked' },
    vehicle: { label: 'Metros de Veículo', icon: '🚗', field: 'vehicle_distance' },
    reconnects: { label: 'Reconexões', icon: '🔄', field: 'reconnects' },
    builder: { label: 'Construções', icon: '🏗️', field: 'buildings_built' },
    raider: { label: 'Cadeados Rodados', icon: '🔓', field: 'locks_picked' }
};

document.addEventListener('DOMContentLoaded', function () {
    loadRankings();
    setupEventListeners();
});

function setupEventListeners() {
    document.querySelectorAll('.ranking-tab').forEach(tab => {
        tab.addEventListener('click', function () {
            document.querySelectorAll('.ranking-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentRanking = this.dataset.ranking;
            renderRanking();
        });
    });
}

async function loadRankings() {
    try {
        const response = await fetch('/api/leaderboard');
        rankingsData = await response.json();
        renderRanking();
    } catch (error) {
        console.error('Erro ao carregar rankings:', error);
        renderEmptyRanking();
    }
}

function renderRanking() {
    const config = rankingConfig[currentRanking];
    const data = rankingsData[currentRanking] || [];

    // Pódio (Top 3)
    if (data.length >= 1) {
        updatePodiumPlace(1, data[0], config);
    }
    if (data.length >= 2) {
        updatePodiumPlace(2, data[1], config);
    }
    if (data.length >= 3) {
        updatePodiumPlace(3, data[2], config);
    }

    // Lista (4º em diante)
    const listContainer = document.getElementById('ranking-list');
    const remaining = data.slice(3);

    if (remaining.length === 0) {
        listContainer.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 2rem;">Nenhum dado disponível</p>';
        return;
    }

    listContainer.innerHTML = remaining.map((player, index) => `
        <div class="ranking-item">
            <div class="ranking-position">${index + 4}</div>
            <div class="ranking-avatar">${getPlayerAvatar(player.name)}</div>
            <div class="ranking-info">
                <div class="ranking-name">${player.name}</div>
                <div class="ranking-stats">${getPlayerStats(player)}</div>
            </div>
            <div class="ranking-value">${formatValue(player.value, currentRanking)}</div>
        </div>
    `).join('');
}

function updatePodiumPlace(position, player, config) {
    const element = document.getElementById(`rank-${position}`);
    if (!element || !player) {
        element.querySelector('.player-name').textContent = '-';
        element.querySelector('.player-value').textContent = '0';
        return;
    }

    element.querySelector('.player-name').textContent = player.name;
    element.querySelector('.player-value').textContent = formatValue(player.value, currentRanking);
}

function getPlayerAvatar(name) {
    // Pega primeira letra do nome
    return name.charAt(0).toUpperCase();
}

function getPlayerStats(player) {
    // Retorna estatísticas adicionais do jogador
    return `Jogador desde ${new Date().getFullYear()}`;
}

function formatValue(value, ranking) {
    if (ranking === 'kd') {
        return value.toFixed(2);
    } else if (ranking === 'distance' || ranking === 'vehicle') {
        return `${formatNumber(Math.floor(value))}m`;
    } else {
        return formatNumber(value);
    }
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function renderEmptyRanking() {
    document.getElementById('ranking-list').innerHTML = `
        <p style="text-align: center; color: var(--text-muted); padding: 2rem;">
            Carregando rankings...
        </p>
    `;
}
