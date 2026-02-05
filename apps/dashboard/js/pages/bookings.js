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
            Toast.error('ã‚¨ãƒ©ãƒ¼', 'äºˆç´„ã®èª­ã¿è¾¼ã¿ã«å¤±æ•—ã—ã¾ã—ãŸ');
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
                                    <option value="">ã™ã¹ã¦ã®ã‚¹ãƒ†ãƒ¼ã‚¿ã‚¹</option>
                                    <option value="confirmed" ${this.filters.status === 'confirmed' ? 'selected' : ''}>ç¢ºå®š</option>
                                    <option value="pending" ${this.filters.status === 'pending' ? 'selected' : ''}>ä¿ç•™ä¸­</option>
                                    <option value="cancelled" ${this.filters.status === 'cancelled' ? 'selected' : ''}>ã‚­ãƒ£ãƒ³ã‚»ãƒ«</option>
                                </select>
                            </div>
                            <button class="btn btn-secondary btn-sm" id="refreshBtn">æ›´æ–°</button>
                            <div style="margin-left: auto;">
                                <button class="btn btn-primary" id="newBookingBtn">+ æ–°è¦äºˆç´„</button>
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
            return EmptyState.render('ðŸ“…', 'äºˆç´„ãŒã‚ã‚Šã¾ã›ã‚“', 'é¸æŠžã—ãŸæ—¥ä»˜ã®äºˆç´„ã¯ã‚ã‚Šã¾ã›ã‚“', 'äºˆç´„ã‚’è¿½åŠ ');
        }

        const sorted = [...this.bookings].sort((a, b) => a.time.localeCompare(b.time));

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>æ™‚é–“</th>
                        <th>ãŠå®¢æ§˜å</th>
                        <th>äººæ•°</th>
                        <th>é›»è©±ç•ªå·</th>
                        <th>ã‚¹ãƒ†ãƒ¼ã‚¿ã‚¹</th>
                        <th>å‚™è€ƒ</th>
                        <th>æ“ä½œ</th>
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
                                    <button class="btn btn-sm btn-secondary view-btn" data-id="${booking.id}">è©³ç´°</button>
                                    ${booking.status === 'pending' ?
                                        `<button class="btn btn-sm btn-primary confirm-btn" data-id="${booking.id}">ç¢ºå®š</button>` :
                                        ''}
                                    ${booking.status !== 'cancelled' ?
                                        `<button class="btn btn-sm btn-icon cancel-btn" data-id="${booking.id}" title="ã‚­ãƒ£ãƒ³ã‚»ãƒ«">âœ•</button>` :
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
            Toast.success('æ›´æ–°å®Œäº†', 'äºˆç´„ãƒªã‚¹ãƒˆã‚’æ›´æ–°ã—ã¾ã—ãŸ');
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
                Modal.confirm('ã‚­ãƒ£ãƒ³ã‚»ãƒ«ç¢ºèª', 'ã“ã®äºˆç´„ã‚’ã‚­ãƒ£ãƒ³ã‚»ãƒ«ã—ã¾ã™ã‹ï¼Ÿ', async () => {
                    await this.cancelBooking(btn.dataset.id);
                });
            });
        });
    },

    async showBookingDetail(id) {
        const booking = this.bookings.find(b => b.id === id);
        if (!booking) return;

        Modal.open({
            title: 'äºˆç´„è©³ç´°',
            content: `
                <div class="booking-detail">
                    <div class="detail-row">
                        <label>äºˆç´„ID</label>
                        <span>${booking.id}</span>
                    </div>
                    <div class="detail-row">
                        <label>æ—¥æ™‚</label>
                        <span>${Format.date(booking.date)} ${Format.time(booking.time)}</span>
                    </div>
                    <div class="detail-row">
                        <label>ãŠå®¢æ§˜å</label>
                        <span>${booking.guest_name || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>äººæ•°</label>
                        <span>${Format.guests(booking.guests)}</span>
                    </div>
                    <div class="detail-row">
                        <label>é›»è©±ç•ªå·</label>
                        <span>${Format.phone(booking.guest_phone)}</span>
                    </div>
                    <div class="detail-row">
                        <label>ãƒ¡ãƒ¼ãƒ«</label>
                        <span>${booking.guest_email || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>ã‚¹ãƒ†ãƒ¼ã‚¿ã‚¹</label>
                        ${Badge.create(booking.status)}
                    </div>
                    <div class="detail-row">
                        <label>äºˆç´„çµŒè·¯</label>
                        <span>${booking.source || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>å‚™è€ƒ</label>
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
            <button class="btn btn-secondary" id="modalCancel">ã‚­ãƒ£ãƒ³ã‚»ãƒ«</button>
            <button class="btn btn-primary" id="modalSave">ä¿å­˜</button>
        `;

        Modal.open({
            title: 'æ–°è¦äºˆç´„',
            content: `
                <form id="bookingForm">
                    <div class="form-group">
                        <label class="form-label">æ—¥ä»˜ *</label>
                        <input type="date" class="form-input" name="date" value="${this.filters.date}" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">æ™‚é–“ *</label>
                        <input type="time" class="form-input" name="time" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">äººæ•° *</label>
                        <input type="number" class="form-input" name="guests" min="1" max="50" value="2" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">ãŠå®¢æ§˜å</label>
                        <input type="text" class="form-input" name="guest_name">
                    </div>
                    <div class="form-group">
                        <label class="form-label">é›»è©±ç•ªå·</label>
                        <input type="tel" class="form-input" name="guest_phone">
                    </div>
                    <div class="form-group">
                        <label class="form-label">ãƒ¡ãƒ¼ãƒ«</label>
                        <input type="email" class="form-input" name="guest_email">
                    </div>
                    <div class="form-group">
                        <label class="form-label">å‚™è€ƒ</label>
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
                Toast.error('å…¥åŠ›ã‚¨ãƒ©ãƒ¼', 'å¿…é ˆé …ç›®ã‚’å…¥åŠ›ã—ã¦ãã ã•ã„');
                return;
            }

            try {
                await api.createBooking(data);
                Modal.close();
                Toast.success('äºˆç´„ä½œæˆ', 'äºˆç´„ã‚’ä½œæˆã—ã¾ã—ãŸ');
                await this.loadData();
                document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
                this.attachTableListeners();
            } catch (error) {
                Toast.error('ã‚¨ãƒ©ãƒ¼', error.message);
            }
        });
    },

    async confirmBooking(id) {
        try {
            await api.confirmBooking(id);
            Toast.success('ç¢ºå®šå®Œäº†', 'äºˆç´„ã‚’ç¢ºå®šã—ã¾ã—ãŸ');
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        } catch (error) {
            Toast.error('ã‚¨ãƒ©ãƒ¼', error.message);
        }
    },

    async cancelBooking(id) {
        try {
            await api.cancelBooking(id);
            Toast.success('ã‚­ãƒ£ãƒ³ã‚»ãƒ«å®Œäº†', 'äºˆç´„ã‚’ã‚­ãƒ£ãƒ³ã‚»ãƒ«ã—ã¾ã—ãŸ');
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        } catch (error) {
            Toast.error('ã‚¨ãƒ©ãƒ¼', error.message);
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



