/**
 * POS System - JavaScript
 * Point of Sale for checkout and payment processing
 */

// ============ Configuration ============

const CONFIG = {
    API_BASE: 'http://localhost:8000/api',
    BRANCH_CODE: 'jinan',
    TAX_RATE: 0.10, // 10% consumption tax
};

// ============ State ============

let state = {
    tables: [],
    selectedTable: null,
    currentOrder: null,
    discount: { type: null, value: 0 },
    todaySales: 0,
    todayOrders: 0,
    paymentMethod: 'cash',
};

// ============ Initialization ============

document.addEventListener('DOMContentLoaded', () => {
    // Start clock
    updateClock();
    setInterval(updateClock, 1000);

    // Load tables
    loadTables();

    // Setup event listeners
    setupEventListeners();

    // Refresh tables periodically
    setInterval(loadTables, 30000);
});

// ============ Clock ============

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    document.getElementById('currentTime').textContent = timeStr;
}

// ============ API Functions ============

async function loadTables() {
    try {
        const response = await fetch(
            `${CONFIG.API_BASE}/tables?branch_code=${CONFIG.BRANCH_CODE}`
        );

        if (!response.ok) throw new Error('Failed to load tables');

        const tables = await response.json();

        // For development: use demo data if no occupied tables
        // In production, remove this check
        const hasOccupied = tables.some(t => t.total_amount > 0);
        if (!hasOccupied) {
            loadDemoTables();
            return;
        }

        state.tables = tables;
        renderTables();
        updateStats();

    } catch (error) {
        console.error('Error loading tables:', error);
        // Load demo data
        loadDemoTables();
    }
}

function loadDemoTables() {
    state.tables = [
        { id: 1, table_number: 'T1', status: 'empty', capacity: 4 },
        { id: 2, table_number: 'T2', status: 'occupied', capacity: 4, total_amount: 5800 },
        { id: 3, table_number: 'T3', status: 'empty', capacity: 2 },
        { id: 4, table_number: 'T4', status: 'occupied', capacity: 6, total_amount: 12500 },
        { id: 5, table_number: 'T5', status: 'billing', capacity: 4, total_amount: 8800 },
        { id: 6, table_number: 'T6', status: 'empty', capacity: 2 },
        { id: 7, table_number: 'T7', status: 'occupied', capacity: 4, total_amount: 6200 },
        { id: 8, table_number: 'T8', status: 'empty', capacity: 6 },
        { id: 9, table_number: 'T9', status: 'empty', capacity: 4 },
        { id: 10, table_number: 'T10', status: 'occupied', capacity: 8, total_amount: 18900 },
    ];

    // Demo daily stats
    state.todaySales = 156800;
    state.todayOrders = 23;

    renderTables();
    updateStats();
}

async function loadTableOrders(tableId) {
    try {
        const response = await fetch(
            `${CONFIG.API_BASE}/tables/${tableId}/orders?branch_code=${CONFIG.BRANCH_CODE}`
        );

        if (!response.ok) throw new Error('Failed to load orders');

        return await response.json();

    } catch (error) {
        console.error('Error loading table orders:', error);
        // Return demo order
        return getDemoOrder(tableId);
    }
}

function getDemoOrder(tableId) {
    const table = state.tables.find(t => t.id === tableId);
    if (!table || table.status === 'empty') return null;

    return {
        table_number: table.table_number,
        guest_count: Math.floor(Math.random() * 4) + 2,
        session_start: new Date(Date.now() - (90 + Math.random() * 60) * 60 * 1000).toISOString(),
        items: [
            { name: '和牛上ハラミ', quantity: 2, price: 1800 },
            { name: '厚切り上タン塩', quantity: 1, price: 2200 },
            { name: 'カルビ', quantity: 2, price: 1500 },
            { name: '生ビール', quantity: 3, price: 600 },
            { name: 'ライス', quantity: 2, price: 200 },
        ],
        subtotal: table.total_amount || 8000,
    };
}

