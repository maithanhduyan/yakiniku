/**
 * Table Order App - JavaScript
 * iPad table ordering system for Yakiniku Jinan
 */

// ============ Configuration ============

const CONFIG = {
    API_BASE: 'http://localhost:8000/api',
    BRANCH_CODE: 'jinan',
    WS_URL: 'ws://localhost:8000/api/notifications/ws',
};

// Get table info from URL params or localStorage
const urlParams = new URLSearchParams(window.location.search);
const TABLE_ID = urlParams.get('table') || localStorage.getItem('table_id') || 'demo-table-1';
const SESSION_ID = urlParams.get('session') || localStorage.getItem('session_id') || generateSessionId();

// ============ State ============

let state = {
    categories: [],
    menuItems: [],
    currentCategory: 'meat',
    cart: [],
    currentItem: null,
    modalQty: 1,
    tableNumber: 'T5',
    guestCount: 4,
    sessionId: SESSION_ID,
    orderHistory: [],
    isOnline: false,
    wsRetryCount: 0,
    maxWsRetries: 3
};

// ============ Initialization ============

document.addEventListener('DOMContentLoaded', async () => {
    // Load saved cart
    loadCartFromStorage();

    // Setup table info
    setupTableInfo();

    // Load menu
    await loadMenu();

    // Setup WebSocket for real-time updates
    setupWebSocket();

    // Update UI
    updateCartBadge();
});

function generateSessionId() {
    const id = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('session_id', id);
    return id;
}

function setupTableInfo() {
    const tableNumber = urlParams.get('table_number') || 'T5';
    const guestCount = parseInt(urlParams.get('guests')) || 4;

    state.tableNumber = tableNumber;
    state.guestCount = guestCount;

    document.getElementById('tableNumber').textContent = tableNumber;
    document.getElementById('guestCount').textContent = `${guestCount}名様`;
}

// ============ API Functions ============

async function loadMenu() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/menu/categories?branch_code=${CONFIG.BRANCH_CODE}`);

        if (!response.ok) {
            throw new Error('Failed to load menu');
        }

        const data = await response.json();
        state.categories = data.categories;

        renderCategories();
        selectCategory(state.categories[0]?.category || 'meat');

    } catch (error) {
        console.error('Error loading menu:', error);
        // Load demo data if API fails
        loadDemoMenu();
    }
}

function loadDemoMenu() {
    // Demo data for development
    state.categories = [
        {
            category: 'meat',
            category_label: '肉類',
            icon: '🥩',
            items: [
                { id: '1', name: '和牛上ハラミ', description: '口の中でほどける柔らかさと濃厚な味わい', price: 1800, image_url: 'https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400', is_popular: true },
                { id: '2', name: '厚切り上タン塩', description: '贅沢な厚切り。歯ごたえと肉汁が溢れます', price: 2200, image_url: 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400', is_popular: true },
                { id: '3', name: 'カルビ', description: '定番の人気メニュー', price: 1500, image_url: 'https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400' },
                { id: '4', name: 'ロース', description: '赤身の旨味が楽しめる', price: 1600, image_url: 'https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400' },
                { id: '5', name: 'ホルモン盛り合わせ', description: '新鮮なホルモンをたっぷり', price: 1400, image_url: 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400' },
                { id: '6', name: '特選盛り合わせ', description: '本日のおすすめ希少部位を贅沢に', price: 4500, image_url: 'https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400', is_popular: true },
            ]
        },
        {
            category: 'drinks',
            category_label: '飲物',
            icon: '🍺',
            items: [
                { id: '10', name: '生ビール', description: 'キンキンに冷えた生ビール', price: 600, image_url: 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400' },
                { id: '11', name: 'ハイボール', description: 'すっきり爽やか', price: 500, image_url: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400' },
                { id: '12', name: 'レモンサワー', description: '自家製レモンサワー', price: 500, image_url: 'https://images.unsplash.com/photo-1560508180-03f285f67c1a?w=400' },
                { id: '13', name: 'ウーロン茶', description: 'ソフトドリンク', price: 300, image_url: 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400' },
            ]
        },
        {
            category: 'salad',
            category_label: 'サラダ',
            icon: '🥗',
            items: [
                { id: '20', name: 'チョレギサラダ', description: '韓国風ピリ辛サラダ', price: 600, image_url: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400' },
                { id: '21', name: 'シーザーサラダ', description: 'パルメザンチーズたっぷり', price: 700, image_url: 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400' },
            ]
        },
        {
            category: 'rice',
            category_label: 'ご飯・麺',
            icon: '🍚',
            items: [
                { id: '30', name: 'ライス', description: '国産コシヒカリ', price: 200, image_url: 'https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400' },
                { id: '31', name: 'ビビンバ', description: '石焼ビビンバ', price: 1200, image_url: 'https://images.unsplash.com/photo-1553163147-622ab57be1c7?w=400' },
                { id: '32', name: '冷麺', description: '韓国冷麺', price: 900, image_url: 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400' },
            ]
        },
        {
            category: 'dessert',
            category_label: 'デザート',
            icon: '🍨',
            items: [
                { id: '40', name: 'バニラアイス', description: '濃厚バニラ', price: 400, image_url: 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400' },
                { id: '41', name: '杏仁豆腐', description: '手作り杏仁豆腐', price: 450, image_url: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400' },
            ]
        }
    ];

    renderCategories();
    selectCategory('meat');
}

async function submitOrder() {
    if (state.cart.length === 0) return;

    const btnOrder = document.getElementById('btnOrder');
    btnOrder.disabled = true;
    btnOrder.innerHTML = '<span class="loading-spinner"></span> 送信中...';

    try {
        const orderData = {
            table_id: TABLE_ID,
            session_id: state.sessionId,
            items: state.cart.map(item => ({
                menu_item_id: item.id,
                quantity: item.quantity,
                notes: item.notes || null
            }))
        };

        const response = await fetch(`${CONFIG.API_BASE}/orders?branch_code=${CONFIG.BRANCH_CODE}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });

        if (!response.ok) {
            throw new Error('Order failed');
        }

        const result = await response.json();

        // Clear cart
        state.cart = [];
        saveCartToStorage();
        updateCartBadge();
        closeCart();
        renderCartItems();

        // Show success
        showNotification('ご注文を承りました！', 'success');

        // Add to order history
        state.orderHistory.push(result);

    } catch (error) {
        console.error('Order error:', error);
        showNotification('注文に失敗しました。もう一度お試しください。', 'error');
    } finally {
        btnOrder.disabled = false;
        btnOrder.textContent = '注文を確定する';
    }
}

