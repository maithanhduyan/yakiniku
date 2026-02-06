/**
 * API Client for Kitchen Display System
 * REST API wrapper — all backend communication goes through here.
 *
 * ┌──────────────────────────────────────────────────────────────────────┐
 * │ Endpoint                          │ Method │ Purpose                │
 * ├──────────────────────────────────────────────────────────────────────┤
 * │ /api/kitchen/orders               │ GET    │ Fetch active orders    │
 * │ /api/kitchen/orders/{id}/start    │ PATCH  │ Mark "preparing"       │
 * │ /api/kitchen/orders/{id}/ready    │ PATCH  │ Mark "ready"           │
 * │ /api/kitchen/orders/{id}/served   │ PATCH  │ Mark "served"          │
 * │ /api/kitchen/items/{id}/done      │ PATCH  │ Mark item done         │
 * │ /api/kitchen/events/              │ POST   │ Log kitchen event      │
 * │ /api/kitchen/events/history       │ GET    │ Query event history    │
 * └──────────────────────────────────────────────────────────────────────┘
 */

class KitchenAPI {
    constructor() {
        this.apiUrl = CONFIG.API_URL;
        this.branchCode = CONFIG.BRANCH_CODE;
    }

    // ============ Internal Helpers ============

    /**
     * Generic fetch wrapper with JSON response.
     * @param {string} path - relative to apiUrl
     * @param {Object} options - fetch options
     * @returns {Promise<Object>}
     */
    async _fetch(path, options = {}) {
        const url = `${this.apiUrl}${path}`;
        const defaults = {
            headers: { 'Content-Type': 'application/json' },
        };
        const res = await fetch(url, { ...defaults, ...options });
        if (!res.ok) {
            const body = await res.text().catch(() => '');
            throw new Error(`API ${res.status}: ${body}`);
        }
        return res.json();
    }

    /**
     * Fire-and-forget POST via sendBeacon (for page unload).
     */
    _beacon(path, data) {
        const url = `${this.apiUrl}${path}`;
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        if (navigator.sendBeacon) {
            navigator.sendBeacon(url, blob);
        } else {
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                keepalive: true,
            }).catch(() => {});
        }
    }

    // ============ Orders ============

    /**
     * Fetch active orders for kitchen display.
     * Uses the domain endpoint which returns richer data
     * (wait_time_seconds, urgency, summary).
     * @param {string} [status] - Optional filter: pending, preparing, ready
     * @returns {Promise<{orders: Array, total: number, summary: Object}>}
     */
    async getOrders(status = null) {
        let path = `/kitchen/orders?branch_code=${this.branchCode}`;
        if (status) path += `&status=${status}`;
        return this._fetch(path);
    }

    /**
     * Mark order as "preparing"
     * @param {string} orderId
     */
    async startOrder(orderId) {
        return this._fetch(`/kitchen/orders/${orderId}/start`, { method: 'PATCH' });
    }

    /**
     * Mark order as "ready" for serving
     * @param {string} orderId
     */
    async markReady(orderId) {
        return this._fetch(`/kitchen/orders/${orderId}/ready`, { method: 'PATCH' });
    }

    /**
     * Mark order as "served"
     * @param {string} orderId
     */
    async markServed(orderId) {
        return this._fetch(`/kitchen/orders/${orderId}/served`, { method: 'PATCH' });
    }

    /**
     * Mark individual item as done/prepared
     * @param {string} itemId - The OrderItem UUID
     */
    async completeItem(itemId) {
        return this._fetch(`/kitchen/items/${itemId}/done`, { method: 'PATCH' });
    }

    // ============ Event Sourcing ============

    /**
     * Log a kitchen event (serve, cancel, etc.)
     * @param {Object} eventData
     */
    async logEvent(eventData) {
        return this._fetch(`/kitchen/events/`, {
            method: 'POST',
            body: JSON.stringify(eventData),
        });
    }

    /**
     * Fire-and-forget event log (for non-critical logging)
     * @param {Object} eventData
     */
    beaconLogEvent(eventData) {
        this._beacon(`/kitchen/events/`, eventData);
    }

    /**
     * Get kitchen event history
     * @param {Object} filters - { station, event_type, limit, offset, since_hours }
     * @returns {Promise<{events: Array, summary: Object}>}
     */
    async getHistory(filters = {}) {
        let path = `/kitchen/events/history?branch_code=${this.branchCode}`;
        if (filters.station && filters.station !== 'all') path += `&station=${filters.station}`;
        if (filters.event_type) path += `&event_type=${filters.event_type}`;
        if (filters.limit) path += `&limit=${filters.limit}`;
        if (filters.offset) path += `&offset=${filters.offset}`;
        if (filters.since_hours) path += `&since_hours=${filters.since_hours}`;
        return this._fetch(path);
    }
}

// Create singleton instance
const API = new KitchenAPI();