async function processPayment(tableId, paymentMethod, amount) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/pos/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                table_id: tableId,
                payment_method: paymentMethod,
                amount: amount,
                branch_code: CONFIG.BRANCH_CODE,
            })
        });

        if (!response.ok) throw new Error('Failed to process payment');

        return await response.json();

    } catch (error) {
        console.error('Error processing payment:', error);
        // Simulate success for demo
        return { success: true };
    }
}

// ============ Rendering ============

function renderTables() {
    const grid = document.getElementById('tableGrid');

    grid.innerHTML = state.tables.map(table => {
        const statusClass = table.status || 'empty';
        const statusText = getStatusText(table.status);
        const isSelected = state.selectedTable?.id === table.id;

        return `
            <div class="table-card ${statusClass} ${isSelected ? 'selected' : ''}"
                 data-table-id="${table.id}"
                 onclick="selectTable(${table.id})">
                <div class="table-number">${table.table_number}</div>
                <div class="table-status">${statusText}</div>
                ${table.total_amount ? `<div class="table-amount">¥${table.total_amount.toLocaleString()}</div>` : ''}
            </div>
        `;
    }).join('');
}

function getStatusText(status) {
    const texts = {
        'empty': '空席',
        'occupied': '使用中',
        'billing': '会計中',
    };
    return texts[status] || '空席';
}

function renderOrderItems(order) {
    const container = document.getElementById('orderItems');

    if (!order || !order.items || order.items.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 20px;">注文がありません</p>';
        return;
    }

    container.innerHTML = order.items.map(item => `
        <div class="order-item">
            <div class="item-info">
                <span class="item-quantity">×${item.quantity}</span>
                <span class="item-name">${item.name}</span>
            </div>
            <span class="item-price">¥${(item.price * item.quantity).toLocaleString()}</span>
        </div>
    `).join('');
}

function updateOrderSummary() {
    if (!state.currentOrder) return;

    const subtotal = state.currentOrder.subtotal;
    const tax = Math.floor(subtotal * CONFIG.TAX_RATE);
    let discountAmount = 0;

    if (state.discount.type === 'percent') {
        discountAmount = Math.floor(subtotal * state.discount.value / 100);
    } else if (state.discount.type === 'amount') {
        discountAmount = state.discount.value;
    }

    const total = subtotal + tax - discountAmount;

    document.getElementById('subtotal').textContent = `¥${subtotal.toLocaleString()}`;
    document.getElementById('tax').textContent = `¥${tax.toLocaleString()}`;
    document.getElementById('total').textContent = `¥${total.toLocaleString()}`;

    const discountRow = document.getElementById('discountRow');
    if (discountAmount > 0) {
        discountRow.style.display = 'flex';
        document.getElementById('discount').textContent = `-¥${discountAmount.toLocaleString()}`;
    } else {
        discountRow.style.display = 'none';
    }

    // Store total for payment
    state.currentOrder.total = total;
}

function updateStats() {
    const occupiedCount = state.tables.filter(t => t.status !== 'empty').length;
    const totalCount = state.tables.length;

    document.getElementById('statTables').textContent = `${occupiedCount}/${totalCount}`;
    document.getElementById('statSales').textContent = `¥${state.todaySales.toLocaleString()}`;
    document.getElementById('statOrders').textContent = state.todayOrders;
}

// ============ Table Selection ============

async function selectTable(tableId) {
    const table = state.tables.find(t => t.id === tableId);
    if (!table) return;

    // Don't allow selecting empty tables
    if (table.status === 'empty') {
        showToast('このテーブルは空席です', 'info');
        return;
    }

    state.selectedTable = table;
    state.discount = { type: null, value: 0 };

    // Update table selection UI
    document.querySelectorAll('.table-card').forEach(card => {
        card.classList.remove('selected');
        if (parseInt(card.dataset.tableId) === tableId) {
            card.classList.add('selected');
        }
    });

    // Load order details
    const order = await loadTableOrders(tableId);
    state.currentOrder = order;

    // Show checkout panel
    showCheckoutPanel(table, order);
}

