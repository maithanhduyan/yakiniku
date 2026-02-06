/**
 * Japanese translations - 日本語
 * File: i18n/ja.js
 */

const ja = {
    // Header
    'header.call': '呼出',
    'header.bill': '会計',

    // Guest info
    'guest.suffix': '名様',

    // Category labels (fallback when API doesn't provide)
    'cat.meat': '肉類',
    'cat.drinks': '飲物',
    'cat.salad': 'サラダ',
    'cat.rice': 'ご飯・麺',
    'cat.side': 'サイドメニュー',
    'cat.dessert': 'デザート',
    'cat.set': 'セットメニュー',

    // Menu
    'menu.popular': '🔥 人気',
    'menu.noItems': 'メニューがありません',
    'menu.add': '追加',

    // Pagination
    'pagination.prev': '← 前へ',
    'pagination.next': '次へ →',

    // Cart
    'cart.title': '🛒 カート',
    'cart.empty': 'カートは空です',
    'cart.total': '合計',
    'cart.submit': '注文を確定する',
    'cart.itemCount': '{count}点',
    'cart.goToOrder': '注文へ →',

    // Modal
    'modal.notes.label': 'ご要望（オプション）',
    'modal.notes.placeholder': 'よく焼き、タレ多め など',
    'modal.cancel': 'キャンセル',
    'modal.addToCart': 'カートに追加',

    // Notifications
    'notify.addedToCart': '{name} をカートに追加しました',
    'notify.quickAdd': '{name} を追加',
    'notify.orderSuccess': 'ご注文を承りました！',
    'notify.orderFailed': '注文に失敗しました。もう一度お試しください。',
    'notify.orderReady': '注文 #{number} が完成しました！',

    // Call staff
    'call.assistance': 'スタッフを呼びました',
    'call.water': 'お水をお持ちします',
    'call.bill': 'お会計をお待ちください',

    // Order
    'order.submitting': '送信中...',

    // Connection
    'connection.online': 'オンライン接続中',
    'connection.offline': 'オフラインモード - デモデータ使用中',
    'connection.statusOnline': 'オンライン',
    'connection.statusOffline': 'オフライン',
    'connection.offlineNotice': '⚠️ リアルタイム通知は現在利用できません。ご注文は通常通りお受けできます。',

    // Order History
    'header.history': '履歴',
    'history.title': '📋 注文履歴',
    'history.empty': 'まだ注文がありません',
    'history.totalItems': '合計品数',
    'history.totalAmount': '合計金額',
    'history.itemUnit': '品',

    // Loading
    'loading.text': 'メニューを読み込み中...',
    'loading.api': 'API接続',
    'loading.realtime': 'リアルタイム',

    // Demo menu items - Meat
    'demo.meat.wagyu_harami': '和牛上ハラミ',
    'demo.meat.wagyu_harami.desc': '口の中でほどける柔らかさと濃厚な味わい。当店自慢の一品',
    'demo.meat.atsugiri_tan': '厚切り上タン塩',
    'demo.meat.atsugiri_tan.desc': '贅沢な厚切り。歯ごたえと肉汁が溢れます',
    'demo.meat.tokusen_kalbi': '特選カルビ',
    'demo.meat.tokusen_kalbi.desc': '霜降りが美しい最高級カルビ',
    'demo.meat.kalbi': 'カルビ',
    'demo.meat.kalbi.desc': '定番の人気メニュー。ジューシーな味わい',
    'demo.meat.jo_rosu': '上ロース',
    'demo.meat.jo_rosu.desc': '赤身の旨味が楽しめる上質なロース',
    'demo.meat.rosu': 'ロース',
    'demo.meat.rosu.desc': 'あっさりとした赤身の美味しさ',
    'demo.meat.horumon': 'ホルモン盛り合わせ',
    'demo.meat.horumon.desc': '新鮮なホルモンをたっぷり。ミノ・ハチノス・シマチョウ',
    'demo.meat.tokusen_mori': '特選盛り合わせ',
    'demo.meat.tokusen_mori.desc': '本日のおすすめ希少部位を贅沢に盛り合わせ',
    'demo.meat.buta_kalbi': '豚カルビ',
    'demo.meat.buta_kalbi.desc': '甘みのある豚バラ肉',
    'demo.meat.tori_momo': '鶏もも',
    'demo.meat.tori_momo.desc': '柔らかくジューシーな鶏もも肉',

    // Demo menu items - Drinks
    'demo.drinks.nama_beer': '生ビール',
    'demo.drinks.nama_beer.desc': 'キンキンに冷えた生ビール（中）',
    'demo.drinks.bin_beer': '瓶ビール',
    'demo.drinks.bin_beer.desc': 'アサヒスーパードライ',
    'demo.drinks.highball': 'ハイボール',
    'demo.drinks.highball.desc': 'すっきり爽やかなウイスキーソーダ',
    'demo.drinks.lemon_sour': 'レモンサワー',
    'demo.drinks.lemon_sour.desc': '自家製レモンサワー。さっぱり飲みやすい',
    'demo.drinks.umeshu': '梅酒サワー',
    'demo.drinks.umeshu.desc': '甘酸っぱい梅酒ソーダ割り',
    'demo.drinks.makgeolli': 'マッコリ',
    'demo.drinks.makgeolli.desc': '韓国の伝統酒。まろやかな甘さ',
    'demo.drinks.shochu': '焼酎（芋）',
    'demo.drinks.shochu.desc': '本格芋焼酎。ロック・水割り・お湯割り',
    'demo.drinks.oolong': 'ウーロン茶',
    'demo.drinks.oolong.desc': 'ソフトドリンク',
    'demo.drinks.cola': 'コーラ',
    'demo.drinks.cola.desc': 'コカ・コーラ',
    'demo.drinks.oj': 'オレンジジュース',
    'demo.drinks.oj.desc': '100%果汁オレンジジュース',

    // Demo menu items - Salad
    'demo.salad.choregi': 'チョレギサラダ',
    'demo.salad.choregi.desc': '韓国風ピリ辛サラダ。ごま油が香る',
    'demo.salad.caesar': 'シーザーサラダ',
    'demo.salad.caesar.desc': 'パルメザンチーズたっぷり',
    'demo.salad.namul': 'ナムル盛り合わせ',
    'demo.salad.namul.desc': '3種のナムル（もやし・ほうれん草・大根）',
    'demo.salad.kimchi': 'キムチ盛り合わせ',
    'demo.salad.kimchi.desc': '白菜・カクテキ・オイキムチ',

    // Demo menu items - Rice & Noodles
    'demo.rice.rice': 'ライス',
    'demo.rice.rice.desc': '国産コシヒカリ使用',
    'demo.rice.rice_large': '大盛りライス',
    'demo.rice.rice_large.desc': '国産コシヒカリ大盛り',
    'demo.rice.bibimbap': '石焼ビビンバ',
    'demo.rice.bibimbap.desc': '熱々の石鍋で提供。おこげが美味しい',
    'demo.rice.naengmyeon': '冷麺',
    'demo.rice.naengmyeon.desc': '韓国冷麺。さっぱりとした味わい',
    'demo.rice.kuppa': 'カルビクッパ',
    'demo.rice.kuppa.desc': 'カルビ入りの韓国風スープご飯',

    // Demo menu items - Sides
    'demo.side.wakame': 'わかめスープ',
    'demo.side.wakame.desc': '韓国風わかめスープ',
    'demo.side.oxtail': 'テールスープ',
    'demo.side.oxtail.desc': 'コラーゲンたっぷり牛テールスープ',
    'demo.side.edamame': '枝豆',
    'demo.side.edamame.desc': '塩茹で枝豆',
    'demo.side.nori': '韓国海苔',
    'demo.side.nori.desc': 'ごま油香る韓国海苔',
    'demo.side.jeon': 'チヂミ',
    'demo.side.jeon.desc': '海鮮チヂミ。外はカリッと中はもっちり',

    // Demo menu items - Dessert
    'demo.dessert.vanilla': 'バニラアイス',
    'demo.dessert.vanilla.desc': '濃厚バニラアイスクリーム',
    'demo.dessert.annin': '杏仁豆腐',
    'demo.dessert.annin.desc': '手作り杏仁豆腐。なめらかな口当たり',
    'demo.dessert.sorbet': 'シャーベット',
    'demo.dessert.sorbet.desc': 'マンゴーシャーベット',

    // Demo menu items - Set Menu
    'demo.set.yakiniku_set': '焼肉定食',
    'demo.set.yakiniku_set.desc': 'カルビ・ロース・ライス・スープ・サラダ',
    'demo.set.jo_yakiniku_set': '上焼肉定食',
    'demo.set.jo_yakiniku_set.desc': '上カルビ・上ロース・ライス・スープ・サラダ',
    'demo.set.joshikai': '女子会コース',
    'demo.set.joshikai.desc': 'サラダ・お肉5種・デザート・ドリンク付き',
};

// Register to global i18n object
if (typeof window.i18n === 'undefined') window.i18n = {};
window.i18n.ja = ja;