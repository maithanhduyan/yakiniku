/**
 * Home Page - Dashboard Overview
 */
const HomePage = {
    stats: null,
    bookings: [],

    async init() {
        await this.loadData();
        this.render();
        this.setupWebSocket();
    },

    async loadData() {
        try {
            const [stats, bookings] = await Promise.all([
                api.getDashboardStats().catch(() => null),
                api.getTodayBookings().catch(() => [])
            ]);

            this.stats = stats;
            this.bookings = bookings;
        } catch (error) {
            console.error('Failed to load home data:', error);
        }
    },

    render() {
        const content = document.getElementById('pageContent');

        content.innerHTML = `
            <div class="home-page">
                ${this.renderStats()}

                <div class="grid-2">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">本日の予約</h3>
                            <span class="text-muted">${Format.date(new Date())}</span>
                        </div>
                        <div class="card-body" id="todayBookings">
                            ${this.renderTodayBookings()}
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">テーブル状況</h3>
                        </div>
                        <div class="card-body" id="tableOverview">
                            ${this.renderTableOverview()}
                        </div>
                    </div>
                </div>

                <div class="card" style="margin-top: 20px;">
                    <div class="card-header">
                        <h3 class="card-title">最近のアクティビティ</h3>
                    </div>
                    <div class="card-body" id="recentActivity">
                        ${this.renderRecentActivity()}
                    </div>
                </div>
            </div>
        `;
    },

    renderStats() {
        const stats = this.stats || {
            todayBookings: 0,
            pendingBookings: 0,
            availableTables: 0,
            totalGuests: 0
        };

        return `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="icon">📅</div>
                    <div class="value">${stats.todayBookings || this.bookings.length}</div>
                    <div class="label">本日の予約</div>
                </div>
                <div class="stat-card">
                    <div class="icon">⏳</div>
                    <div class="value">${stats.pendingBookings || this.bookings.filter(b => b.status === 'pending').length}</div>
                    <div class="label">保留中</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🪑</div>
                    <div class="value">${stats.availableTables || '-'}</div>
                    <div class="label">空きテーブル</div>
                </div>
                <div class="stat-card">
                    <div class="icon">👥</div>
                    <div class="value">${stats.totalGuests || this.bookings.reduce((sum, b) => sum + b.guests, 0)}</div>
                    <div class="label">本日の来客数</div>
                </div>
            </div>
        `;
    },

    renderTodayBookings() {
        if (this.bookings.length === 0) {
            return EmptyState.render('📅', '予約なし', '本日の予約はありません');
        }

        const sorted = [...this.bookings].sort((a, b) => a.time.localeCompare(b.time));

        return `
            <div class="timeline">
                ${sorted.slice(0, 8).map(booking => `
                    <div class="timeline-item">
                        <div class="timeline-time">${Format.time(booking.time)}</div>
                        <div class="timeline-content">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong>${booking.guest_name || '名前なし'}</strong>
                                ${Badge.create(booking.status)}
                            </div>
                            <div class="text-muted" style="font-size: 0.85rem; margin-top: 4px;">
                                ${Format.guests(booking.guests)} ${booking.note ? `・${booking.note.substring(0, 30)}...` : ''}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            ${sorted.length > 8 ? `<div class="text-center" style="margin-top: 12px;"><a href="#" data-page="bookings">すべて見る →</a></div>` : ''}
        `;
    },

    renderTableOverview() {
        return `
            <div class="table-summary">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center;">
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--success);">-</div>
                        <div class="text-muted">空席</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--danger);">-</div>
                        <div class="text-muted">使用中</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--warning);">-</div>
                        <div class="text-muted">予約済</div>
                    </div>
                </div>
            </div>
            <div style="margin-top: 16px; text-align: center;">
                <a href="#" data-page="tables" class="btn btn-secondary btn-sm">テーブル管理 →</a>
            </div>
        `;
    },

    renderRecentActivity() {
        return `
            <div class="text-muted text-center" style="padding: 20px;">
                WebSocket接続後にリアルタイムで表示されます
            </div>
        `;
    },

    setupWebSocket() {
        // Subscribe to booking updates
        ws.subscribe('bookings');

        ws.on('booking:created', (booking) => {
            this.bookings.push(booking);
            document.getElementById('todayBookings').innerHTML = this.renderTodayBookings();
            Toast.info('新規予約', `\${booking.guest_name}様 ${Format.time(booking.time)}`);
        });

        ws.on('booking:updated', (booking) => {
            const index = this.bookings.findIndex(b => b.id === booking.id);
            if (index !== -1) {
                this.bookings[index] = booking;
                document.getElementById('todayBookings').innerHTML = this.renderTodayBookings();
            }
        });
    }
};
