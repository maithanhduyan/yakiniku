/**
 * Check-in App - JavaScript
 * Customer reception and seating management
 */

// ============ Configuration ============

const CONFIG = {
    API_BASE: 'http://localhost:8000/api',
    BRANCH_CODE: 'hirama',
    SCAN_INTERVAL: 100,      // ms between scans
    RESULT_DISPLAY_TIME: 8000,  // ms to show result
    REFRESH_INTERVAL: 30000,    // ms to refresh dashboard
};

// ============ State ============

let state = {
    currentMode: 'scan',
    isScanning: false,
    scanner: null,
    guestCount: 2,
    pendingAssignment: null,  // Booking or waiting entry to assign table
    dashboardData: null,
};

// ============ Initialization ============

document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);

    // Start in scan mode
    switchMode('scan');

    // Refresh dashboard periodically
    setInterval(refreshDashboard, CONFIG.REFRESH_INTERVAL);
});

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
    document.getElementById('currentTime').textContent = timeStr;
}

// ============ Mode Switching ============

function switchMode(mode) {
    state.currentMode = mode;

    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Update mode label
    const labels = {
        'scan': 'QRスキャン',
        'dashboard': 'ダッシュボード',
        'result': '結果'
    };
    document.getElementById('modeLabel').textContent = labels[mode] || '';

    // Show/hide panels
    document.getElementById('scanMode').classList.toggle('active', mode === 'scan');
    document.getElementById('resultMode').classList.toggle('active', mode === 'result');
    document.getElementById('dashboardMode').classList.toggle('active', mode === 'dashboard');

    // Start/stop scanner
    if (mode === 'scan') {
        startScanner();
    } else {
        stopScanner();
    }

    // Load dashboard data
    if (mode === 'dashboard') {
        loadDashboard();
    }
}

// ============ QR Scanner ============

async function startScanner() {
    if (state.isScanning) return;

    try {
        const video = document.getElementById('qrVideo');
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });

        video.srcObject = stream;
        state.isScanning = true;

        // Use simple interval-based scanning
        scanLoop();

    } catch (error) {
        console.error('Camera error:', error);
        // Show manual input as fallback
        document.querySelector('.manual-input').style.display = 'block';
    }
}

function stopScanner() {
    state.isScanning = false;

    const video = document.getElementById('qrVideo');
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
}

async function scanLoop() {
    if (!state.isScanning) return;

    // If we have QR scanner library
    if (typeof QrScanner !== 'undefined') {
        // Use library
    } else {
        // For demo, just wait for manual input
    }

    setTimeout(scanLoop, CONFIG.SCAN_INTERVAL);
}

// Demo function to simulate QR scan
async function simulateScan(token) {
    await processQRCode(token);
}

async function processQRCode(token) {
    stopScanner();

    try {
        const response = await fetch(`${CONFIG.API_BASE}/checkin/scan?qr_token=${token}&branch_code=${CONFIG.BRANCH_CODE}`, {
            method: 'POST'
        });

        const result = await response.json();
        showResult(result);

    } catch (error) {
        console.error('Scan error:', error);
        showResult({
            success: false,
            message: 'エラーが発生しました。\nスタッフにお声がけください。'
        });
    }
}

// ============ Result Display ============

