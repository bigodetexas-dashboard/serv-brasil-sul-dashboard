// realtime.js
// Handles WebSocket connections for live updates

document.addEventListener('DOMContentLoaded', () => {
    // Check if socket.io is loaded
    if (typeof io === 'undefined') {
        console.warn('Socket.IO not loaded');
        return;
    }

    const socket = io();

    socket.on('connect', () => {
        console.log('🔗 Connected to Real-Time Server');
    });

    socket.on('disconnect', () => {
        console.log('🔌 Disconnected from Server');
    });

    // Killfeed Updates
    socket.on('killfeed_update', (data) => {
        console.log('☠️ New Killfeed Event:', data);
        updateKillfeedUI(data);
    });

    // Server Status Updates
    socket.on('status_update', (data) => {
        console.log('🖥️ Server Status Update:', data);
        updateStatusUI(data);
    });
});

function updateKillfeedUI(data) {
    // Assuming there's a list with id 'killfeed-list'
    const list = document.getElementById('killfeed-list');
    if (!list) return;

    // Create new element
    const li = document.createElement('li');
    li.className = 'killfeed-item new-event'; // Add animation class
    li.innerHTML = `
        <span class="timestamp">${data.timestamp || new Date().toLocaleTimeString()}</span>
        <span class="message">${data.message}</span>
    `;

    // Prepend to list
    list.prepend(li);

    // Limit list size (e.g., keep last 20)
    if (list.children.length > 20) {
        list.removeChild(list.lastElementChild);
    }
}

function updateStatusUI(data) {
    const statusEl = document.getElementById('server-status-text');
    const playersEl = document.getElementById('player-count');

    if (statusEl && data.status) {
        statusEl.textContent = data.status;
        statusEl.className = data.status === 'Online' ? 'text-success' : 'text-danger';
    }

    if (playersEl && data.players !== undefined) {
        playersEl.textContent = `${data.players}/60`; // Assuming 60 slots
    }
}
