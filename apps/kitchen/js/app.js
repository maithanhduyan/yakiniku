/**
 * Kitchen Display System - 焼肉ヅアン
 * Station-based Layout với Item Timer
 * Calm Kitchen Design
 */

// ============ Configuration ============
// Auto-detect: Dev (Live Server) → backend :8000 | Prod (Traefik) → same origin
const _host = window.location.hostname;
const _port = window.location.port;
const _isDev = _port && !['80', '443', ''].includes(_port);
const _proto = window.location.protocol;
const _wsProto = _proto === 'https:' ? 'wss:' : 'ws:';
const _base = _isDev ? `${_proto}//${_host}:8000` : `${_proto}//${_host}`;

const CONFIG = {
    API_BASE: `${_base}/api`,
    WS_BASE: `${_isDev ? 'ws:' : _wsProto}//${_host}${_isDev ? ':8000' : ''}/ws`,
    BRANCH_CODE: 'hirama',
    REFRESH_INTERVAL: 30000,
    TIMER_INTERVAL: 1000
};

// Time thresholds (seconds) - Default values, can be overridden by backend
const THRESHOLDS = {
    WARNING: 180,   // 3 min = yellow
    URGENT: 300     // 5 min = red
};

// Station definitions
const STATIONS = {
    all: {
        name: 'すべて',
        icon: '📋',
        keywords: []  // All items
    },
    meat: {
        name: '肉',
        icon: '🥩',
        keywords: ['カルビ', 'ハラミ', 'タン', 'ロース', 'ホルモン', '牛', '豚', '鶏', 'サガリ', 'ミノ', 'レバー', 'ハツ', 'テッチャン']
    },
    side: {
        name: '他',
        icon: '🍚',
        keywords: ['ライス', 'ナムル', 'キムチ', 'サラダ', 'ビビンバ', '麺', '冷麺', 'スープ', '豆腐', 'チヂミ', 'ポテト', '枝豆']
    },
    drink: {
        name: '飲物',
        icon: '🍺',
        keywords: ['ビール', 'ハイボール', 'サワー', 'ジュース', '茶', 'コーラ', '酎ハイ', 'ワイン', '日本酒', '焼酎', 'ソフトドリンク']
    }
};

// ============ State ============
const state = {
    items: [],          // All individual items
    activeStation: 'all',
    isOnline: false,
    isLoading: true,
    isDemoMode: false,
    soundEnabled: true,
    historyVisible: false,
    history: []         // Cached history events
};

// ============ DOM Elements ============
const elements = {
    stationLayout: document.getElementById('stationLayout'),
    emptyState: document.getElementById('emptyState'),
    currentTime: document.getElementById('currentTime'),
    connectionStatus: document.getElementById('connectionStatus'),
    notification: document.getElementById('notification'),
    notificationText: document.getElementById('notificationText'),
    soundToggle: document.getElementById('soundToggle'),
    soundIcon: document.getElementById('soundIcon'),
    notificationSound: document.getElementById('notificationSound'),
    thresholdWarning: document.getElementById('thresholdWarning'),
    thresholdUrgent: document.getElementById('thresholdUrgent'),
    // Stats
    statTotal: document.getElementById('statTotal'),
    statWarning: document.getElementById('statWarning'),
    statUrgent: document.getElementById('statUrgent'),
    // Station counts
    countAll: document.getElementById('countAll'),
    countMeat: document.getElementById('countMeat'),
    countSide: document.getElementById('countSide'),
    countDrink: document.getElementById('countDrink'),
    // Panels
    panelAll: document.getElementById('panelAll'),
    panelMeat: document.getElementById('panelMeat'),
    panelSide: document.getElementById('panelSide'),
    panelDrink: document.getElementById('panelDrink'),
    // Item lists
    itemsAll: document.getElementById('itemsAll'),
    itemsMeat: document.getElementById('itemsMeat'),
    itemsSide: document.getElementById('itemsSide'),
    itemsDrink: document.getElementById('itemsDrink')
};

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', init);

