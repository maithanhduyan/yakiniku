/**
 * Tables Page - Table Management
 */
const TablesPage = {
    tables: [],

    async init() {
        await this.loadData();
        this.render();
        this.setupEventListeners();
        this.setupWebSocket();
    },

    async loadData() {
        try {
            Loading.show('#pageContent');
            this.tables = await api.getTables();
        } catch (error) {
            console.error('Failed to load tables:', error);
            Toast.error(t('common.error'), t('tables.loadFailed'));
            this.tables = [];
        }
    },

    render() {
        const content = document.getElementById('pageContent');

        // Group tables by zone
        const zones = this.groupByZone();

        content.innerHTML = `
            <div class="tables-page">
                <!-- Summary -->
                <div class="stats-grid" style="margin-bottom: 24px;">
                    <div class="stat-card">
                        <div class="icon" style="color: var(--success);">🟢</div>
                        <div class="value">${this.tables.filter(t => t.status === 'available').length}</div>
                        <div class="label">${t('tables.available')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--danger);">🔴</div>
                        <div class="value">${this.tables.filter(t => t.status === 'occupied').length}</div>
                        <div class="label">${t('tables.occupied')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--warning);">🟡</div>
                        <div class="value">${this.tables.filter(t => t.status === 'reserved').length}</div>
                        <div class="label">${t('tables.reserved')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">🪑</div>
                        <div class="value">${this.tables.length}</div>
                        <div class="label">${t('tables.total')}</div>
                    </div>
                </div>

                <!-- Tables by Zone -->
                ${Object.entries(zones).map(([zone, tables]) => `
                    <div class="card" style="margin-bottom: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">${zone || t('tables.other')}</h3>
                            <span class="text-muted">${t('tables.tableCount', { count: tables.length })}</span>
                        </div>
                        <div class="card-body">
                            <div class="table-grid">
                                ${tables.map(table => this.renderTableCard(table)).join('')}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    groupByZone() {
        const zones = {};
        this.tables.forEach(table => {
            const zone = table.zone || 'main';
            if (!zones[zone]) zones[zone] = [];
            zones[zone].push(table);
        });

        // Sort tables by number within each zone
        Object.values(zones).forEach(tables => {
            tables.sort((a, b) => a.table_number - b.table_number);
        });

        return zones;
    },

    renderTableCard(table) {
        const status = table.status || 'available';

        return `
            <div class="table-card ${status}" data-table-id="${table.id}">
                <div class="table-number">${table.table_number}</div>
                <div class="table-info">
                    <div>${Format.tableType(table.table_type)}</div>
                    <div>${t('tables.capacity', { count: table.max_capacity })}</div>
                    <div class="text-muted" style="margin-top: 4px;">${Format.status(status)}</div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        // Table card click
        document.querySelectorAll('.table-card').forEach(card => {
            card.addEventListener('click', () => {
                this.showTableDetail(card.dataset.tableId);
            });
        });
    },

    showTableDetail(id) {
        const table = this.tables.find(t => t.id === id);
        if (!table) return;

        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" onclick="Modal.close()">${t('common.close')}</button>
            ${table.status === 'available' ?
                `<button class="btn btn-danger" id="occupyBtn">${t('tables.startUse')}</button>` :
                table.status === 'occupied' ?
                `<button class="btn btn-success" id="releaseBtn">${t('tables.endUse')}</button>` :
                ''
            }
        `;

        Modal.open({
            title: `${t('nav.tables')} ${table.table_number}`,
            content: `
                <div class="table-detail">
                    <div class="detail-row">
                        <label>${t('tables.type')}</label>
                        <span>${Format.tableType(table.table_type)}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('tables.capacity_label')}</label>
                        <span>${t('tables.capacity', { count: table.max_capacity })}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('tables.zone')}</label>
                        <span>${table.zone || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('tables.window')}</label>
                        <span>${table.has_window ? t('tables.yes') : t('tables.no')}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('common.status')}</label>
                        ${Badge.create(table.status || 'available')}
                    </div>
                    <div class="detail-row">
                        <label>${t('common.notes')}</label>
                        <span>${table.notes || '-'}</span>
                    </div>
                </div>
                <style>
                    .detail-row { display: flex; padding: 10px 0; border-bottom: 1px solid var(--bg-tertiary); }
                    .detail-row label { width: 100px; color: var(--text-muted); }
                    .detail-row span { flex: 1; }
                </style>
            `,
            footer
        });

        // Status change handlers
        footer.querySelector('#occupyBtn')?.addEventListener('click', async () => {
            await this.updateTableStatus(id, 'occupied');
            Modal.close();
        });

        footer.querySelector('#releaseBtn')?.addEventListener('click', async () => {
            await this.updateTableStatus(id, 'available');
            Modal.close();
        });
    },

    async updateTableStatus(id, status) {
        try {
            await api.updateTableStatus(id, status);
            Toast.success(t('tables.updated'), t('tables.updatedMessage'));
            await this.loadData();
            this.render();
            this.setupEventListeners();
        } catch (error) {
            Toast.error(t('common.error'), error.message);
        }
    },

    setupWebSocket() {
        ws.subscribe('tables');

        ws.on('table:status', async () => {
            await this.loadData();
            this.render();
            this.setupEventListeners();
        });
    }
};
