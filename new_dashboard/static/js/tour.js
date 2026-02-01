/**
 * BIGODETEXAS - Welcome Tour
 * Guia interativo para novos usuários
 */

const tourSteps = [
    {
        title: "BEM-VINDO AO BIGODETEXAS",
        content: `
            <p>Seu painel de controle completo para o apocalipse.</p>
            <p>Aqui você gerencia sua sobrevivência, economia e reputação no servidor mais brabo do Xbox.</p>
            <ul style="text-align: left; margin: 1.5rem auto; display: inline-block;">
                <li>🛡️ Proteção de Base</li>
                <li>💰 Economia Real</li>
                <li>💀 Killfeed & Ranking</li>
            </ul>
        `,
        image: null // Optional icon/image
    },
    {
        title: "UNIÃO DE CONTAS",
        content: `
            <p style="font-weight: bold; color: #ff4444; margin-bottom: 1rem;">O Fim das Contas Fantasmas.</p>
            <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #107C10; text-align: left;">
                <h4 style="margin: 0 0 0.5rem 0; color: #107C10;">⚠️ POR QUE VINCULAR?</h4>
                <p style="font-size: 0.9rem; margin: 0;">Ao vincular, o sistema UNE seu Discord e Xbox em <strong>UMA ÚNICA IDENTIDADE</strong>.</p>
                <p style="font-size: 0.9rem; margin: 0.5rem 0 0 0;">Isso evita que você tenha duas contas (uma no site, outra no jogo) e garante que seu dinheiro caia na conta certa.</p>
            </div>
            <p style="margin-top: 1rem; font-size: 0.9rem; color: #aaa;">Não perca seu progresso. Vincule agora.</p>
        `
    },
    {
        title: "LOJA & ECONOMIA",
        content: `
            <p>Use seus <strong>DZCoins</strong> para comprar equipamentos e receber no mapa.</p>
            <div style="display: flex; gap: 1rem; justify-content: center; margin: 1.5rem 0;">
                <div style="text-align: center;">
                    <span style="font-size: 2rem;">🪙</span>
                    <p style="font-size: 0.8rem;">Ganhe jogando</p>
                </div>
                <div style="text-align: center;">
                    <span style="font-size: 2rem;">🛒</span>
                    <p style="font-size: 0.8rem;">Compre no Site</p>
                </div>
                <div style="text-align: center;">
                    <span style="font-size: 2rem;">📍</span>
                    <p style="font-size: 0.8rem;">Receba no Jogo</p>
                </div>
            </div>
        `
    },
    {
        title: "ESTÁ PRONTO?",
        content: `
            <p>Explore o painel, confira o Ranking e domine o servidor!</p>
            <p style="margin-top: 1rem;">Boa sorte, sobrevivente.</p>
        `
    }
];

let currentStep = 0;

function initTour() {
    console.log("BigodeTexas Tour: Iniciando...");
    // Check if seen (DISABLED DEBUG)
    // if (localStorage.getItem('bigode_tour_seen_v2')) {
    //    console.log("BigodeTexas Tour: Já visto, mas forçando exibição.");
    //    // return;
    // }

    // Insert Modal HTML if not exists
    if (!document.getElementById('tour-modal')) {
        const modalHTML = `
            <div id="tour-modal" class="tour-overlay">
                <div class="tour-card">
                    <div class="tour-header">
                        <img src="/static/img/logo_texas.png" alt="Logo" class="tour-logo">
                    </div>
                    <div id="tour-content" class="tour-content">
                        <!-- Dynamic Content -->
                    </div>

                    <div class="tour-dots" id="tour-dots">
                        <!-- Dots -->
                    </div>

                    <div class="tour-actions">
                        <button id="tour-skip" class="btn-text">Pular</button>
                        <button id="tour-next" class="btn-primary-tour">COMEÇAR TOUR ➔</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    // Bind Events
    document.getElementById('tour-next').addEventListener('click', nextStep);
    document.getElementById('tour-skip').addEventListener('click', closeTour);

    // Show initial
    renderStep(0);
}

function renderStep(index) {
    const step = tourSteps[index];
    const contentDiv = document.getElementById('tour-content');
    const dotsDiv = document.getElementById('tour-dots');
    const bttn = document.getElementById('tour-next');
    const skipBtn = document.getElementById('tour-skip');

    // Animate content out
    contentDiv.style.opacity = 0;

    setTimeout(() => {
        contentDiv.innerHTML = `
            <h2 class="tour-title">${step.title}</h2>
            <div class="tour-body">${step.content}</div>
        `;
        contentDiv.style.opacity = 1;
    }, 200);

    // Update Dots
    dotsDiv.innerHTML = tourSteps.map((_, i) =>
        `<span class="tour-dot ${i === index ? 'active' : ''}"></span>`
    ).join('');

    // Update Buttons
    if (index === 0) {
        bttn.innerHTML = 'COMEÇAR TOUR ➔';
        skipBtn.style.visibility = 'visible';
    } else if (index === tourSteps.length - 1) {
        bttn.innerHTML = 'VERIFICAR CONTA 🔒';
        skipBtn.style.visibility = 'hidden';
    } else {
        bttn.innerHTML = 'PRÓXIMO ➔';
        skipBtn.style.visibility = 'visible';
        skipBtn.innerText = 'Fechar';
    }
}

function nextStep() {
    if (currentStep < tourSteps.length - 1) {
        currentStep++;
        renderStep(currentStep);
    } else {
        // Close and Redirect to Profile for Verification
        closeTour();
        window.location.href = '/dashboard';
    }
}

function closeTour() {
    const modal = document.getElementById('tour-modal');
    modal.style.opacity = 0;
    setTimeout(() => {
        modal.remove();
        localStorage.setItem('bigode_tour_seen_v2', 'true');
    }, 500);
}

// Auto Init
document.addEventListener('DOMContentLoaded', () => {
    // Small delay for effect
    setTimeout(initTour, 1000);
});
