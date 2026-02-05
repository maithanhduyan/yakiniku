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
            Toast.error('エラー', '顧客の読み込みに失敗しました');
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
                                placeholder="名前または電話番号で検索..."
                                value="${this.searchQuery}"
                                style="flex: 1;">
                            <button class="btn btn-secondary" id="searchBtn">検索</button>
                        </div>
                    </div>
                </div>

                <!-- Stats -->
                <div class="stats-grid" style="margin-bottom: 24px;">
                    <div class="stat-card">
                        <div class="icon">👥</div>
                        <div class="value">${this.customers.length}</div>
                        <div class="label">総顧客数</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">⭐</div>
                        <div class="value">${this.customers.filter(c => c.is_vip).length}</div>
                        <div class="label">VIP顧客</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">🔄</div>
                        <div class="value">${this.customers.filter(c => c.visit_count >= 5).length}</div>
                        <div class="label">リピーター</div>
                    </div>
                </div>

                <!-- Customer List -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">顧客一覧</h3>
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
            return EmptyState.render('👥', '顧客がいません', this.searchQuery ? '検索条件に一致する顧客がいません' : '顧客データがありません');
        }

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>お客様名</th>
                        <th>電話番号</th>
                        <th>来店回数</th>
                        <th>最終来店</th>
                        <th>ステータス</th>
                        <th>操作</th>
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
                            <td>${customer.visit_count || 0}回</td>
                            <td>${customer.last_visit ? Format.relativeTime(customer.last_visit) : '-'}</td>
                            <td>
                                ${customer.is_vip ? Badge.create('confirmed', 'VIP') : ''}
                                ${customer.visit_count >= 10 ? Badge.create('completed', '常連') : ''}
                            </td>
                            <td>
                                <button class="btn btn-sm btn-secondary view-btn" data-id="${customer.id}">詳細</button>
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
            title: '顧客詳細',
            content: `
                <div class="customer-detail">
                    <div class="detail-header" style="text-align: center; margin-bottom: 20px;">
                        <div style="font-size: 3rem; margin-bottom: 10px;">
                            ${customer.is_vip ? '⭐' : '👤'}
                        </div>
                        <h2 style="margin: 0;">${customer.name || '名前なし'}</h2>
                        ${customer.is_vip ? '<span class="badge confirmed">VIP</span>' : ''}
                    </div>

                    <div class="detail-row">
                        <label>電話番号</label>
                        <span>${Format.phone(customer.phone)}</span>
                    </div>
                    <div class="detail-row">
                        <label>メール</label>
                        <span>${customer.email || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>来店回数</label>
                        <span>${customer.visit_count || 0}回</span>
                    </div>
                    <div class="detail-row">
                        <label>最終来店</label>
                        <span>${customer.last_visit ? Format.datetime(customer.last_visit) : '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>備考</label>
                        <span>${customer.notes || '-'}</span>
                    </div>

                    ${preferences.length > 0 ? `
                        <div style="margin-top: 20px;">
                            <h4 style="margin-bottom: 10px;">好み・アレルギー</h4>
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
