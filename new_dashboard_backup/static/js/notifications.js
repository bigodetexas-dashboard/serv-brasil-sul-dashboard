/**
 * Sistema de Notificações Visuais
 * BigodeTexas Dashboard
 */

// Fila de notificações
let notificationQueue = [];
let isShowingNotification = false;

/**
 * Mostra uma notificação de conquista desbloqueada
 */
function showAchievementNotification(achievement) {
    const notification = {
        type: 'achievement',
        icon: achievement.icon || '🏆',
        title: 'Conquista Desbloqueada!',
        name: achievement.title || achievement.name,
        reward: achievement.reward || achievement.points + ' pontos',
        tier: achievement.tier || 'bronze',
        duration: 5000
    };
    
    addToQueue(notification);
}

/**
 * Mostra uma notificação de evento
 */
function showEventNotification(event) {
    const notification = {
        type: 'event',
        icon: event.icon || '📢',
        title: event.title || 'Novo Evento',
        description: event.description || '',
        duration: 4000
    };
    
    addToQueue(notification);
}

/**
 * Mostra uma notificação de compra
 */
function showPurchaseNotification(purchase) {
    const notification = {
        type: 'purchase',
        icon: '🛒',
        title: 'Compra Realizada!',
        description: `${purchase.itemCount} item(ns) - ${purchase.total} DZCoins`,
        duration: 3000
    };
    
    addToQueue(notification);
}

/**
 * Adiciona notificação à fila
 */
function addToQueue(notification) {
    notificationQueue.push(notification);
    
    if (!isShowingNotification) {
        processQueue();
    }
}

/**
 * Processa a fila de notificações
 */
function processQueue() {
    if (notificationQueue.length === 0) {
        isShowingNotification = false;
        return;
    }
    
    isShowingNotification = true;
    const notification = notificationQueue.shift();
    
    displayNotification(notification);
}

/**
 * Exibe a notificação na tela
 */
function displayNotification(notification) {
    // Criar elemento da notificação
    const notifElement = document.createElement('div');
    notifElement.className = `achievement-notification ${notification.type}`;
    
    // Definir cor baseada no tier (para conquistas)
    let tierColor = '#f5576c'; // padrão
    if (notification.tier === 'silver') tierColor = '#c0c0c0';
    if (notification.tier === 'gold') tierColor = '#ffd700';
    if (notification.tier === 'platinum') tierColor = '#e5e4e2';
    if (notification.tier === 'diamond') tierColor = '#b9f2ff';
    
    // HTML da notificação
    if (notification.type === 'achievement') {
        notifElement.innerHTML = `
            <div class="notification-glow" style="background: ${tierColor}"></div>
            <div class="notification-icon">${notification.icon}</div>
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-name">${notification.name}</div>
                <div class="notification-reward">${notification.reward}</div>
            </div>
            <div class="notification-close">×</div>
        `;
    } else {
        notifElement.innerHTML = `
            <div class="notification-icon">${notification.icon}</div>
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-description">${notification.description}</div>
            </div>
            <div class="notification-close">×</div>
        `;
    }
    
    // Adicionar ao body
    document.body.appendChild(notifElement);
    
    // Animar entrada
    setTimeout(() => {
        notifElement.classList.add('show');
    }, 10);
    
    // Botão de fechar
    const closeBtn = notifElement.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        removeNotification(notifElement);
    });
    
    // Auto-remover após duração
    setTimeout(() => {
        removeNotification(notifElement);
    }, notification.duration);
}

/**
 * Remove a notificação
 */
function removeNotification(element) {
    element.classList.remove('show');
    element.classList.add('hide');
    
    setTimeout(() => {
        element.remove();
        processQueue(); // Processar próxima da fila
    }, 300);
}

/**
 * Adiciona estilos CSS para as notificações
 */
function injectNotificationStyles() {
    if (document.getElementById('notification-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        .achievement-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(26, 31, 58, 0.98);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 1.5rem;
            min-width: 350px;
            max-width: 400px;
            display: flex;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            z-index: 10000;
            transform: translateX(450px);
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        
        .achievement-notification.show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .achievement-notification.hide {
            transform: translateX(450px);
            opacity: 0;
        }
        
        .achievement-notification.achievement {
            border-color: rgba(245, 87, 108, 0.5);
        }
        
        .achievement-notification.event {
            border-color: rgba(78, 205, 196, 0.5);
        }
        
        .achievement-notification.purchase {
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        .notification-glow {
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            border-radius: 20px;
            opacity: 0.3;
            filter: blur(10px);
            z-index: -1;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .notification-icon {
            font-size: 3rem;
            flex-shrink: 0;
            animation: bounce 0.6s ease-out;
        }
        
        .notification-content {
            flex: 1;
            min-width: 0;
        }
        
        .notification-title {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.3rem;
        }
        
        .notification-name {
            color: #fff;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .notification-description {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            line-height: 1.4;
        }
        
        .notification-reward {
            color: #ffd700;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .notification-close {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255, 255, 255, 0.5);
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 50%;
        }
        
        .notification-close:hover {
            color: #fff;
            background: rgba(255, 255, 255, 0.1);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.5; }
        }
        
        @keyframes bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        @media (max-width: 768px) {
            .achievement-notification {
                top: 10px;
                right: 10px;
                left: 10px;
                min-width: auto;
                max-width: none;
            }
            
            .achievement-notification.show {
                transform: translateY(0);
            }
            
            .achievement-notification.hide {
                transform: translateY(-150px);
            }
        }
    `;
    
    document.head.appendChild(style);
}

// Inicializar estilos quando o script carregar
injectNotificationStyles();

// Exportar funções globalmente
window.showAchievementNotification = showAchievementNotification;
window.showEventNotification = showEventNotification;
window.showPurchaseNotification = showPurchaseNotification;