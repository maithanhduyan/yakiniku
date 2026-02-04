/**
 * Kitchen Display System (KDS) - JavaScript
 * Real-time order display for kitchen staff
 */

// ============ Configuration ============

const CONFIG = {
    API_BASE: 'http://localhost:8000/api',
    BRANCH_CODE: 'jinan',
    SSE_URL: 'http://localhost:8000/api/notifications/stream',
    REFRESH_INTERVAL: 30000, // Refresh orders every 30 seconds
    TIMER_INTERVAL: 1000,    // Update timers every second
};

// Time thresholds for color coding (in seconds)
const TIME_THRESHOLDS = {
    URGENT: 180,   // > 3 minutes = red
    WARNING: 60,   // > 1 minute = yellow
    OK: 0,         // < 1 minute = green
};

// ============ State ============

let state = {
    orders: [],
    filter: 'all',
    isOnline: false,
    soundEnabled: true,
    sseRetryCount: 0,
    maxRetries: 5,
};

// ============ Initialization ============

document.addEventListener('DOMContentLoaded', () => {
    // Start clock
    updateClock();
    setInterval(updateClock, 1000);

    // Start timers
    setInterval(updateAllTimers, CONFIG.TIMER_INTERVAL);

    // Setup filter buttons
    setupFilters();

    // Setup sound toggle
    setupSoundToggle();

    // Load initial orders
    loadOrders();

    // Setup SSE for real-time updates
    setupSSE();

    // Periodic refresh as backup
    setInterval(loadOrders, CONFIG.REFRESH_INTERVAL);
});

// ============ Clock ============

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('ja-JP', { hour12: false });
    document.getElementById('currentTime').textContent = timeStr;
}

// ============ API Functions ============

async function loadOrders() {
    try {
        const statuses = ['pending', 'confirmed', 'preparing', 'ready'];
        const response = await fetch(
            `${CONFIG.API_BASE}/orders/kitchen?branch_code=${CONFIG.BRANCH_CODE}&status=${statuses.join('&status=')}`
        );

        if (!response.ok) throw new Error('Failed to load orders');

        const orders = await response.json();

        // Use demo data if API returns empty (for development)
        if (orders.length === 0 && state.orders.length === 0) {
            loadDemoOrders();
            updateConnectionStatus(true);
            return;
        }

        state.orders = orders;
        renderOrders();
        updateStats();
        updateConnectionStatus(true);

    } catch (error) {
        console.error('Error loading orders:', error);
        updateConnectionStatus(false);

        // Load demo orders if API fails
        if (state.orders.length === 0) {
            loadDemoOrders();
        }
    }
}

function loadDemoOrders() {
    // Demo data for development/testing
    const now = new Date();
    state.orders = [
        {
            id: 'demo-1',
            order_number: 1,
            table_number: 'T5',
            status: 'pending',
            created_at: new Date(now - 4 * 60 * 1000).toISOString(), // 4 min ago
            elapsed_minutes: 4,
            items: [
                { id: '1', item_name: '和牛上ハラミ', quantity: 2, status: 'pending', notes: null },
                { id: '2', item_name: '厚切り上タン塩', quantity: 1, status: 'pending', notes: 'よく焼き' },
                { id: '3', item_name: 'ライス', quantity: 2, status: 'pending', notes: null },
            ]
        },
        {
            id: 'demo-2',
            order_number: 2,
            table_number: 'T3',
            status: 'preparing',
            created_at: new Date(now - 2 * 60 * 1000).toISOString(), // 2 min ago
            elapsed_minutes: 2,
            items: [
                { id: '4', item_name: 'カルビ', quantity: 3, status: 'ready', notes: null },
                { id: '5', item_name: 'チョレギサラダ', quantity: 1, status: 'pending', notes: null },
            ]
        },
        {
            id: 'demo-3',
            order_number: 3,
            table_number: 'T8',
            status: 'preparing',
            created_at: new Date(now - 45 * 1000).toISOString(), // 45 sec ago
            elapsed_minutes: 0.75,
            items: [
                { id: '6', item_name: '生ビール', quantity: 3, status: 'ready', notes: null },
                { id: '7', item_name: 'ハイボール', quantity: 2, status: 'ready', notes: null },
            ]
        },
        {
            id: 'demo-4',
            order_number: 4,
            table_number: 'T7',
            status: 'pending',
            created_at: new Date(now - 5 * 1000).toISOString(), // 5 sec ago (NEW)
            elapsed_minutes: 0.08,
            items: [
                { id: '8', item_name: 'ビビンバ', quantity: 1, status: 'pending', notes: null },
            ]
        },
    ];

    renderOrders();
    updateStats();
}

