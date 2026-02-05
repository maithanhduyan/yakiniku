/**
 * Table Order App - 焼肉ヅアン
 * iPad table ordering system for Yakiniku JIAN
 */

// ============ Configuration ============
const CONFIG = {
    API_BASE: 'http://localhost:8000/api',
    WS_BASE: 'ws://localhost:8000/ws',
    DEFAULT_BRANCH: 'hirama',
    TAX_RATE: 0.10,
    CURRENCY: '¥'
};

// ============ State ============
let state = {
    branchCode: CONFIG.DEFAULT_BRANCH,
    tableId: null,
    tableNumber: 'T1',
    guestCount: 2,
    menu: [],
    cart: [],
    currentCategory: 'all',
    selectedItem: null,
    quantity: 1,
    ws: null
};

// ============ DOM Elements ============
const elements = {
    tableNumber: document.getElementById('tableNumber'),
    guestCount: document.getElementById('guestCount'),
    categoryNav: document.getElementById('categoryNav'),
    menuGrid: document.getElementById('menuGrid'),
    cartBtn: document.getElementById('cartBtn'),
    cartCount: document.getElementById('cartCount'),
    cartPanel: document.getElementById('cartPanel'),
    cartItems: document.getElementById('cartItems'),
    cartSubtotal: document.getElementById('cartSubtotal'),
    cartTotal: document.getElementById('cartTotal'),
    overlay: document.getElementById('overlay'),
    itemModal: document.getElementById('itemModal'),
    itemName: document.getElementById('itemName'),
    itemDescription: document.getElementById('itemDescription'),
    itemPrice: document.getElementById('itemPrice'),
    itemImage: document.getElementById('itemImage'),
    qtyValue: document.getElementById('qtyValue'),
    confirmModal: document.getElementById('confirmModal'),
    confirmItems: document.getElementById('confirmItems'),
    confirmTotal: document.getElementById('confirmTotal'),
    successModal: document.getElementById('successModal')
};

// ============ Menu Data (Mock) ============
const menuData = [
    // 牛肉
    { id: 1, name: '特選カルビ', category: 'beef', price: 1980, description: '厳選された上質な牛カルビ。霜降りの脂が絶品。', image: '🥩' },
    { id: 2, name: '上ハラミ', category: 'beef', price: 1680, description: '柔らかく旨味たっぷりのハラミ。', image: '🥩' },
    { id: 3, name: '牛タン塩', category: 'beef', price: 1480, description: 'コリコリ食感の牛タン。レモンでさっぱりと。', image: '🥩' },
    { id: 4, name: '和牛ロース', category: 'beef', price: 2480, description: 'A5ランク和牛の上質なロース。', image: '🥩' },
    { id: 5, name: '特選5種盛り', category: 'beef', price: 4980, description: 'カルビ、ロース、ハラミ、タン、ホルモンの豪華盛り合わせ。', image: '🍖' },

    // 豚肉
    { id: 10, name: 'サムギョプサル', category: 'pork', price: 1280, description: '厚切り豚バラ肉。野菜と一緒にどうぞ。', image: '🥓' },
    { id: 11, name: '豚トロ', category: 'pork', price: 980, description: 'ジューシーな豚トロ。', image: '🥓' },

    // 鶏肉
    { id: 20, name: '鶏もも', category: 'chicken', price: 780, description: 'プリプリの鶏もも肉。', image: '🍗' },
    { id: 21, name: 'ぼんじり', category: 'chicken', price: 680, description: 'コラーゲンたっぷり。', image: '🍗' },

    // ホルモン
    { id: 30, name: 'ホルモン盛り', category: 'hormone', price: 1580, description: 'ミノ、ハチノス、シマチョウの3種盛り。', image: '🫀' },
    { id: 31, name: 'マルチョウ', category: 'hormone', price: 880, description: '甘みのあるマルチョウ。', image: '🫀' },

    // 海鮮
    { id: 40, name: 'エビ', category: 'seafood', price: 780, description: 'プリプリの大エビ。', image: '🦐' },
    { id: 41, name: 'イカ', category: 'seafood', price: 680, description: '新鮮なイカ。', image: '🦑' },
    { id: 42, name: 'ホタテ', category: 'seafood', price: 880, description: '北海道産ホタテ。', image: '🐚' },

    // 野菜
    { id: 50, name: '野菜盛り合わせ', category: 'vegetable', price: 680, description: 'キャベツ、玉ねぎ、ピーマン、かぼちゃなど。', image: '🥬' },
    { id: 51, name: 'キムチ盛り合わせ', category: 'vegetable', price: 780, description: '白菜、カクテキ、オイキムチの3種。', image: '🥗' },
    { id: 52, name: 'サンチュ', category: 'vegetable', price: 380, description: 'お肉を包んでどうぞ。', image: '🥬' },

    // ご飯・麺
    { id: 60, name: 'ライス', category: 'rice', price: 300, description: '国産コシヒカリ。', image: '🍚' },
    { id: 61, name: '大盛りライス', category: 'rice', price: 400, description: '大盛りでお腹いっぱい。', image: '🍚' },
    { id: 62, name: '冷麺', category: 'rice', price: 880, description: 'さっぱり冷麺。〆にどうぞ。', image: '🍜' },
    { id: 63, name: 'ビビンバ', category: 'rice', price: 980, description: '石焼ビビンバ。', image: '🍲' },

    // サイドメニュー
    { id: 70, name: 'ナムル3種', category: 'side', price: 480, description: 'もやし、ほうれん草、大根のナムル。', image: '🥗' },
    { id: 71, name: 'チヂミ', category: 'side', price: 780, description: 'カリッと焼いたチヂミ。', image: '🥞' },
    { id: 72, name: '韓国のり', category: 'side', price: 280, description: 'ごま油香る韓国のり。', image: '🍃' },

    // ドリンク
    { id: 80, name: '生ビール', category: 'drink', price: 550, description: 'キンキンに冷えた生ビール。', image: '🍺' },
    { id: 81, name: '瓶ビール', category: 'drink', price: 600, description: 'アサヒスーパードライ。', image: '🍺' },
    { id: 82, name: 'チャミスル', category: 'drink', price: 680, description: '韓国焼酎。', image: '🍶' },
    { id: 83, name: 'マッコリ', category: 'drink', price: 580, description: '甘くてまろやか。', image: '🥛' },
    { id: 84, name: 'ハイボール', category: 'drink', price: 480, description: 'さっぱりハイボール。', image: '🥃' },
    { id: 85, name: 'ソフトドリンク', category: 'drink', price: 380, description: 'コーラ、ウーロン茶、オレンジジュースなど。', image: '🥤' },

    // デザート
    { id: 90, name: 'バニラアイス', category: 'dessert', price: 380, description: '濃厚バニラ。', image: '🍨' },
    { id: 91, name: 'シャーベット', category: 'dessert', price: 380, description: '柚子シャーベット。', image: '🍧' }
];

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    console.log('🍖 Table Order - 焼肉ヅアン initialized');

    // Get table info from URL params
    const params = new URLSearchParams(window.location.search);
    state.tableId = params.get('table') || 'demo-table-1';
    state.tableNumber = params.get('number') || 'T1';
    state.guestCount = parseInt(params.get('guests')) || 2;

    // Update display
    elements.tableNumber.textContent = state.tableNumber;
    elements.guestCount.textContent = `${state.guestCount}名様`;

    // Load menu
    state.menu = menuData;
    renderMenu();

    setupEventListeners();
    connectWebSocket();
}

