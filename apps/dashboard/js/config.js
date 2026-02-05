/**
 * Dashboard Configuration
 * Yakiniku.io Platform
 */
const CONFIG = {
    // API endpoints
    API_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000/ws',

    // Default branch
    DEFAULT_BRANCH: 'hirama',

    // Reconnect settings
    WS_RECONNECT_INTERVAL: 3000,
    WS_MAX_RECONNECT_ATTEMPTS: 10,

    // Toast duration
    TOAST_DURATION: 5000,

    // Pagination
    DEFAULT_PAGE_SIZE: 20,

    // Status labels
    STATUS_LABELS: {
        confirmed: 'ç¢ºå®š',
        pending: 'ä¿ç•™ä¸­',
        cancelled: 'ã‚­ãƒ£ãƒ³ã‚»ãƒ«',
        completed: 'å®Œäº†',
        available: 'ç©ºå¸­',
        occupied: 'ä½¿ç”¨ä¸­',
        reserved: 'äºˆç´„æ¸ˆ'
    },

    // Table types
    TABLE_TYPES: {
        counter: 'ã‚«ã‚¦ãƒ³ã‚¿ãƒ¼',
        table: 'ãƒ†ãƒ¼ãƒ–ãƒ«',
        private: 'å€‹å®¤',
        tatami: 'åº§æ•·'
    }
};

// Freeze config to prevent modifications
Object.freeze(CONFIG);
Object.freeze(CONFIG.STATUS_LABELS);
Object.freeze(CONFIG.TABLE_TYPES);
