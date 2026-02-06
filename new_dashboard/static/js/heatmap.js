// ==================== HEATMAP.JS (Versão Completa) ====================

document.addEventListener('DOMContentLoaded', function () {
    initMap();
    setupControls();
    setupCharts();

    // Carregamento inicial
    loadAllData('24h');
    loadWeaponList();
});

let map;
let heatLayer;
let markersLayer;
let timelineChart;
let hourlyChart;

// Loading State Management
function showMapLoading() {
    document.getElementById('mapLoadingOverlay')?.classList.remove('hidden');
    document.getElementById('mapErrorOverlay')?.classList.add('hidden');
    document.getElementById('mapEmptyOverlay')?.classList.add('hidden');
}

function showMapError() {
    document.getElementById('mapLoadingOverlay')?.classList.add('hidden');
    document.getElementById('mapErrorOverlay')?.classList.remove('hidden');
    document.getElementById('mapEmptyOverlay')?.classList.add('hidden');
}

function showMapEmpty() {
    document.getElementById('mapLoadingOverlay')?.classList.add('hidden');
    document.getElementById('mapErrorOverlay')?.classList.add('hidden');
    document.getElementById('mapEmptyOverlay')?.classList.remove('hidden');
}

function hideMapOverlays() {
    document.getElementById('mapLoadingOverlay')?.classList.add('hidden');
    document.getElementById('mapErrorOverlay')?.classList.add('hidden');
    document.getElementById('mapEmptyOverlay')?.classList.add('hidden');
}

// Configurações do mapa Chernarus (DayZ)
const MAP_CONFIG = {
    minX: 0, maxX: 15360,
    minZ: 0, maxZ: 15360
};

// Estado atual dos filtros
const currentFilters = {
    range: '24h',
    type: 'all',
    weapon: 'all'
};

function initMap() {
    console.log('🗺️ Inicializando mapa Chernarus (Tiles)...');

    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: 0,
        maxZoom: 7,
        zoomControl: false, // Usaremos controles customizados
        attributionControl: false
    });

    // Camada de Tiles (Mosaicos)
    // Estrutura: /static/tiles/{z}/{x}/{y}.png
    L.tileLayer('/static/tiles/{z}/{x}/{y}.png', {
        tileSize: 256,
        minZoom: 0,
        maxZoom: 7,
        noWrap: true,
        tms: false,
        attribution: 'Map data &copy; Bohemia Interactive, iZurvive'
    }).addTo(map);

    // Centralizar o mapa
    // O mapa tem 256x256 unidades no zoom 0
    // Centro = [128, 128] (mas Y é negativo no CRS.Simple padrão)
    map.setView([-128, 128], 2);

    // Configuração do heatmap - Manchas orgânicas de calor (Blobs "Mockup")
    const cfg = {
        radius: getRadiusByZoom(map.getZoom()), // Raio dinâmico
        blur: 0.95,                             // Desfoque alto para efeito orgânico/esfumaçado
        maxOpacity: 0.6,                        // Opacidade suave para sobreposição
        scaleRadius: false,                     // Pixels de tela fixos que ajustamos via zoomend
        useLocalExtrema: false,
        latField: 'lat',
        lngField: 'lng',
        valueField: 'count',
        gradient: {
            0.0: 'rgba(0, 0, 255, 0)',      // Invisível
            0.05: 'rgba(0, 255, 255, 0.5)', // Ciano (Sensibilidade aumentada para 0.05)
            0.2: 'rgba(0, 255, 0, 0.7)',    // Verde
            0.5: 'rgba(255, 255, 0, 0.8)',  // Amarelo
            1.0: 'rgba(255, 0, 0, 1.0)'     // Vermelho
        }
    };

    heatLayer = new HeatmapOverlay(cfg).addTo(map);
    markersLayer = L.layerGroup().addTo(map);

    // Listener para ajustar o raio conforme o zoom (Lógica INVERSA: Zoom+ => Raio-)
    map.on('zoomend', function () {
        const currentZoom = Math.round(map.getZoom());
        const newRadius = getRadiusByZoom(currentZoom);
        console.log(`🔍 Precisão: Zoom ${currentZoom} | Raio: ${newRadius}px`);

        // Atualizar options do plugin e forçar redraw
        heatLayer.cfg.radius = newRadius;

        if (lastHeatmapResult) {
            updateHeatmap(lastHeatmapResult);
        }
    });

    // Controles de Zoom Customizados
    document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
    document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());
    document.getElementById('resetView').addEventListener('click', () => {
        map.setView([-128, 128], 2);
    });

    // Carregar estatísticas do banner inicial
    loadHeroStats('24h');
}

/**
 * Lógica do Mockup: O raio DIMINUI conforme o zoom AUMENTA para mostrar precisão.
 * @param {number} zoom
 * @returns {number}
 */