// ============ Event Listeners ============
function setupEventListeners() {
    // Category navigation
    elements.categoryNav.addEventListener('click', (e) => {
        if (e.target.classList.contains('category-btn')) {
            document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            state.currentCategory = e.target.dataset.category;
            renderMenu();
        }
    });

    // Cart button
    elements.cartBtn.addEventListener('click', openCart);
    document.getElementById('closeCart').addEventListener('click', closeCart);
    elements.overlay.addEventListener('click', closeCart);

    // Cart actions
    document.getElementById('btnClearCart').addEventListener('click', clearCart);
    document.getElementById('btnOrder').addEventListener('click', openConfirmModal);

    // Item modal
    document.getElementById('btnCloseItem').addEventListener('click', closeItemModal);
    document.getElementById('qtyMinus').addEventListener('click', () => updateQuantity(-1));
    document.getElementById('qtyPlus').addEventListener('click', () => updateQuantity(1));
    document.getElementById('btnAddToCart').addEventListener('click', addToCart);

    // Confirm modal
    document.getElementById('btnCancelOrder').addEventListener('click', closeConfirmModal);
    document.getElementById('btnConfirmOrder').addEventListener('click', submitOrder);

    // Success modal
    document.getElementById('btnCloseSuccess').addEventListener('click', closeSuccessModal);

    // Call staff
    document.getElementById('callStaffBtn').addEventListener('click', callStaff);
}

// ============ Menu Functions ============
function renderMenu() {
    const filteredMenu = state.currentCategory === 'all'
        ? state.menu
        : state.menu.filter(item => item.category === state.currentCategory);

    elements.menuGrid.innerHTML = filteredMenu.map(item => `
        <div class="menu-item" data-item-id="${item.id}" onclick="openItemModal(${item.id})">
            <div class="item-image">${item.image}</div>
            <div class="item-info">
                <h3 class="item-name">${item.name}</h3>
                <p class="item-price">¥${item.price.toLocaleString()}</p>
            </div>
            <button class="quick-add-btn" onclick="event.stopPropagation(); quickAdd(${item.id})">+</button>
        </div>
    `).join('');
}