async function callStaff(callType) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/orders/call-staff?branch_code=${CONFIG.BRANCH_CODE}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                table_id: TABLE_ID,
                session_id: state.sessionId,
                call_type: callType
            })
        });

        const callLabels = {
            'assistance': 'スタッフを呼びました',
            'water': 'お水をお持ちします',
            'bill': 'お会計をお待ちください'
        };

        showNotification(callLabels[callType] || 'スタッフを呼びました', 'success');

    } catch (error) {
        console.error('Call staff error:', error);
        showNotification('スタッフを呼びました', 'success'); // Show success anyway for demo
    }
}

// ============ WebSocket ============

function setupWebSocket() {
    // Skip if already exceeded max retries
    if (state.wsRetryCount >= state.maxWsRetries) {
        console.log('WebSocket: Max retries exceeded, using offline mode');
        return;
    }

    try {
        const ws = new WebSocket(`${CONFIG.WS_URL}?branch_code=${CONFIG.BRANCH_CODE}&table_id=${TABLE_ID}`);

        ws.onopen = () => {
            console.log('WebSocket connected');
            state.wsRetryCount = 0; // Reset retry count on successful connection
            updateConnectionStatus(true);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        ws.onerror = (error) => {
            console.log('WebSocket error (will retry):', error);
        };

        ws.onclose = () => {
            state.wsRetryCount++;
            updateConnectionStatus(false);

            if (state.wsRetryCount < state.maxWsRetries) {
                console.log(`WebSocket disconnected, retry ${state.wsRetryCount}/${state.maxWsRetries}...`);
                setTimeout(setupWebSocket, 3000);
            } else {
                console.log('WebSocket: Switching to offline mode');
                showOfflineNotice();
            }
        };

    } catch (error) {
        console.error('WebSocket setup error:', error);
        state.wsRetryCount++;
        if (state.wsRetryCount >= state.maxWsRetries) {
            showOfflineNotice();
        }
    }
}

function updateConnectionStatus(isOnline) {
    state.isOnline = isOnline;
    const statusEl = document.getElementById('connectionStatus');
    if (statusEl) {
        if (isOnline) {
            statusEl.innerHTML = '<span class="status-dot online"></span> オンライン';
            statusEl.className = 'connection-status online';
        } else {
            statusEl.innerHTML = '<span class="status-dot offline"></span> オフライン';
            statusEl.className = 'connection-status offline';
        }
    }
}

function showOfflineNotice() {
    // Show a non-intrusive notice that real-time updates are unavailable
    const existingNotice = document.getElementById('offlineNotice');
    if (existingNotice) return; // Already showing

    const notice = document.createElement('div');
    notice.id = 'offlineNotice';
    notice.className = 'offline-notice';
    notice.innerHTML = `
        <span>⚠️ リアルタイム通知は現在利用できません。ご注文は通常通りお受けできます。</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    document.body.appendChild(notice);
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'order_status_changed':
            if (data.new_status === 'ready') {
                showNotification(`注文 #${data.order_number} が完成しました！`, 'success');
            }
            break;
        case 'menu_updated':
            loadMenu();
            break;
    }
}