function getRadiusByZoom(zoom) {
    const zoomMap = {
        0: 60,
        1: 50,
        2: 38,
        3: 25,
        4: 20,
        5: 15,
        6: 12, // Aumentado de 7 para 12 para melhor visibilidade
        7: 10  // Aumentado de 5 para 10 para melhor visibilidade
    };
    return zoomMap[zoom] || 38;
}

/**
 * Carrega os dados do Hero Stats Banner superior
 */
async function loadHeroStats(range) {
    try {
        const response = await fetch(`/api/heatmap/hero_stats?range=${range}`);
        const result = await response.json();

        if (result.success) {
            document.getElementById('heroTotalKills').innerText = result.total_kills || 0;
            document.getElementById('heroKillsToday').innerText = result.kills_today || 0;
            document.getElementById('heroTopWeapon').innerText = result.top_weapon || '-';
            document.getElementById('heroTopPlayer').innerText = result.top_player || '-';
            document.getElementById('heroPeakHour').innerText = result.peak_hour ? result.peak_hour + 'h' : '-';
            document.getElementById('heroHottestZone').innerText = result.hottest_zone || '-';
        }
    } catch (error) {
        console.error('Erro ao carregar Hero Stats:', error);
    }
}

function setupCharts() {
    // Configuração comum para gráficos dark mode
    Chart.defaults.color = '#a0a0a0';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

    // Timeline Chart
    const ctxTimeline = document.getElementById('timelineChart').getContext('2d');
    timelineChart = new Chart(ctxTimeline, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: window.heatmapTranslations.mortesPvP,
                borderColor: '#ff4757',
                backgroundColor: 'rgba(255, 71, 87, 0.2)',
                data: [],
                fill: true,
                tension: 0.4
            }, {
                label: window.heatmapTranslations.mortesPvE,
                borderColor: '#2ed573',
                backgroundColor: 'rgba(46, 213, 115, 0.2)',
                data: [],
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Hourly Chart
    const ctxHourly = document.getElementById('hourlyChart').getContext('2d');
    hourlyChart = new Chart(ctxHourly, {
        type: 'bar',
        data: {
            labels: Array.from({ length: 24 }, (_, i) => `${i}h`),
            datasets: [{
                label: window.heatmapTranslations.atividadeHora,
                backgroundColor: '#ffa502',
                data: []
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function setupControls() {
    // Filtros de Tempo
    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.control-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilters.range = e.target.dataset.time;
            loadAllData(currentFilters.range);
        });
    });

    // Filtros de Tipo
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilters.type = e.target.dataset.type;
            // Recarregar apenas o heatmap com filtro local (simulado por enquanto)
            // Idealmente o backend filtraria, mas vamos recarregar tudo por simplicidade
            loadAllData(currentFilters.range);
        });
    });

    // Filtro de Arma
    document.getElementById('weaponFilter').addEventListener('change', (e) => {
        currentFilters.weapon = e.target.value;
        // TODO: Implementar filtro de arma no backend
        console.log('Filtro de arma alterado:', currentFilters.weapon);
    });
}

let lastHeatmapResult = null; // Guardar último resultado para re-render no zoom

function loadAllData(range) {
    loadHeroStats(range);
    loadHeatmapData(range);
    loadTopLocations(range);
    loadTimelineData(range);
    loadHourlyData(range);
    loadWeaponStats(range);
}

async function loadHeatmapData(range) {
    showMapLoading();
    try {
        const response = await fetch(`/api/heatmap?range=${range}&grid=50`);
        const result = await response.json();

        if (result.success) {
            lastHeatmapResult = result;
            updateHeatmap(result);

            // Atualizar Card de Total
            document.getElementById('totalDeaths').innerText = result.total_events;
            hideMapOverlays();
        } else {
            showMapError();
        }
    } catch (error) {
        console.error('Erro heatmap:', error);
        showMapError();
    }
}

/**
 * Atualiza os dados do layer de heatmap
 * @param {Object} result
 */
function updateHeatmap(result) {
    if (!result.points || result.points.length === 0) {
        showMapEmpty();
        return;
    }

    // Calcular o valor máximo real para escala dinâmica
    const maxCount = Math.max(...result.points.map(p => p.count));
    // Se tiver pouca atividade, usamos um max menor para as cores aparecerem vibrantes
    const dynamicMax = Math.max(maxCount, 5);

    const heatmapData = {
        max: dynamicMax,
        data: result.points.map(point => {
            const [lat, lng] = gameToLatLng(point.x, point.z);
            return { lat, lng, count: point.count };
        })
    };

    heatLayer.setData(heatmapData);
}

async function loadTopLocations(range) {
    try {
        const response = await fetch(`/api/heatmap/top_locations?range=${range}`);
        const result = await response.json();

        if (result.success) {
            updateTopLocationsUI(result.locations);
            updateMapMarkers(result.locations);
        }
    } catch (error) {
        console.error('Erro top locations:', error);
    }
}