async function init() {
    console.log('🍳 Kitchen Display - 焼肉ヅアン - Station Mode');

    // Initialize i18n
    I18N.init();

    // Show loading overlay
    showLoading();

    // Update threshold display
    elements.thresholdWarning.textContent = THRESHOLDS.WARNING / 60;
    elements.thresholdUrgent.textContent = THRESHOLDS.URGENT / 60;

    updateClock();
    setInterval(updateClock, 1000);
    setInterval(updateTimers, CONFIG.TIMER_INTERVAL);

    setupEventListeners();
    loadConfig();
    await loadOrders();
    connectWebSocket();

    // Hide loading after initial load
    setTimeout(() => {
        hideLoading();
    }, 800);

    setInterval(loadOrders, CONFIG.REFRESH_INTERVAL);
}

// ============ Event Listeners ============
function setupEventListeners() {
    // Station tabs
    document.querySelectorAll('.station-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            setActiveStation(tab.dataset.station);
        });
    });

    // Mini panels click to switch
    document.querySelectorAll('.mini-panel').forEach(panel => {
        panel.addEventListener('click', (e) => {
            // Don't switch if clicking on item button
            if (e.target.closest('.item-done-btn')) return;
            setActiveStation(panel.dataset.station);
        });
    });

    // Sound toggle
    elements.soundToggle?.addEventListener('click', toggleSound);

    // Fullscreen
    document.getElementById('fullscreenBtn')?.addEventListener('click', toggleFullscreen);

    // Confirm modal
    document.getElementById('modalConfirm')?.addEventListener('click', confirmComplete);
    document.getElementById('modalCancel')?.addEventListener('click', closeConfirmModal);
    document.getElementById('confirmModal')?.addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeConfirmModal();
    });

    // Cancel modal
    document.getElementById('cancelModalConfirm')?.addEventListener('click', confirmCancel);
    document.getElementById('cancelModalBack')?.addEventListener('click', closeCancelModal);
    document.getElementById('cancelModal')?.addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeCancelModal();
    });

    // Demo banner close
    document.getElementById('demoBannerClose')?.addEventListener('click', hideDemoBanner);

    // History panel
    document.getElementById('historyToggle')?.addEventListener('click', toggleHistory);
    document.getElementById('historyClose')?.addEventListener('click', closeHistory);
    document.getElementById('historyOverlay')?.addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeHistory();
    });
    document.getElementById('historyStationFilter')?.addEventListener('change', loadHistory);
    document.getElementById('historyTypeFilter')?.addEventListener('change', loadHistory);
}

// ============ Station Management ============
function setActiveStation(station) {
    state.activeStation = station;

    // Update tabs
    document.querySelectorAll('.station-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.station === station);
    });

    // Update panel layout
    updatePanelLayout();
}

function updatePanelLayout() {
    const active = state.activeStation;
    const allStations = ['all', 'meat', 'side', 'drink'];

    // Clear layout
    elements.stationLayout.innerHTML = '';

    // Create main panel for active station
    const mainPanel = createPanel(active, true);
    elements.stationLayout.appendChild(mainPanel);

    // Create mini panels container
    const miniContainer = document.createElement('aside');
    miniContainer.className = 'mini-panels';

    // Add other stations as mini panels
    allStations
        .filter(s => s !== active)
        .forEach(station => {
            const miniPanel = createPanel(station, false);
            miniContainer.appendChild(miniPanel);
        });

    elements.stationLayout.appendChild(miniContainer);

    // Re-render items
    renderAllPanels();
}