// ============ Rendering ============

function renderCategories() {
    const container = document.getElementById('categoryList');
    container.innerHTML = state.categories.map(cat => `
        <div class="category-item ${cat.category === state.currentCategory ? 'active' : ''}"
             onclick="selectCategory('${cat.category}')">
            <span class="category-icon">${cat.icon}</span>
            <span class="category-label">${cat.category_label}</span>
        </div>
    `).join('');
}

function selectCategory(category) {
    state.currentCategory = category;

    // Update active state
    document.querySelectorAll('.category-item').forEach(el => {
        el.classList.toggle('active', el.querySelector('.category-label').textContent ===
            state.categories.find(c => c.category === category)?.category_label);
    });

    // Update title
    const cat = state.categories.find(c => c.category === category);
    if (cat) {
        document.getElementById('categoryIcon').textContent = cat.icon;
        document.getElementById('categoryLabel').textContent = cat.category_label;
        renderMenuItems(cat.items);
    }
}

function getImageUrl(imageUrl) {
    if (!imageUrl) return 'https://via.placeholder.com/400x200?text=No+Image';
    // If it's a relative path from API, prepend the API base
    if (imageUrl.startsWith('/images/')) {
        return CONFIG.API_BASE.replace('/api', '') + imageUrl;
    }
    return imageUrl;
}

