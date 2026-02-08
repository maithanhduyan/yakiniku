/**
 * POS Register App - 焼肉ヅアン
 * Point of Sale system for restaurant checkout
 */

// ============ Configuration ============
// Auto-detect: Dev (Live Server) → backend :8000 | Prod (Traefik) → same origin
const _host = window.location.hostname;
const _port = window.location.port;
const _isDev = _port && !['80', '443', ''].includes(_port);
const _proto = window.location.protocol;
const _wsProto = _proto === 'https:' ? 'wss:' : 'ws:';
const _base = _isDev ? `http://${_host}:8000` : `${_proto}//${_host}`;  // Dev: backend always HTTP

const CONFIG = {
    API_BASE: `${_base}/api`,
    WS_BASE: `${_isDev ? 'ws:' : _wsProto}//${_host}${_isDev ? ':8000' : ''}/ws`,
    DEFAULT_BRANCH: 'hirama',
    TAX_RATE: 0.10,
    CURRENCY: '¥'
};

// ============ State ============
let state = {
    branchCode: CONFIG.DEFAULT_BRANCH,
    tables: [],
    selectedTable: null,
    currentOrder: null,
    discount: { type: null, value: 0 },
    ws: null
};

// ============ DOM Elements ============
const elements = {
    tableGrid: document.getElementById('tableGrid'),
    emptyCheckout: document.getElementById('emptyCheckout'),
    checkoutContent: document.getElementById('checkoutContent'),
    selectedTable: document.getElementById('selectedTable'),
    guestCount: document.getElementById('guestCount'),
    sessionTime: document.getElementById('sessionTime'),
    orderItems: document.getElementById('orderItems'),
    subtotal: document.getElementById('subtotal'),
    tax: document.getElementById('tax'),
    discount: document.getElementById('discount'),
    discountRow: document.getElementById('discountRow'),
    total: document.getElementById('total'),
    statTables: document.getElementById('statTables'),
    statSales: document.getElementById('statSales'),
    statOrders: document.getElementById('statOrders'),
    currentTime: document.getElementById('currentTime'),
    paymentModal: document.getElementById('paymentModal'),
    paymentTitle: document.getElementById('paymentTitle'),
    paymentAmount: document.getElementById('paymentAmount'),
    cashPayment: document.getElementById('cashPayment'),
    cardPayment: document.getElementById('cardPayment'),
    receivedAmount: document.getElementById('receivedAmount'),
    changeAmount: document.getElementById('changeAmount'),
    discountModal: document.getElementById('discountModal'),
    successToast: document.getElementById('successToast'),
    toastMessage: document.getElementById('toastMessage')
};

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    console.log('💰 POS Register - 焼肉ヅアン initialized');

    setupEventListeners();
    updateClock();
    setInterval(updateClock, 1000);

    loadTables();
    loadDailyStats();
    connectWebSocket();
}

// ============ Event Listeners ============
function setupEventListeners() {
    // Close checkout
    document.getElementById('btnCloseCheckout')?.addEventListener('click', closeCheckout);

    // Payment buttons
    document.getElementById('btnPayCash')?.addEventListener('click', () => openPaymentModal('cash'));
    document.getElementById('btnPayCard')?.addEventListener('click', () => openPaymentModal('card'));

    // Payment modal
    document.getElementById('btnClosePayment')?.addEventListener('click', closePaymentModal);
    document.getElementById('btnCancelPayment')?.addEventListener('click', closePaymentModal);
    document.getElementById('btnConfirmPayment')?.addEventListener('click', confirmPayment);

    // Quick amount buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const amount = btn.dataset.amount;
            if (amount === 'exact') {
                elements.receivedAmount.value = calculateTotal();
            } else {
                elements.receivedAmount.value = parseInt(amount);
            }
            updateChange();
        });
    });

    // Received amount input
    elements.receivedAmount?.addEventListener('input', updateChange);

    // Discount
    document.getElementById('btnDiscount')?.addEventListener('click', openDiscountModal);
    document.getElementById('btnCloseDiscount')?.addEventListener('click', closeDiscountModal);
    document.getElementById('btnCancelDiscount')?.addEventListener('click', closeDiscountModal);
    document.getElementById('btnApplyDiscount')?.addEventListener('click', applyDiscount);

    // Discount options
    document.querySelectorAll('.discount-option').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.discount-option').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (btn.dataset.type === 'custom') {
                document.getElementById('customDiscount').style.display = 'block';
            } else {
                document.getElementById('customDiscount').style.display = 'none';
            }
        });
    });

    // Print receipt
    document.getElementById('btnPrintReceipt')?.addEventListener('click', printReceipt);
}

