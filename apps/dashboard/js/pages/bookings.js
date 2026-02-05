/**
 * Bookings Page - Booking Management
 */
const BookingsPage = {
    bookings: [],
    filters: {
        date: null,
        status: null
    },

    async init() {
        this.filters.date = new Date().toISOString().split('T')[0];
        await this.loadData();
        this.render();
        this.setupEventListeners();
        this.setupWebSocket();
    },

    async loadData() {
        try {
            Loading.show('#pageContent');
            this.bookings = await api.getBookings({
                date: this.filters.date,
                status: this.filters.status
            });
        } catch (error) {
            console.error('Failed to load bookings:', error);
            Toast.error('エラー', '予約の読み込みに失敗しました');
            this.bookings = [];
        }
    },

    render() {
        const content = document.getElementById('pageContent');

        content.innerHTML = `
            <div class="bookings-page">
                <!-- Filters -->
                <div class="card" style="margin-bottom: 20px;">
                    <div class="card-body" style="padding: 16px;">
                        <div class="filters" style="display: flex; gap: 16px; flex-wrap: wrap; align-items: center;">
                            <div class="form-group" style="margin: 0;">
                                <input type="date"
                                    class="form-input"
                                    id="filterDate"
                                    value="${this.filters.date}"
                                    style="width: 180px;">
                            </div>
                            <div class="form-group" style="margin: 0;">
                                <select class="form-select" id="filterStatus" style="width: 150px;">
                                    <option value="">すべてのステータス</option>
                                    <option value="confirmed" ${this.filters.status === 'confirmed' ? 'selected' : ''}>確定</option>
                                    <option value="pending" ${this.filters.status === 'pending' ? 'selected' : ''}>保留中</option>
                                    <option value="cancelled" ${this.filters.status === 'cancelled' ? 'selected' : ''}>キャンセル</option>
                                </select>
                            </div>
                            <button class="btn btn-secondary btn-sm" id="refreshBtn">更新</button>
                            <div style="margin-left: auto;">
                                <button class="btn btn-primary" id="newBookingBtn">+ 新規予約</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Bookings Table -->
                <div class="card">
                    <div class="card-body" style="padding: 0;">
                        ${this.renderTable()}
                    </div>
                </div>
            </div>
        `;
    },

    renderTable() {
        if (this.bookings.length === 0) {
            return EmptyState.render('📅', '予約がありません', '選択した日付の予約はありません', '予約を追加');
        }

        const sorted = [...this.bookings].sort((a, b) => a.time.localeCompare(b.time));

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>時間</th>
                        <th>お客様名</th>
                        <th>人数</th>
                        <th>電話番号</th>
                        <th>ステータス</th>
                        <th>備考</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${sorted.map(booking => `
                        <tr data-booking-id="${booking.id}">
                            <td><strong>${Format.time(booking.time)}</strong></td>
                            <td>${booking.guest_name || '-'}</td>
                            <td>${Format.guests(booking.guests)}</td>
                            <td>${Format.phone(booking.guest_phone)}</td>
                            <td>${Badge.create(booking.status)}</td>
                            <td class="text-muted">${booking.note ? booking.note.substring(0, 30) + '...' : '-'}</td>
                            <td>
                                <div style="display: flex; gap: 6px;">
                                    <button class="btn btn-sm btn-secondary view-btn" data-id="${booking.id}">詳細</button>
                                    ${booking.status === 'pending' ?
                                        `<button class="btn btn-sm btn-primary confirm-btn" data-id="${booking.id}">確定</button>` :
                                        ''}
                                    ${booking.status !== 'cancelled' ?
                                        `<button class="btn btn-sm btn-icon cancel-btn" data-id="${booking.id}" title="キャンセル">✕</button>` :
                                        ''}
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },

    setupEventListeners() {
        // Filter events
        document.getElementById('filterDate').addEventListener('change', async (e) => {
            this.filters.date = e.target.value;
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        });

        document.getElementById('filterStatus').addEventListener('change', async (e) => {
            this.filters.status = e.target.value || null;
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        });

        document.getElementById('refreshBtn').addEventListener('click', async () => {
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
            Toast.success('更新完了', '予約リストを更新しました');
        });

        document.getElementById('newBookingBtn').addEventListener('click', () => {
            this.showNewBookingModal();
        });

        this.attachTableListeners();
    },

    attachTableListeners() {
        // View buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => this.showBookingDetail(btn.dataset.id));
        });

        // Confirm buttons
        document.querySelectorAll('.confirm-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                await this.confirmBooking(btn.dataset.id);
            });
        });

        // Cancel buttons
        document.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                Modal.confirm('キャンセル確認', 'この予約をキャンセルしますか？', async () => {
                    await this.cancelBooking(btn.dataset.id);
                });
            });
        });
    },

    async showBookingDetail(id) {
        const booking = this.bookings.find(b => b.id === id);
        if (!booking) return;

        Modal.open({
            title: '予約詳細',
            content: `
                <div class="booking-detail">
                    <div class="detail-row">
                        <label>予約ID</label>
                        <span>${booking.id}</span>
                    </div>
                    <div class="detail-row">
                        <label>日時</label>
                        <span>${Format.date(booking.date)} ${Format.time(booking.time)}</span>
                    </div>
                    <div class="detail-row">
                        <label>お客様名</label>
                        <span>${booking.guest_name || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>人数</label>
                        <span>${Format.guests(booking.guests)}</span>
                    </div>
                    <div class="detail-row">
                        <label>電話番号</label>
                        <span>${Format.phone(booking.guest_phone)}</span>
                    </div>
                    <div class="detail-row">
                        <label>メール</label>
                        <span>${booking.guest_email || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>ステータス</label>
                        ${Badge.create(booking.status)}
                    </div>
                    <div class="detail-row">
                        <label>予約経路</label>
                        <span>${booking.source || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>備考</label>
                        <span>${booking.note || '-'}</span>
                    </div>
                </div>
                <style>
                    .detail-row { display: flex; padding: 10px 0; border-bottom: 1px solid var(--bg-tertiary); }
                    .detail-row label { width: 120px; color: var(--text-muted); }
                    .detail-row span { flex: 1; }
                </style>
            `,
            size: 'md'
        });
    },

    showNewBookingModal() {
        const footer = document.createElement('div');
        footer.innerHTML = `
            <button class="btn btn-secondary" id="modalCancel">キャンセル</button>
            <button class="btn btn-primary" id="modalSave">保存</button>
        `;

        Modal.open({
            title: '新規予約',
            content: `
                <form id="bookingForm">
                    <div class="form-group">
                        <label class="form-label">日付 *</label>
                        <input type="date" class="form-input" name="date" value="${this.filters.date}" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">時間 *</label>
                        <input type="time" class="form-input" name="time" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">人数 *</label>
                        <input type="number" class="form-input" name="guests" min="1" max="50" value="2" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">お客様名</label>
                        <input type="text" class="form-input" name="guest_name">
                    </div>
                    <div class="form-group">
                        <label class="form-label">電話番号</label>
                        <input type="tel" class="form-input" name="guest_phone">
                    </div>
                    <div class="form-group">
                        <label class="form-label">メール</label>
                        <input type="email" class="form-input" name="guest_email">
                    </div>
                    <div class="form-group">
                        <label class="form-label">備考</label>
                        <textarea class="form-textarea" name="note" rows="3"></textarea>
                    </div>
                </form>
            `,
            footer,
            size: 'md'
        });

        footer.querySelector('#modalCancel').addEventListener('click', () => Modal.close());
        footer.querySelector('#modalSave').addEventListener('click', async () => {
            const form = document.getElementById('bookingForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            if (!data.date || !data.time || !data.guests) {
                Toast.error('入力エラー', '必須項目を入力してください');
                return;
            }

            try {
                await api.createBooking(data);
                Modal.close();
                Toast.success('予約作成', '予約を作成しました');
                await this.loadData();
                document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
                this.attachTableListeners();
            } catch (error) {
                Toast.error('エラー', error.message);
            }
        });
    },

    async confirmBooking(id) {
        try {
            await api.confirmBooking(id);
            Toast.success('確定完了', '予約を確定しました');
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        } catch (error) {
            Toast.error('エラー', error.message);
        }
    },

    async cancelBooking(id) {
        try {
            await api.cancelBooking(id);
            Toast.success('キャンセル完了', '予約をキャンセルしました');
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        } catch (error) {
            Toast.error('エラー', error.message);
        }
    },

    setupWebSocket() {
        ws.subscribe('bookings');

        ws.on('booking:created', async () => {
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        });

        ws.on('booking:updated', async () => {
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        });
    }
};
