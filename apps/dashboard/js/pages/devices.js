/**
 * Devices Page — Device Management + QR Code Authorization
 * Team: dashboard
 */
const DevicesPage = {
    devices: [],
    tables: [],

    async init() {
        await this.loadData();
        this.render();
        this.setupEventListeners();
    },

    async loadData() {
        try {
            Loading.show('#pageContent');
            const [devicesRes, tablesRes] = await Promise.all([
                api.getDevices(),
                api.getTables(),
            ]);
            this.devices = devicesRes.devices || [];
            this.tables = Array.isArray(tablesRes) ? tablesRes : [];
        } catch (error) {
            console.error('Failed to load devices:', error);
            Toast.error('エラー', 'デバイスの読み込みに失敗しました');
            this.devices = [];
        }
    },

    render() {
        const content = document.getElementById('pageContent');

        const byType = { 'table-order': [], kitchen: [], pos: [], checkin: [] };
        this.devices.forEach(d => {
            if (byType[d.device_type]) byType[d.device_type].push(d);
        });

        const typeLabels = {
            'table-order': { icon: '🍽️', label: 'テーブルオーダー' },
            kitchen:       { icon: '👨‍🍳', label: 'キッチン (KDS)' },
            pos:           { icon: '💰', label: 'POS' },
            checkin:       { icon: '📋', label: 'チェックイン' },
        };

        content.innerHTML = `
            <div class="devices-page">
                <!-- Header actions -->
                <div class="page-actions">
                    <button class="btn btn-primary" id="addDeviceBtn">
                        ＋ 新規デバイス登録
                    </button>
                </div>

                <!-- Summary stats -->
                <div class="stats-grid" style="margin-bottom: 24px;">
                    <div class="stat-card">
                        <div class="icon" style="color: var(--success);">🟢</div>
                        <div class="value">${this.devices.filter(d => d.status === 'active').length}</div>
                        <div class="label">アクティブ</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--warning);">🟡</div>
                        <div class="value">${this.devices.filter(d => d.status === 'pending').length}</div>
                        <div class="label">認証待ち</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--danger);">🔴</div>
                        <div class="value">${this.devices.filter(d => d.status === 'inactive').length}</div>
                        <div class="label">無効</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">📱</div>
                        <div class="value">${this.devices.length}</div>
                        <div class="label">総デバイス数</div>
                    </div>
                </div>

                <!-- Devices by type -->
                ${Object.entries(byType).map(([type, devices]) => `
                    <div class="card" style="margin-bottom: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">${typeLabels[type].icon} ${typeLabels[type].label}</h3>
                            <span class="text-muted">${devices.length}台</span>
                        </div>
                        <div class="card-body">
                            ${devices.length === 0
                                ? '<div class="text-muted text-center" style="padding:24px;">登録されたデバイスはありません</div>'
                                : `<div class="device-list">
                                    ${devices.map(d => this.renderDeviceRow(d, typeLabels)).join('')}
                                </div>`
                            }
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    renderDeviceRow(device, typeLabels) {
        const statusBadge = this._statusBadge(device.status);
        const lastSeen = device.last_seen_at
            ? Format.relativeTime(device.last_seen_at)
            : '未接続';
        const tablePart = device.table_number
            ? `<span class="device-table">テーブル ${device.table_number}</span>`
            : '';

        return `
            <div class="device-row" data-device-id="${device.id}">
                <div class="device-info">
                    <div class="device-name">${device.name}</div>
                    <div class="device-meta">
                        ${tablePart}
                        <span class="device-seen">最終接続: ${lastSeen}</span>
                    </div>
                </div>
                <div class="device-actions">
                    ${statusBadge}
                    <button class="btn btn-sm btn-secondary device-qr-btn" data-id="${device.id}" title="QRコード表示">
                        📲
                    </button>
                    <button class="btn btn-sm btn-secondary device-edit-btn" data-id="${device.id}" title="編集">
                        ✏️
                    </button>
                    <button class="btn btn-sm btn-danger device-delete-btn" data-id="${device.id}" title="削除">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    },

    _statusBadge(status) {
        const map = {
            active:   '<span class="badge confirmed">アクティブ</span>',
            pending:  '<span class="badge pending">認証待ち</span>',
            inactive: '<span class="badge cancelled">無効</span>',
        };
        return map[status] || `<span class="badge">${status}</span>`;
    },

    // ──────────────────────────────────────────
    // Event listeners
    // ──────────────────────────────────────────
    setupEventListeners() {
        // Add device
        document.getElementById('addDeviceBtn')?.addEventListener('click', () => {
            this.showCreateModal();
        });

        // QR buttons
        document.querySelectorAll('.device-qr-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showQRCode(btn.dataset.id);
            });
        });

        // Edit buttons
        document.querySelectorAll('.device-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showEditModal(btn.dataset.id);
            });
        });

        // Delete buttons
        document.querySelectorAll('.device-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.confirmDelete(btn.dataset.id);
            });
        });

        // Row click → show detail/QR
        document.querySelectorAll('.device-row').forEach(row => {
            row.addEventListener('click', () => {
                this.showQRCode(row.dataset.deviceId);
            });
        });
    },

    // ──────────────────────────────────────────
    // Create Device Modal
    // ──────────────────────────────────────────
    showCreateModal() {
        const tableOptions = this.tables.map(t =>
            `<option value="${t.id}" data-number="${t.table_number}">テーブル ${t.table_number}${t.zone ? ` (${t.zone})` : ''}</option>`
        ).join('');

        const formContent = `
            <form id="deviceForm">
                <div class="form-group">
                    <label class="form-label">デバイスタイプ <span style="color:var(--danger)">*</span></label>
                    <select class="form-select" name="device_type" required>
                        <option value="">選択してください</option>
                        <option value="table-order">🍽️ テーブルオーダー</option>
                        <option value="kitchen">👨‍🍳 キッチン (KDS)</option>
                        <option value="pos">💰 POS</option>
                        <option value="checkin">📋 チェックイン</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">デバイス名 <span style="color:var(--danger)">*</span></label>
                    <input class="form-input" name="name" placeholder="例: iPad-テーブル1" required />
                </div>
                <div class="form-group device-table-group" style="display:none;">
                    <label class="form-label">テーブル <span style="color:var(--danger)">*</span></label>
                    <select class="form-select" name="table_id">
                        <option value="">テーブルを選択</option>
                        ${tableOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">備考</label>
                    <textarea class="form-textarea" name="notes" rows="2" placeholder="メモ（任意）"></textarea>
                </div>
            </form>
        `;

        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" id="cancelCreate">キャンセル</button>
            <button class="btn btn-primary" id="submitCreate">登録</button>
        `;

        Modal.open({ title: '新規デバイス登録', content: formContent, footer });

        // Show/hide table select based on device type
        const typeSelect = document.querySelector('#deviceForm select[name="device_type"]');
        const tableGroup = document.querySelector('.device-table-group');

        typeSelect.addEventListener('change', () => {
            const needTable = typeSelect.value === 'table-order';
            tableGroup.style.display = needTable ? 'block' : 'none';
            const tableSelect = tableGroup.querySelector('select');
            if (needTable) {
                tableSelect.setAttribute('required', '');
            } else {
                tableSelect.removeAttribute('required');
                tableSelect.value = '';
            }
        });

        footer.querySelector('#cancelCreate').addEventListener('click', () => Modal.close());
        footer.querySelector('#submitCreate').addEventListener('click', () => this.handleCreate());
    },

    async handleCreate() {
        const form = document.getElementById('deviceForm');
        const type = form.querySelector('[name="device_type"]').value;
        const name = form.querySelector('[name="name"]').value.trim();
        const tableSelect = form.querySelector('[name="table_id"]');
        const tableId = tableSelect.value || null;
        const tableNumber = tableId
            ? tableSelect.options[tableSelect.selectedIndex].dataset.number
            : null;
        const notes = form.querySelector('[name="notes"]').value.trim() || null;

        // Validation
        if (!type) { Toast.warning('入力エラー', 'デバイスタイプを選択してください'); return; }
        if (!name) { Toast.warning('入力エラー', 'デバイス名を入力してください'); return; }
        if (type === 'table-order' && !tableId) {
            Toast.warning('入力エラー', 'テーブルオーダーにはテーブルの選択が必須です');
            return;
        }

        try {
            const device = await api.createDevice({
                branch_code: api.branchCode,
                name,
                device_type: type,
                table_id: tableId,
                table_number: tableNumber || null,
                notes,
            });

            Modal.close();
            Toast.success('登録完了', `${name} を登録しました`);

            // Reload and show QR
            await this.loadData();
            this.render();
            this.setupEventListeners();
            this.showQRCode(device.id);
        } catch (error) {
            Toast.error('登録失敗', error.message);
        }
    },

    // ──────────────────────────────────────────
    // QR Code Display
    // ──────────────────────────────────────────
    showQRCode(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        const apiUrl = CONFIG.API_URL;
        const qrPayload = JSON.stringify({
            token: device.token,
            branch_code: device.branch_code,
            device_type: device.device_type,
            table_number: device.table_number,
            api_url: apiUrl,
        });

        const statusBadge = this._statusBadge(device.status);

        const modalContent = `
            <div class="qr-display">
                <div class="qr-container" id="qrCanvas"></div>
                <div class="qr-info">
                    <div class="detail-row">
                        <label>デバイス名</label>
                        <span>${device.name}</span>
                    </div>
                    <div class="detail-row">
                        <label>タイプ</label>
                        <span>${this._typeLabel(device.device_type)}</span>
                    </div>
                    ${device.table_number ? `
                    <div class="detail-row">
                        <label>テーブル</label>
                        <span>テーブル ${device.table_number}</span>
                    </div>` : ''}
                    <div class="detail-row">
                        <label>ステータス</label>
                        <span>${statusBadge}</span>
                    </div>
                    <div class="detail-row">
                        <label>作成日</label>
                        <span>${Format.datetime(device.created_at)}</span>
                    </div>
                    ${device.activated_at ? `
                    <div class="detail-row">
                        <label>認証日</label>
                        <span>${Format.datetime(device.activated_at)}</span>
                    </div>` : ''}
                    ${device.last_seen_at ? `
                    <div class="detail-row">
                        <label>最終接続</label>
                        <span>${Format.relativeTime(device.last_seen_at)}</span>
                    </div>` : ''}
                </div>
            </div>
            <style>
                .qr-display { text-align: center; }
                .qr-container {
                    display: inline-flex;
                    justify-content: center;
                    align-items: center;
                    background: white;
                    padding: 16px;
                    border-radius: var(--radius-md);
                    margin-bottom: 20px;
                }
                .qr-container canvas, .qr-container img { max-width: 220px; height: auto; }
                .qr-info { text-align: left; }
                .detail-row { display: flex; padding: 8px 0; border-bottom: 1px solid var(--bg-tertiary); }
                .detail-row label { width: 100px; color: var(--text-muted); flex-shrink: 0; }
                .detail-row span { flex: 1; }
            </style>
        `;

        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" onclick="Modal.close()">閉じる</button>
            <button class="btn btn-sm btn-secondary" id="regenerateTokenBtn" data-id="${device.id}">🔄 トークン再生成</button>
        `;

        Modal.open({ title: `📲 QRコード — ${device.name}`, content: modalContent, footer, size: 'md' });

        // Generate QR code after modal is open
        this._renderQR('qrCanvas', qrPayload);

        // Regenerate token
        footer.querySelector('#regenerateTokenBtn').addEventListener('click', async () => {
            Modal.confirm('トークン再生成', 'トークンを再生成すると、既存のQRコードは無効になります。続行しますか？', async () => {
                try {
                    await api.regenerateDeviceToken(device.id);
                    Toast.success('再生成完了', 'トークンを再生成しました');
                    await this.loadData();
                    this.render();
                    this.setupEventListeners();
                    this.showQRCode(device.id);
                } catch (error) {
                    Toast.error('エラー', error.message);
                }
            });
        });
    },

    /**
     * Render QR code into container using qrcode-generator (inline)
     */
    _renderQR(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Use the lightweight qrcode lib loaded from CDN
        if (typeof qrcode === 'undefined') {
            container.innerHTML = '<div style="color:#999;padding:20px;">QRライブラリ読み込み中...</div>';
            // Retry after script loads
            setTimeout(() => this._renderQR(containerId, data), 500);
            return;
        }

        try {
            const qr = qrcode(0, 'M');
            qr.addData(data);
            qr.make();
            container.innerHTML = qr.createSvgTag({ cellSize: 4, margin: 2 });
        } catch (e) {
            console.error('QR generation failed:', e);
            container.innerHTML = '<div style="color:var(--danger);">QR生成に失敗しました</div>';
        }
    },

    _typeLabel(type) {
        const map = {
            'table-order': '🍽️ テーブルオーダー',
            kitchen: '👨‍🍳 キッチン (KDS)',
            pos: '💰 POS',
            checkin: '📋 チェックイン',
        };
        return map[type] || type;
    },

    // ──────────────────────────────────────────
    // Edit Device Modal
    // ──────────────────────────────────────────
    showEditModal(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        const tableOptions = this.tables.map(t =>
            `<option value="${t.id}" data-number="${t.table_number}" ${t.id === device.table_id ? 'selected' : ''}>テーブル ${t.table_number}${t.zone ? ` (${t.zone})` : ''}</option>`
        ).join('');

        const isTableOrder = device.device_type === 'table-order';

        const formContent = `
            <form id="editDeviceForm">
                <div class="form-group">
                    <label class="form-label">デバイスタイプ</label>
                    <input class="form-input" value="${this._typeLabel(device.device_type)}" disabled />
                </div>
                <div class="form-group">
                    <label class="form-label">デバイス名</label>
                    <input class="form-input" name="name" value="${device.name}" required />
                </div>
                <div class="form-group device-table-group" style="display:${isTableOrder ? 'block' : 'none'};">
                    <label class="form-label">テーブル</label>
                    <select class="form-select" name="table_id">
                        <option value="">テーブルを選択</option>
                        ${tableOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">ステータス</label>
                    <select class="form-select" name="status">
                        <option value="active" ${device.status === 'active' ? 'selected' : ''}>アクティブ</option>
                        <option value="pending" ${device.status === 'pending' ? 'selected' : ''}>認証待ち</option>
                        <option value="inactive" ${device.status === 'inactive' ? 'selected' : ''}>無効</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">備考</label>
                    <textarea class="form-textarea" name="notes" rows="2">${device.notes || ''}</textarea>
                </div>
            </form>
        `;

        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" id="cancelEdit">キャンセル</button>
            <button class="btn btn-primary" id="submitEdit">更新</button>
        `;

        Modal.open({ title: `デバイス編集 — ${device.name}`, content: formContent, footer });

        footer.querySelector('#cancelEdit').addEventListener('click', () => Modal.close());
        footer.querySelector('#submitEdit').addEventListener('click', () => this.handleEdit(deviceId));
    },

    async handleEdit(deviceId) {
        const form = document.getElementById('editDeviceForm');
        const name = form.querySelector('[name="name"]').value.trim();
        const tableSelect = form.querySelector('[name="table_id"]');
        const tableId = tableSelect.value || null;
        const tableNumber = tableId
            ? tableSelect.options[tableSelect.selectedIndex].dataset.number
            : null;
        const status = form.querySelector('[name="status"]').value;
        const notes = form.querySelector('[name="notes"]').value.trim() || null;

        if (!name) { Toast.warning('入力エラー', 'デバイス名を入力してください'); return; }

        try {
            await api.updateDevice(deviceId, {
                name,
                status,
                table_id: tableId,
                table_number: tableNumber || null,
                notes,
            });

            Modal.close();
            Toast.success('更新完了', `${name} を更新しました`);
            await this.loadData();
            this.render();
            this.setupEventListeners();
        } catch (error) {
            Toast.error('更新失敗', error.message);
        }
    },

    // ──────────────────────────────────────────
    // Delete Device
    // ──────────────────────────────────────────
    confirmDelete(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        Modal.confirm(
            'デバイス削除',
            `「${device.name}」を削除しますか？この操作は取り消せません。`,
            async () => {
                try {
                    await api.deleteDevice(deviceId);
                    Toast.success('削除完了', `${device.name} を削除しました`);
                    await this.loadData();
                    this.render();
                    this.setupEventListeners();
                } catch (error) {
                    Toast.error('削除失敗', error.message);
                }
            }
        );
    },
};