function showResult(result) {
    const container = document.getElementById('resultContainer');

    if (result.success && result.table_assigned) {
        // Success - show table assignment
        container.innerHTML = `
            <div class="animate-in">
                <div class="result-icon">🎉</div>
                <div class="result-message">${escapeHtml(result.message)}</div>
                <div class="result-table-info">
                    <div class="result-table-number">テーブル ${escapeHtml(result.table_number)}</div>
                    ${result.table_zone ? `<div class="result-table-zone">${escapeHtml(result.table_zone)}</div>` : ''}
                </div>
                <div class="result-submessage">スタッフがご案内いたします</div>
            </div>
        `;

        // Show success animation
        showSuccessAnimation(result.table_number);

    } else if (result.success && result.need_to_wait) {
        // Need to wait
        container.innerHTML = `
            <div class="animate-in">
                <div class="result-icon">⏳</div>
                <div class="result-message">${escapeHtml(result.message)}</div>
                <div class="result-waiting-info">
                    ${result.queue_number ? `<div class="result-queue-number">番号: ${result.queue_number}</div>` : ''}
                    <div class="result-wait-time">
                        待ち時間目安: 約${result.estimated_wait_minutes || 15}分
                        ${result.waiting_ahead ? `<br>${result.waiting_ahead}組お待ちです` : ''}
                    </div>
                </div>
                <div class="result-submessage">お呼びするまでお待ちください</div>
            </div>
        `;

    } else {
        // Error or not found
        container.innerHTML = `
            <div class="animate-in">
                <div class="result-icon">❌</div>
                <div class="result-message">${escapeHtml(result.message)}</div>
                <div class="result-actions">
                    <button class="btn-primary btn-large" onclick="switchMode('scan')">
                        もう一度スキャン
                    </button>
                </div>
            </div>
        `;
    }

    switchMode('result');

    // Auto return to scan after delay (for success)
    if (result.success) {
        setTimeout(() => {
            switchMode('scan');
        }, CONFIG.RESULT_DISPLAY_TIME);
    }
}

function showSuccessAnimation(tableNumber) {
    const overlay = document.createElement('div');
    overlay.className = 'success-animation';
    overlay.innerHTML = `
        <div class="checkmark">✔</div>
        <div class="message">テーブル ${escapeHtml(tableNumber)}</div>
    `;

    document.body.appendChild(overlay);

    setTimeout(() => {
        overlay.remove();
    }, 2000);
}

// ============ Dashboard ============

async function loadDashboard() {
    try {
        const response = await fetch(
            `${CONFIG.API_BASE}/checkin/dashboard?branch_code=${CONFIG.BRANCH_CODE}`
        );

        if (!response.ok) throw new Error('Failed to load dashboard');

        state.dashboardData = await response.json();
        renderDashboard();

    } catch (error) {
        console.error('Dashboard error:', error);
        renderDemoDashboard();
    }
}

async function refreshDashboard() {
    if (state.currentMode === 'dashboard') {
        await loadDashboard();
    }
}

function renderDashboard() {
    const data = state.dashboardData;
    if (!data) return;

    // Render bookings
    const bookingList = document.getElementById('bookingList');
    if (data.upcoming_bookings.length === 0) {
        bookingList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <p>本日の予約はありません</p>
            </div>
        `;
    } else {
        bookingList.innerHTML = data.upcoming_bookings.map(b => `
            <div class="booking-item" onclick="selectBookingForAssign('${b.id}')">
                <div class="booking-time">${escapeHtml(b.time)}</div>
                <div class="booking-info">
                    <div class="booking-name">${escapeHtml(b.guest_name)}様</div>
                    <div class="booking-guests">${b.guest_count}名</div>
                </div>
                <span class="booking-status ${b.status}">${getStatusLabel(b.status)}</span>
            </div>
        `).join('');
    }

    // Render waiting list
    const waitingList = document.getElementById('waitingList');
    if (data.waiting_list.length === 0) {
        waitingList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">👥</div>
                <p>順番待ちはいません</p>
            </div>
        `;
    } else {
        waitingList.innerHTML = data.waiting_list.map(w => `
            <div class="waiting-item ${w.status === 'called' ? 'called' : ''}">
                <div class="waiting-number">${w.queue_number}</div>
                <div class="waiting-info">
                    <div class="waiting-name">${escapeHtml(w.customer_name)}様</div>
                    <div class="waiting-guests">${w.guest_count}名</div>
                </div>
                <div class="waiting-actions">
                    ${w.status === 'waiting' ? `
                        <button class="btn-call" onclick="callWaiting('${w.id}')">呼出</button>
                    ` : ''}
                    <button class="btn-seat" onclick="selectWaitingForAssign('${w.id}')">案内</button>
                </div>
            </div>
        `).join('');
    }

    // Render tables
    const tableGrid = document.getElementById('tableGrid');
    tableGrid.innerHTML = data.available_tables.map(t => `
        <div class="table-item available" onclick="quickAssignTable('${t.id}')">
            <div class="table-number">${escapeHtml(t.table_number)}</div>
            <div class="table-capacity">${t.capacity}名</div>
        </div>
    `).join('');

    // Update stats
    document.getElementById('statCheckedIn').textContent = data.stats.checked_in_today;
    document.getElementById('statWaiting').textContent = data.stats.waiting_count;
    document.getElementById('statAvailable').textContent = data.stats.available_tables_count;
}