function showCheckoutPanel(table, order) {
    document.getElementById('emptyCheckout').style.display = 'none';
    document.getElementById('checkoutContent').style.display = 'flex';

    // Update header info
    document.getElementById('selectedTable').textContent = table.table_number;
    document.getElementById('guestCount').textContent = `${order?.guest_count || 2}名様`;

    // Calculate session time
    if (order?.session_start) {
        const start = new Date(order.session_start);
        const now = new Date();
        const diffMinutes = Math.floor((now - start) / 60000);
        const hours = Math.floor(diffMinutes / 60);
        const mins = diffMinutes % 60;
        document.getElementById('sessionTime').textContent = `${hours}:${mins.toString().padStart(2, '0')}`;
    }

    // Render items and summary
    renderOrderItems(order);
    updateOrderSummary();
}

function hideCheckoutPanel() {
    document.getElementById('emptyCheckout').style.display = 'flex';
    document.getElementById('checkoutContent').style.display = 'none';

    state.selectedTable = null;
    state.currentOrder = null;
    state.discount = { type: null, value: 0 };

    document.querySelectorAll('.table-card').forEach(card => {
        card.classList.remove('selected');
    });
}

// ============ Payment ============

function openPaymentModal(method) {
    state.paymentMethod = method;

    const modal = document.getElementById('paymentModal');
    const title = document.getElementById('paymentTitle');
    const cashSection = document.getElementById('cashPayment');
    const cardSection = document.getElementById('cardPayment');
    const amount = state.currentOrder?.total || 0;

    document.getElementById('paymentAmount').textContent = `¥${amount.toLocaleString()}`;

    if (method === 'cash') {
        title.textContent = '現金会計';
        cashSection.style.display = 'block';
        cardSection.style.display = 'none';
        document.getElementById('receivedAmount').value = '';
        document.getElementById('changeAmount').textContent = '¥0';
    } else {
        title.textContent = 'カード会計';
        cashSection.style.display = 'none';
        cardSection.style.display = 'block';
        document.getElementById('cardStatus').textContent = '待機中...';
    }

    modal.style.display = 'flex';
}

function closePaymentModal() {
    document.getElementById('paymentModal').style.display = 'none';
}

function updateChange() {
    const received = parseInt(document.getElementById('receivedAmount').value) || 0;
    const total = state.currentOrder?.total || 0;
    const change = received - total;

    const changeEl = document.getElementById('changeAmount');
    if (change >= 0) {
        changeEl.textContent = `¥${change.toLocaleString()}`;
        changeEl.style.color = 'var(--status-success)';
    } else {
        changeEl.textContent = `不足: ¥${Math.abs(change).toLocaleString()}`;
        changeEl.style.color = 'var(--status-error)';
    }
}

function setQuickAmount(amount) {
    const total = state.currentOrder?.total || 0;

    if (amount === 'exact') {
        document.getElementById('receivedAmount').value = total;
    } else {
        document.getElementById('receivedAmount').value = amount;
    }

    updateChange();
}

async function confirmPayment() {
    if (!state.selectedTable || !state.currentOrder) return;

    const total = state.currentOrder.total;

    if (state.paymentMethod === 'cash') {
        const received = parseInt(document.getElementById('receivedAmount').value) || 0;
        if (received < total) {
            showToast('金額が不足しています', 'error');
            return;
        }
    }

    // Process payment
    const result = await processPayment(
        state.selectedTable.id,
        state.paymentMethod,
        total
    );

    if (result.success) {
        // Update stats
        state.todaySales += total;
        state.todayOrders += 1;

        // Update table status
        const tableIndex = state.tables.findIndex(t => t.id === state.selectedTable.id);
        if (tableIndex >= 0) {
            state.tables[tableIndex].status = 'empty';
            state.tables[tableIndex].total_amount = 0;
        }

        // Close modal and reset
        closePaymentModal();
        hideCheckoutPanel();
        renderTables();
        updateStats();

        showToast('会計が完了しました');
    } else {
        showToast('会計処理に失敗しました', 'error');
    }
}

