/**
 * Table Order App Configuration
 * Yakiniku.io Platform
 */

// Auto-detect API server based on current hostname & port
// Dev (Live Server :5500) → backend at :8000
// Prod (Traefik :80/443) → same origin, no port needed
const API_HOST = window.location.hostname;
const _port = window.location.port;
const _isDev = _port && !['80', '443', ''].includes(_port);
const _proto = window.location.protocol;  // 'http:' or 'https:'
const _wsProto = _proto === 'https:' ? 'wss:' : 'ws:';
const API_BASE = _isDev
    ? `http://${API_HOST}:8000`           // Dev: backend always HTTP on :8000
    : `${_proto}//${API_HOST}`;

const CONFIG = {
    // API endpoints (auto-detected)
    API_BASE: API_BASE,
    API_URL: `${API_BASE}/api`,
    WS_URL: `${_isDev ? 'ws:' : _wsProto}//${API_HOST}${_isDev ? ':8000' : ''}/ws`,

    // Default branch
    BRANCH_CODE: 'hirama',

    // Reconnect settings
    WS_RECONNECT_INTERVAL: 3000,
    WS_MAX_RECONNECT_ATTEMPTS: 10,

    // Toast duration
    TOAST_DURATION: 5000,

    // Pagination
    DEFAULT_PAGE_SIZE: 20,

    // Status labels
    STATUS_LABELS: {
        confirmed: '確定',
        pending: '保留中',
        cancelled: 'キャンセル',
        completed: '完了',
        available: '空席',
        occupied: '使用中',
        reserved: '予約済',
    },

    // Table types
    TABLE_TYPES: {
        counter: 'カウンター',
        table: 'テーブル',
        private: '個室',
        tatami: '座敷',
    },

    // Session phases (4-phase lifecycle)
    SESSION_PHASES: {
        WELCOME: 'welcome',
        ORDERING: 'ordering',
        BILL_REVIEW: 'bill_review',
        CLEANING: 'cleaning',
    },

    // Valid phase transitions
    SESSION_TRANSITIONS: {
        welcome: ['ordering'],
        ordering: ['bill_review'],
        bill_review: ['ordering', 'cleaning'],
        cleaning: ['welcome'],
    },

    // Inactivity timeout (ms) - 30 minutes
    INACTIVITY_TIMEOUT: 30 * 60 * 1000,

    // Long-press duration (ms) - 3 seconds
    LONG_PRESS_DURATION: 3000,
};

// Freeze config to prevent modifications
Object.freeze(CONFIG);
Object.freeze(CONFIG.STATUS_LABELS);
Object.freeze(CONFIG.TABLE_TYPES);
Object.freeze(CONFIG.SESSION_PHASES);
Object.freeze(CONFIG.SESSION_TRANSITIONS);
