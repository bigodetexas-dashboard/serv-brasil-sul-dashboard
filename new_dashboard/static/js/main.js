// ==================== MAIN.JS ====================
// Carrega estatísticas do servidor

document.addEventListener('DOMContentLoaded', function () {
    loadStats();
    addDiscordFloat();
    initHamburgerMenu();
});

function addDiscordFloat() {
    if (document.querySelector('.discord-float')) return;

    const discordBtn = document.createElement('a');
    discordBtn.href = '/login'; // Leva para o Login com Discord
    discordBtn.className = 'discord-float';
    discordBtn.target = '_blank';
    discordBtn.innerHTML = '<i class="ri-discord-fill"></i>';
    discordBtn.title = 'Entrar no Discord';

    document.body.appendChild(discordBtn);
}

async function loadStats() {
    const statsContainer = document.getElementById('total-players');
    if (!statsContainer) return; // Só carrega se estiver na home com os contadores

    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        // Anima os números
        animateValue('total-players', 0, data.total_players || 0, 1500);
        animateValue('total-kills', 0, data.total_kills || 0, 1500);
        animateValue('total-coins', 0, data.total_coins || 0, 1500);
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

function animateValue(id, start, end, duration) {
    const element = document.getElementById(id);
    if (!element) return;

    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            element.textContent = formatNumber(end);
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(Math.floor(current));
        }
    }, 16);
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// ==================== HAMBURGER MENU ====================
function initHamburgerMenu() {
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const navbarMenu = document.getElementById('navbar-menu');

    if (!hamburgerMenu || !navbarMenu) return;

    // Toggle menu
    hamburgerMenu.addEventListener('click', function () {
        hamburgerMenu.classList.toggle('active');
        navbarMenu.classList.toggle('active');
    });

    // Close menu when clicking on a link
    const menuLinks = navbarMenu.querySelectorAll('.navbar-link');
    menuLinks.forEach(link => {
        link.addEventListener('click', function () {
            hamburgerMenu.classList.remove('active');
            navbarMenu.classList.remove('active');
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function (event) {
        if (!hamburgerMenu.contains(event.target) && !navbarMenu.contains(event.target)) {
            hamburgerMenu.classList.remove('active');
            navbarMenu.classList.remove('active');
        }
    });
}