async function loadTimelineData(range) {
    try {
        const response = await fetch(`/api/heatmap/timeline?range=${range}`);
        const result = await response.json();

        if (result.success) {
            timelineChart.data.labels = result.timeline.map(t => {
                const date = new Date(t.period);
                return range === '24h' ?
                    date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
                    date.toLocaleDateString();
            });
            timelineChart.data.datasets[0].data = result.timeline.map(t => t.pvp);
            timelineChart.data.datasets[1].data = result.timeline.map(t => t.pve);
            timelineChart.update();

            // Calcular porcentagens
            const totalPvP = result.timeline.reduce((acc, curr) => acc + curr.pvp, 0);
            const totalPvE = result.timeline.reduce((acc, curr) => acc + curr.pve, 0);
            const total = totalPvP + totalPvE;

            if (total > 0) {
                document.getElementById('pvpPercent').innerText = Math.round((totalPvP / total) * 100) + '%';
                document.getElementById('pvePercent').innerText = Math.round((totalPvE / total) * 100) + '%';
            }
        }
    } catch (error) {
        console.error('Erro timeline:', error);
    }
}

async function loadHourlyData(range) {
    try {
        const response = await fetch(`/api/heatmap/hourly?range=${range}`);
        const result = await response.json();

        if (result.success) {
            hourlyChart.data.datasets[0].data = result.hourly;
            hourlyChart.update();
        }
    } catch (error) {
        console.error('Erro hourly:', error);
    }
}

async function loadWeaponStats(range) {
    try {
        const response = await fetch(`/api/heatmap/weapons?range=${range}`);
        const result = await response.json();

        if (result.success && result.weapons.length > 0) {
            const topWeapon = result.weapons[0];
            document.getElementById('topWeapon').innerText = topWeapon.name;
        } else {
            document.getElementById('topWeapon').innerText = '-';
        }
    } catch (error) {
        console.error('Erro weapons:', error);
    }
}

async function loadWeaponList() {
    try {
        const response = await fetch('/api/heatmap/weapons?range=30d'); // Pegar histórico maior
        const result = await response.json();

        if (result.success) {
            const select = document.getElementById('weaponFilter');
            result.weapons.forEach(w => {
                const option = document.createElement('option');
                option.value = w.name;
                option.innerText = `${w.name} (${w.count})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro lista armas:', error);
    }
}

function updateTopLocationsUI(locations) {
    const grid = document.getElementById('topLocations');
    if (!grid) return;

    grid.innerHTML = '';
    locations.forEach((loc, index) => {
        const dangerLevel = loc.deaths > 50 ? 'high' : loc.deaths > 20 ? 'medium' : 'low';
        const dangerText = loc.deaths > 50 ? window.heatmapTranslations.extremo : loc.deaths > 20 ? window.heatmapTranslations.alto : window.heatmapTranslations.medio;

        const card = document.createElement('div');
        card.className = 'location-card';
        card.innerHTML = `
            <span class="rank">#${index + 1}</span>
            <div class="loc-info">
                <h3>${loc.location_name || `${window.heatmapTranslations.zona} ${index + 1}`}</h3>
                <p>${loc.deaths} ${window.heatmapTranslations.mortes}</p>
            </div>
            <div class="danger-level ${dangerLevel}">${dangerText}</div>
        `;

        card.addEventListener('click', () => {
            const [lat, lng] = gameToLatLng(loc.center_x, loc.center_z);
            map.setView([lat, lng], 0);
        });

        grid.appendChild(card);
    });
}

function updateMapMarkers(locations) {
    // DESABILITADO: Não mostrar círculos no mapa
    // Apenas o heatmap gradiente será exibido (verde-amarelo-laranja-vermelho)
    // conforme design do mockup
    markersLayer.clearLayers();

    // Código comentado - círculos removidos
    /*
    locations.forEach((loc, index) => {
        const [lat, lng] = gameToLatLng(loc.center_x, loc.center_z);
        const marker = L.circleMarker([lat, lng], {
            radius: 10 + (5 - index) * 2,
            fillColor: index === 0 ? '#ff0000' : '#ffaa00',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.7
        });

        marker.bindPopup(`<b>${loc.location_name || 'Zona Quente'}</b><br>Mortes: ${loc.deaths}`);
        marker.addTo(markersLayer);
    });
    */
}

function gameToLatLng(gameX, gameZ) {
    // Normalizar coordenadas do jogo (0-15360) para 0-1
    const nx = (gameX - MAP_CONFIG.minX) / (MAP_CONFIG.maxX - MAP_CONFIG.minX);
    const nz = (gameZ - MAP_CONFIG.minZ) / (MAP_CONFIG.maxZ - MAP_CONFIG.minZ);

    // Leaflet CRS.Simple usa coordenadas relativas ao zoom 0 (256px)
    // Não escalar para maxZoom pois os tiles já fazem isso automaticamente
    const mapSize = 256;

    const px = nx * mapSize;
    const py = (1 - nz) * mapSize; // Inverter Y (DayZ usa bottom-left origin)

    // Leaflet CRS.Simple: lat = -y, lng = x
    return [-py, px];
}
