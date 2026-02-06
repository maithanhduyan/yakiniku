/**
 * Table Order App - JavaScript
 * iPad table ordering system for Yakiniku Jinan
 */

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
    wsConnected: false,
    wsRetryCount: 0,
    maxWsRetries: 3,
    isLoading: true,
    apiStatus: 'pending', // pending, success, error
    wsStatus: 'pending',  // pending, success, error
    // Pagination
    currentPage: 1,
    itemsPerPage: 10  // Default for tablet landscape (5 cols × 2 rows)
};

// ============ Dynamic Grid Layout ============

/**
 * Calculate how many items fit on screen without scrolling.
 * Reads CSS grid columns AND rows from computed style.
 * Tablet-first: grid-template-rows is explicit so we read it directly.
 */
function calculateItemsPerPage() {
    const menuSection = document.getElementById('menuSection');
    const menuGrid = document.getElementById('menuGrid');
    if (!menuSection || !menuGrid) return;

    // Get computed grid style
    const gridStyle = window.getComputedStyle(menuGrid);

    // Read columns from CSS grid
    const colTracks = gridStyle.gridTemplateColumns.split(' ').filter(s => s.length > 0);
    const columns = colTracks.length || 4;

    // Read rows from CSS grid-template-rows (explicit rows set by media queries)
    const rowTracks = gridStyle.gridTemplateRows.split(' ').filter(s => s.length > 0);
    let rows;

    if (rowTracks.length > 0 && rowTracks[0] !== 'none') {
        // Use explicit row count from CSS
        rows = rowTracks.length;
    } else {
        // Fallback: calculate from available height
        const sectionHeight = menuSection.clientHeight;
        if (sectionHeight <= 0) return;
        const gap = parseFloat(gridStyle.rowGap) || parseFloat(gridStyle.gap) || 8;
        const minCardHeight = window.innerWidth >= 1024 ? 180 : (window.innerWidth >= 600 ? 160 : 140);
        rows = Math.max(1, Math.floor((sectionHeight + gap) / (minCardHeight + gap)));
    }

    const newItemsPerPage = columns * rows;

    // Only re-render if items per page actually changed
    if (newItemsPerPage !== state.itemsPerPage) {
        state.itemsPerPage = newItemsPerPage;
        state.currentPage = 1;
        // Re-render current category
        const cat = state.categories.find(c => c.category === state.currentCategory);
        if (cat) {
            renderMenuItems(cat.items);
        }
    }
}

// ============ Loading State Management ============

function updateLoadingStatus(type, status) {
    const statusEl = document.getElementById(`${type}Status`);
    if (!statusEl) return;

    statusEl.classList.remove('success', 'error');

    if (status === 'success') {
        statusEl.classList.add('success');
    } else if (status === 'error') {
        statusEl.classList.add('error');
    }

    state[`${type}Status`] = status;
}

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

    // Remove skeleton loaders
    document.querySelectorAll('.category-skeleton, .menu-skeleton').forEach(el => {
        el.remove();
    });
}

function showConnectionBar(isOnline) {
    const bar = document.getElementById('connectionBar');
    if (!bar) return;

    bar.classList.remove('online', 'offline');
    bar.classList.add('show', isOnline ? 'online' : 'offline');

    const icon = bar.querySelector('.connection-icon');
    const text = bar.querySelector('.connection-text');

    if (isOnline) {
        icon.textContent = '🟢';
        text.textContent = t('connection.online');
        // Auto-hide after 3 seconds when online
        setTimeout(() => {
            bar.classList.remove('show');
        }, 3000);
    } else {
        icon.textContent = '🔴';
        text.textContent = t('connection.offline');
    }
}

function hideConnectionBar() {
    const bar = document.getElementById('connectionBar');
    if (bar) {
        bar.classList.remove('show');
    }
}