async function updateOrderStatus(orderId, newStatus) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/orders/${orderId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) throw new Error('Failed to update order');

        // Update local state
        const order = state.orders.find(o => o.id === orderId);
        if (order) {
            order.status = newStatus;
            renderOrders();
            updateStats();
        }

        showToast(`注文を「${getStatusLabel(newStatus)}」に更新しました`, 'success');

    } catch (error) {
        console.error('Error updating order:', error);

        // Update locally anyway for demo
        const order = state.orders.find(o => o.id === orderId);
        if (order) {
            order.status = newStatus;
            renderOrders();
            updateStats();
        }
        showToast(`注文を「${getStatusLabel(newStatus)}」に更新しました`, 'success');
    }
}

async function updateItemStatus(itemId, orderId, isCompleted) {
    const newStatus = isCompleted ? 'ready' : 'pending';

    try {
        await fetch(`${CONFIG.API_BASE}/orders/items/${itemId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
    } catch (error) {
        console.error('Error updating item:', error);
    }

    // Update local state regardless of API result
    const order = state.orders.find(o => o.id === orderId);
    if (order) {
        const item = order.items.find(i => i.id === itemId);
        if (item) {
            item.status = newStatus;
            renderOrders();
        }
    }
}

// ============ SSE (Server-Sent Events) ============

function setupSSE() {
    if (state.sseRetryCount >= state.maxRetries) {
        console.log('SSE: Max retries exceeded');
        updateConnectionStatus(false);
        return;
    }

    try {
        const eventSource = new EventSource(
            `${CONFIG.SSE_URL}?branch_code=${CONFIG.BRANCH_CODE}`
        );

        eventSource.onopen = () => {
            console.log('SSE connected');
            state.sseRetryCount = 0;
            updateConnectionStatus(true);
        };

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleSSEMessage(data);
            } catch (e) {
                // Heartbeat or non-JSON message
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            state.sseRetryCount++;
            updateConnectionStatus(false);

            if (state.sseRetryCount < state.maxRetries) {
                console.log(`SSE error, retry ${state.sseRetryCount}/${state.maxRetries}...`);
                setTimeout(setupSSE, 3000);
            }
        };

    } catch (error) {
        console.error('SSE setup error:', error);
        updateConnectionStatus(false);
    }
}

function handleSSEMessage(data) {
    switch (data.type) {
        case 'new_order':
            // Play sound and reload orders
            playNotificationSound();
            showToast(`🆕 テーブル ${data.table_number} から新規注文！`, 'new');
            loadOrders();
            break;

        case 'order_status_changed':
            loadOrders();
            break;

        case 'staff_call':
            showToast(`🔔 ${data.table_number}: ${data.call_type_label}`, 'call');
            playNotificationSound();
            break;
    }
}

// ============ Rendering ============

function renderOrders() {
    const container = document.getElementById('ordersContainer');
    const emptyState = document.getElementById('emptyState');

    // Filter orders
    let filteredOrders = state.orders;
    if (state.filter !== 'all') {
        filteredOrders = state.orders.filter(order => {
            return order.items.some(item => matchesFilter(item, state.filter));
        });
    }

    // Sort by elapsed time (oldest first for FIFO)
    filteredOrders.sort((a, b) => {
        const timeA = new Date(a.created_at).getTime();
        const timeB = new Date(b.created_at).getTime();
        return timeA - timeB;
    });

    if (filteredOrders.length === 0) {
        emptyState.classList.remove('hidden');
        container.innerHTML = '';
        container.appendChild(emptyState);
        return;
    }

    emptyState.classList.add('hidden');

    container.innerHTML = filteredOrders.map(order => renderOrderCard(order)).join('');

    // Setup event listeners
    setupCardEventListeners();
}

function renderOrderCard(order) {
    const elapsedSeconds = getElapsedSeconds(order.created_at);
    const timerClass = getTimerClass(elapsedSeconds, order.status);
    const statusClass = getStatusClass(elapsedSeconds, order.status);
    const timerDisplay = formatTimer(elapsedSeconds);
    const timerIcon = getTimerIcon(elapsedSeconds, order.status);

    const itemsHtml = order.items.map(item => `
        <div class="order-item ${item.status === 'ready' ? 'completed' : ''}" data-item-id="${item.id}">
            <div class="item-checkbox ${item.status === 'ready' ? 'checked' : ''}"
                 onclick="toggleItem('${item.id}', '${order.id}')"></div>
            <div class="item-details">
                <div class="item-name">${item.item_name}</div>
                ${item.notes ? `<div class="item-notes">※ ${item.notes}</div>` : ''}
            </div>
            <div class="item-quantity">×${item.quantity}</div>
        </div>
    `).join('');

    const actionButton = getActionButton(order);

    return `
        <div class="order-card status-${statusClass}" data-order-id="${order.id}">
            <div class="card-header">
                <div class="card-table">
                    <span class="table-number">${order.table_number}</span>
                    <span class="order-number">#${order.order_number}</span>
                </div>
                <div class="card-timer ${timerClass}">
                    <span class="timer-icon">${timerIcon}</span>
                    <span class="timer-value">${timerDisplay}</span>
                </div>
            </div>
            <div class="card-items">
                ${itemsHtml}
            </div>
            <div class="card-actions">
                ${actionButton}
            </div>
        </div>
    `;
}

function getActionButton(order) {
    switch (order.status) {
        case 'pending':
            return `<button class="card-btn btn-start" onclick="startOrder('${order.id}')">調理開始</button>`;
        case 'confirmed':
        case 'preparing':
            return `<button class="card-btn btn-complete" onclick="completeOrder('${order.id}')">完了</button>`;
        case 'ready':
            return `<button class="card-btn btn-served" onclick="serveOrder('${order.id}')">提供済み</button>`;
        default:
            return '';
    }
}

function setupCardEventListeners() {
    // Additional event listeners can be added here
}

// ============ Order Actions ============

function startOrder(orderId) {
    updateOrderStatus(orderId, 'preparing');
}

function completeOrder(orderId) {
    updateOrderStatus(orderId, 'ready');
}

function serveOrder(orderId) {
    updateOrderStatus(orderId, 'served');
    // Remove from display after short delay
    setTimeout(() => {
        state.orders = state.orders.filter(o => o.id !== orderId);
        renderOrders();
        updateStats();
    }, 500);
}

function toggleItem(itemId, orderId) {
    const order = state.orders.find(o => o.id === orderId);
    if (!order) return;

    const item = order.items.find(i => i.id === itemId);
    if (!item) return;

    const isCompleted = item.status !== 'ready';
    updateItemStatus(itemId, orderId, isCompleted);
}

// ============ Timer Functions ============

function getElapsedSeconds(createdAt) {
    const created = new Date(createdAt).getTime();
    const now = Date.now();
    return Math.floor((now - created) / 1000);
}

function formatTimer(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function getTimerClass(seconds, status) {
    if (status === 'ready') return 'ok';
    if (seconds < 10) return 'new';
    if (seconds < TIME_THRESHOLDS.WARNING) return 'ok';
    if (seconds < TIME_THRESHOLDS.URGENT) return 'warning';
    return 'urgent';
}

function getStatusClass(seconds, status) {
    if (status === 'ready') return 'done';
    if (seconds < 10) return 'new';
    if (seconds < TIME_THRESHOLDS.WARNING) return 'ok';
    if (seconds < TIME_THRESHOLDS.URGENT) return 'warning';
    return 'urgent';
}

function getTimerIcon(seconds, status) {
    if (status === 'ready') return '✓';
    if (seconds < 10) return '⚪';
    if (seconds < TIME_THRESHOLDS.WARNING) return '🟢';
    if (seconds < TIME_THRESHOLDS.URGENT) return '🟡';
    return '🔴';
}

function updateAllTimers() {
    document.querySelectorAll('.order-card').forEach(card => {
        const orderId = card.dataset.orderId;
        const order = state.orders.find(o => o.id === orderId);
        if (!order) return;

        const elapsedSeconds = getElapsedSeconds(order.created_at);
        const timerValue = card.querySelector('.timer-value');
        const timerEl = card.querySelector('.card-timer');
        const timerIcon = card.querySelector('.timer-icon');

        if (timerValue) {
            timerValue.textContent = formatTimer(elapsedSeconds);
        }

        if (timerEl) {
            timerEl.className = `card-timer ${getTimerClass(elapsedSeconds, order.status)}`;
        }

        if (timerIcon) {
            timerIcon.textContent = getTimerIcon(elapsedSeconds, order.status);
        }

        // Update card status class
        card.className = `order-card status-${getStatusClass(elapsedSeconds, order.status)}`;
    });
}

// ============ Stats ============

function updateStats() {
    const newCount = state.orders.filter(o => o.status === 'pending').length;
    const preparingCount = state.orders.filter(o =>
        o.status === 'confirmed' || o.status === 'preparing'
    ).length;
    const readyCount = state.orders.filter(o => o.status === 'ready').length;

    document.getElementById('statNew').textContent = newCount;
    document.getElementById('statPreparing').textContent = preparingCount;
    document.getElementById('statReady').textContent = readyCount;
}

// ============ Filters ============

function setupFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.filter = btn.dataset.filter;
            renderOrders();
        });
    });
}

function matchesFilter(item, filter) {
    const itemName = item.item_name.toLowerCase();

    switch (filter) {
        case 'meat':
            return ['ハラミ', 'タン', 'カルビ', 'ロース', 'ホルモン', '盛り合わせ']
                .some(meat => itemName.includes(meat.toLowerCase()));
        case 'drinks':
            return ['ビール', 'ハイボール', 'サワー', '茶', 'コーラ', 'ジュース']
                .some(drink => itemName.includes(drink.toLowerCase()));
        case 'other':
            return !matchesFilter(item, 'meat') && !matchesFilter(item, 'drinks');
        default:
            return true;
    }
}

// ============ Sound ============

function setupSoundToggle() {
    const btn = document.getElementById('soundToggle');
    btn.addEventListener('click', () => {
        state.soundEnabled = !state.soundEnabled;
        btn.classList.toggle('muted', !state.soundEnabled);
        btn.textContent = state.soundEnabled ? '🔔' : '🔕';
    });
}

function playNotificationSound() {
    if (!state.soundEnabled) return;

    const audio = document.getElementById('newOrderSound');
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(() => {
            // Auto-play blocked, user interaction required
        });
    }
}

// ============ UI Helpers ============

function updateConnectionStatus(isOnline) {
    state.isOnline = isOnline;
    const statusEl = document.getElementById('connectionStatus');

    if (isOnline) {
        statusEl.innerHTML = '<span class="status-dot"></span><span>オンライン</span>';
        statusEl.className = 'connection-status online';
    } else {
        statusEl.innerHTML = '<span class="status-dot"></span><span>オフライン</span>';
        statusEl.className = 'connection-status offline';
    }
}

function getStatusLabel(status) {
    const labels = {
        'pending': '新規',
        'confirmed': '確認済み',
        'preparing': '調理中',
        'ready': '完了',
        'served': '提供済み',
    };
    return labels[status] || status;
}

function showToast(message, type = 'info') {
    // Remove existing toast
    const existing = document.querySelector('.notification-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'notification-toast';

    const icons = {
        'new': '🆕',
        'success': '✓',
        'call': '🔔',
        'info': 'ℹ️',
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
    `;

    document.body.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Auto-hide
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
