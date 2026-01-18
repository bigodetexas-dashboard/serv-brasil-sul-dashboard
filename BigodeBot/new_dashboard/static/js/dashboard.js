// ==================== DASHBOARD.JS ====================
// Dashboard do usuário

document.addEventListener('DOMContentLoaded', function () {
    loadUserProfile();
    loadUserStats();
    loadBounties();
    loadClanWar();
    loadClanStatus();
    loadInvites();
    setupLogout();
});

async function loadClanStatus() {
    try {
        const response = await fetch('/api/clan/my');
        const data = await response.json();
        const container = document.getElementById('clan-status-container');
        if (!container) return;

        if (data.has_clan) {
            const clan = data.info;
            container.innerHTML = `
                <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; border-left: 4px solid var(--accent); display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h3 style="margin: 0; font-size: 1.2rem;">${clan.name}</h3>
                        <p style="margin: 5px 0 0; color: #aaa; font-size: 0.9rem;">Função: ${clan.role.toUpperCase()}</p>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <a href="/clan" class="btn btn-sm btn-primary">Gerenciar</a>
                        ${clan.role !== 'leader' ?
                    `<button onclick="leaveClanDashboard()" class="btn btn-sm" style="background: #ef4444; color: white;">Sair</button>` : ''
                }
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div style="text-align: center; color: #888; padding: 20px; border: 1px dashed #444; border-radius: 8px;">
                    Você não pertence a nenhum clã.
                    <a href="/clan" style="color: var(--accent); text-decoration: none; margin-left: 5px;">Criar ou Buscar Clã</a>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar status do clã:', error);
    }
}

async function loadInvites() {
    try {
        const response = await fetch('/api/user/invites');
        const invites = await response.json();
        const container = document.getElementById('invites-container');
        const list = document.getElementById('invites-list');

        if (!container || !list) return;

        if (invites && invites.length > 0) {
            container.style.display = 'block';
            let html = '';
            invites.forEach(invite => {
                html += `
                    <div style="background: rgba(0, 0, 0, 0.3); padding: 10px 15px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; border: 1px solid var(--accent);">
                        <div>
                            <strong style="color: white;">${invite.clan_name}</strong>
                            <div style="font-size: 0.8rem; color: #bbb;">Convite pendente</div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button onclick="respondInvite(${invite.id}, true)" class="btn btn-sm" style="background: #22c55e; color: white;">Aceitar</button>
                            <button onclick="respondInvite(${invite.id}, false)" class="btn btn-sm" style="background: #ef4444; color: white;">Recusar</button>
                        </div>
                    </div>
                `;
            });
            list.innerHTML = html;
        } else {
            container.style.display = 'none';
        }
    } catch (e) {
        console.error('Erro ao carregar convites:', e);
    }
}

async function respondInvite(inviteId, accept) {
    if (!confirm(accept ? "Aceitar convite?" : "Recusar convite?")) return;

    try {
        const response = await fetch('/api/clan/invite/respond', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ invite_id: inviteId, accept: accept })
        });

        if (response.ok) {
            alert(accept ? "Convite aceito!" : "Convite recusado.");
            loadInvites();
            loadClanStatus(); // Refresh status if accepted
        } else {
            alert("Erro ao processar convite.");
        }
    } catch (e) {
        console.error(e);
    }
}

async function leaveClanDashboard() {
    if (!confirm('Tem certeza que deseja sair do clã?')) return;
    try {
        const response = await fetch('/api/clan/leave', { method: 'POST' });
        if (response.ok) {
            loadClanStatus();
            alert("Você saiu do clã.");
        } else {
            const data = await response.json();
            alert(data.error || 'Erro ao sair.');
        }
    } catch (e) {
        console.error(e);
    }
}

async function loadClanWar() {
    try {
        const response = await fetch('/api/clan/my');
        const data = await response.json();
        const section = document.getElementById('clan-war-section');
        const container = document.getElementById('clan-war-container');

        if (!section || !container) return;

        if (data.has_clan && data.war) {
            section.style.display = 'block';
            const war = data.war;
            const info = data.info;
            const isClan1 = war.clan1_id === info.id;
            const myPoints = isClan1 ? war.clan1_points : war.clan2_points;
            const enemyPoints = isClan1 ? war.clan2_points : war.clan1_points;

            container.innerHTML = `
                <div class="war-card">
                    <div class="war-score-container">
                        <div class="war-team">
                            <div class="war-team-name">${info.name}</div>
                            <div class="war-points">${myPoints}</div>
                            <div style="font-size: 0.8rem; color: #888;">SEU CLÃ</div>
                        </div>
                        <div class="war-vs">VS</div>
                        <div class="war-team">
                            <div class="war-team-name">${war.enemy_name}</div>
                            <div class="war-points enemy">${enemyPoints}</div>
                            <div style="font-size: 0.8rem; color: #888;">INIMIGO</div>
                        </div>
                    </div>
                    <div class="war-expiry">
                        <i class="ri-time-line"></i>
                        Expira em: ${new Date(war.expires_at).toLocaleString('pt-BR')}
                    </div>
                </div>
            `;
        } else {
            section.style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao carregar guerra de clãs:', error);
    }
}

async function loadBounties() {
    try {
        const response = await fetch('/api/bounties');
        const data = await response.json();
        const container = document.getElementById('bounties-container');

        if (!container) return;

        if (!data || data.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhuma recompensa ativa no momento.</p>';
            return;
        }

        let html = '';
        data.forEach(bounty => {
            html += `
                <div class="bounty-card">
                    <div>
                        <div style="font-weight: bold; color: #ff4d4d; font-family: 'Oswald', sans-serif; letter-spacing: 1px;">ALVO: ${bounty.victim_gamertag}</div>
                        <div style="font-size: 0.8rem; color: #888;">Postado em: ${new Date(bounty.created_at).toLocaleDateString('pt-BR')}</div>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #ffd700; font-family: 'Bebas Neue', sans-serif;">
                        ${formatNumber(bounty.amount)} 💰
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch (error) {
        console.error('Erro ao carregar bounties:', error);
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch('/api/user/profile');
        const data = await response.json();

        const userName = document.getElementById('user-name');
        const userGamertag = document.getElementById('user-gamertag');
        const userBalance = document.getElementById('user-balance');
        const userAvatar = document.getElementById('user-avatar');

        if (userName) userName.textContent = data.username || 'Usuário';
        if (userGamertag) userGamertag.textContent = data.gamertag ? `Xbox: ${data.gamertag}` : 'Xbox: Não vinculado';
        if (userBalance) userBalance.textContent = formatNumber(data.balance || 0);

        // Avatar
        if (data.avatar && userAvatar) {
            userAvatar.src = data.avatar;
        }

        // Selo Xbox Verificado
        const xboxBadge = document.getElementById('xbox-verified-badge');
        const verificationWarning = document.getElementById('verification-warning');

        const isVerified = data.xbox_connected_to_discord;

        if (xboxBadge) {
            xboxBadge.style.display = isVerified ? 'inline-flex' : 'none';
        }

        if (verificationWarning) {
            verificationWarning.style.display = isVerified ? 'none' : 'block';
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
        const statKills = document.getElementById('stat-kills');
        const statDeaths = document.getElementById('stat-deaths');
        const statKD = document.getElementById('stat-kd');
        const statZombies = document.getElementById('stat-zombies');
        const statStreak = document.getElementById('stat-streak');

        if (statKills) statKills.textContent = data.kills || 0;
        if (statDeaths) statDeaths.textContent = data.deaths || 0;
        if (statKD) statKD.textContent = data.kd || '0.00';
        if (statZombies) statZombies.textContent = data.zombies || 0;
        if (statStreak) statStreak.textContent = data.streak || 0;

        // Sobrevivência
        const statPlaytime = document.getElementById('stat-playtime');
        const statDistance = document.getElementById('stat-distance');
        const statDriving = document.getElementById('stat-driving');
        const statBuilt = document.getElementById('stat-built');

        if (statPlaytime) statPlaytime.textContent = formatTime(data.total_playtime || 0);
        if (statDistance) statDistance.textContent = formatDistance(data.distance_walked || 0);
        if (statDriving) statDriving.textContent = formatDistance(data.vehicle_distance || 0);
        if (statBuilt) statBuilt.textContent = data.buildings_built || 0;
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Helpers
function formatNumber(num) {
    if (!num) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function formatTime(seconds) {
    if (!seconds) return '0h 0m';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

function formatDistance(meters) {
    if (!meters) return '0km';
    return (meters / 1000).toFixed(2) + 'km';
}

// ==================== ONBOARDING TUTORIAL LOGIC ==================== //

let currentSlide = 1;
const totalSlides = 4;

document.addEventListener('DOMContentLoaded', () => {
    // Check if tutorial seen
    if (!localStorage.getItem('tutorial_completed_v1')) {
        setTimeout(() => {
            const modal = document.getElementById('onboarding-modal');
            if (modal) modal.style.display = 'flex';
        }, 1000); // Small delay for effect
    }
});

function updateSlides() {
    // Hide all
    document.querySelectorAll('.tutorial-slide').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));

    // Show current
    const activeSlide = document.querySelector(`.tutorial-slide[data-step="${currentSlide}"]`);
    const activeDot = document.getElementById(`step-dot-${currentSlide}`);

    if (activeSlide) activeSlide.classList.add('active');
    if (activeDot) activeDot.classList.add('active');
}

window.nextSlide = function () {
    if (currentSlide < totalSlides) {
        currentSlide++;
        updateSlides();
    }
};

window.prevSlide = function () {
    if (currentSlide > 1) {
        currentSlide--;
        updateSlides();
    }
};

window.finishTutorial = function () {
    localStorage.setItem('tutorial_completed_v1', 'true');
    closeTutorial();

    // Optional: Celebrate
    // confetti or toast message
};

window.closeTutorial = function () {
    const modal = document.getElementById('onboarding-modal');
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => modal.style.display = 'none', 500);
    }
    // Assume closed = skipped/finished for user annoyance prevention
    localStorage.setItem('tutorial_completed_v1', 'true');
};