// ============ Initialization ============

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize i18n
    I18N.init();

    // Show loading overlay
    showLoading();

    // Load saved cart
    loadCartFromStorage();

    // Setup table info
    setupTableInfo();

    // Load menu with loading state
    await loadMenu();

    // Setup WebSocket for real-time updates
    setupWebSocket();

    // Update UI
    updateCartBadge();

    // Calculate dynamic items per page based on viewport
    // Delay slightly to ensure layout is settled
    requestAnimationFrame(() => {
        calculateItemsPerPage();
    });

    // Recalculate on resize / orientation change
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => calculateItemsPerPage(), 150);
    });
    window.addEventListener('orientationchange', () => {
        setTimeout(() => calculateItemsPerPage(), 300);
    });

    // Hide loading after initial load (with minimum display time)
    setTimeout(() => {
        hideLoading();
        showConnectionBar(state.isOnline);
    }, 1000);
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
    document.getElementById('guestCount').textContent = `${guestCount}${t('guest.suffix')}`;
}

// ============ API Functions ============

async function loadMenu() {
    try {
        updateLoadingStatus('api', 'pending');

        const response = await fetch(`${CONFIG.API_URL}/menu/categories?branch_code=${CONFIG.BRANCH_CODE}`);

        if (!response.ok) {
            throw new Error('Failed to load menu');
        }

        const data = await response.json();

        // Check if API returned valid data
        if (data.categories && data.categories.length > 0) {
            state.categories = data.categories;
            state.isOnline = true;
            updateLoadingStatus('api', 'success');
        } else {
            // API returned empty data, use demo
            throw new Error('Empty menu data');
        }

        renderCategories();
        selectCategory(state.categories[0]?.category || 'meat');

    } catch (error) {
        console.error('Error loading menu:', error);
        state.isOnline = false;
        updateLoadingStatus('api', 'error');
        // Load demo data if API fails
        loadDemoMenu();
    }
}

// Unsplash fallback images by category
const UNSPLASH_IMAGES = {
    meat: {
        default: 'https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400',
        items: {
            'ハラミ': 'https://images.unsplash.com/photo-1546833998-877b37c2e5c6?w=400',
            'タン': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400',
            'カルビ': 'https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400',
            'ロース': 'https://images.unsplash.com/photo-1558030089-02acba3c214e?w=400',
            'ホルモン': 'https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=400',
            '盛り合わせ': 'https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400',
            '豚': 'https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=400',
            '鶏': 'https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=400',
        }
    },
    drinks: {
        default: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400',
        items: {
            'ビール': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400',
            'ハイボール': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400',
            'サワー': 'https://images.unsplash.com/photo-1560508180-03f285f67c1a?w=400',
            '梅酒': 'https://images.unsplash.com/photo-1560508180-03f285f67c1a?w=400',
            'マッコリ': 'https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=400',
            '焼酎': 'https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=400',
            'ウーロン茶': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400',
            'コーラ': 'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400',
            'ジュース': 'https://images.unsplash.com/photo-1534353473418-4cfa6c56fd38?w=400',
        }
    },
    salad: {
        default: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
        items: {
            'チョレギ': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
            'シーザー': 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400',
            'ナムル': 'https://images.unsplash.com/photo-1547496502-affa22d38842?w=400',
            'キムチ': 'https://images.unsplash.com/photo-1583224964978-2257b960c3d3?w=400',
        }
    },
    rice: {
        default: 'https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400',
        items: {
            'ライス': 'https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400',
            'ビビンバ': 'https://images.unsplash.com/photo-1553163147-622ab57be1c7?w=400',
            '冷麺': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
            'クッパ': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400',
        }
    },
    side: {
        default: 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400',
        items: {
            'スープ': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400',
            '枝豆': 'https://images.unsplash.com/photo-1564894809611-1742fc40ed80?w=400',
            '海苔': 'https://images.unsplash.com/photo-1519984388953-d2406bc725e1?w=400',
            'チヂミ': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400',
        }
    },
    dessert: {
        default: 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400',
        items: {
            'アイス': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400',
            '杏仁豆腐': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400',
            'シャーベット': 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=400',
        }
    },
    set: {
        default: 'https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400',
        items: {
            '定食': 'https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400',
            'コース': 'https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?w=400',
        }
    }
};

