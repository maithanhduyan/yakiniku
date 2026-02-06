/**
 * WebSocket Manager for Kitchen Display System
 * Handles real-time communication with backend.
 *
 * Connects to: /ws/kitchen?branch=hirama
 * Auto-subscribes to: "orders" channel
 *
 * Events emitted:
 *   - connected        : WebSocket open
 *   - disconnected     : WebSocket closed
 *   - new_order        : New order from customer  → { data }
 *   - order_update     : Order status changed     → { data }
 *   - item_update      : Item status changed      → { data }
 *   - config_update    : Kitchen config changed    → { data }
 */

class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.handlers = new Map();
        this.branchCode = CONFIG.BRANCH_CODE;
        this._reconnectTimer = null;
    }

    /**
     * Connect to WebSocket server
     */
    connect(branchCode = null) {
        if (branchCode) {
            this.branchCode = branchCode;
        }

        // Clean up any existing connection
        if (this.ws) {
            try { this.ws.close(); } catch (e) {}
            this.ws = null;
        }

        const url = `${CONFIG.WS_URL}/kitchen?branch=${this.branchCode}`;
        console.log(`[WS] Connecting to ${url}...`);

        try {
            this.ws = new WebSocket(url);
            this._setupHandlers();
        } catch (error) {
            console.error('[WS] Connection error:', error);
            this._scheduleReconnect();
        }
    }

    /**
     * Setup WebSocket event handlers
     */
    _setupHandlers() {
        this.ws.onopen = () => {
            console.log('[WS] Connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.emit('connected');
        };

        this.ws.onclose = (event) => {
            console.log(`[WS] Disconnected: ${event.code} ${event.reason || ''}`);
            this.isConnected = false;
            this.emit('disconnected');
            this._scheduleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('[WS] Error:', error);
            this.isConnected = false;
            this.emit('error', error);
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this._handleMessage(message);
            } catch (e) {
                console.error('[WS] Failed to parse message:', e);
            }
        };
    }

    /**
     * Handle incoming message and dispatch to handlers
     */
    _handleMessage(message) {
        const { type, data } = message;
        console.log(`[WS] Received: ${type}`, data);

        // Emit specific event type
        this.emit(type, data || message);
    }

    /**
     * Send message to server
     */
    send(message) {
        if (!this.isConnected || !this.ws) {
            console.warn('[WS] Not connected');
            return false;
        }

        try {
            this.ws.send(JSON.stringify(message));
            return true;
        } catch (error) {
            console.error('[WS] Send error:', error);
            return false;
        }
    }

    /**
     * Send ping to keep connection alive
     */
    ping() {
        return this.send({ type: 'ping' });
    }

    /**
     * Register event handler
     * @param {string} event - Event name
     * @param {Function} handler - Callback
     * @returns {Function} Unsubscribe function
     */
    on(event, handler) {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, new Set());
        }
        this.handlers.get(event).add(handler);

        // Return unsubscribe function
        return () => {
            this.handlers.get(event)?.delete(handler);
        };
    }

    /**
     * Remove event handler
     */
    off(event, handler) {
        this.handlers.get(event)?.delete(handler);
    }

    /**
     * Emit event to registered handlers
     */
    emit(event, data) {
        this.handlers.get(event)?.forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`[WS] Handler error for ${event}:`, error);
            }
        });
    }

    /**
     * Schedule reconnection with exponential backoff
     */
    _scheduleReconnect() {
        if (this.reconnectAttempts >= CONFIG.WS_MAX_RECONNECT_ATTEMPTS) {
            console.error('[WS] Max reconnect attempts reached');
            this.emit('failed');
            return;
        }

        // Clear any existing timer
        if (this._reconnectTimer) {
            clearTimeout(this._reconnectTimer);
        }

        this.reconnectAttempts++;
        const delay = Math.min(
            CONFIG.WS_RECONNECT_INTERVAL * this.reconnectAttempts,
            30000 // cap at 30s
        );

        console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${CONFIG.WS_MAX_RECONNECT_ATTEMPTS})`);

        this._reconnectTimer = setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }

    /**
     * Disconnect and stop reconnecting
     */
    disconnect() {
        if (this._reconnectTimer) {
            clearTimeout(this._reconnectTimer);
            this._reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.isConnected = false;
        this.reconnectAttempts = CONFIG.WS_MAX_RECONNECT_ATTEMPTS; // prevent auto-reconnect
    }
}

// Create singleton instance
const wsManager = new WebSocketManager();
