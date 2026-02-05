/**
 * UI Components for Dashboard
 */

// ============================================
// Toast Notifications
// ============================================

const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toastContainer');
    },

    show(type, title, message, duration = CONFIG.TOAST_DURATION) {
        const icons = {
            success: 'âœ“',
            error: 'âœ•',
            warning: 'âš ',
            info: 'â„¹'
        };

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || 'â„¹'}</span>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                ${message ? `<div class="toast-message">${message}</div>` : ''}
            </div>
            <button class="toast-close">âœ•</button>
        `;

        // Close button handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.remove(toast);
        });

        this.container.appendChild(toast);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }

        return toast;
    },

    remove(toast) {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    },

    success(title, message) {
        return this.show('success', title, message);
    },

    error(title, message) {
        return this.show('error', title, message);
    },

    warning(title, message) {
        return this.show('warning', title, message);
    },

    info(title, message) {
        return this.show('info', title, message);
    }
};

// ============================================
// Modal
// ============================================

const Modal = {
    overlay: null,
    modal: null,
    titleEl: null,
    bodyEl: null,
    footerEl: null,

    init() {
        this.overlay = document.getElementById('modalOverlay');
        this.modal = document.getElementById('modal');
        this.titleEl = document.getElementById('modalTitle');
        this.bodyEl = document.getElementById('modalBody');
        this.footerEl = document.getElementById('modalFooter');

        // Close handlers
        document.getElementById('modalClose').addEventListener('click', () => this.close());
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });

        // ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.overlay.classList.contains('open')) {
                this.close();
            }
        });
    },

    open(options = {}) {
        const { title, content, footer, size = 'md' } = options;

        this.titleEl.textContent = title || '';
        this.bodyEl.innerHTML = typeof content === 'string' ? content : '';

        if (typeof content !== 'string' && content) {
            this.bodyEl.innerHTML = '';
            this.bodyEl.appendChild(content);
        }

        if (footer) {
            this.footerEl.innerHTML = '';
            this.footerEl.appendChild(footer);
            this.footerEl.style.display = 'flex';
        } else {
            this.footerEl.style.display = 'none';
        }

        this.modal.style.maxWidth = size === 'lg' ? '700px' : size === 'sm' ? '400px' : '500px';
        this.overlay.classList.add('open');
    },

    close() {
        this.overlay.classList.remove('open');
    },

    confirm(title, message, onConfirm) {
        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" id="modalCancel">ã‚­ãƒ£ãƒ³ã‚»ãƒ«</button>
            <button class="btn btn-danger" id="modalConfirm">ç¢ºèª</button>
        `;

        this.open({ title, content: `<p>${message}</p>`, footer });

        footer.querySelector('#modalCancel').addEventListener('click', () => this.close());
        footer.querySelector('#modalConfirm').addEventListener('click', () => {
            this.close();
            onConfirm();
        });
    }
};

// ============================================
// Loading States
// ============================================

const Loading = {
    show(container) {
        const el = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        el.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
            </div>
        `;
    },

    skeleton(container, rows = 3) {
        const el = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        let html = '';
        for (let i = 0; i < rows; i++) {
            html += `
                <div style="margin-bottom: 12px;">
                    <div class="skeleton" style="height: 20px; width: 60%; margin-bottom: 8px;"></div>
                    <div class="skeleton" style="height: 16px; width: 40%;"></div>
                </div>
            `;
        }
        el.innerHTML = html;
    }
};

// ============================================
// Data Formatters
// ============================================

const Format = {
    date(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    time(timeStr) {
        if (!timeStr) return '-';
        return timeStr.substring(0, 5); // HH:MM
    },

    datetime(datetimeStr) {
        if (!datetimeStr) return '-';
        const date = new Date(datetimeStr);
        return date.toLocaleString('ja-JP', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    relativeTime(datetimeStr) {
        if (!datetimeStr) return '-';
        const date = new Date(datetimeStr);
        const now = new Date();
        const diff = now - date;

        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'ãŸã£ãŸä»Š';
        if (minutes < 60) return `${minutes}åˆ†å‰`;
        if (hours < 24) return `${hours}æ™‚é–“å‰`;
        if (days < 7) return `${days}æ—¥å‰`;
        return this.date(datetimeStr);
    },

    status(status) {
        return CONFIG.STATUS_LABELS[status] || status;
    },

    tableType(type) {
        return CONFIG.TABLE_TYPES[type] || type;
    },

    guests(count) {
        return `${count}å`;
    },

    phone(phone) {
        if (!phone) return '-';
        return phone;
    }
};

// ============================================
// Badge Component
// ============================================

const Badge = {
    create(status, text = null) {
        const label = text || Format.status(status);
        return `<span class="badge ${status}">${label}</span>`;
    }
};

// ============================================
// Empty State Component
// ============================================

const EmptyState = {
    render(icon, title, message, action = null) {
        return `
            <div class="empty-state">
                <div class="icon">${icon}</div>
                <div class="title">${title}</div>
                <div class="message">${message}</div>
                ${action ? `<button class="btn btn-primary">${action}</button>` : ''}
            </div>
        `;
    }
};

// ============================================
// Initialize Components
// ============================================

function initComponents() {
    Toast.init();
    Modal.init();
}