// Get fallback image URL for an item
function getFallbackImage(category, itemName) {
    const catImages = UNSPLASH_IMAGES[category] || UNSPLASH_IMAGES.meat;
    // Try to find a matching keyword in item name
    for (const [keyword, url] of Object.entries(catImages.items || {})) {
        if (itemName.includes(keyword)) {
            return url;
        }
    }
    return catImages.default;
}

function loadDemoMenu() {
    // Full menu data matching backend (40 items)
    state.categories = [
        {
            category: 'meat',
            category_label: t('cat.meat'),
            icon: '🥩',
            items: [
                { id: 'menu-001', name: t('demo.meat.wagyu_harami'), description: t('demo.meat.wagyu_harami.desc'), price: 1800, image_url: getFallbackImage('meat', 'ハラミ'), is_popular: true },
                { id: 'menu-002', name: t('demo.meat.atsugiri_tan'), description: t('demo.meat.atsugiri_tan.desc'), price: 2200, image_url: getFallbackImage('meat', 'タン'), is_popular: true },
                { id: 'menu-003', name: t('demo.meat.tokusen_kalbi'), description: t('demo.meat.tokusen_kalbi.desc'), price: 1800, image_url: getFallbackImage('meat', 'カルビ'), is_popular: true },
                { id: 'menu-004', name: t('demo.meat.kalbi'), description: t('demo.meat.kalbi.desc'), price: 1500, image_url: getFallbackImage('meat', 'カルビ') },
                { id: 'menu-005', name: t('demo.meat.jo_rosu'), description: t('demo.meat.jo_rosu.desc'), price: 1700, image_url: getFallbackImage('meat', 'ロース') },
                { id: 'menu-006', name: t('demo.meat.rosu'), description: t('demo.meat.rosu.desc'), price: 1400, image_url: getFallbackImage('meat', 'ロース') },
                { id: 'menu-007', name: t('demo.meat.horumon'), description: t('demo.meat.horumon.desc'), price: 1400, image_url: getFallbackImage('meat', 'ホルモン') },
                { id: 'menu-008', name: t('demo.meat.tokusen_mori'), description: t('demo.meat.tokusen_mori.desc'), price: 4500, image_url: getFallbackImage('meat', '盛り合わせ'), is_popular: true },
                { id: 'menu-009', name: t('demo.meat.buta_kalbi'), description: t('demo.meat.buta_kalbi.desc'), price: 900, image_url: getFallbackImage('meat', '豚') },
                { id: 'menu-010', name: t('demo.meat.tori_momo'), description: t('demo.meat.tori_momo.desc'), price: 800, image_url: getFallbackImage('meat', '鶏') },
            ]
        },
        {
            category: 'drinks',
            category_label: t('cat.drinks'),
            icon: '🍺',
            items: [
                { id: 'menu-011', name: t('demo.drinks.nama_beer'), description: t('demo.drinks.nama_beer.desc'), price: 600, image_url: getFallbackImage('drinks', 'ビール') },
                { id: 'menu-012', name: t('demo.drinks.bin_beer'), description: t('demo.drinks.bin_beer.desc'), price: 650, image_url: getFallbackImage('drinks', 'ビール') },
                { id: 'menu-013', name: t('demo.drinks.highball'), description: t('demo.drinks.highball.desc'), price: 500, image_url: getFallbackImage('drinks', 'ハイボール') },
                { id: 'menu-014', name: t('demo.drinks.lemon_sour'), description: t('demo.drinks.lemon_sour.desc'), price: 500, image_url: getFallbackImage('drinks', 'サワー') },
                { id: 'menu-015', name: t('demo.drinks.umeshu'), description: t('demo.drinks.umeshu.desc'), price: 550, image_url: getFallbackImage('drinks', '梅酒') },
                { id: 'menu-016', name: t('demo.drinks.makgeolli'), description: t('demo.drinks.makgeolli.desc'), price: 600, image_url: getFallbackImage('drinks', 'マッコリ') },
                { id: 'menu-017', name: t('demo.drinks.shochu'), description: t('demo.drinks.shochu.desc'), price: 500, image_url: getFallbackImage('drinks', '焼酎') },
                { id: 'menu-018', name: t('demo.drinks.oolong'), description: t('demo.drinks.oolong.desc'), price: 300, image_url: getFallbackImage('drinks', 'ウーロン茶') },
                { id: 'menu-019', name: t('demo.drinks.cola'), description: t('demo.drinks.cola.desc'), price: 300, image_url: getFallbackImage('drinks', 'コーラ') },
                { id: 'menu-020', name: t('demo.drinks.oj'), description: t('demo.drinks.oj.desc'), price: 350, image_url: getFallbackImage('drinks', 'ジュース') },
            ]
        },
        {
            category: 'salad',
            category_label: t('cat.salad'),
            icon: '🥗',
            items: [
                { id: 'menu-021', name: t('demo.salad.choregi'), description: t('demo.salad.choregi.desc'), price: 600, image_url: getFallbackImage('salad', 'チョレギ'), is_spicy: true },
                { id: 'menu-022', name: t('demo.salad.caesar'), description: t('demo.salad.caesar.desc'), price: 700, image_url: getFallbackImage('salad', 'シーザー') },
                { id: 'menu-023', name: t('demo.salad.namul'), description: t('demo.salad.namul.desc'), price: 500, image_url: getFallbackImage('salad', 'ナムル') },
                { id: 'menu-024', name: t('demo.salad.kimchi'), description: t('demo.salad.kimchi.desc'), price: 550, image_url: getFallbackImage('salad', 'キムチ'), is_spicy: true },
            ]
        },
        {
            category: 'rice',
            category_label: t('cat.rice'),
            icon: '🍚',
            items: [
                { id: 'menu-025', name: t('demo.rice.rice'), description: t('demo.rice.rice.desc'), price: 200, image_url: getFallbackImage('rice', 'ライス') },
                { id: 'menu-026', name: t('demo.rice.rice_large'), description: t('demo.rice.rice_large.desc'), price: 300, image_url: getFallbackImage('rice', 'ライス') },
                { id: 'menu-027', name: t('demo.rice.bibimbap'), description: t('demo.rice.bibimbap.desc'), price: 1200, image_url: getFallbackImage('rice', 'ビビンバ'), is_popular: true, is_spicy: true },
                { id: 'menu-028', name: t('demo.rice.naengmyeon'), description: t('demo.rice.naengmyeon.desc'), price: 900, image_url: getFallbackImage('rice', '冷麺') },
                { id: 'menu-029', name: t('demo.rice.kuppa'), description: t('demo.rice.kuppa.desc'), price: 950, image_url: getFallbackImage('rice', 'クッパ'), is_spicy: true },
            ]
        },
        {
            category: 'side',
            category_label: t('cat.side'),
            icon: '🍲',
            items: [
                { id: 'menu-030', name: t('demo.side.wakame'), description: t('demo.side.wakame.desc'), price: 350, image_url: getFallbackImage('side', 'スープ') },
                { id: 'menu-031', name: t('demo.side.oxtail'), description: t('demo.side.oxtail.desc'), price: 800, image_url: getFallbackImage('side', 'スープ') },
                { id: 'menu-032', name: t('demo.side.edamame'), description: t('demo.side.edamame.desc'), price: 350, image_url: getFallbackImage('side', '枝豆') },
                { id: 'menu-033', name: t('demo.side.nori'), description: t('demo.side.nori.desc'), price: 300, image_url: getFallbackImage('side', '海苔') },
                { id: 'menu-034', name: t('demo.side.jeon'), description: t('demo.side.jeon.desc'), price: 850, image_url: getFallbackImage('side', 'チヂミ') },
            ]
        },
        {
            category: 'dessert',
            category_label: t('cat.dessert'),
            icon: '🍨',
            items: [
                { id: 'menu-035', name: t('demo.dessert.vanilla'), description: t('demo.dessert.vanilla.desc'), price: 400, image_url: getFallbackImage('dessert', 'アイス') },
                { id: 'menu-036', name: t('demo.dessert.annin'), description: t('demo.dessert.annin.desc'), price: 450, image_url: getFallbackImage('dessert', '杏仁豆腐') },
                { id: 'menu-037', name: t('demo.dessert.sorbet'), description: t('demo.dessert.sorbet.desc'), price: 400, image_url: getFallbackImage('dessert', 'シャーベット') },
            ]
        },
        {
            category: 'set',
            category_label: t('cat.set'),
            icon: '🍱',
            items: [
                { id: 'menu-038', name: t('demo.set.yakiniku_set'), description: t('demo.set.yakiniku_set.desc'), price: 1800, image_url: getFallbackImage('set', '定食'), is_popular: true },
                { id: 'menu-039', name: t('demo.set.jo_yakiniku_set'), description: t('demo.set.jo_yakiniku_set.desc'), price: 2500, image_url: getFallbackImage('set', '定食') },
                { id: 'menu-040', name: t('demo.set.joshikai'), description: t('demo.set.joshikai.desc'), price: 3500, image_url: getFallbackImage('set', 'コース') },
            ]
        }
    ];

    console.log('Loaded offline menu with', state.categories.reduce((sum, cat) => sum + cat.items.length, 0), 'items');
    renderCategories();
    selectCategory('meat');
}

