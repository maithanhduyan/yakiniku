/**
 * English translations
 * File: i18n/en.js
 */

const en = {
    // Header
    'header.call': 'Call',
    'header.bill': 'Bill',

    // Guest info
    'guest.suffix': ' guests',

    // Category labels
    'cat.meat': 'Meat',
    'cat.drinks': 'Drinks',
    'cat.salad': 'Salad',
    'cat.rice': 'Rice & Noodles',
    'cat.side': 'Sides',
    'cat.dessert': 'Dessert',
    'cat.set': 'Set Menu',

    // Menu
    'menu.popular': '🔥 Popular',
    'menu.noItems': 'No items available',
    'menu.add': 'Add',

    // Pagination
    'pagination.prev': '← Prev',
    'pagination.next': 'Next →',

    // Cart
    'cart.title': '🛒 Cart',
    'cart.empty': 'Your cart is empty',
    'cart.total': 'Total',
    'cart.submit': 'Place Order',
    'cart.itemCount': '{count} items',
    'cart.goToOrder': 'Order →',

    // Modal
    'modal.notes.label': 'Special requests (optional)',
    'modal.notes.placeholder': 'e.g. Well done, extra sauce',
    'modal.cancel': 'Cancel',
    'modal.addToCart': 'Add to Cart',

    // Notifications
    'notify.addedToCart': '{name} added to cart',
    'notify.quickAdd': '{name} added',
    'notify.orderSuccess': 'Your order has been placed!',
    'notify.orderFailed': 'Order failed. Please try again.',
    'notify.orderReady': 'Order #{number} is ready!',

    // Call staff
    'call.assistance': 'Staff has been called',
    'call.water': 'Water is on its way',
    'call.bill': 'Bill is being prepared',

    // Order
    'order.submitting': 'Submitting...',

    // Connection
    'connection.online': 'Connected',
    'connection.offline': 'Offline mode - Using demo data',
    'connection.statusOnline': 'Online',
    'connection.statusOffline': 'Offline',
    'connection.offlineNotice': '⚠️ Real-time notifications are unavailable. You can still place orders normally.',

    // Order History
    'header.history': 'History',
    'history.title': '📋 Order History',
    'history.empty': 'No orders yet',
    'history.totalItems': 'Total items',
    'history.totalAmount': 'Total amount',
    'history.itemUnit': ' items',

    // Loading
    'loading.text': 'Loading menu...',
    'loading.api': 'API',
    'loading.realtime': 'Real-time',

    // Session - Welcome Screen
    'welcome.title': 'Yakiniku Jian',
    'welcome.subtitle': 'Table Ordering System',
    'welcome.start': 'Touch to start ordering',
    'welcome.tableLabel': 'Table',
    'welcome.guestsLabel': 'Guests',
    'welcome.langHint': '🌐 日本語も対応',

    // Session - Bill Review Screen
    'bill.title': '📋 Order Summary',
    'bill.subtitle': 'Staff will prepare your bill',
    'bill.addMore': '＋ Add More',
    'bill.waiting': 'Preparing your bill...',
    'bill.totalItems': 'Total items',
    'bill.totalAmount': 'Total amount',

    // Session - Cleaning Screen
    'cleaning.title': 'Thank you!',
    'cleaning.subtitle': 'We look forward to seeing you again',
    'cleaning.summary': 'Session Summary',
    'cleaning.orders': 'Orders placed',
    'cleaning.items': 'Total items',
    'cleaning.total': 'Total amount',
    'cleaning.reset': 'Reset',
    'cleaning.resetHint': 'Hold 3 seconds to reset',
    'cleaning.resetting': 'Resetting...',

    // Session - Inactivity
    'inactivity.warning': '🔔 No activity for 30 minutes',
    'inactivity.dismiss': 'Dismiss',

    // Demo menu items - Meat
    'demo.meat.wagyu_harami': 'Wagyu Harami',
    'demo.meat.wagyu_harami.desc': 'Melt-in-your-mouth tender skirt steak with rich flavor. Our signature dish',
    'demo.meat.atsugiri_tan': 'Thick-Cut Beef Tongue',
    'demo.meat.atsugiri_tan.desc': 'Luxuriously thick cut. Great texture and juicy',
    'demo.meat.tokusen_kalbi': 'Premium Kalbi',
    'demo.meat.tokusen_kalbi.desc': 'Beautifully marbled top-grade short rib',
    'demo.meat.kalbi': 'Kalbi (Short Rib)',
    'demo.meat.kalbi.desc': 'Classic favorite. Juicy and flavorful',
    'demo.meat.jo_rosu': 'Premium Loin',
    'demo.meat.jo_rosu.desc': 'Quality loin with rich lean meat flavor',
    'demo.meat.rosu': 'Loin',
    'demo.meat.rosu.desc': 'Light and delicious lean cut',
    'demo.meat.horumon': 'Offal Platter',
    'demo.meat.horumon.desc': 'Fresh assorted offal: Tripe, Honeycomb, Intestine',
    'demo.meat.tokusen_mori': 'Premium Assorted Platter',
    'demo.meat.tokusen_mori.desc': "Today's recommended rare cuts, luxuriously plated",
    'demo.meat.buta_kalbi': 'Pork Belly',
    'demo.meat.buta_kalbi.desc': 'Sweet and tender pork belly',
    'demo.meat.tori_momo': 'Chicken Thigh',
    'demo.meat.tori_momo.desc': 'Tender and juicy chicken thigh',

    // Demo menu items - Drinks
    'demo.drinks.nama_beer': 'Draft Beer',
    'demo.drinks.nama_beer.desc': 'Ice-cold draft beer (medium)',
    'demo.drinks.bin_beer': 'Bottled Beer',
    'demo.drinks.bin_beer.desc': 'Asahi Super Dry',
    'demo.drinks.highball': 'Highball',
    'demo.drinks.highball.desc': 'Refreshing whisky soda',
    'demo.drinks.lemon_sour': 'Lemon Sour',
    'demo.drinks.lemon_sour.desc': 'House-made lemon sour. Light and refreshing',
    'demo.drinks.umeshu': 'Plum Wine Sour',
    'demo.drinks.umeshu.desc': 'Sweet and tangy plum wine soda',
    'demo.drinks.makgeolli': 'Makgeolli',
    'demo.drinks.makgeolli.desc': 'Korean traditional rice wine. Smooth and sweet',
    'demo.drinks.shochu': 'Shochu (Sweet Potato)',
    'demo.drinks.shochu.desc': 'Authentic sweet potato shochu. On the rocks / with water / hot water',
    'demo.drinks.oolong': 'Oolong Tea',
    'demo.drinks.oolong.desc': 'Non-alcoholic',
    'demo.drinks.cola': 'Cola',
    'demo.drinks.cola.desc': 'Coca-Cola',
    'demo.drinks.oj': 'Orange Juice',
    'demo.drinks.oj.desc': '100% fresh orange juice',

    // Demo menu items - Salad
    'demo.salad.choregi': 'Choregi Salad',
    'demo.salad.choregi.desc': 'Korean-style spicy salad with sesame oil',
    'demo.salad.caesar': 'Caesar Salad',
    'demo.salad.caesar.desc': 'Loaded with Parmesan cheese',
    'demo.salad.namul': 'Namul Assortment',
    'demo.salad.namul.desc': '3 kinds of namul (bean sprout, spinach, radish)',
    'demo.salad.kimchi': 'Kimchi Assortment',
    'demo.salad.kimchi.desc': 'Napa cabbage, cubed radish, cucumber kimchi',

    // Demo menu items - Rice & Noodles
    'demo.rice.rice': 'Rice',
    'demo.rice.rice.desc': 'Premium Japanese Koshihikari rice',
    'demo.rice.rice_large': 'Large Rice',
    'demo.rice.rice_large.desc': 'Large serving of Koshihikari rice',
    'demo.rice.bibimbap': 'Stone Pot Bibimbap',
    'demo.rice.bibimbap.desc': 'Served sizzling hot in a stone pot. Crispy rice bottom',
    'demo.rice.naengmyeon': 'Cold Noodles',
    'demo.rice.naengmyeon.desc': 'Korean cold noodles. Light and refreshing',
    'demo.rice.kuppa': 'Kalbi Kuppa',
    'demo.rice.kuppa.desc': 'Korean-style soup rice with kalbi',

    // Demo menu items - Sides
    'demo.side.wakame': 'Seaweed Soup',
    'demo.side.wakame.desc': 'Korean-style seaweed soup',
    'demo.side.oxtail': 'Oxtail Soup',
    'demo.side.oxtail.desc': 'Collagen-rich oxtail soup',
    'demo.side.edamame': 'Edamame',
    'demo.side.edamame.desc': 'Salted boiled edamame',
    'demo.side.nori': 'Korean Seaweed',
    'demo.side.nori.desc': 'Sesame oil flavored Korean seaweed',
    'demo.side.jeon': 'Jeon (Korean Pancake)',
    'demo.side.jeon.desc': 'Seafood pancake. Crispy outside, soft inside',

    // Demo menu items - Dessert
    'demo.dessert.vanilla': 'Vanilla Ice Cream',
    'demo.dessert.vanilla.desc': 'Rich and creamy vanilla ice cream',
    'demo.dessert.annin': 'Almond Tofu',
    'demo.dessert.annin.desc': 'Handmade almond tofu. Silky smooth',
    'demo.dessert.sorbet': 'Sorbet',
    'demo.dessert.sorbet.desc': 'Mango sorbet',

    // Demo menu items - Set Menu
    'demo.set.yakiniku_set': 'Yakiniku Set',
    'demo.set.yakiniku_set.desc': 'Kalbi, Loin, Rice, Soup & Salad',
    'demo.set.jo_yakiniku_set': 'Premium Yakiniku Set',
    'demo.set.jo_yakiniku_set.desc': 'Premium Kalbi, Premium Loin, Rice, Soup & Salad',
    'demo.set.joshikai': 'Ladies Course',
    'demo.set.joshikai.desc': 'Salad, 5 kinds of meat, Dessert & Drink included',
};

// Register to global i18n object
if (typeof window.i18n === 'undefined') window.i18n = {};
window.i18n.en = en;