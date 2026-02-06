/**
 * English translations
 * Kitchen Display System
 * File: i18n/en.js
 */

const en = {
    // Header
    'header.kitchen': '🍳 Kitchen',
    'header.connecting': 'Connecting',
    'header.total': 'Total',
    'header.warning': '>3min',
    'header.urgent': '>5min',

    // Connection
    'connection.online': 'Online',
    'connection.offline': 'Offline',

    // Stations
    'station.all': 'All',
    'station.meat': 'Meat',
    'station.side': 'Sides',
    'station.drink': 'Drinks',

    // Main content
    'empty.title': 'Waiting for orders',
    'empty.subtitle': 'New orders will appear here',

    // Item row
    'item.minute': 'min',
    'item.cancel': 'Cancel',
    'item.done': 'Done',

    // Footer
    'footer.warning': 'Warning',
    'footer.urgent': 'Urgent',
    'footer.minute': 'min',

    // Confirm modal (serve)
    'modal.serve.title': 'Serve Confirmation',
    'modal.serve.qty': 'Qty',
    'modal.serve.table': 'Table',
    'modal.serve.wait': 'Wait',
    'modal.serve.message': 'Mark this item as served?',
    'modal.serve.cancel': 'Cancel',
    'modal.serve.confirm': 'Served',

    // Cancel modal
    'modal.cancel.title': 'Cancel Confirmation',
    'modal.cancel.qty': 'Qty',
    'modal.cancel.table': 'Table',
    'modal.cancel.reasonLabel': 'Reason (optional):',
    'modal.cancel.reasonPlaceholder': 'e.g. Out of stock, customer request',
    'modal.cancel.message': 'Cancel this item?',
    'modal.cancel.back': 'Back',
    'modal.cancel.confirm': 'Cancel Item',

    // History panel
    'history.title': '📜 Kitchen History',
    'history.filterAll': 'All',
    'history.filterMeat': '🥩 Meat',
    'history.filterSide': '🍚 Sides',
    'history.filterDrink': '🍺 Drinks',
    'history.filterAllEvents': 'All Events',
    'history.filterServed': '✅ Served',
    'history.filterCancelled': '❌ Cancelled',
    'history.empty': 'No history yet',
    'history.loadError': 'Failed to load history',
    'history.served': '✅ Served:',
    'history.cancelled': '❌ Cancelled:',
    'history.avgWait': '⏱ Avg Wait:',
    'history.reason': 'Reason',

    // Notifications
    'notify.newOrder': 'New order from table {table}',
    'notify.cancelled': '{name} cancelled',

    // Language
    'lang.toggle': 'JP',
    'lang.toggleTitle': '日本語に切替',

    // Loading
    'loading.text': 'Loading order data...',
    'loading.api': 'API Connection',
    'loading.realtime': 'Realtime',

    // Demo mode
    'demo.banner': 'Demo Mode — Showing sample data',
};

// Register to global i18n object
if (typeof window.i18n === 'undefined') window.i18n = {};
window.i18n.en = en;
