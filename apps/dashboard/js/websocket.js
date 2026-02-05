/**
 * WebSocket Manager for Dashboard
 * Handles real-time communication with backend
 */
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.subscriptions = new Set();
        this.handlers = new Map();
        this.branchCode = CONFIG.DEFAULT_BRANCH;
    }

    /**
     * Connect to WebSocket server
     */
    connect(branchCode = null) {
        if (branchCode) {
            this.branchCode = branchCode;
        }

        const url = `${CONFIG.WS_URL}/dashboard?branch=${this.branchCode}`;

        this.updateStatus('connecting');
        console.log(`[WS] Connecting to ${url}...`);

        try {
            this.ws = new WebSocket(url);
            this.setupEventHandlers();
        } catch (error) {
            console.error('[WS] Connection error:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Setup WebSocket event handlers
     */
    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('[WS] Connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateStatus('connected');

            // Re-subscribe to all channels
            this.subscriptions.forEach(channel => {
                this.send({ type: 'subscribe', channel });
            });

            // Notify handlers
            this.emit('connected');
        };

        this.ws.onclose = (event) => {
            console.log(`[WS] Disconnected: ${event.code} ${event.reason}`);
            this.isConnected = false;
            this.updateStatus('disconnected');
            this.emit('disconnected');
            this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('[WS] Error:', error);
            this.emit('error', error);
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('[WS] Failed to parse message:', error);
            }
        };
    }

    /**
     * Handle incoming message
     */
    handleMessage(message) {
        const { type, data, channel } = message;

        console.log(`[WS] Received: ${type}`, data);

        // Emit to specific handlers
        this.emit(type, data);

        // Emit to channel handlers
        if (channel) {
            this.emit(`${channel}:${type}`, data);
        }
    }

    /**
     * Send message to server
     */
    send(message) {
        if (!this.isConnected) {
            console.warn('[WS] Not connected, message queued');
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
     * Subscribe to a channel
     */
    subscribe(channel) {
        this.subscriptions.add(channel);
        if (this.isConnected) {
            this.send({ type: 'subscribe', channel });
        }
    }

    /**
     * Unsubscribe from a channel
     */
    unsubscribe(channel) {
        this.subscriptions.delete(channel);
        if (this.isConnected) {
            this.send({ type: 'unsubscribe', channel });
        }
    }

    /**
     * Register event handler
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
     * Emit event to handlers
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
     * Schedule reconnection
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= CONFIG.WS_MAX_RECONNECT_ATTEMPTS) {
            console.error('[WS] Max reconnect attempts reached');
            this.updateStatus('failed');
            return;
        }

        this.reconnectAttempts++;
        const delay = CONFIG.WS_RECONNECT_INTERVAL * this.reconnectAttempts;

        console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }

    /**
     * Update connection status UI
     */
    updateStatus(status) {
        const statusEl = document.getElementById('connectionStatus');
        if (!statusEl) return;

        statusEl.className = `connection-status ${status}`;

        const textEl = statusEl.querySelector('.status-text');
        if (textEl) {
            const texts = {
                connecting: 'æŽ¥ç¶šä¸­...',
                connected: 'æŽ¥ç¶šæ¸ˆã¿',
                disconnected: 'åˆ‡æ–­',
                failed: 'æŽ¥ç¶šå¤±æ•—'
            };
            textEl.textContent = texts[status] || status;
        }
    }

    /**
     * Change branch
     */
    changeBranch(branchCode) {
        if (branchCode === this.branchCode) return;

        this.branchCode = branchCode;

        // Reconnect with new branch
        if (this.ws) {
            this.ws.close();
        }
        this.connect();
    }

    /**
     * Disconnect
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
    }
}

// Create singleton instance
const ws = new WebSocketManager();



