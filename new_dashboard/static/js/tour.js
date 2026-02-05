/**
 * BIGODETEXAS - Welcome Tour
 * Guia interativo para novos usuários
 */

const tourSteps = [
    {
        title: window.tourTranslations ? window.tourTranslations.welcomeTitle : "BEM-VINDO AO BIGODETEXAS",
        content: `
            <p>${window.tourTranslations ? window.tourTranslations.welcomeContent1 : "Seu painel de controle completo para o apocalipse."}</p>
            <p>${window.tourTranslations ? window.tourTranslations.welcomeContent2 : "Aqui você gerencia sua sobrevivência, economia e reputação no servidor mais brabo do Xbox."}</p>
            <ul style="text-align: left; margin: 1.5rem auto; display: inline-block;">
                <li>🛡️ ${window.tourTranslations ? window.tourTranslations.baseProtection : "Proteção de Base"}</li>
                <li>💰 ${window.tourTranslations ? window.tourTranslations.realEconomy : "Economia Real"}</li>
                <li>💀 ${window.tourTranslations ? window.tourTranslations.killfeedRanking : "Killfeed & Ranking"}</li>
            </ul>
        `,
        image: null
    },
    {
        title: window.tourTranslations ? window.tourTranslations.unionTitle : "UNIÃO DE CONTAS",
        content: `
            <p style="font-weight: bold; color: #ff4444; margin-bottom: 1rem;">${window.tourTranslations ? window.tourTranslations.unionSubtitle : "O Fim das Contas Fantasmas."}</p>
            <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #107C10; text-align: left;">
                <h4 style="margin: 0 0 0.5rem 0; color: #107C10;">⚠️ ${window.tourTranslations ? window.tourTranslations.whyLinkTitle : "POR QUE VINCULAR?"}</h4>
                <p style="font-size: 0.9rem; margin: 0;">${window.tourTranslations ? window.tourTranslations.whyLinkText1 : "Ao vincular, o sistema UNE seu Discord e Xbox em <strong>UMA ÚNICA IDENTIDADE</strong>."}</p>
                <p style="font-size: 0.9rem; margin: 0.5rem 0 0 0;">${window.tourTranslations ? window.tourTranslations.whyLinkText2 : "Isso evita que você tenha duas contas (uma no site, outra no jogo) e garante que seu dinheiro caia na conta certa."}</p>
            </div>
            <p style="margin-top: 1rem; font-size: 0.9rem; color: #aaa;">${window.tourTranslations ? window.tourTranslations.dontLoseProgress : "Não perca seu progresso. Vincule agora."}</p>
        `
    },
    {
        title: window.tourTranslations ? window.tourTranslations.shopTitle : "LOJA & ECONOMIA",
        content: `
            <p>${window.tourTranslations ? window.tourTranslations.shopContent : "Use seus <strong>DZCoins</strong> para comprar equipamentos e receber no mapa."}</p>
            <div style="display: flex; gap: 1rem; justify-content: center; margin: 1.5rem 0;">
                <div style="text-align: center;">
                    <span style="font-size: 2rem;">🪙</span>
                    <p style="font-size: 0.8rem;">${window.tourTranslations ? window.tourTranslations.earnPlaying : "Ganhe jogando"}</p>
                </div>
                <div style="text-align: center;">
                    <span style="font-size: 2rem;">🛒</span>
                    <p style="font-size: 0.8rem;">${window.tourTranslations ? window.tourTranslations.buySite : "Compre no Site"}</p>
                </div>
                <div style="text-align: center;">
                    <span style="font-size: 2rem;">📍</span>
                    <p style="font-size: 0.8rem;">${window.tourTranslations ? window.tourTranslations.receiveGame : "Receba no Jogo"}</p>
                </div>
            </div>
        `
    },
    {
        title: window.tourTranslations ? window.tourTranslations.readyTitle : "ESTÁ PRONTO?",
        content: `
            <p>${window.tourTranslations ? window.tourTranslations.readyContent1 : "Explore o painel, confira o Ranking e domine o servidor!"}</p>
            <p style="margin-top: 1rem;">${window.tourTranslations ? window.tourTranslations.readyContent2 : "Boa sorte, sobrevivente."}</p>
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
                        <button id="tour-skip" class="btn-text">${window.tourTranslations ? window.tourTranslations.skip : "Pular"}</button>
                        <button id="tour-next" class="btn-primary-tour">${window.tourTranslations ? window.tourTranslations.startTour : "COMEÇAR TOUR ➔"}</button>
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
        bttn.innerHTML = window.tourTranslations ? window.tourTranslations.startTour : 'COMEÇAR TOUR ➔';
        skipBtn.style.visibility = 'visible';
    } else if (index === tourSteps.length - 1) {
        bttn.innerHTML = window.tourTranslations ? window.tourTranslations.verifyAccount : 'VERIFICAR CONTA 🔒';
        skipBtn.style.visibility = 'hidden';
    } else {
        bttn.innerHTML = window.tourTranslations ? window.tourTranslations.next : 'PRÓXIMO ➔';
        skipBtn.style.visibility = 'visible';
        skipBtn.innerText = window.tourTranslations ? window.tourTranslations.close : 'Fechar';
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