async function submitOrder() {
    if (state.cart.length === 0) return;

    const btnOrder = document.getElementById('btnOrder');
    btnOrder.disabled = true;
    btnOrder.innerHTML = `<span class="loading-spinner"></span> ${t('order.submitting')}`;

    try {
        const orderData = {
            table_id: TABLE_ID,
            session_id: state.sessionId,
            branch_code: CONFIG.BRANCH_CODE,
            items: state.cart.map(item => ({
                menu_item_id: item.id,
                quantity: item.quantity,
                notes: item.notes || null,
                // Include item details for demo mode
                item_name: item.name,
                item_price: item.price
            }))
        };

        const response = await fetch(`${CONFIG.API_URL}/tableorder/`, {
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
        showNotification(t('notify.orderSuccess'), 'success');

        // Add to order history
        state.orderHistory.push(result);

    } catch (error) {
        console.error('Order error:', error);
        showNotification(t('notify.orderFailed'), 'error');
    } finally {
        btnOrder.disabled = false;
        btnOrder.textContent = t('cart.submit');
    }
}

async function callStaff(callType) {
    try {
        const response = await fetch(`${CONFIG.API_URL}/tableorder/call-staff?branch_code=${CONFIG.BRANCH_CODE}`, {
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
            'assistance': t('call.assistance'),
            'water': t('call.water'),
            'bill': t('call.bill')
        };

        showNotification(callLabels[callType] || t('call.assistance'), 'success');

    } catch (error) {
        console.error('Call staff error:', error);
        showNotification(t('call.assistance'), 'success'); // Show success anyway for demo
    }
}

// ============ WebSocket ============

function setupWebSocket() {
    // Skip if already exceeded max retries
    if (state.wsRetryCount >= state.maxWsRetries) {
        console.log('WebSocket: Max retries exceeded, using offline mode');
        updateLoadingStatus('ws', 'error');
        state.wsConnected = false;
        return;
    }

    updateLoadingStatus('ws', 'pending');

    try {
        const ws = new WebSocket(`${CONFIG.WS_URL}?branch_code=${CONFIG.BRANCH_CODE}&table_id=${TABLE_ID}`);

        ws.onopen = () => {
            console.log('WebSocket connected');
            state.wsRetryCount = 0; // Reset retry count on successful connection
            state.wsConnected = true;
            updateConnectionStatus(true);
            updateLoadingStatus('ws', 'success');
            showConnectionBar(true);
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
            state.wsConnected = false;
            updateConnectionStatus(false);

            if (state.wsRetryCount < state.maxWsRetries) {
                console.log(`WebSocket disconnected, retry ${state.wsRetryCount}/${state.maxWsRetries}...`);
                setTimeout(setupWebSocket, 3000);
            } else {
                console.log('WebSocket: Switching to offline mode');
                updateLoadingStatus('ws', 'error');
                showOfflineNotice();
                showConnectionBar(false);
            }
        };

    } catch (error) {
        console.error('WebSocket setup error:', error);
        state.wsRetryCount++;
        updateLoadingStatus('ws', 'error');
        if (state.wsRetryCount >= state.maxWsRetries) {
            showOfflineNotice();
            showConnectionBar(false);
        }
    }
}

function updateConnectionStatus(isOnline) {
    state.isOnline = isOnline;
    const statusEl = document.getElementById('connectionStatus');
    if (statusEl) {
        if (isOnline) {
            statusEl.innerHTML = `<span class="status-dot online"></span> ${t('connection.statusOnline')}`;
            statusEl.className = 'connection-status online';
        } else {
            statusEl.innerHTML = `<span class="status-dot offline"></span> ${t('connection.statusOffline')}`;
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
        <span>${t('connection.offlineNotice')}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    document.body.appendChild(notice);
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'order_status_changed':
            if (data.new_status === 'ready') {
                showNotification(t('notify.orderReady', { number: data.order_number }), 'success');
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
        <div class="category-tab ${cat.category === state.currentCategory ? 'active' : ''}"
             onclick="selectCategory('${cat.category}')">
            <span class="cat-icon">${cat.icon}</span>
            <span class="cat-label">${cat.category_label}</span>
        </div>
    `).join('');
}

function selectCategory(category) {
    state.currentCategory = category;
    state.currentPage = 1; // Reset to first page

    // Update active state
    document.querySelectorAll('.category-tab').forEach(el => {
        const label = el.querySelector('.cat-label');
        const cat = state.categories.find(c => c.category === category);
        el.classList.toggle('active', label && cat && label.textContent === cat.category_label);
    });

    // Render menu items with pagination
    const cat = state.categories.find(c => c.category === category);
    if (cat) {
        renderMenuItems(cat.items);
    }
}

function renderMenuItems(items) {
    const container = document.getElementById('menuGrid');

    if (!items || items.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted);">${t('menu.noItems')}</p>`;
        updatePagination(0, 0);
        return;
    }

    // Sort: popular items first
    const sortedItems = [...items].sort((a, b) => {
        if (a.is_popular && !b.is_popular) return -1;
        if (!a.is_popular && b.is_popular) return 1;
        return 0;
    });

    // Pagination
    const totalItems = sortedItems.length;
    const totalPages = Math.ceil(totalItems / state.itemsPerPage);
    const startIndex = (state.currentPage - 1) * state.itemsPerPage;
    const endIndex = startIndex + state.itemsPerPage;
    const pageItems = sortedItems.slice(startIndex, endIndex);

    container.innerHTML = pageItems.map(item => {
        const inCart = state.cart.find(c => c.id === item.id);
        const cartQty = inCart ? inCart.quantity : 0;

        return `
            <div class="menu-card ${inCart ? 'in-cart' : ''}" data-item-id="${item.id}">
                ${cartQty > 0 ? `<div class="menu-card-cart-indicator">${cartQty}</div>` : ''}
                <div class="menu-card-image-wrap" onclick="openItemModal('${item.id}')">
                    <img class="menu-card-image" src="${item.image_url || ''}" alt="${item.name}" loading="lazy"
                         onerror="this.src='https://via.placeholder.com/400x200?text=No+Image'">
                    ${item.is_popular ? `<span class="popular-badge">${t('menu.popular')}</span>` : ''}
                    ${item.is_spicy ? '<span class="spicy-badge">🌶️</span>' : ''}
                </div>
                <div class="menu-card-content">
                    <h3 class="menu-card-name" onclick="openItemModal('${item.id}')">${item.name}</h3>
                    <div class="menu-card-footer">
                        <span class="menu-card-price">¥${item.price.toLocaleString()}</span>
                        <button class="quick-add-btn" onclick="quickAddToCart('${item.id}')" aria-label="${t('menu.add')}">
                            ${cartQty > 0 ? `<span class="quick-add-qty">${cartQty}</span>` : '＋'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    updatePagination(state.currentPage, totalPages);
}

// Pagination functions
function updatePagination(currentPage, totalPages) {
    const pagination = document.getElementById('pagination');
    const pageInfo = document.getElementById('pageInfo');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');

    // Always show pagination (never hide)
    pagination.style.display = 'flex';
    pageInfo.textContent = totalPages > 0 ? `${currentPage} / ${totalPages}` : '1 / 1';
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages || totalPages <= 1;
}

function changePage(delta) {
    const cat = state.categories.find(c => c.category === state.currentCategory);
    if (!cat) return;

    const totalPages = Math.ceil(cat.items.length / state.itemsPerPage);
    const newPage = state.currentPage + delta;

    if (newPage >= 1 && newPage <= totalPages) {
        state.currentPage = newPage;
        renderMenuItems(cat.items);
    }
}

// Quick add - add 1 item without opening modal
function quickAddToCart(itemId) {
    event.stopPropagation();

    let item = null;
    for (const cat of state.categories) {
        item = cat.items.find(i => i.id === itemId);
        if (item) break;
    }
    if (!item) return;

    addToCart(item, 1, '');

    // Visual feedback - animate the card
    const card = document.querySelector(`[data-item-id="${itemId}"]`);
    if (card) {
        card.classList.add('item-added');
        setTimeout(() => card.classList.remove('item-added'), 400);
    }

    showNotification(t('notify.quickAdd', { name: item.name }), 'success');
}

function renderCartItems() {
    const container = document.getElementById('cartItems');

    if (state.cart.length === 0) {
        container.innerHTML = `<div class="cart-empty">${t('cart.empty')}</div>`;
        document.getElementById('btnOrder').disabled = true;
        return;
    }

    container.innerHTML = state.cart.map((item, index) => `
        <div class="cart-item">
            <img class="cart-item-image" src="${item.image_url || ''}" alt="${item.name}"
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
    const totalPrice = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    // Header badge
    const badge = document.getElementById('cartBadge');
    badge.textContent = totalItems;
    badge.classList.toggle('hidden', totalItems === 0);

    // Floating cart bar
    const floatingBar = document.getElementById('floatingCartBar');
    const floatingCount = document.getElementById('floatingCartCount');
    const floatingTotal = document.getElementById('floatingCartTotal');

    if (floatingBar) {
        floatingBar.classList.toggle('visible', totalItems > 0);
        if (floatingCount) floatingCount.textContent = t('cart.itemCount', { count: totalItems });
        if (floatingTotal) floatingTotal.textContent = `¥${totalPrice.toLocaleString()}`;
    }
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

    document.getElementById('modalImage').src = item.image_url || '';
    document.getElementById('modalTitle').textContent = item.name;
    document.getElementById('modalDescription').textContent = item.description || '';
    document.getElementById('modalPrice').textContent = `¥${item.price.toLocaleString()}`;
    document.getElementById('modalQty').textContent = '1';
    document.getElementById('modalNotes').value = '';

    // Show options field only if item has options
    const modalOptions = document.getElementById('modalOptions');
    if (item.options || item.has_options) {
        modalOptions.style.display = 'block';
    } else {
        modalOptions.style.display = 'none';
    }

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
    const itemName = state.currentItem.name; // Save before closeItemModal nulls it
    addToCart(state.currentItem, state.modalQty, notes);

    closeItemModal();
    showNotification(t('notify.addedToCart', { name: itemName }), 'success');
}

// ============ Notifications ============

function showNotification(message, type = 'success', duration = 1500) {
    const toast = document.getElementById('notificationToast');
    const icon = document.getElementById('notificationIcon');
    const msg = document.getElementById('notificationMessage');

    icon.textContent = type === 'success' ? '✓' : '✕';
    msg.textContent = message;

    toast.className = 'notification-toast ' + type;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
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
