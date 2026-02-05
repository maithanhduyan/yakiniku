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