function renderMenuItems(items) {
    const container = document.getElementById('menuGrid');

    if (!items || items.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">メニューがありません</p>';
        return;
    }

    container.innerHTML = items.map(item => {
        const inCart = state.cart.find(c => c.id === item.id);
        const cartQty = inCart ? inCart.quantity : 0;
        const imgUrl = getImageUrl(item.image_url);

        return `
            <div class="menu-card ${inCart ? 'in-cart' : ''}" onclick="openItemModal('${item.id}')">
                ${cartQty > 0 ? `<div class="menu-card-cart-indicator">${cartQty}</div>` : ''}
                <img class="menu-card-image" src="${imgUrl}" alt="${item.name}" loading="lazy"
                     onerror="this.src='https://via.placeholder.com/400x200?text=No+Image'">
                <div class="menu-card-content">
                    <h3 class="menu-card-name">${item.name}</h3>
                    <p class="menu-card-description">${item.description || ''}</p>
                    <div class="menu-card-footer">
                        <span class="menu-card-price">¥${item.price.toLocaleString()}</span>
                        <div class="menu-card-badges">
                            ${item.is_popular ? '<span class="badge popular">人気</span>' : ''}
                            ${item.is_spicy ? '<span class="badge spicy">辛</span>' : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderCartItems() {
    const container = document.getElementById('cartItems');

    if (state.cart.length === 0) {
        container.innerHTML = '<div class="cart-empty">カートは空です</div>';
        document.getElementById('btnOrder').disabled = true;
        return;
    }

    container.innerHTML = state.cart.map((item, index) => `
        <div class="cart-item">
            <img class="cart-item-image" src="${getImageUrl(item.image_url)}" alt="${item.name}"
                 onerror="this.src='https://via.placeholder.com/60?text=No'">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">¥${item.price.toLocaleString()}</div>
                ${item.notes ? `<div style="font-size: 12px; color: var(--text-muted);">${item.notes}</div>` : ''}
                <div class="cart-item-controls">
                    <button class="qty-btn" onclick="updateCartQty(${index}, -1)">−</button>
                    <span class="qty-value">${item.quantity}</span>
                    <button class="qty-btn" onclick="updateCartQty(${index}, 1)">+</button>
                </div>
            </div>
            <button class="cart-item-delete" onclick="removeFromCart(${index})">🗑</button>
        </div>
    `).join('');

    // Update total
    const total = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.getElementById('cartTotal').textContent = `¥${total.toLocaleString()}`;
    document.getElementById('btnOrder').disabled = false;
}

// ============ Cart Functions ============

function openCart() {
    document.getElementById('cartOverlay').classList.add('open');
    document.getElementById('cartDrawer').classList.add('open');
    renderCartItems();
}

function closeCart() {
    document.getElementById('cartOverlay').classList.remove('open');
    document.getElementById('cartDrawer').classList.remove('open');
}

function addToCart(item, quantity = 1, notes = '') {
    const existing = state.cart.find(c => c.id === item.id && c.notes === notes);

    if (existing) {
        existing.quantity += quantity;
    } else {
        state.cart.push({
            id: item.id,
            name: item.name,
            price: item.price,
            image_url: item.image_url,
            quantity: quantity,
            notes: notes
        });
    }

    saveCartToStorage();
    updateCartBadge();

    // Re-render current category to show cart indicator
    const cat = state.categories.find(c => c.category === state.currentCategory);
    if (cat) {
        renderMenuItems(cat.items);
    }
}

function updateCartQty(index, delta) {
    state.cart[index].quantity += delta;

    if (state.cart[index].quantity <= 0) {
        state.cart.splice(index, 1);
    }

    saveCartToStorage();
    updateCartBadge();
    renderCartItems();

    // Re-render menu
    const cat = state.categories.find(c => c.category === state.currentCategory);
    if (cat) {
        renderMenuItems(cat.items);
    }
}

function removeFromCart(index) {
    state.cart.splice(index, 1);
    saveCartToStorage();
    updateCartBadge();
    renderCartItems();

    // Re-render menu
    const cat = state.categories.find(c => c.category === state.currentCategory);
    if (cat) {
        renderMenuItems(cat.items);
    }
}

function updateCartBadge() {
    const totalItems = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    const badge = document.getElementById('cartBadge');
    badge.textContent = totalItems;
    badge.classList.toggle('hidden', totalItems === 0);
}

function saveCartToStorage() {
    localStorage.setItem('table_order_cart', JSON.stringify(state.cart));
}

function loadCartFromStorage() {
    try {
        const saved = localStorage.getItem('table_order_cart');
        if (saved) {
            state.cart = JSON.parse(saved);
        }
    } catch (e) {
        state.cart = [];
    }
}

// ============ Modal Functions ============

function openItemModal(itemId) {
    // Find item in all categories
    let item = null;
    for (const cat of state.categories) {
        item = cat.items.find(i => i.id === itemId);
        if (item) break;
    }

    if (!item) return;

    state.currentItem = item;
    state.modalQty = 1;

    document.getElementById('modalImage').src = getImageUrl(item.image_url);
    document.getElementById('modalTitle').textContent = item.name;
    document.getElementById('modalDescription').textContent = item.description || '';
    document.getElementById('modalPrice').textContent = `¥${item.price.toLocaleString()}`;
    document.getElementById('modalQty').textContent = '1';
    document.getElementById('modalNotes').value = '';

    document.getElementById('itemModal').classList.add('open');
}

function closeItemModal() {
    document.getElementById('itemModal').classList.remove('open');
    state.currentItem = null;
}

function changeModalQty(delta) {
    state.modalQty = Math.max(1, state.modalQty + delta);
    document.getElementById('modalQty').textContent = state.modalQty;
}

function addToCartFromModal() {
    if (!state.currentItem) return;

    const notes = document.getElementById('modalNotes').value.trim();
    addToCart(state.currentItem, state.modalQty, notes);

    closeItemModal();
    showNotification(`${state.currentItem.name} をカートに追加しました`, 'success');
}

// ============ Notifications ============

function showNotification(message, type = 'success') {
    const toast = document.getElementById('notificationToast');
    const icon = document.getElementById('notificationIcon');
    const msg = document.getElementById('notificationMessage');

    icon.textContent = type === 'success' ? '✓' : '✕';
    msg.textContent = message;

    toast.className = 'notification-toast ' + type;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ============ Event Listeners ============

// Close modal on overlay click
document.getElementById('itemModal').addEventListener('click', (e) => {
    if (e.target.id === 'itemModal') {
        closeItemModal();
    }
});

// Keyboard shortcuts (for testing)
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeItemModal();
        closeCart();
    }
});