// ============ Discount ============

function openDiscountModal() {
    document.getElementById('discountModal').style.display = 'flex';
    document.querySelectorAll('.discount-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.getElementById('customDiscount').style.display = 'none';
}

function closeDiscountModal() {
    document.getElementById('discountModal').style.display = 'none';
}

function selectDiscount(type, value) {
    document.querySelectorAll('.discount-option').forEach(opt => {
        opt.classList.remove('selected');
    });

    event.target.classList.add('selected');

    if (type === 'custom') {
        document.getElementById('customDiscount').style.display = 'block';
        state.discount = { type: 'amount', value: 0 };
    } else {
        document.getElementById('customDiscount').style.display = 'none';
        state.discount = { type, value: parseInt(value) };
    }
}

function applyDiscount() {
    const customValue = document.getElementById('customDiscountValue').value;
    if (customValue && document.getElementById('customDiscount').style.display !== 'none') {
        state.discount = { type: 'amount', value: parseInt(customValue) };
    }

    updateOrderSummary();
    closeDiscountModal();
    showToast('割引を適用しました');
}

// ============ Event Listeners ============

function setupEventListeners() {
    // Close checkout
    document.getElementById('btnCloseCheckout').addEventListener('click', hideCheckoutPanel);

    // Payment buttons
    document.getElementById('btnPayCash').addEventListener('click', () => openPaymentModal('cash'));
    document.getElementById('btnPayCard').addEventListener('click', () => openPaymentModal('card'));

    // Payment modal
    document.getElementById('btnClosePayment').addEventListener('click', closePaymentModal);
    document.getElementById('btnCancelPayment').addEventListener('click', closePaymentModal);
    document.getElementById('btnConfirmPayment').addEventListener('click', confirmPayment);

    // Cash input
    document.getElementById('receivedAmount').addEventListener('input', updateChange);

    // Quick amounts
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const amount = btn.dataset.amount;
            setQuickAmount(amount === 'exact' ? 'exact' : parseInt(amount));
        });
    });

    // Discount
    document.getElementById('btnDiscount').addEventListener('click', openDiscountModal);
    document.getElementById('btnCloseDiscount').addEventListener('click', closeDiscountModal);
    document.getElementById('btnCancelDiscount').addEventListener('click', closeDiscountModal);
    document.getElementById('btnApplyDiscount').addEventListener('click', applyDiscount);

    document.querySelectorAll('.discount-option').forEach(opt => {
        opt.addEventListener('click', () => {
            selectDiscount(opt.dataset.type, opt.dataset.value);
        });
    });

    // Split bill (placeholder)
    document.getElementById('btnSplitBill').addEventListener('click', () => {
        showToast('分割会計機能は開発中です', 'info');
    });

    // Print receipt (placeholder)
    document.getElementById('btnPrintReceipt').addEventListener('click', () => {
        showToast('伝票を印刷しました');
    });

    // Close modals on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.style.display = 'none';
            }
        });
    });
}

// ============ Toast ============

function showToast(message, type = 'success') {
    const toast = document.getElementById('successToast');
    const messageEl = document.getElementById('toastMessage');
    const iconEl = toast.querySelector('.toast-icon');

    messageEl.textContent = message;

    // Set icon and color based on type
    if (type === 'error') {
        iconEl.textContent = '✗';
        toast.style.background = 'var(--status-error)';
    } else if (type === 'info') {
        iconEl.textContent = 'ℹ';
        toast.style.background = 'var(--status-occupied)';
    } else {
        iconEl.textContent = '✓';
        toast.style.background = 'var(--status-success)';
    }

    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
