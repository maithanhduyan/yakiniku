/**
 * API Client for Table Order App
 * REST API wrapper — all backend communication goes through here.
 *
 * ┌──────────────────────────────────────────────────────────────────────┐
 * │ Endpoint                   │ Method │ Purpose                       │
 * ├──────────────────────────────────────────────────────────────────────┤
 * │ /api/menu/items            │ GET    │ Fetch menu for branch         │
 * │ /api/tableorder/           │ POST   │ Submit new order              │
 * │ /api/tableorder/call-staff │ POST   │ 🔔 Call staff / 💳 Request bill│
 * │ /api/tableorder/events/sync│ POST   │ Batch-sync local events       │
 * │ /api/tableorder/session-log│ POST   │ Legacy session analytics      │
 * └──────────────────────────────────────────────────────────────────────┘
 */

class APIClient {
    constructor() {
        this.baseUrl = CONFIG.API_BASE;
        this.apiUrl = CONFIG.API_URL;
        this.branchCode = CONFIG.BRANCH_CODE;
    }

    // ============ Internal helpers ============

    /**
     * Generic fetch wrapper with JSON response.
     * @param {string} path    - relative to apiUrl (e.g. '/tableorder/')
     * @param {Object} options - fetch options override
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
     * Fire-and-forget POST (uses sendBeacon if available, falls back to fetch).
     * Returns void — caller must not depend on response.
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

    // ============ Menu ============

    /**
     * Fetch menu items grouped by category.
     * @returns {Promise<Object[]>} categories with items
     */
    async getMenu() {
        return this._fetch(`/menu/items?branch_code=${this.branchCode}`);
    }

    // ============ Orders ============

    /**
     * Submit a new order.
     * @param {Object} orderData - { table_id, session_id, items: [...] }
     * @returns {Promise<Object>} created order
     */
    async submitOrder(orderData) {
        return this._fetch(`/tableorder/?branch_code=${this.branchCode}`, {
            method: 'POST',
            body: JSON.stringify(orderData),
        });
    }

    // ============ Staff Calls ============

    /**
     * 🔔 Call staff for assistance.
     * @param {string} tableId
     * @param {string} sessionId
     * @returns {Promise<{success, message, call_type, correlation_id}>}
     */
    async callStaff(tableId, sessionId) {
        return this._fetch(`/tableorder/call-staff?branch_code=${this.branchCode}`, {
            method: 'POST',
            body: JSON.stringify({
                table_id: tableId,
                session_id: sessionId,
                call_type: 'assistance',
            }),
        });
    }

    /**
     * 💳 Request bill / payment.
     * @param {string} tableId
     * @param {string} sessionId
     * @returns {Promise<{success, message, call_type, correlation_id}>}
     */
    async requestBill(tableId, sessionId) {
        return this._fetch(`/tableorder/call-staff?branch_code=${this.branchCode}`, {
            method: 'POST',
            body: JSON.stringify({
                table_id: tableId,
                session_id: sessionId,
                call_type: 'bill',
            }),
        });
    }

    /**
     * Generic call-staff (water, assistance, bill).
     * Fire-and-forget variant for use in phase transitions.
     * @param {string} callType
     * @param {string} tableId
     * @param {string} sessionId
     */
    fireCallStaff(callType, tableId, sessionId) {
        this._beacon(`/tableorder/call-staff?branch_code=${this.branchCode}`, {
            table_id: tableId,
            session_id: sessionId,
            call_type: callType,
        });
    }

    // ============ Event Sync ============

    /**
     * Batch-sync local EventStore events to backend.
     * @param {EventEntry[]} events - array of un-synced events
     * @returns {Promise<{received: number, synced_ids: string[]}>}
     */
    async syncEvents(events) {
        if (!events.length) return { received: 0, synced_ids: [] };
        return this._fetch(`/tableorder/events/sync?branch_code=${this.branchCode}`, {
            method: 'POST',
            body: JSON.stringify({
                table_id: events[0].table_id,
                events: events.map(e => ({
                    id: e.id,
                    type: e.type,
                    source: e.source,
                    ts: e.ts,
                    session_id: e.session_id,
                    table_id: e.table_id,
                    data: e.data,
                })),
            }),
        });
    }

    /**
     * Fire-and-forget event sync (uses sendBeacon).
     * Best for page unload / visibilitychange.
     * @param {EventEntry[]} events
     */
    beaconSyncEvents(events) {
        if (!events.length) return;
        this._beacon(`/tableorder/events/sync?branch_code=${this.branchCode}`, {
            table_id: events[0].table_id,
            events: events.map(e => ({
                id: e.id,
                type: e.type,
                source: e.source,
                ts: e.ts,
                session_id: e.session_id,
                table_id: e.table_id,
                data: e.data,
            })),
        });
    }

    // ============ Session Log (legacy compat) ============

    /**
     * Send session log entries (legacy analytics).
     * @param {string} tableId
     * @param {string} sessionId
     * @param {Object[]} entries
     */
    beaconSessionLog(tableId, sessionId, entries) {
        this._beacon('/tableorder/session-log', {
            table_id: tableId,
            session_id: sessionId,
            entries,
        });
    }
}
