/**
 * Table Order App Configuration
 * Yakiniku.io Platform
 */

// Auto-detect API server based on current hostname
// This allows the app to work from both localhost and internal network
// Use the SAME hostname as the browser to avoid CORS issues
const API_HOST = window.location.hostname;

const CONFIG = {
    // API endpoints
    API_URL: `http://${API_HOST}:8000/api`,
    WS_URL: `ws://${API_HOST}:8000/ws`,

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
