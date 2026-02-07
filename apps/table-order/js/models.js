/**
 * Event Sourcing Models for Table Order App
 * Stores customer behavior events in localStorage with 1-month rotation.
 *
 * Architecture:
 *   localStorage key: `events_${TABLE_ID}`
 *   Value: JSON array of EventEntry objects, ordered by timestamp
 *   Rotation: on every append, entries older than 30 days are pruned
 *
 * Usage:
 *   const store = new EventStore('demo-table-1');
 *   store.append(EventType.MENU_VIEW, { category: 'meat' });
 *   store.append(EventType.CALL_STAFF, { call_type: 'assistance' });
 *   const pending = store.pending();       // un-synced events
 *   store.markSynced(pending.map(e=>e.id)); // after successful POST
 */

// ============ Event Type Enum ============
// Mirror backend EventType (domains/tableorder/events.py) + client-only types

const EventType = Object.freeze({
    // --- Session lifecycle ---
    SESSION_STARTED:   'session.started',
    SESSION_ENDED:     'session.ended',
    PHASE_TRANSITION:  'session.phase_transition',

    // --- Menu browsing ---
    MENU_VIEW:         'menu.view',          // opened a category
    ITEM_VIEW:         'item.view',          // opened item detail modal
    ITEM_ADDED:        'item.added',         // added item to cart
    ITEM_REMOVED:      'item.removed',       // removed item from cart

    // --- Cart / Order ---
    CART_OPENED:       'cart.opened',
    CART_CLEARED:      'cart.cleared',
    ORDER_SUBMITTED:   'order.submitted',    // POST /api/tableorder/

    // --- Staff interaction (synced to backend) ---
    CALL_STAFF:        'call.staff',         // 🔔 bell button
    CALL_WATER:        'call.water',
    CALL_BILL:         'call.bill',          // 💳 payment button
    CALL_ACKNOWLEDGED: 'call.acknowledged',  // backend confirmed

    // --- UI behaviour (client-only analytics) ---
    PAGE_SWIPE:        'ui.page_swipe',
    CATEGORY_SWITCH:   'ui.category_switch',
    LANG_TOGGLE:       'ui.lang_toggle',
    HISTORY_OPENED:    'ui.history_opened',

    // --- Connectivity ---
    WS_CONNECTED:      'ws.connected',
    WS_DISCONNECTED:   'ws.disconnected',
    OFFLINE_RECOVERY:  'offline.recovery',
});


// ============ Event Source Enum ============

const EventSource = Object.freeze({
    CUSTOMER: 'customer',   // user action
    SYSTEM:   'system',     // auto (timer, reconnect, etc.)
});


// ============ EventEntry ============
// A single immutable event record

/**
 * @typedef {Object} EventEntry
 * @property {string}  id           - UUID v4
 * @property {string}  type         - EventType value
 * @property {string}  source       - EventSource value
 * @property {number}  ts           - Unix epoch ms (Date.now())
 * @property {string}  session_id   - current session
 * @property {string}  table_id     - current table
 * @property {Object}  data         - arbitrary payload
 * @property {boolean} synced       - true after sent to backend
 */

function createEvent(type, tableId, sessionId, data = {}, source = EventSource.CUSTOMER) {
    // crypto.randomUUID() requires Secure Context (HTTPS or localhost).
    // Fallback to crypto.getRandomValues for HTTP + LAN IP access.
    const uuid = (typeof crypto.randomUUID === 'function')
        ? crypto.randomUUID()
        : ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
          );
    return {
        id: uuid,
        type,
        source,
        ts: Date.now(),
        session_id: sessionId || null,
        table_id: tableId,
        data,
        synced: false,
    };
}


// ============ EventStore ============

class EventStore {
    /** @param {string} tableId */
    constructor(tableId) {
        this.tableId = tableId;
        this._storageKey = `events_${tableId}`;
        this._maxAgeDays = 30; // 1-month rotation
    }

    // --- Core CRUD ---

    /**
     * Append a new event. Auto-prunes old entries.
     * @param {string} type      - EventType value
     * @param {Object} [data={}] - event payload
     * @param {string} [source]  - EventSource value
     * @returns {EventEntry} the created event
     */
    append(type, data = {}, source = EventSource.CUSTOMER) {
        const sessionId = typeof SESSION_ID !== 'undefined' ? SESSION_ID : null;
        const event = createEvent(type, this.tableId, sessionId, data, source);

        const events = this._load();
        events.push(event);
        this._save(this._prune(events));

        return event;
    }