function openItemModal(itemId) {
    const item = state.menu.find(i => i.id === itemId);
    if (!item) return;

    state.selectedItem = item;
    state.quantity = 1;

    elements.itemName.textContent = item.name;
    elements.itemDescription.textContent = item.description;
    elements.itemPrice.textContent = `¥${item.price.toLocaleString()}`;
    elements.itemImage.textContent = item.image;
    elements.qtyValue.textContent = '1';

    elements.itemModal.style.display = 'flex';
}

function closeItemModal() {
    elements.itemModal.style.display = 'none';
    state.selectedItem = null;
    state.quantity = 1;
}

function updateQuantity(delta) {
    state.quantity = Math.max(1, Math.min(10, state.quantity + delta));
    elements.qtyValue.textContent = state.quantity;
}

function quickAdd(itemId) {
    const item = state.menu.find(i => i.id === itemId);
    if (!item) return;

    addItemToCart(item, 1);
}

function addToCart() {
    if (!state.selectedItem) return;

    addItemToCart(state.selectedItem, state.quantity);
    closeItemModal();
}

function addItemToCart(item, quantity) {
    const existingIndex = state.cart.findIndex(i => i.id === item.id);

    if (existingIndex >= 0) {
        state.cart[existingIndex].quantity += quantity;
    } else {
        state.cart.push({
            ...item,
            quantity: quantity
        });
    }

    updateCartUI();
    showToast(`${item.name} を追加しました`);
}

// ============ Cart Functions ============
function openCart() {
    elements.cartPanel.classList.add('open');
    elements.overlay.classList.add('show');
    renderCart();
}

function closeCart() {
    elements.cartPanel.classList.remove('open');
    elements.overlay.classList.remove('show');
}

function renderCart() {
    if (state.cart.length === 0) {
        elements.cartItems.innerHTML = '<div class="empty-cart">カートは空です</div>';
    } else {
        elements.cartItems.innerHTML = state.cart.map((item, index) => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <span class="cart-item-name">${item.name}</span>
                    <span class="cart-item-price">¥${item.price.toLocaleString()}</span>
                </div>
                <div class="cart-item-controls">
                    <button class="qty-btn small" onclick="updateCartItem(${index}, -1)">−</button>
                    <span class="cart-item-qty">${item.quantity}</span>
                    <button class="qty-btn small" onclick="updateCartItem(${index}, 1)">+</button>
                    <button class="remove-btn" onclick="removeCartItem(${index})">×</button>
                </div>
            </div>
        `).join('');
    }

    updateCartTotals();
}

function updateCartItem(index, delta) {
    state.cart[index].quantity += delta;

    if (state.cart[index].quantity <= 0) {
        state.cart.splice(index, 1);
    }

    renderCart();
    updateCartUI();
}

function removeCartItem(index) {
    state.cart.splice(index, 1);
    renderCart();
    updateCartUI();
}

function clearCart() {
    state.cart = [];
    renderCart();
    updateCartUI();
}

function updateCartUI() {
    const totalItems = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    elements.cartCount.textContent = totalItems;
    elements.cartCount.style.display = totalItems > 0 ? 'flex' : 'none';
}

function updateCartTotals() {
    const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const total = Math.floor(subtotal * (1 + CONFIG.TAX_RATE));

    elements.cartSubtotal.textContent = `¥${subtotal.toLocaleString()}`;
    elements.cartTotal.textContent = `¥${total.toLocaleString()}`;
}

function getCartTotal() {
    const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    return Math.floor(subtotal * (1 + CONFIG.TAX_RATE));
}

// ============ Order Functions ============
function openConfirmModal() {
    if (state.cart.length === 0) {
        showToast('カートに商品がありません', 'error');
        return;
    }

    closeCart();

    elements.confirmItems.innerHTML = state.cart.map(item => `
        <div class="confirm-item">
            <span class="confirm-item-name">${item.name} ×${item.quantity}</span>
            <span class="confirm-item-price">¥${(item.price * item.quantity).toLocaleString()}</span>
        </div>
    `).join('');

    elements.confirmTotal.textContent = `¥${getCartTotal().toLocaleString()}`;
    elements.confirmModal.style.display = 'flex';
}

function closeConfirmModal() {
    elements.confirmModal.style.display = 'none';
}

async function submitOrder() {
    closeConfirmModal();

    // Show loading
    showToast('注文を送信中...');

    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Show success
    elements.successModal.style.display = 'flex';

    // Clear cart
    state.cart = [];
    updateCartUI();
}

function closeSuccessModal() {
    elements.successModal.style.display = 'none';
}

// ============ Staff Call ============
function callStaff() {
    showToast('スタッフを呼びました。しばらくお待ちください。');

    // Mock API call to notify staff
    console.log('Calling staff for table:', state.tableNumber);
}

// ============ Utility Functions ============
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============ WebSocket ============
function connectWebSocket() {
    console.log('WebSocket connection placeholder');
}

// Make functions globally accessible
window.openItemModal = openItemModal;
window.quickAdd = quickAdd;
window.updateCartItem = updateCartItem;
window.removeCartItem = removeCartItem;
