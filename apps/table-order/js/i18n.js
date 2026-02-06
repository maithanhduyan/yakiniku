/**
 * i18n - Internationalization for Table Order App
 * Supports: ja (Japanese), en (English)
 *
 * Translations are loaded from separate files:
 *   - js/i18n/ja.js → window.i18n.ja
 *   - js/i18n/en.js → window.i18n.en
 */

const I18N = {
    // Current language
    currentLang: localStorage.getItem('table_order_lang') || 'ja',

    // Translation dictionaries - loaded from external files via window.i18n
    translations: {
        ja: (window.i18n && window.i18n.ja) || {},
        en: (window.i18n && window.i18n.en) || {},
    },

    /**
     * Get translation for a key with optional parameter substitution
     * @param {string} key - Translation key
     * @param {Object} params - Parameters to substitute {name}, {count}, etc.
     * @returns {string}
     */
    t(key, params = {}) {
        const dict = this.translations[this.currentLang] || this.translations['ja'];
        let text = dict[key];

        // Fallback to Japanese if key not found in current language
        if (text === undefined) {
            text = this.translations['ja'][key];
        }

        // Final fallback: return the key itself
        if (text === undefined) {
            return key;
        }

        // Substitute parameters like {name}, {count}
        for (const [param, value] of Object.entries(params)) {
            text = text.replace(`{${param}}`, value);
        }

        return text;
    },

    /**
     * Set language and update all data-i18n elements
     * @param {string} lang - 'ja' or 'en'
     */
    setLanguage(lang) {
        if (!this.translations[lang]) return;

        this.currentLang = lang;
        localStorage.setItem('table_order_lang', lang);

        // Update HTML lang attribute
        document.documentElement.lang = lang === 'ja' ? 'ja' : 'en';

        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            el.textContent = this.t(key);
        });

        // Update elements with data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            el.placeholder = this.t(key);
        });

        // Update lang toggle button
        const langBtn = document.getElementById('langToggle');
        if (langBtn) {
            langBtn.textContent = lang === 'ja' ? 'EN' : 'JP';
            langBtn.title = lang === 'ja' ? 'Switch to English' : '日本語に切替';
        }
    },

    /**
     * Toggle between ja and en
     */
    toggle() {
        this.setLanguage(this.currentLang === 'ja' ? 'en' : 'ja');
    },

    /**
     * Initialize - apply saved language on load
     */
    init() {
        this.setLanguage(this.currentLang);
    }
};

// Shortcut function
function t(key, params = {}) {
    return I18N.t(key, params);
}

function toggleLanguage() {
    I18N.toggle();
    // Re-render dynamic content with new language
    if (typeof state !== 'undefined' && !state.isOnline) {
        // Reload demo menu with translated names
        if (typeof loadDemoMenu === 'function') {
            loadDemoMenu();
        }
    } else {
        // API data: re-render with existing data (names stay from API)
        if (typeof renderCategories === 'function') {
            renderCategories();
            const cat = state.categories.find(c => c.category === state.currentCategory);
            if (cat) renderMenuItems(cat.items);
        }
    }
    if (typeof renderCartItems === 'function') {
        renderCartItems();
    }
    if (typeof updateCartBadge === 'function') {
        updateCartBadge();
    }
    // Update guest count suffix
    if (typeof state !== 'undefined') {
        const guestEl = document.getElementById('guestCount');
        if (guestEl) guestEl.textContent = `${state.guestCount}${t('guest.suffix')}`;
    }
}
