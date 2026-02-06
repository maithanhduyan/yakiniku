/**
 * Dashboard Configuration
 * Yakiniku.io Platform
 */
// Auto-detect: Dev (Live Server) → backend :8000 | Prod (Traefik) → same origin
const _host = window.location.hostname;
const _port = window.location.port;
const _isDev = _port && !['80', '443', ''].includes(_port);
const _proto = window.location.protocol;
const _wsProto = _proto === 'https:' ? 'wss:' : 'ws:';
const _apiBase = _isDev ? `${_proto}//${_host}:8000` : `${_proto}//${_host}`;

const CONFIG = {
    // API endpoints (auto-detected)
    API_URL: _apiBase,
    WS_URL: `${_isDev ? 'ws:' : _wsProto}//${_host}${_isDev ? ':8000' : ''}/ws`,

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
        confirmed: '確定',
        pending: '保留中',
        cancelled: 'キャンセル',
        completed: '完了',
        available: '空席',
        occupied: '使用中',
        reserved: '予約済'
    },

    // Table types
    TABLE_TYPES: {
        counter: 'カウンター',
        table: 'テーブル',
        private: '個室',
        tatami: '座敷'
    }
};

// Freeze config to prevent modifications
Object.freeze(CONFIG);
Object.freeze(CONFIG.STATUS_LABELS);
Object.freeze(CONFIG.TABLE_TYPES);
