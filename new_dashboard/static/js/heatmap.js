// ==================== HEATMAP.JS ====================

document.addEventListener('DOMContentLoaded', function () {
    initMap();
    setupControls();
});

let map;
let heatLayer;

// Dados simulados de PvP (X, Z, Intensidade)
// No futuro, isso virá do banco de dados (API)
const heatData = [
    // NWAF (Alta intensidade)
    [4500, 10000, 1.0], [4600, 10100, 0.9], [4550, 10050, 0.8], [4700, 9900, 0.7],
    [4400, 10200, 0.6], [4800, 9800, 0.5], [4500, 10000, 1.0], [4600, 10100, 0.9],

    // Tisy (Alta intensidade)
    [1500, 14000, 1.0], [1600, 14100, 0.9], [1550, 14050, 0.8], [1700, 13900, 0.7],

    // Cherno (Média intensidade)
    [6500, 2500, 0.6], [6600, 2600, 0.5], [6700, 2400, 0.4], [6400, 2700, 0.3],

    // Berezino (Média intensidade)
    [12000, 9000, 0.6], [12100, 9100, 0.5], [11900, 8900, 0.4],

    // Pontos aleatórios (Baixa intensidade)
    [8000, 8000, 0.2], [7500, 7500, 0.2], [9000, 6000, 0.2], [3000, 5000, 0.2]
];

function initMap() {
    // Configuração do mapa (Chernarus)
    // Coordenadas do DayZ são (0,0) no canto inferior esquerdo até (15360, 15360)
    // Leaflet usa (Latitude, Longitude), então precisamos converter

    // Fator de conversão simples para visualização
    const mapSize = 15360;
    const center = [mapSize / 2, mapSize / 2];

    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -3,
        maxZoom: 2,
        zoomControl: true,
        attributionControl: false
    });

    // Limites do mapa
    const bounds = [[0, 0], [mapSize, mapSize]];

    // Adicionar imagem do mapa (usando iZurvive ou similar se disponível, ou tiles)
    // Por enquanto, vamos usar uma cor de fundo sólida para simular
    // Idealmente, usaríamos tiles do iZurvive aqui

    // Usando tiles do iZurvive (Chernarus+)
    L.tileLayer('https://tiles.izurvive.com/maps/chernarusplus/{z}/{x}/{y}.png', {
        minZoom: 0,
        maxZoom: 5,
        noWrap: true,
        tms: true // iZurvive usa TMS (y invertido)
    }).addTo(map);

    map.fitBounds(bounds);
    map.setView([7680, 7680], -1); // Centro do mapa

    // Converter coordenadas DayZ (X, Z) para Leaflet (Lat, Lng)
    // No Leaflet Simple CRS: [y, x]
    // DayZ: X (Leste-Oeste), Z (Norte-Sul) -> Leaflet: [Z, X]

    const formattedHeatData = heatData.map(point => {
        // [Z, X, Intensidade]
        // Inverter Y (Z) porque o mapa pode estar invertido dependendo da fonte
        return [point[1], point[0], point[2]];
    });

    // Adicionar camada de calor
    heatLayer = L.heatLayer(formattedHeatData, {
        radius: 25,
        blur: 15,
        maxZoom: 1,
        max: 1.0,
        gradient: {
            0.4: 'blue',
            0.6: 'lime',
            1.0: 'red'
        }
    }).addTo(map);
}

function setupControls() {
    const buttons = document.querySelectorAll('.control-btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remover classe active de todos
            buttons.forEach(b => b.classList.remove('active'));
            // Adicionar ao clicado
            btn.classList.add('active');

            // Simular mudança de dados
            const timeRange = btn.dataset.time;
            updateHeatmap(timeRange);
        });
    });
}

function updateHeatmap(range) {
    // Aqui faríamos uma chamada API para buscar novos dados
    console.log(`Carregando dados para: ${range}`);

    // Simulação: mudar aleatoriamente a intensidade para parecer dinâmico
    const newData = heatData.map(point => [
        point[1],
        point[0],
        Math.random() // Intensidade aleatória
    ]);

    heatLayer.setLatLngs(newData);
}
