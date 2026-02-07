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
            Toast.error(t('common.error'), t('bookings.loadFailed'));
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
                                    <option value="">${t('bookings.allStatus')}</option>
                                    <option value="confirmed" ${this.filters.status === 'confirmed' ? 'selected' : ''}>${t('bookings.confirmed')}</option>
                                    <option value="pending" ${this.filters.status === 'pending' ? 'selected' : ''}>${t('bookings.pending')}</option>
                                    <option value="cancelled" ${this.filters.status === 'cancelled' ? 'selected' : ''}>${t('bookings.cancelled')}</option>
                                </select>
                            </div>
                            <button class="btn btn-secondary btn-sm" id="refreshBtn">${t('common.refresh')}</button>
                            <div style="margin-left: auto;">
                                <button class="btn btn-primary" id="newBookingBtn">${t('bookings.newBooking')}</button>
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
            return EmptyState.render('📅', t('bookings.noBookings'), t('bookings.noBookingsDesc'), t('bookings.addBooking'));
        }

        const sorted = [...this.bookings].sort((a, b) => a.time.localeCompare(b.time));

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>${t('bookings.time')}</th>
                        <th>${t('bookings.guestName')}</th>
                        <th>${t('bookings.guests')}</th>
                        <th>${t('bookings.phone')}</th>
                        <th>${t('bookings.status')}</th>
                        <th>${t('bookings.notes')}</th>
                        <th>${t('bookings.actions')}</th>
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
                                    <button class="btn btn-sm btn-secondary view-btn" data-id="${booking.id}">${t('common.detail')}</button>
                                    ${booking.status === 'pending' ?
                                        `<button class="btn btn-sm btn-primary confirm-btn" data-id="${booking.id}">${t('bookings.confirm')}</button>` :
                                        ''}
                                    ${booking.status !== 'cancelled' ?
                                        `<button class="btn btn-sm btn-icon cancel-btn" data-id="${booking.id}" title="${t('common.cancel')}">✕</button>` :
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
            Toast.success(t('bookings.refreshed'), t('bookings.refreshedMessage'));
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
                Modal.confirm(t('bookings.cancelTitle'), t('bookings.cancelMessage'), async () => {
                    await this.cancelBooking(btn.dataset.id);
                });
            });
        });
    },

    async showBookingDetail(id) {
        const booking = this.bookings.find(b => b.id === id);
        if (!booking) return;

        Modal.open({
            title: t('bookings.detail'),
            content: `
                <div class="booking-detail">
                    <div class="detail-row">
                        <label>${t('bookings.bookingId')}</label>
                        <span>${booking.id}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('bookings.dateTime')}</label>
                        <span>${Format.date(booking.date)} ${Format.time(booking.time)}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('bookings.guestName')}</label>
                        <span>${booking.guest_name || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('bookings.guests')}</label>
                        <span>${Format.guests(booking.guests)}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('bookings.phone')}</label>
                        <span>${Format.phone(booking.guest_phone)}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('bookings.email')}</label>
                        <span>${booking.guest_email || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('bookings.status')}</label>
                        ${Badge.create(booking.status)}
                    </div>
                    <div class="detail-row">
                        <label>${t('bookings.source')}</label>
                        <span>${booking.source || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <label>${t('common.notes')}</label>
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
            <button class="btn btn-secondary" id="modalCancel">${t('common.cancel')}</button>
            <button class="btn btn-primary" id="modalSave">${t('common.save')}</button>
        `;

        Modal.open({
            title: t('bookings.createTitle'),
            content: `
                <form id="bookingForm">
                    <div class="form-group">
                        <label class="form-label">${t('bookings.dateLabel')} ${t('common.required')}</label>
                        <input type="date" class="form-input" name="date" value="${this.filters.date}" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">${t('bookings.timeLabel')} ${t('common.required')}</label>
                        <input type="time" class="form-input" name="time" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">${t('bookings.guestsLabel')} ${t('common.required')}</label>
                        <input type="number" class="form-input" name="guests" min="1" max="50" value="2" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">${t('bookings.nameLabel')}</label>
                        <input type="text" class="form-input" name="guest_name">
                    </div>
                    <div class="form-group">
                        <label class="form-label">${t('bookings.phoneLabel')}</label>
                        <input type="tel" class="form-input" name="guest_phone">
                    </div>
                    <div class="form-group">
                        <label class="form-label">${t('bookings.emailLabel')}</label>
                        <input type="email" class="form-input" name="guest_email">
                    </div>
                    <div class="form-group">
                        <label class="form-label">${t('bookings.notesLabel')}</label>
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
                Toast.error(t('toast.inputError'), t('bookings.requiredError'));
                return;
            }

            try {
                await api.createBooking(data);
                Modal.close();
                Toast.success(t('bookings.created'), t('bookings.createdMessage'));
                await this.loadData();
                document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
                this.attachTableListeners();
            } catch (error) {
                Toast.error(t('common.error'), error.message);
            }
        });
    },

    async confirmBooking(id) {
        try {
            await api.confirmBooking(id);
            Toast.success(t('bookings.confirmedToast'), t('bookings.confirmedMessage'));
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        } catch (error) {
            Toast.error(t('common.error'), error.message);
        }
    },

    async cancelBooking(id) {
        try {
            await api.cancelBooking(id);
            Toast.success(t('bookings.cancelledToast'), t('bookings.cancelledMessage'));
            await this.loadData();
            document.querySelector('.card-body[style*="padding: 0"]').innerHTML = this.renderTable();
            this.attachTableListeners();
        } catch (error) {
            Toast.error(t('common.error'), error.message);
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
