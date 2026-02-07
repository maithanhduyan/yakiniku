/**
 * i18n - Internationalization for Dashboard App
 * Supports: ja (Japanese), en (English)
 *
 * Translations loaded from separate files:
 *   - js/i18n/ja.js → window.i18n.ja
 *   - js/i18n/en.js → window.i18n.en
 */

const I18N = {
    currentLang: localStorage.getItem('dashboard_lang') || 'ja',

    // Loaded from external files via window.i18n
    translations: {
        ja: (window.i18n && window.i18n.ja) || {},
        en: (window.i18n && window.i18n.en) || {},
    },

    /**
     * Get translation for a key with optional parameter substitution
     * @param {string} key - dot-separated key e.g. 'nav.home'
     * @param {Object} params - {name}, {count} etc.
     * @returns {string}
     */
    t(key, params = {}) {
        const dict = this.translations[this.currentLang] || this.translations['ja'];
        let text = dict[key];

        // Fallback to Japanese
        if (text === undefined) {
            text = this.translations['ja'][key];
        }
        // Final fallback: return key
        if (text === undefined) {
            return key;
        }

        // Substitute {param}
        for (const [param, value] of Object.entries(params)) {
            text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), value);
        }
        return text;
    },

    /**
     * Set language, persist, update static elements
     */
    setLanguage(lang) {
        if (!this.translations[lang]) return;
        this.currentLang = lang;
        localStorage.setItem('dashboard_lang', lang);
        document.documentElement.lang = lang === 'ja' ? 'ja' : 'en';

        // Update all [data-i18n] text
        document.querySelectorAll('[data-i18n]').forEach(el => {
            el.textContent = this.t(el.getAttribute('data-i18n'));
        });

        // Update [data-i18n-placeholder]
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            el.placeholder = this.t(el.getAttribute('data-i18n-placeholder'));
        });

        // Update [data-i18n-title]
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            el.title = this.t(el.getAttribute('data-i18n-title'));
        });

        // Update language toggle button
        const langBtn = document.getElementById('langToggle');
        if (langBtn) {
            langBtn.textContent = lang === 'ja' ? 'EN' : 'JP';
            langBtn.title = lang === 'ja' ? 'Switch to English' : '日本語に切替';
        }
    },

    /**
     * Toggle between ja ↔ en
     */
    toggle() {
        this.setLanguage(this.currentLang === 'ja' ? 'en' : 'ja');
    },

    /**
     * Initialize: apply saved language
     */
    init() {
        this.setLanguage(this.currentLang);
    },

    /**
     * Get date locale string matching current language
     */
    get dateLocale() {
        return this.currentLang === 'ja' ? 'ja-JP' : 'en-US';
    }
};

// Global shortcut
function t(key, params = {}) {
    return I18N.t(key, params);
}