function renderDemoDashboard() {
    // Demo data for development
    state.dashboardData = {
        upcoming_bookings: [
            { id: '1', time: '17:00', guest_name: '田中', guest_count: 4, status: 'confirmed' },
            { id: '2', time: '17:30', guest_name: '佐藤', guest_count: 2, status: 'pending' },
            { id: '3', time: '18:00', guest_name: '鈴木', guest_count: 6, status: 'confirmed' },
        ],
        waiting_list: [
            { id: 'w1', queue_number: 1, customer_name: '山田', guest_count: 3, status: 'called' },
            { id: 'w2', queue_number: 2, customer_name: '高橋', guest_count: 2, status: 'waiting' },
        ],
        available_tables: [
            { id: 't1', table_number: 'T1', capacity: 4 },
            { id: 't3', table_number: 'T3', capacity: 2 },
            { id: 't7', table_number: 'T7', capacity: 6 },
        ],
        stats: {
            checked_in_today: 12,
            waiting_count: 2,
            available_tables_count: 3
        }
    };

    renderDashboard();
}

function getStatusLabel(status) {
    const labels = {
        'pending': '未確認',
        'confirmed': '確認済',
        'checked_in': 'チェックイン済'
    };
    return labels[status] || status;
}

// ============ Walk-in Registration ============

function showWalkInForm() {
    document.getElementById('walkInModal').classList.add('active');
    document.getElementById('walkInName').focus();
}

function adjustGuests(delta) {
    state.guestCount = Math.max(1, Math.min(20, state.guestCount + delta));
    document.getElementById('guestCount').textContent = state.guestCount;
}