    /**
     * Get all stored events, newest first.
     * @param {Object} [filter] - optional filters
     * @param {string} [filter.type]
     * @param {string} [filter.session_id]
     * @param {number} [filter.since] - epoch ms
     * @returns {EventEntry[]}
     */
    query(filter = {}) {
        let events = this._load();
        if (filter.type) events = events.filter(e => e.type === filter.type);
        if (filter.session_id) events = events.filter(e => e.session_id === filter.session_id);
        if (filter.since) events = events.filter(e => e.ts >= filter.since);
        return events.slice().reverse(); // newest first
    }

    /**
     * Get un-synced events (pending upload to backend).
     * @returns {EventEntry[]} oldest first (for sequential POST)
     */
    pending() {
        return this._load().filter(e => !e.synced);
    }

    /**
     * Mark events as synced after successful backend POST.
     * @param {string[]} ids - event IDs to mark
     */
    markSynced(ids) {
        const idSet = new Set(ids);
        const events = this._load();
        for (const e of events) {
            if (idSet.has(e.id)) e.synced = true;
        }
        this._save(events);
    }

    /**
     * Total event count.
     */
    get length() {
        return this._load().length;
    }

    /**
     * Clear all events for this table.
     */
    clear() {
        localStorage.removeItem(this._storageKey);
    }

    // --- Convenience appenders (typed shortcuts) ---

    /** Customer viewed a menu category */
    logMenuView(category) {
        return this.append(EventType.MENU_VIEW, { category });
    }

    /** Customer opened an item detail */
    logItemView(itemId, itemName) {
        return this.append(EventType.ITEM_VIEW, { item_id: itemId, item_name: itemName });
    }

    /** Customer added item to cart */
    logItemAdded(itemId, itemName, qty, price) {
        return this.append(EventType.ITEM_ADDED, {
            item_id: itemId, item_name: itemName, quantity: qty, price
        });
    }

    /** Customer removed item from cart */
    logItemRemoved(itemId, itemName) {
        return this.append(EventType.ITEM_REMOVED, { item_id: itemId, item_name: itemName });
    }

    /** Customer pressed 🔔 call staff */
    logCallStaff(callType = 'assistance') {
        return this.append(EventType.CALL_STAFF, { call_type: callType });
    }

    /** Customer pressed 💳 request bill */
    logCallBill() {
        return this.append(EventType.CALL_BILL, { call_type: 'bill' });
    }

    /** Order submitted to backend */
    logOrderSubmitted(orderId, items, total) {
        return this.append(EventType.ORDER_SUBMITTED, {
            order_id: orderId,
            item_count: items.length,
            total_quantity: items.reduce((s, i) => s + (i.quantity || 1), 0),
            total_amount: total,
        });
    }

    /** Session phase changed */
    logPhaseTransition(from, to) {
        return this.append(EventType.PHASE_TRANSITION, { from, to }, EventSource.SYSTEM);
    }

    /** Swipe navigation */
    logSwipe(direction, fromCategory, toCategory) {
        return this.append(EventType.PAGE_SWIPE, {
            direction, from_category: fromCategory, to_category: toCategory
        });
    }

    // --- Internal helpers ---

    /** @returns {EventEntry[]} */
    _load() {
        try {
            return JSON.parse(localStorage.getItem(this._storageKey) || '[]');
        } catch {
            return [];
        }
    }

    /** @param {EventEntry[]} events */
    _save(events) {
        try {
            localStorage.setItem(this._storageKey, JSON.stringify(events));
        } catch (e) {
            // localStorage full — prune aggressively then retry once
            console.warn('[EventStore] Storage full, aggressive prune');
            const pruned = this._prune(events, 7); // keep only 7 days
            try {
                localStorage.setItem(this._storageKey, JSON.stringify(pruned));
            } catch {
                // Last resort: keep only un-synced events
                const unsyncedOnly = pruned.filter(ev => !ev.synced);
                localStorage.setItem(this._storageKey, JSON.stringify(unsyncedOnly));
            }
        }
    }

    /**
     * Remove events older than maxDays.
     * @param {EventEntry[]} events
     * @param {number} [maxDays]
     * @returns {EventEntry[]}
     */
    _prune(events, maxDays) {
        const cutoff = Date.now() - (maxDays || this._maxAgeDays) * 24 * 60 * 60 * 1000;
        return events.filter(e => e.ts >= cutoff);
    }
}
