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
            Toast.error('ã‚¨ãƒ©ãƒ¼', 'ãƒ†ãƒ¼ãƒ–ãƒ«ã®èª­ã¿è¾¼ã¿ã«å¤±æ•—ã—ã¾ã—ãŸ');
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
                        <div class="icon" style="color: var(--success);">ðŸŸ¢</div>
                        <div class="value">${this.tables.filter(t => t.status === 'available').length}</div>
                        <div class="label">ç©ºå¸­</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--danger);">ðŸ”´</div>
                        <div class="value">${this.tables.filter(t => t.status === 'occupied').length}</div>
                        <div class="label">ä½¿ç”¨ä¸­</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--warning);">ðŸŸ¡</div>
                        <div class="value">${this.tables.filter(t => t.status === 'reserved').length}</div>
                        <div class="label">äºˆç´„æ¸ˆ</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">ðŸª‘</div>
                        <div class="value">${this.tables.length}</div>
                        <div class="label">ç·ãƒ†ãƒ¼ãƒ–ãƒ«æ•°</div>
                    </div>
                </div>

                <!-- Tables by Zone -->
                ${Object.entries(zones).map(([zone, tables]) => `
                    <div class="card" style="margin-bottom: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">${zone || 'ãã®ä»–'}</h3>
                            <span class="text-muted">${tables.length}ãƒ†ãƒ¼ãƒ–ãƒ«</span>
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
                    <div>${table.max_capacity}åã¾ã§</div>
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
            <button class="btn btn-secondary" onclick="Modal.close()">é–‰ã˜ã‚‹</button>
            ${table.status === 'available' ?
                `<button class="btn btn-danger" id="occupyBtn">ä½¿ç”¨é–‹å§‹</button>` :
                table.status === 'occupied' ?
                `<button class="btn btn-success" id="releaseBtn">ä½¿ç”¨çµ‚äº†</button>` :
                ''
            }
        `;

        Modal.open({
            title: `ãƒ†ãƒ¼ãƒ–ãƒ« ${table.table_number}`,
            content: `
                <div class="table-detail">
                    <div class="detail-row">
                        <label>ã‚¿ã‚¤ãƒ—</label>
                        <span>${Format.tableType(table.table_type)}</span>
                    </div>
                    <div class="detail-row">
                        <label>å®šå“¡</label>
                        <span>${table.max_capacity}å</span>
                    </div>
                    <div class="detail-row">
                        <label>ã‚¾ãƒ¼ãƒ³</label>
                        <span>${table.zone || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>çª“å´</label>
                        <span>${table.has_window ? 'ã¯ã„' : 'ã„ã„ãˆ'}</span>
                    </div>
                    <div class="detail-row">
                        <label>ã‚¹ãƒ†ãƒ¼ã‚¿ã‚¹</label>
                        ${Badge.create(table.status || 'available')}
                    </div>
                    <div class="detail-row">
                        <label>å‚™è€ƒ</label>
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
            Toast.success('æ›´æ–°å®Œäº†', 'ãƒ†ãƒ¼ãƒ–ãƒ«ã‚¹ãƒ†ãƒ¼ã‚¿ã‚¹ã‚’æ›´æ–°ã—ã¾ã—ãŸ');
            await this.loadData();
            this.render();
            this.setupEventListeners();
        } catch (error) {
            Toast.error('ã‚¨ãƒ©ãƒ¼', error.message);
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