async function submitWalkIn(event) {
    event.preventDefault();

    const data = {
        branch_code: CONFIG.BRANCH_CODE,
        customer_name: document.getElementById('walkInName').value,
        customer_phone: document.getElementById('walkInPhone').value || null,
        guest_count: state.guestCount,
        note: document.getElementById('walkInNote').value || null
    };

    try {
        const response = await fetch(`${CONFIG.API_BASE}/checkin/walkin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Failed to register');

        const result = await response.json();

        closeModal('walkInModal');

        // Show result
        showResult({
            success: true,
            need_to_wait: true,
            message: `${data.customer_name}様\n登録完了しました`,
            queue_number: result.queue_number,
            estimated_wait_minutes: result.estimated_wait_minutes,
            waiting_ahead: result.waiting_ahead
        });

        // Reset form
        document.getElementById('walkInForm').reset();
        state.guestCount = 2;
        document.getElementById('guestCount').textContent = 2;

    } catch (error) {
        console.error('Walk-in error:', error);
        alert('登録に失敗しました。もう一度お試しください。');
    }
}

// ============ Manual QR Input ============

function showManualInput() {
    document.getElementById('manualInputModal').classList.add('active');
    document.getElementById('manualCode').focus();
}

async function submitManualCode(event) {
    event.preventDefault();

    const code = document.getElementById('manualCode').value.trim();
    if (!code) return;

    closeModal('manualInputModal');
    await processQRCode(code);

    document.getElementById('manualCode').value = '';
}

// ============ Table Assignment ============

function selectBookingForAssign(bookingId) {
    const booking = state.dashboardData?.upcoming_bookings.find(b => b.id === bookingId);
    if (!booking) return;

    state.pendingAssignment = { type: 'booking', id: bookingId, data: booking };
    showTableAssignModal(booking.guest_name, booking.guest_count);
}

function selectWaitingForAssign(waitingId) {
    const waiting = state.dashboardData?.waiting_list.find(w => w.id === waitingId);
    if (!waiting) return;

    state.pendingAssignment = { type: 'waiting', id: waitingId, data: waiting };
    showTableAssignModal(waiting.customer_name, waiting.guest_count);
}

function showTableAssignModal(customerName, guestCount) {
    const availableTables = state.dashboardData?.available_tables || [];

    document.getElementById('assignInfo').innerHTML = `
        <div class="assign-customer">${escapeHtml(customerName)}様</div>
        <div class="assign-guests">${guestCount}名</div>
    `;

    const suitable = availableTables.filter(t => t.capacity >= guestCount);

    document.getElementById('tableSelection').innerHTML = suitable.length > 0
        ? suitable.map(t => `
            <div class="table-option" onclick="assignTable('${t.id}')">
                <div class="table-number">${escapeHtml(t.table_number)}</div>
                <div class="table-capacity">${t.capacity}名席</div>
            </div>
        `).join('')
        : '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">適切な空席がありません</p>';

    document.getElementById('assignTableModal').classList.add('active');
}

async function assignTable(tableId) {
    if (!state.pendingAssignment) return;

    const body = {
        table_id: tableId
    };

    if (state.pendingAssignment.type === 'booking') {
        body.booking_id = state.pendingAssignment.id;
    } else {
        body.waiting_id = state.pendingAssignment.id;
    }

    try {
        const response = await fetch(
            `${CONFIG.API_BASE}/checkin/assign-table?branch_code=${CONFIG.BRANCH_CODE}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            }
        );

        if (!response.ok) throw new Error('Failed to assign');

        const result = await response.json();

        closeModal('assignTableModal');

        // Show success
        showResult({
            success: true,
            table_assigned: true,
            message: `${state.pendingAssignment.data.customer_name || state.pendingAssignment.data.guest_name}様`,
            table_number: result.table_number,
            table_zone: result.table_zone
        });

        state.pendingAssignment = null;

        // Refresh dashboard
        loadDashboard();

    } catch (error) {
        console.error('Assign error:', error);
        alert('テーブル割り当てに失敗しました');
    }
}

function quickAssignTable(tableId) {
    // If there's someone waiting, assign them
    const waiting = state.dashboardData?.waiting_list.find(w => w.status === 'called');
    if (waiting) {
        state.pendingAssignment = { type: 'waiting', id: waiting.id, data: waiting };
        assignTable(tableId);
        return;
    }

    // Otherwise show who to assign
    if (state.dashboardData?.waiting_list.length > 0 || state.dashboardData?.upcoming_bookings.length > 0) {
        alert('先に予約またはお待ちのお客様を選択してください');
    }
}

async function callWaiting(waitingId) {
    try {
        const response = await fetch(
            `${CONFIG.API_BASE}/checkin/waiting/${waitingId}/call`,
            { method: 'POST' }
        );

        if (!response.ok) throw new Error('Failed to call');

        const result = await response.json();

        // Play sound
        playCallSound();

        // Refresh
        loadDashboard();

    } catch (error) {
        console.error('Call error:', error);
    }
}

function playCallSound() {
    // Simple beep sound
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.frequency.value = 880;
        gain.gain.value = 0.3;

        osc.start();
        osc.stop(ctx.currentTime + 0.2);
    } catch (e) {}
}

// ============ Utilities ============

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modals on backdrop click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// For demo/testing - expose functions
window.simulateScan = simulateScan;
window.loadDashboard = loadDashboard;
