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
            Toast.error('エラー', 'テーブルの読み込みに失敗しました');
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
                        <div class="label">空席</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--danger);">🔴</div>
                        <div class="value">${this.tables.filter(t => t.status === 'occupied').length}</div>
                        <div class="label">使用中</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--warning);">🟡</div>
                        <div class="value">${this.tables.filter(t => t.status === 'reserved').length}</div>
                        <div class="label">予約済</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">🪑</div>
                        <div class="value">${this.tables.length}</div>
                        <div class="label">総テーブル数</div>
                    </div>
                </div>

                <!-- Tables by Zone -->
                ${Object.entries(zones).map(([zone, tables]) => `
                    <div class="card" style="margin-bottom: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">${zone || 'その他'}</h3>
                            <span class="text-muted">${tables.length}テーブル</span>
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
                    <div>${table.max_capacity}名まで</div>
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
            <button class="btn btn-secondary" onclick="Modal.close()">閉じる</button>
            ${table.status === 'available' ?
                `<button class="btn btn-danger" id="occupyBtn">使用開始</button>` :
                table.status === 'occupied' ?
                `<button class="btn btn-success" id="releaseBtn">使用終了</button>` :
                ''
            }
        `;

        Modal.open({
            title: `テーブル ${table.table_number}`,
            content: `
                <div class="table-detail">
                    <div class="detail-row">
                        <label>タイプ</label>
                        <span>${Format.tableType(table.table_type)}</span>
                    </div>
                    <div class="detail-row">
                        <label>定員</label>
                        <span>${table.max_capacity}名</span>
                    </div>
                    <div class="detail-row">
                        <label>ゾーン</label>
                        <span>${table.zone || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>窓側</label>
                        <span>${table.has_window ? 'はい' : 'いいえ'}</span>
                    </div>
                    <div class="detail-row">
                        <label>ステータス</label>
                        ${Badge.create(table.status || 'available')}
                    </div>
                    <div class="detail-row">
                        <label>備考</label>
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
            Toast.success('更新完了', 'テーブルステータスを更新しました');
            await this.loadData();
            this.render();
            this.setupEventListeners();
        } catch (error) {
            Toast.error('エラー', error.message);
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
