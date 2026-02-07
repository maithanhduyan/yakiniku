/**
 * Japanese translations - 日本語
 * Kitchen Display System
 * File: i18n/ja.js
 */

const ja = {
    // Header
    'header.kitchen': '🍳 キッチン',
    'header.connecting': '接続中',
    'header.total': '合計',
    'header.warning': '3分超',
    'header.urgent': '5分超',

    // Connection
    'connection.online': 'オンライン',
    'connection.offline': 'オフライン',

    // Stations
    'station.all': 'すべて',
    'station.meat': '肉',
    'station.side': '他',
    'station.drink': '飲物',

    // Main content
    'empty.title': '注文を待っています',
    'empty.subtitle': '新しい注文が入ると表示されます',

    // Item row
    'item.minute': '分',
    'item.cancel': 'キャンセル',
    'item.done': '完了',

    // Footer
    'footer.warning': '警告',
    'footer.urgent': '緊急',
    'footer.minute': '分',

    // Confirm modal (serve)
    'modal.serve.title': '提供確認',
    'modal.serve.qty': '数量',
    'modal.serve.table': 'テーブル',
    'modal.serve.wait': '待ち',
    'modal.serve.message': 'この料理を提供済みにしますか？',
    'modal.serve.cancel': 'キャンセル',
    'modal.serve.confirm': '提供済み',

    // Cancel modal
    'modal.cancel.title': 'キャンセル確認',
    'modal.cancel.qty': '数量',
    'modal.cancel.table': 'テーブル',
    'modal.cancel.reasonLabel': '理由（任意）:',
    'modal.cancel.reasonPlaceholder': '例: 品切れ、お客様都合',
    'modal.cancel.message': 'この料理をキャンセルしますか？',
    'modal.cancel.back': '戻る',
    'modal.cancel.confirm': 'キャンセルする',

    // History panel
    'history.title': '📜 調理履歴',
    'history.filterAll': 'すべて',
    'history.filterMeat': '🥩 肉',
    'history.filterSide': '🍚 他',
    'history.filterDrink': '🍺 飲物',
    'history.filterAllEvents': '全イベント',
    'history.filterServed': '✅ 提供済み',
    'history.filterCancelled': '❌ キャンセル',
    'history.empty': '履歴がありません',
    'history.loadError': '履歴を取得できませんでした',
    'history.served': '✅ 提供:',
    'history.cancelled': '❌ キャンセル:',
    'history.avgWait': '⏱ 平均待ち:',
    'history.reason': '理由',

    // Notifications
    'notify.newOrder': 'テーブル {table} から新規注文',
    'notify.cancelled': '{name} キャンセル済み',
    'notify.servedByOther': '他のデバイスで提供済み',
    'notify.cancelledByOther': '他のデバイスでキャンセル済み',

    // Language
    'lang.toggle': 'EN',
    'lang.toggleTitle': 'Switch to English',

    // Loading
    'loading.text': '注文データを読み込み中...',
    'loading.api': 'API接続',
    'loading.realtime': 'リアルタイム',

    // Demo mode
    'demo.banner': 'デモモード — サンプルデータを表示中',
};

// Register to global i18n object
if (typeof window.i18n === 'undefined') window.i18n = {};
window.i18n.ja = ja;
