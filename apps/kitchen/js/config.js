/**
 * Kitchen Display System - Configuration
 * Yakiniku.io Platform
 *
 * Auto-detects dev vs prod environment for API/WS endpoints.
 */

// Auto-detect: Dev (Live Server / http.server) → backend at :8000
// Prod (Traefik :80/443) → same origin, no port needed
const API_HOST = window.location.hostname;
const _port = window.location.port;
const _isDev = _port && !['80', '443', ''].includes(_port);
const _proto = window.location.protocol;
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

    // Polling interval (ms) — fallback when WebSocket is down
    REFRESH_INTERVAL: 30000,

    // Timer update interval (ms)
    TIMER_INTERVAL: 1000,

    // Time thresholds (seconds) — can be overridden by backend config
    THRESHOLDS: {
        WARNING: 180,   // 3 min → yellow
        URGENT: 300,    // 5 min → red
    },

    // WebSocket reconnect settings
    WS_RECONNECT_INTERVAL: 3000,
    WS_MAX_RECONNECT_ATTEMPTS: 20,

    // Notification display duration (ms)
    TOAST_DURATION: 4000,
};

// Freeze config to prevent accidental modifications
Object.freeze(CONFIG);
Object.freeze(CONFIG.THRESHOLDS);