// ============ Clock ============
function updateClock() {
    const now = new Date();
    elements.currentTime.textContent = now.toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============ API Functions ============
async function loadTables() {
    try {
        // Mock data for demo
        state.tables = [
            { id: 'T1', name: 'T1', capacity: 4, status: 'occupied', guests: 3, startTime: '18:30' },
            { id: 'T2', name: 'T2', capacity: 4, status: 'empty', guests: 0 },
            { id: 'T3', name: 'T3', capacity: 6, status: 'occupied', guests: 5, startTime: '19:00' },
            { id: 'T4', name: 'T4', capacity: 2, status: 'billing', guests: 2, startTime: '17:45' },
            { id: 'T5', name: 'T5', capacity: 4, status: 'empty', guests: 0 },
            { id: 'T6', name: 'T6', capacity: 8, status: 'occupied', guests: 7, startTime: '19:30' },
            { id: 'T7', name: 'T7', capacity: 4, status: 'empty', guests: 0 },
            { id: 'T8', name: 'T8', capacity: 6, status: 'empty', guests: 0 },
            { id: 'T9', name: 'T9', capacity: 4, status: 'occupied', guests: 4, startTime: '18:00' },
            { id: 'T10', name: 'T10', capacity: 10, status: 'empty', guests: 0 }
        ];

        renderTables();
        updateTableStats();
    } catch (error) {
        console.error('Failed to load tables:', error);
    }
}

async function loadDailyStats() {
    // Mock data
    elements.statSales.textContent = '¥128,500';
    elements.statOrders.textContent = '23';
}

async function loadTableOrder(tableId) {
    // Mock order data
    const mockOrders = {
        'T1': {
            items: [
                { name: '特選カルビ', quantity: 2, price: 1980 },
                { name: '上ハラミ', quantity: 1, price: 1680 },
                { name: '牛タン塩', quantity: 2, price: 1480 },
                { name: 'ビール（中）', quantity: 3, price: 550 },
                { name: 'ライス', quantity: 2, price: 300 }
            ]
        },
        'T3': {
            items: [
                { name: '焼肉盛り合わせ（3人前）', quantity: 1, price: 5980 },
                { name: 'サムギョプサル', quantity: 2, price: 1280 },
                { name: 'キムチ盛り合わせ', quantity: 1, price: 780 },
                { name: 'チャミスル', quantity: 2, price: 680 }
            ]
        },
        'T4': {
            items: [
                { name: '和牛ロース', quantity: 1, price: 2480 },
                { name: '野菜盛り合わせ', quantity: 1, price: 680 },
                { name: 'ソフトドリンク', quantity: 2, price: 380 }
            ]
        },
        'T6': {
            items: [
                { name: '焼肉食べ放題（90分）', quantity: 7, price: 3980 },
                { name: '飲み放題（90分）', quantity: 5, price: 1500 }
            ]
        },
        'T9': {
            items: [
                { name: '特選5種盛り', quantity: 1, price: 4980 },
                { name: 'ホルモン盛り', quantity: 1, price: 1580 },
                { name: '冷麺', quantity: 2, price: 880 },
                { name: '生ビール', quantity: 4, price: 550 }
            ]
        }
    };

    return mockOrders[tableId] || { items: [] };
}

// ============ Render Functions ============
function renderTables() {
    elements.tableGrid.innerHTML = state.tables.map(table => `
        <div class="table-card ${table.status}" data-table-id="${table.id}" onclick="selectTable('${table.id}')">
            <div class="table-number">${table.name}</div>
            <div class="table-capacity">${table.capacity}名</div>
            ${table.status !== 'empty' ? `
                <div class="table-guests">${table.guests}名様</div>
                <div class="table-time">${table.startTime}〜</div>
            ` : ''}
            <div class="table-status-badge">${getStatusText(table.status)}</div>
        </div>
    `).join('');
}

function getStatusText(status) {
    const texts = {
        'empty': '空席',
        'occupied': '使用中',
        'billing': '会計中'
    };
    return texts[status] || status;
}

function updateTableStats() {
    const occupied = state.tables.filter(t => t.status !== 'empty').length;
    const total = state.tables.length;
    elements.statTables.textContent = `${occupied}/${total}`;
}

// ============ Checkout Functions ============
async function selectTable(tableId) {
    const table = state.tables.find(t => t.id === tableId);
    if (!table || table.status === 'empty') {
        showToast('このテーブルは空席です');
        return;
    }

    state.selectedTable = table;
    state.currentOrder = await loadTableOrder(tableId);
    state.discount = { type: null, value: 0 };

    renderCheckout();

    elements.emptyCheckout.style.display = 'none';
    elements.checkoutContent.style.display = 'flex';
}

function renderCheckout() {
    const table = state.selectedTable;
    const order = state.currentOrder;

    elements.selectedTable.textContent = table.name;
    elements.guestCount.textContent = `${table.guests}名様`;
    elements.sessionTime.textContent = calculateSessionTime(table.startTime);

    // Render order items
    elements.orderItems.innerHTML = order.items.map(item => `
        <div class="order-item">
            <div class="item-info">
                <span class="item-name">${item.name}</span>
                <span class="item-quantity">×${item.quantity}</span>
            </div>
            <div class="item-price">¥${(item.price * item.quantity).toLocaleString()}</div>
        </div>
    `).join('');

    updateTotals();
}

function calculateSessionTime(startTime) {
    if (!startTime) return '--:--';

    const [hours, minutes] = startTime.split(':').map(Number);
    const start = new Date();
    start.setHours(hours, minutes, 0);

    const now = new Date();
    const diff = Math.floor((now - start) / 60000); // minutes

    const h = Math.floor(diff / 60);
    const m = diff % 60;

    return `${h}:${m.toString().padStart(2, '0')}`;
}

function updateTotals() {
    const subtotal = calculateSubtotal();
    const discountAmount = calculateDiscountAmount(subtotal);
    const taxableAmount = subtotal - discountAmount;
    const tax = Math.floor(taxableAmount * CONFIG.TAX_RATE);
    const total = taxableAmount + tax;

    elements.subtotal.textContent = `¥${subtotal.toLocaleString()}`;
    elements.tax.textContent = `¥${tax.toLocaleString()}`;

    if (discountAmount > 0) {
        elements.discountRow.style.display = 'flex';
        elements.discount.textContent = `-¥${discountAmount.toLocaleString()}`;
    } else {
        elements.discountRow.style.display = 'none';
    }

    elements.total.textContent = `¥${total.toLocaleString()}`;
}

function calculateSubtotal() {
    if (!state.currentOrder) return 0;
    return state.currentOrder.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

function calculateDiscountAmount(subtotal) {
    if (!state.discount.type) return 0;

    if (state.discount.type === 'percent') {
        return Math.floor(subtotal * (state.discount.value / 100));
    } else {
        return state.discount.value;
    }
}

function calculateTotal() {
    const subtotal = calculateSubtotal();
    const discountAmount = calculateDiscountAmount(subtotal);
    const taxableAmount = subtotal - discountAmount;
    const tax = Math.floor(taxableAmount * CONFIG.TAX_RATE);
    return taxableAmount + tax;
}

function closeCheckout() {
    state.selectedTable = null;
    state.currentOrder = null;
    state.discount = { type: null, value: 0 };

    elements.emptyCheckout.style.display = 'flex';
    elements.checkoutContent.style.display = 'none';
}

// ============ Payment Functions ============
function openPaymentModal(type) {
    const total = calculateTotal();

    elements.paymentAmount.textContent = `¥${total.toLocaleString()}`;

    if (type === 'cash') {
        elements.paymentTitle.textContent = '現金会計';
        elements.cashPayment.style.display = 'block';
        elements.cardPayment.style.display = 'none';
        elements.receivedAmount.value = '';
        elements.changeAmount.textContent = '¥0';
    } else {
        elements.paymentTitle.textContent = 'カード会計';
        elements.cashPayment.style.display = 'none';
        elements.cardPayment.style.display = 'block';
    }

    elements.paymentModal.style.display = 'flex';
}

function closePaymentModal() {
    elements.paymentModal.style.display = 'none';
}

function updateChange() {
    const received = parseInt(elements.receivedAmount.value) || 0;
    const total = calculateTotal();
    const change = received - total;

    elements.changeAmount.textContent = change >= 0 ? `¥${change.toLocaleString()}` : '¥0';
    elements.changeAmount.style.color = change >= 0 ? '#22c55e' : '#ef4444';
}

async function confirmPayment() {
    const total = calculateTotal();
    const received = parseInt(elements.receivedAmount.value) || 0;

    // Validate cash payment
    if (elements.cashPayment.style.display !== 'none' && received < total) {
        showToast('お預かり金額が不足しています', 'error');
        return;
    }

    // Process payment (mock)
    console.log('Processing payment:', {
        table: state.selectedTable.id,
        total: total,
        received: received,
        change: received - total
    });

    // Update table status
    const tableIndex = state.tables.findIndex(t => t.id === state.selectedTable.id);
    if (tableIndex >= 0) {
        state.tables[tableIndex].status = 'empty';
        state.tables[tableIndex].guests = 0;
        state.tables[tableIndex].startTime = null;
    }

    // Update UI
    renderTables();
    updateTableStats();
    closePaymentModal();
    closeCheckout();

    // Update daily stats (mock increment)
    const currentSales = parseInt(elements.statSales.textContent.replace(/[¥,]/g, '')) || 0;
    const currentOrders = parseInt(elements.statOrders.textContent) || 0;
    elements.statSales.textContent = `¥${(currentSales + total).toLocaleString()}`;
    elements.statOrders.textContent = (currentOrders + 1).toString();

    showToast('会計が完了しました');
}

// ============ Discount Functions ============
function openDiscountModal() {
    elements.discountModal.style.display = 'flex';
    document.querySelectorAll('.discount-option').forEach(b => b.classList.remove('active'));
    document.getElementById('customDiscount').style.display = 'none';
}

function closeDiscountModal() {
    elements.discountModal.style.display = 'none';
}

function applyDiscount() {
    const activeOption = document.querySelector('.discount-option.active');
    if (!activeOption) {
        showToast('割引を選択してください', 'error');
        return;
    }

    if (activeOption.dataset.type === 'custom') {
        const customValue = parseInt(document.getElementById('customDiscountValue').value) || 0;
        if (customValue <= 0) {
            showToast('金額を入力してください', 'error');
            return;
        }
        state.discount = { type: 'amount', value: customValue };
    } else {
        state.discount = {
            type: activeOption.dataset.type,
            value: parseInt(activeOption.dataset.value)
        };
    }

    updateTotals();
    closeDiscountModal();
    showToast('割引を適用しました');
}

// ============ Utility Functions ============
function printReceipt() {
    showToast('伝票を印刷中...');
    // Implement actual printing logic
}

function showToast(message, type = 'success') {
    elements.toastMessage.textContent = message;
    elements.successToast.className = `toast ${type}`;
    elements.successToast.classList.add('show');

    setTimeout(() => {
        elements.successToast.classList.remove('show');
    }, 3000);
}

// ============ WebSocket ============
function connectWebSocket() {
    // WebSocket connection for real-time updates
    console.log('WebSocket connection placeholder');
}

// Make selectTable globally accessible
window.selectTable = selectTable;