function createPanel(station, isMain) {
    const info = STATIONS[station];
    const panel = document.createElement('section');
    panel.className = `station-panel ${isMain ? 'main-panel' : 'mini-panel'}`;
    panel.dataset.station = station;
    panel.id = `panel${capitalize(station)}`;

    if (!isMain) {
        panel.addEventListener('click', (e) => {
            if (e.target.closest('.item-done-btn') || e.target.closest('.item-cancel-btn')) return;
            setActiveStation(station);
        });
    }

    const stationKey = `station.${station}`;
    panel.innerHTML = `
        <div class="panel-header">
            <span class="panel-title">${info.icon} ${t(stationKey)}</span>
            <span class="panel-count">0</span>
        </div>
        <div class="items-list" id="items${capitalize(station)}"></div>
    `;

    return panel;
}

// ============ Clock ============
function updateClock() {
    const now = new Date();
    const locale = I18N.currentLang === 'en' ? 'en-US' : 'ja-JP';
    elements.currentTime.textContent = now.toLocaleTimeString(locale, {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============ Config from Backend ============
async function loadConfig() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/kitchen/config?branch_code=${CONFIG.BRANCH_CODE}`);
        if (response.ok) {
            const config = await response.json();
            if (config.warning_threshold) {
                THRESHOLDS.WARNING = config.warning_threshold;
                elements.thresholdWarning.textContent = THRESHOLDS.WARNING / 60;
            }
            if (config.urgent_threshold) {
                THRESHOLDS.URGENT = config.urgent_threshold;
                elements.thresholdUrgent.textContent = THRESHOLDS.URGENT / 60;
            }
        }
    } catch (e) {
        console.log('Using default thresholds');
    }
}

// ============ API ============
async function loadOrders() {
    try {
        const response = await fetch(
            `${CONFIG.API_BASE}/orders/kitchen?branch_code=${CONFIG.BRANCH_CODE}`
        );

        if (!response.ok) throw new Error('API Error');

        const orders = await response.json();
        processOrders(orders);
        setOnline(true);
        updateLoadingStatus('api', 'success');

        // Clear demo mode if we get real data
        if (state.isDemoMode) {
            state.isDemoMode = false;
            hideDemoBanner();
        }
    } catch (error) {
        console.warn('API unavailable, using demo data');
        updateLoadingStatus('api', 'error');
        if (state.items.length === 0) {
            loadDemoData();
        }
        setOnline(false);
    }
}

function processOrders(orders) {
    // Flatten orders to individual items with order context
    const items = [];

    orders.forEach(order => {
        order.items.forEach(item => {
            if (!item.completed) {
                items.push({
                    id: `${order.id}-${item.id}`,
                    orderId: order.id,
                    orderNumber: order.orderNumber,
                    tableNumber: order.tableNumber,
                    name: item.name,
                    quantity: item.quantity,
                    note: item.note,
                    completed: item.completed || false,
                    createdAt: order.createdAt,
                    station: detectStation(item.name)
                });
            }
        });
    });

    // Sort by time (oldest first)
    items.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));

    state.items = items;
    renderAllPanels();
    updateStats();
}

function loadDemoData() {
    const now = Date.now();

    const demoOrders = [
        {
            id: 'order-1',
            orderNumber: 101,
            tableNumber: 'T3',
            createdAt: new Date(now - 4 * 60 * 1000).toISOString(),
            items: [
                { id: 'i1', name: '特選カルビ', quantity: 2 },
                { id: 'i2', name: '上ハラミ', quantity: 1, note: 'よく焼き' },
                { id: 'i3', name: 'ライス', quantity: 2 }
            ]
        },
        {
            id: 'order-2',
            orderNumber: 102,
            tableNumber: 'T7',
            createdAt: new Date(now - 2 * 60 * 1000).toISOString(),
            items: [
                { id: 'i4', name: '牛タン塩', quantity: 2 },
                { id: 'i5', name: 'ナムル盛り', quantity: 1 },
                { id: 'i6', name: '生ビール', quantity: 3 }
            ]
        },
        {
            id: 'order-3',
            orderNumber: 103,
            tableNumber: 'T5',
            createdAt: new Date(now - 6 * 60 * 1000).toISOString(),
            items: [
                { id: 'i7', name: 'ハイボール', quantity: 2 },
                { id: 'i8', name: 'コーラ', quantity: 1 }
            ]
        },
        {
            id: 'order-4',
            orderNumber: 104,
            tableNumber: 'T1',
            createdAt: new Date(now - 30 * 1000).toISOString(),
            items: [
                { id: 'i9', name: 'ビビンバ', quantity: 1 },
                { id: 'i10', name: '冷麺', quantity: 1 },
                { id: 'i11', name: '生ビール', quantity: 2 }
            ]
        }
    ];

    processOrders(demoOrders);
    setOnline(true);

    // Show demo mode banner
    state.isDemoMode = true;
    showDemoBanner();
}

// ============ Station Detection ============
function detectStation(itemName) {
    for (const [station, info] of Object.entries(STATIONS)) {
        if (station === 'all') continue;
        if (info.keywords.some(kw => itemName.includes(kw))) {
            return station;
        }
    }
    return 'side'; // Default to side dishes
}

// ============ WebSocket ============
function connectWebSocket() {
    try {
        const ws = new WebSocket(`${CONFIG.WS_BASE}/kitchen?branch=${CONFIG.BRANCH_CODE}`);

        ws.onopen = () => {
            console.log('WebSocket connected');
            setOnline(true);
            updateLoadingStatus('ws', 'success');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWSMessage(data);
            } catch (e) {}
        };

        ws.onclose = () => {
            setOnline(false);
            updateLoadingStatus('ws', 'error');
            setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = () => {
            setOnline(false);
            updateLoadingStatus('ws', 'error');
        };
    } catch (error) {
        console.warn('WebSocket not available');
    }
}

function handleWSMessage(data) {
    if (data.type === 'new_order') {
        showNotification(t('notify.newOrder', { table: data.tableNumber }));
        playSound();
        loadOrders();
    } else if (data.type === 'order_update' || data.type === 'config_update') {
        loadOrders();
        if (data.type === 'config_update') loadConfig();
    }
}

// ============ Rendering ============
function renderAllPanels() {
    const stations = ['all', 'meat', 'side', 'drink'];

    stations.forEach(station => {
        renderPanel(station);
    });

    // Update empty state
    const hasItems = state.items.length > 0;
    elements.emptyState.classList.toggle('show', !hasItems);
}

function renderPanel(station) {
    const container = document.getElementById(`items${capitalize(station)}`);
    if (!container) return;

    // Filter items for this station
    let items;
    if (station === 'all') {
        items = state.items;
    } else {
        items = state.items.filter(item => item.station === station);
    }

    // Update panel count
    const panel = container.closest('.station-panel');
    if (panel) {
        const countEl = panel.querySelector('.panel-count');
        if (countEl) countEl.textContent = items.length;
    }

    // Update tab count
    const countId = `count${capitalize(station)}`;
    const countTab = document.getElementById(countId);
    if (countTab) countTab.textContent = items.length;

    // Render items
    container.innerHTML = items.map(item => renderItemRow(item, station !== state.activeStation)).join('');
}

function renderItemRow(item, compact = false) {
    const elapsed = getElapsedSeconds(item.createdAt);
    const statusClass = getStatusClass(elapsed);
    const minutes = Math.floor(elapsed / 60);

    return `
        <div class="item-row ${statusClass} ${item.completed ? 'completed' : ''}"
             data-item-id="${item.id}">
            <div class="item-info">
                <div class="item-name">${item.name}</div>
                ${item.note ? `<div class="item-note">※ ${item.note}</div>` : ''}
            </div>
            <div class="item-quantity">×${item.quantity}</div>
            <div class="item-table">${item.tableNumber}</div>
            <div class="item-timer">${minutes}${t('item.minute')}</div>
            <button class="item-cancel-btn" onclick="cancelItem('${item.id}')" title="${t('item.cancel')}">
                ✕
            </button>
            <button class="item-done-btn" onclick="completeItem('${item.id}')" title="${t('item.done')}">
                ✓
            </button>
        </div>
    `;
}

// ============ Item Actions ============
let _pendingCompleteId = null;
let _pendingCancelId = null;

function completeItem(itemId) {
    const item = state.items.find(i => i.id === itemId);
    if (!item) return;

    _pendingCompleteId = itemId;
    const elapsed = getElapsedSeconds(item.createdAt);
    const minutes = Math.floor(elapsed / 60);

    // Populate modal
    document.getElementById('modalItemName').textContent = item.name;
    document.getElementById('modalItemQty').textContent = `×${item.quantity}`;
    document.getElementById('modalItemTable').textContent = item.tableNumber;
    document.getElementById('modalItemWait').textContent = `${minutes}${t('item.minute')}`;

    // Show modal
    document.getElementById('confirmModal').classList.add('show');
}

function confirmComplete() {
    const itemId = _pendingCompleteId;
    if (!itemId) return;

    const item = state.items.find(i => i.id === itemId);
    closeConfirmModal();

    // Mark as completed with animation
    const row = document.querySelector(`[data-item-id="${itemId}"]`);
    if (row) {
        row.classList.add('removing');
    }

    setTimeout(() => {
        // Remove from state
        state.items = state.items.filter(i => i.id !== itemId);

        // Re-render
        renderAllPanels();
        updateStats();

        // Send to API + log event
        if (item) {
            sendItemComplete(item);
            logKitchenEvent('kitchen.item.served', item);
        }
    }, 300);
}

function closeConfirmModal() {
    document.getElementById('confirmModal').classList.remove('show');
    _pendingCompleteId = null;
}

// ============ Cancel Item ============
function cancelItem(itemId) {
    const item = state.items.find(i => i.id === itemId);
    if (!item) return;

    _pendingCancelId = itemId;

    // Populate cancel modal
    document.getElementById('cancelModalItemName').textContent = item.name;
    document.getElementById('cancelModalItemQty').textContent = `×${item.quantity}`;
    document.getElementById('cancelModalItemTable').textContent = item.tableNumber;
    document.getElementById('cancelReason').value = '';

    // Show modal
    document.getElementById('cancelModal').classList.add('show');
}

function confirmCancel() {
    const itemId = _pendingCancelId;
    if (!itemId) return;

    const item = state.items.find(i => i.id === itemId);
    const reason = document.getElementById('cancelReason').value.trim();
    closeCancelModal();

    // Animate removal
    const row = document.querySelector(`[data-item-id="${itemId}"]`);
    if (row) {
        row.classList.add('removing');
    }

    setTimeout(() => {
        state.items = state.items.filter(i => i.id !== itemId);
        renderAllPanels();
        updateStats();

        if (item) {
            logKitchenEvent('kitchen.item.cancelled', item, { reason });
        }

        showNotification(t('notify.cancelled', { name: item?.name || '-' }));
    }, 300);
}

function closeCancelModal() {
    document.getElementById('cancelModal').classList.remove('show');
    _pendingCancelId = null;
}

async function sendItemComplete(item) {
    try {
        await fetch(`${CONFIG.API_BASE}/orders/${item.orderId}/items/${item.id.split('-')[1]}/complete`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (e) {
        // Silently fail - local state already updated
    }
}

// ============ Timer Functions ============
function getElapsedSeconds(createdAt) {
    return Math.floor((Date.now() - new Date(createdAt).getTime()) / 1000);
}

function getStatusClass(seconds) {
    if (seconds >= THRESHOLDS.URGENT) return 'status-urgent';
    if (seconds >= THRESHOLDS.WARNING) return 'status-warning';
    return '';
}

function updateTimers() {
    document.querySelectorAll('.item-row').forEach(row => {
        const itemId = row.dataset.itemId;
        const item = state.items.find(i => i.id === itemId);
        if (!item) return;

        const elapsed = getElapsedSeconds(item.createdAt);
        const minutes = Math.floor(elapsed / 60);
        const statusClass = getStatusClass(elapsed);

        // Update timer display
        const timerEl = row.querySelector('.item-timer');
        if (timerEl) {
            timerEl.textContent = `${minutes}${t('item.minute')}`;
        }

        // Update status class
        row.classList.remove('status-warning', 'status-urgent');
        if (statusClass) {
            row.classList.add(statusClass);
        }
    });

    // Update stats
    updateStats();
}

// ============ Stats ============
function updateStats() {
    const total = state.items.length;
    let warning = 0;
    let urgent = 0;

    state.items.forEach(item => {
        const elapsed = getElapsedSeconds(item.createdAt);
        if (elapsed >= THRESHOLDS.URGENT) {
            urgent++;
        } else if (elapsed >= THRESHOLDS.WARNING) {
            warning++;
        }
    });

    elements.statTotal.textContent = total;
    elements.statWarning.textContent = warning;
    elements.statUrgent.textContent = urgent;
}

// ============ UI Helpers ============
function setOnline(isOnline) {
    state.isOnline = isOnline;
    elements.connectionStatus.className = `connection-status ${isOnline ? 'online' : 'offline'}`;
    elements.connectionStatus.querySelector('.status-text').textContent =
        isOnline ? t('connection.online') : t('connection.offline');
}

function showNotification(text) {
    elements.notificationText.textContent = text;
    elements.notification.classList.add('show');

    setTimeout(() => {
        elements.notification.classList.remove('show');
    }, 4000);
}

function toggleSound() {
    state.soundEnabled = !state.soundEnabled;
    elements.soundToggle.classList.toggle('muted', !state.soundEnabled);
    elements.soundIcon.textContent = state.soundEnabled ? '🔔' : '🔕';
}

function playSound() {
    if (!state.soundEnabled) return;
    try {
        elements.notificationSound.currentTime = 0;
        elements.notificationSound.play();
    } catch (e) {}
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ============ Loading State ============
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('hidden');
        state.isLoading = true;
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        state.isLoading = false;
    }
}

function updateLoadingStatus(type, status) {
    const statusEl = document.getElementById(`${type}Status`);
    if (!statusEl) return;

    statusEl.classList.remove('success', 'error');
    if (status === 'success' || status === 'error') {
        statusEl.classList.add(status);
    }

    // Update icon
    const iconEl = statusEl.querySelector('.status-icon');
    if (iconEl) {
        iconEl.textContent = status === 'success' ? '✓' : status === 'error' ? '✕' : '⏳';
    }
}

// ============ Demo Mode Banner ============
function showDemoBanner() {
    const banner = document.getElementById('demoBanner');
    if (banner) {
        banner.classList.add('show');
        document.body.classList.add('demo-active');
    }
}

function hideDemoBanner() {
    const banner = document.getElementById('demoBanner');
    if (banner) {
        banner.classList.remove('show');
        document.body.classList.remove('demo-active');
    }
}

// ============ Event Sourcing - Log Kitchen Events ============
async function logKitchenEvent(eventType, item, extraData = {}) {
    const elapsed = getElapsedSeconds(item.createdAt);
    const payload = {
        event_type: eventType,
        event_source: 'kitchen-display',
        branch_code: CONFIG.BRANCH_CODE,
        order_id: item.orderId,
        order_item_id: item.id.split('-')[1],
        item_name: item.name,
        item_quantity: item.quantity,
        table_number: item.tableNumber,
        station: item.station,
        wait_time_seconds: elapsed,
        actor_type: 'staff',
        data: extraData
    };

    try {
        await fetch(`${CONFIG.API_BASE}/kitchen/events/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (e) {
        console.warn('Failed to log kitchen event:', e);
    }
}

// ============ History Panel ============
function toggleHistory() {
    if (state.historyVisible) {
        closeHistory();
    } else {
        openHistory();
    }
}

function openHistory() {
    state.historyVisible = true;
    document.getElementById('historyOverlay').classList.add('show');
    document.getElementById('historyToggle').classList.add('active');
    loadHistory();
}

function closeHistory() {
    state.historyVisible = false;
    document.getElementById('historyOverlay').classList.remove('show');
    document.getElementById('historyToggle').classList.remove('active');
}

async function loadHistory() {
    const station = document.getElementById('historyStationFilter')?.value || 'all';
    const eventType = document.getElementById('historyTypeFilter')?.value || '';

    try {
        let url = `${CONFIG.API_BASE}/kitchen/events/history?branch_code=${CONFIG.BRANCH_CODE}&limit=50&since_hours=24`;
        if (station && station !== 'all') url += `&station=${station}`;
        if (eventType) url += `&event_type=${eventType}`;

        const response = await fetch(url);
        if (!response.ok) throw new Error('History API error');

        const data = await response.json();
        state.history = data.events || [];
        renderHistory(data);
    } catch (e) {
        console.warn('Failed to load history:', e);
        renderHistoryEmpty();
    }
}

function renderHistory(data) {
    const listEl = document.getElementById('historyList');
    const summaryEl = document.getElementById('historySummary');

    // Render summary
    const summary = data.summary || {};
    const avgMin = summary.avg_wait_seconds ? Math.floor(summary.avg_wait_seconds / 60) : 0;
    summaryEl.innerHTML = `
        <div class="history-stat served">
            <span>${t('history.served')}</span>
            <span class="history-stat-value">${summary.served_count || 0}</span>
        </div>
        <div class="history-stat cancelled">
            <span>${t('history.cancelled')}</span>
            <span class="history-stat-value">${summary.cancelled_count || 0}</span>
        </div>
        <div class="history-stat avg-wait">
            <span>${t('history.avgWait')}</span>
            <span class="history-stat-value">${avgMin}${t('item.minute')}</span>
        </div>
    `;

    // Render events
    const events = data.events || [];
    if (events.length === 0) {
        listEl.innerHTML = `<div class="history-empty">${t('history.empty')}</div>`;
        return;
    }

    const historyLocale = I18N.currentLang === 'en' ? 'en-US' : 'ja-JP';
    listEl.innerHTML = events.map(ev => {
        const isCancelled = ev.event_type === 'kitchen.item.cancelled';
        const icon = isCancelled ? '❌' : '✅';
        const cssClass = isCancelled ? 'event-cancelled' : '';
        const time = new Date(ev.timestamp).toLocaleTimeString(historyLocale, { hour: '2-digit', minute: '2-digit' });
        const waitMin = ev.wait_time_seconds ? `${Math.floor(ev.wait_time_seconds / 60)}${t('item.minute')}` : '-';
        const reason = (ev.data?.reason) ? `<div class="history-item-reason">${t('history.reason')}: ${ev.data.reason}</div>` : '';

        return `
            <div class="history-item ${cssClass}">
                <div class="history-item-icon">${icon}</div>
                <div class="history-item-info">
                    <div class="history-item-name">${ev.item_name || '-'}</div>
                    <div class="history-item-meta">${time}${reason ? '' : ''}</div>
                    ${reason}
                </div>
                <div class="history-item-qty">×${ev.item_quantity || 1}</div>
                <div class="history-item-table">${ev.table_number || '-'}</div>
                <div class="history-item-wait">${waitMin}</div>
            </div>
        `;
    }).join('');
}

function renderHistoryEmpty() {
    document.getElementById('historyList').innerHTML = `<div class="history-empty">${t('history.loadError')}</div>`;
    document.getElementById('historySummary').innerHTML = '';
}

// Global functions for onclick handlers
window.completeItem = completeItem;
window.cancelItem = cancelItem;
window.toggleLanguage = toggleLanguage;
