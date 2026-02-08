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
            Toast.error(t('common.error'), t('devices.loadFailed'));
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
            'table-order': { icon: '🍽️', label: t('devices.type.table-order').replace('🍽️ ', '') },
            kitchen:       { icon: '👨‍🍳', label: t('devices.type.kitchen').replace('👨‍🍳 ', '') },
            pos:           { icon: '💰', label: t('devices.type.pos').replace('💰 ', '') },
            checkin:       { icon: '📋', label: t('devices.type.checkin').replace('📋 ', '') },
        };

        content.innerHTML = `
            <div class="devices-page">
                <!-- Header actions -->
                <div class="page-actions">
                    <button class="btn btn-primary" id="addDeviceBtn">
                        ${t('devices.addDevice')}
                    </button>
                </div>

                <!-- Summary stats -->
                <div class="stats-grid" style="margin-bottom: 24px;">
                    <div class="stat-card">
                        <div class="icon" style="color: var(--success);">🟢</div>
                        <div class="value">${this.devices.filter(d => d.status === 'active').length}</div>
                        <div class="label">${t('devices.active')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--warning);">🟡</div>
                        <div class="value">${this.devices.filter(d => d.status === 'pending').length}</div>
                        <div class="label">${t('devices.pending')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon" style="color: var(--danger);">🔴</div>
                        <div class="value">${this.devices.filter(d => d.status === 'inactive').length}</div>
                        <div class="label">${t('devices.inactive')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">📱</div>
                        <div class="value">${this.devices.length}</div>
                        <div class="label">${t('devices.total')}</div>
                    </div>
                </div>

                <!-- Devices by type -->
                ${Object.entries(byType).map(([type, devices]) => `
                    <div class="card" style="margin-bottom: 20px;">
                        <div class="card-header">
                            <h3 class="card-title">${typeLabels[type].icon} ${typeLabels[type].label}</h3>
                            <span class="text-muted">${t('devices.unitCount', { count: devices.length })}</span>
                        </div>
                        <div class="card-body">
                            ${devices.length === 0
                                ? `<div class="text-muted text-center" style="padding:24px;">${t('devices.noDevices')}</div>`
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
            : t('devices.notConnected');
        const tablePart = device.table_number
            ? `<span class="device-table">${t('devices.table', { number: device.table_number })}</span>`
            : '';

        return `
            <div class="device-row" data-device-id="${device.id}">
                <div class="device-info">
                    <div class="device-name">
                        ${device.name}
                        ${device.has_session ? `<span class="badge confirmed" style="font-size:10px;margin-left:6px;">🔗 ${t('devices.connected')}</span>` : ''}
                    </div>
                    <div class="device-meta">
                        ${tablePart}
                        <span class="device-seen">${t('devices.lastSeen', { time: lastSeen })}</span>
                    </div>
                </div>
                <div class="device-actions">
                    ${statusBadge}
                    ${device.has_session ? `
                    <button class="btn btn-sm btn-warning device-logout-btn" data-id="${device.id}" title="${t('devices.logout')}">
                        🔓
                    </button>` : ''}
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
            active:   `<span class="badge confirmed">${t('devices.active')}</span>`,
            pending:  `<span class="badge pending">${t('devices.pending')}</span>`,
            inactive: `<span class="badge cancelled">${t('devices.inactive')}</span>`,
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

        // Logout buttons
        document.querySelectorAll('.device-logout-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.confirmLogout(btn.dataset.id);
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
        const tableOptions = this.tables.map(tbl =>
            `<option value="${tbl.id}" data-number="${tbl.table_number}">${t('devices.table', { number: tbl.table_number })}${tbl.zone ? ` (${tbl.zone})` : ''}</option>`
        ).join('');

        // Resolve current branch name from sidebar selector
        const branchSelect = document.getElementById('branchSelect');
        const branchName = branchSelect ? branchSelect.options[branchSelect.selectedIndex].text : api.branchCode;

        const formContent = `
            <form id="deviceForm">
                <div class="form-group">
                    <label class="form-label">${t('devices.branchLabel')}</label>
                    <input class="form-input" value="${branchName}" disabled />
                </div>
                <div class="form-group">
                    <label class="form-label">${t('devices.typeLabel')} <span style="color:var(--danger)">*</span></label>
                    <select class="form-select" name="device_type" required>
                        <option value="">${t('devices.typePlaceholder')}</option>
                        <option value="table-order">${t('devices.type.table-order')}</option>
                        <option value="kitchen">${t('devices.type.kitchen')}</option>
                        <option value="pos">${t('devices.type.pos')}</option>
                        <option value="checkin">${t('devices.type.checkin')}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">${t('devices.nameLabel')} <span style="color:var(--danger)">*</span></label>
                    <input class="form-input" name="name" placeholder="${t('devices.namePlaceholder')}" required />
                </div>
                <div class="form-group device-table-group" style="display:none;">
                    <label class="form-label">${t('devices.tableLabel')} <span style="color:var(--danger)">*</span></label>
                    <select class="form-select" name="table_id">
                        <option value="">${t('devices.tablePlaceholder')}</option>
                        ${tableOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">${t('devices.notesLabel')}</label>
                    <textarea class="form-textarea" name="notes" rows="2" placeholder="${t('devices.notesPlaceholder')}"></textarea>
                </div>
            </form>
        `;

        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" id="cancelCreate">${t('common.cancel')}</button>
            <button class="btn btn-primary" id="submitCreate">${t('devices.register')}</button>
        `;

        Modal.open({ title: t('devices.createTitle'), content: formContent, footer });

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
        if (!type) { Toast.warning(t('toast.inputError'), t('devices.typeRequired')); return; }
        if (!name) { Toast.warning(t('toast.inputError'), t('devices.nameRequired')); return; }
        if (type === 'table-order' && !tableId) {
            Toast.warning(t('toast.inputError'), t('devices.tableRequired'));
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
            Toast.success(t('devices.created'), t('devices.createdMessage', { name }));

            // Reload and show QR
            await this.loadData();
            this.render();
            this.setupEventListeners();
            this.showQRCode(device.id);
        } catch (error) {
            Toast.error(t('devices.createFailed'), error.message);
        }
    },

    // ──────────────────────────────────────────
    // QR Code Display
    // ──────────────────────────────────────────
    showQRCode(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        const apiUrl = CONFIG.API_URL;
        // NOTE: Do NOT include branch_name here — Japanese characters cause
        // qrcode-generator to use Shift-JIS encoding, which jsQR cannot
        // decode (returns empty string). Only ASCII-safe fields in QR payload.
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
                        <label>${t('devices.branchField')}</label>
                        <span>${device.branch_name || device.branch_code}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('devices.deviceName')}</label>
                        <span>${device.name}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('devices.typeField')}</label>
                        <span>${this._typeLabel(device.device_type)}</span>
                    </div>
                    ${device.table_number ? `
                    <div class="detail-row">
                        <label>${t('devices.tableLabel')}</label>
                        <span>${t('devices.table', { number: device.table_number })}</span>
                    </div>` : ''}
                    <div class="detail-row">
                        <label>${t('devices.statusField')}</label>
                        <span>${statusBadge}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('devices.createdAt')}</label>
                        <span>${Format.datetime(device.created_at)}</span>
                    </div>
                    ${device.activated_at ? `
                    <div class="detail-row">
                        <label>${t('devices.activatedAt')}</label>
                        <span>${Format.datetime(device.activated_at)}</span>
                    </div>` : ''}
                    ${device.last_seen_at ? `
                    <div class="detail-row">
                        <label>${t('devices.lastSeenAt')}</label>
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
            <button class="btn btn-secondary" onclick="Modal.close()">${t('common.close')}</button>
            <button class="btn btn-sm btn-secondary" id="regenerateTokenBtn" data-id="${device.id}">${t('devices.regenerate')}</button>
        `;

        Modal.open({ title: t('devices.qrTitle', { name: device.name }), content: modalContent, footer, size: 'md' });

        // Generate QR code after modal is open
        this._renderQR('qrCanvas', qrPayload);

        // Regenerate token
        footer.querySelector('#regenerateTokenBtn').addEventListener('click', async () => {
            Modal.confirm(t('devices.regenerateTitle'), t('devices.regenerateMessage'), async () => {
                try {
                    await api.regenerateDeviceToken(device.id);
                    Toast.success(t('devices.regenerated'), t('devices.regeneratedMessage'));
                    await this.loadData();
                    this.render();
                    this.setupEventListeners();
                    this.showQRCode(device.id);
                } catch (error) {
                    Toast.error(t('common.error'), error.message);
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
            container.innerHTML = `<div style="color:#999;padding:20px;">${t('devices.qrLoading')}</div>`;
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
            container.innerHTML = `<div style="color:var(--danger);">${t('devices.qrFailed')}</div>`;
        }
    },

    _typeLabel(type) {
        const map = {
            'table-order': t('devices.type.table-order'),
            kitchen: t('devices.type.kitchen'),
            pos: t('devices.type.pos'),
            checkin: t('devices.type.checkin'),
        };
        return map[type] || type;
    },

    // ──────────────────────────────────────────
    // Edit Device Modal
    // ──────────────────────────────────────────
    showEditModal(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        const tableOptions = this.tables.map(tbl =>
            `<option value="${tbl.id}" data-number="${tbl.table_number}" ${tbl.id === device.table_id ? 'selected' : ''}>${t('devices.table', { number: tbl.table_number })}${tbl.zone ? ` (${tbl.zone})` : ''}</option>`
        ).join('');

        const isTableOrder = device.device_type === 'table-order';

        const formContent = `
            <form id="editDeviceForm">
                <div class="form-group">
                    <label class="form-label">${t('devices.typeLabel')}</label>
                    <input class="form-input" value="${this._typeLabel(device.device_type)}" disabled />
                </div>
                <div class="form-group">
                    <label class="form-label">${t('devices.nameLabel')}</label>
                    <input class="form-input" name="name" value="${device.name}" required />
                </div>
                <div class="form-group device-table-group" style="display:${isTableOrder ? 'block' : 'none'};">
                    <label class="form-label">${t('devices.tableLabel')}</label>
                    <select class="form-select" name="table_id">
                        <option value="">${t('devices.tablePlaceholder')}</option>
                        ${tableOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">${t('common.status')}</label>
                    <select class="form-select" name="status">
                        <option value="active" ${device.status === 'active' ? 'selected' : ''}>${t('devices.statusActive')}</option>
                        <option value="pending" ${device.status === 'pending' ? 'selected' : ''}>${t('devices.statusPending')}</option>
                        <option value="inactive" ${device.status === 'inactive' ? 'selected' : ''}>${t('devices.statusInactive')}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">${t('devices.notesLabel')}</label>
                    <textarea class="form-textarea" name="notes" rows="2">${device.notes || ''}</textarea>
                </div>
            </form>
        `;

        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" id="cancelEdit">${t('common.cancel')}</button>
            <button class="btn btn-primary" id="submitEdit">${t('common.update')}</button>
        `;

        Modal.open({ title: t('devices.editTitle', { name: device.name }), content: formContent, footer });

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

        if (!name) { Toast.warning(t('toast.inputError'), t('devices.nameRequired')); return; }

        try {
            await api.updateDevice(deviceId, {
                name,
                status,
                table_id: tableId,
                table_number: tableNumber || null,
                notes,
            });

            Modal.close();
            Toast.success(t('devices.updated'), t('devices.updatedMessage', { name }));
            await this.loadData();
            this.render();
            this.setupEventListeners();
        } catch (error) {
            Toast.error(t('devices.updateFailed'), error.message);
        }
    },

    // ──────────────────────────────────────────
    // Delete Device
    // ──────────────────────────────────────────
    confirmDelete(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        Modal.confirm(
            t('devices.deleteTitle'),
            t('devices.deleteMessage', { name: device.name }),
            async () => {
                try {
                    await api.deleteDevice(deviceId);
                    Toast.success(t('devices.deleted'), t('devices.deletedMessage', { name: device.name }));
                    await this.loadData();
                    this.render();
                    this.setupEventListeners();
                } catch (error) {
                    Toast.error(t('devices.deleteFailed'), error.message);
                }
            }
        );
    },

    confirmLogout(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;

        Modal.confirm(
            t('devices.logoutTitle'),
            t('devices.logoutMessage', { name: device.name }),
            async () => {
                try {
                    await api.logoutDevice(deviceId);
                    Toast.success(t('devices.logoutSuccess'), t('devices.logoutSuccessMessage', { name: device.name }));
                    await this.loadData();
                    this.render();
                    this.setupEventListeners();
                } catch (error) {
                    Toast.error(t('devices.logoutFailed'), error.message);
                }
            }
        );
    },
};
