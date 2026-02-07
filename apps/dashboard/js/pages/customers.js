/**
 * Customers Page - Customer Management
 */
const CustomersPage = {
    customers: [],
    searchQuery: '',

    async init() {
        await this.loadData();
        this.render();
        this.setupEventListeners();
    },

    async loadData() {
        try {
            Loading.show('#pageContent');
            this.customers = await api.getCustomers();
        } catch (error) {
            console.error('Failed to load customers:', error);
            Toast.error(t('common.error'), t('customers.loadFailed'));
            this.customers = [];
        }
    },

    render() {
        const content = document.getElementById('pageContent');

        content.innerHTML = `
            <div class="customers-page">
                <!-- Search & Filters -->
                <div class="card" style="margin-bottom: 20px;">
                    <div class="card-body" style="padding: 16px;">
                        <div class="search-bar" style="display: flex; gap: 12px;">
                            <input type="text"
                                class="form-input"
                                id="searchInput"
                                placeholder="${t('customers.searchPlaceholder')}"
                                value="${this.searchQuery}"
                                style="flex: 1;">
                            <button class="btn btn-secondary" id="searchBtn">${t('common.search')}</button>
                        </div>
                    </div>
                </div>

                <!-- Stats -->
                <div class="stats-grid" style="margin-bottom: 24px;">
                    <div class="stat-card">
                        <div class="icon">👥</div>
                        <div class="value">${this.customers.length}</div>
                        <div class="label">${t('customers.total')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">⭐</div>
                        <div class="value">${this.customers.filter(c => c.is_vip).length}</div>
                        <div class="label">${t('customers.vip')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">🔄</div>
                        <div class="value">${this.customers.filter(c => c.visit_count >= 5).length}</div>
                        <div class="label">${t('customers.repeater')}</div>
                    </div>
                </div>

                <!-- Customer List -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">${t('customers.list')}</h3>
                    </div>
                    <div class="card-body" style="padding: 0;" id="customerList">
                        ${this.renderTable()}
                    </div>
                </div>
            </div>
        `;
    },

    renderTable() {
        const filtered = this.filterCustomers();

        if (filtered.length === 0) {
            return EmptyState.render('👥', t('customers.noCustomers'), this.searchQuery ? t('customers.noResults') : t('customers.noData'));
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>${t('customers.name')}</th>
                        <th>${t('customers.phone')}</th>
                        <th>${t('customers.visits')}</th>
                        <th>${t('customers.lastVisit')}</th>
                        <th>${t('customers.status')}</th>
                        <th>${t('customers.actions')}</th>
                    </tr>
                </thead>
                <tbody>
                    ${filtered.map(customer => `
                        <tr data-customer-id="${customer.id}">
                            <td>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    ${customer.is_vip ? '<span style="color: var(--accent-gold);">⭐</span>' : ''}
                                    <strong>${customer.name || '-'}</strong>
                                </div>
                            </td>
                            <td>${Format.phone(customer.phone)}</td>
                            <td>${customer.visit_count || 0}${t('customers.visitUnit')}</td>
                            <td>${customer.last_visit ? Format.relativeTime(customer.last_visit) : '-'}</td>
                            <td>
                                ${customer.is_vip ? Badge.create('confirmed', 'VIP') : ''}
                                ${customer.visit_count >= 10 ? Badge.create('completed', t('customers.regular')) : ''}
                            </td>
                            <td>
                                <button class="btn btn-sm btn-secondary view-btn" data-id="${customer.id}">${t('common.detail')}</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },

    filterCustomers() {
        if (!this.searchQuery) return this.customers;

        const query = this.searchQuery.toLowerCase();
        return this.customers.filter(c =>
            (c.name && c.name.toLowerCase().includes(query)) ||
            (c.phone && c.phone.includes(query))
        );
    },

    setupEventListeners() {
        // Search
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');

        searchBtn.addEventListener('click', () => {
            this.searchQuery = searchInput.value;
            document.getElementById('customerList').innerHTML = this.renderTable();
            this.attachTableListeners();
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchQuery = searchInput.value;
                document.getElementById('customerList').innerHTML = this.renderTable();
                this.attachTableListeners();
            }
        });

        this.attachTableListeners();
    },

    attachTableListeners() {
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.showCustomerDetail(btn.dataset.id);
            });
        });
    },

    async showCustomerDetail(id) {
        const customer = this.customers.find(c => c.id === id);
        if (!customer) return;

        // Try to load preferences
        let preferences = [];
        try {
            preferences = await api.getCustomerPreferences(id);
        } catch (e) {
            console.log('No preferences found');
        }

        Modal.open({
            title: t('customers.detail'),
            content: `
                <div class="customer-detail">
                    <div class="detail-header" style="text-align: center; margin-bottom: 20px;">
                        <div style="font-size: 3rem; margin-bottom: 10px;">
                            ${customer.is_vip ? '⭐' : '👤'}
                        </div>
                        <h2 style="margin: 0;">${customer.name || t('customers.noName')}</h2>
                        ${customer.is_vip ? '<span class="badge confirmed">VIP</span>' : ''}
                    </div>

                    <div class="detail-row">
                        <label>${t('customers.phone')}</label>
                        <span>${Format.phone(customer.phone)}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('customers.email')}</label>
                        <span>${customer.email || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('customers.visits')}</label>
                        <span>${customer.visit_count || 0}${t('customers.visitUnit')}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('customers.lastVisit')}</label>
                        <span>${customer.last_visit ? Format.datetime(customer.last_visit) : '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('common.notes')}</label>
                        <span>${customer.notes || '-'}</span>
                    </div>

                    ${preferences.length > 0 ? `
                        <div style="margin-top: 20px;">
                            <h4 style="margin-bottom: 10px;">${t('customers.preferences')}</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                ${preferences.map(p => `
                                    <span class="badge ${p.category === 'allergy' ? 'cancelled' : 'pending'}">${p.preference}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                <style>
                    .detail-row { display: flex; padding: 10px 0; border-bottom: 1px solid var(--bg-tertiary); }
                    .detail-row label { width: 100px; color: var(--text-muted); }
                    .detail-row span { flex: 1; }
                </style>
            `,
            size: 'md'
        });
    }
};
