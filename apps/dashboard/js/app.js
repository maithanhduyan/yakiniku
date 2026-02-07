/**
 * Dashboard Main Application
 * Handles routing, navigation, and initialization
 */
class DashboardApp {
    constructor() {
        this.currentPage = 'home';
        this.pages = {
            home: HomePage,
            bookings: BookingsPage,
            tables: TablesPage,
            customers: CustomersPage,
            devices: DevicesPage
        };
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('🍖 Dashboard initializing...');

        // Initialize i18n
        I18N.init();

        // Initialize components
        initComponents();

        // Setup navigation
        this.setupNavigation();

        // Setup sidebar toggle
        this.setupSidebar();

        // Setup notification panel
        this.setupNotifications();

        // Setup branch selector
        this.setupBranchSelector();

        // Update date display
        this.updateDateDisplay();

        // Connect WebSocket
        ws.connect();

        // Load initial page
        await this.navigateTo('home');

        console.log('✓ Dashboard ready');
    }

    /**
     * Setup navigation handlers
     */
    setupNavigation() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', async (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                if (page) {
                    await this.navigateTo(page);
                }
            });
        });

        // Handle clicks on page links
        document.addEventListener('click', async (e) => {
            const link = e.target.closest('[data-page]');
            if (link && !link.classList.contains('nav-item')) {
                e.preventDefault();
                await this.navigateTo(link.dataset.page);
            }
        });
    }

    /**
     * Navigate to a page
     */
    async navigateTo(page) {
        if (!this.pages[page]) {
            console.warn(`Page not found: ${page}`);
            return;
        }

        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });

        // Update page title
        const titleKey = `page.${page}`;
        document.getElementById('pageTitle').textContent = t(titleKey);

        // Close mobile sidebar
        document.getElementById('sidebar').classList.remove('open');

        // Load page
        this.currentPage = page;
        Loading.show('#pageContent');

        try {
            await this.pages[page].init();
        } catch (error) {
            console.error(`Failed to load page ${page}:`, error);
            document.getElementById('pageContent').innerHTML =
                EmptyState.render('❌', t('common.error'), t('common.loadFailed'));
        }
    }

    /**
     * Setup sidebar toggle
     */
    setupSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');

        // Desktop toggle
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
        });

        // Restore state
        if (localStorage.getItem('sidebar_collapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }

        // Mobile toggle
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Close on click outside (mobile)
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 1024 &&
                sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                e.target !== mobileMenuBtn) {
                sidebar.classList.remove('open');
            }
        });
    }

    /**
     * Setup notification panel
     */
    setupNotifications() {
        const notificationBtn = document.getElementById('notificationBtn');
        const notificationPanel = document.getElementById('notificationPanel');
        const closeNotifications = document.getElementById('closeNotifications');

        notificationBtn.addEventListener('click', () => {
            notificationPanel.classList.toggle('open');
        });

        closeNotifications.addEventListener('click', () => {
            notificationPanel.classList.remove('open');
        });

        // WebSocket notification handler
        ws.on('notification', (data) => {
            this.addNotification(data);
            Toast.info(data.title, data.message);
        });
    }

    /**
     * Add notification to panel
     */
    addNotification(notification) {
        const list = document.getElementById('notificationList');
        const badge = document.getElementById('notificationBadge');

        const item = document.createElement('div');
        item.className = 'notification-item unread';
        item.innerHTML = `
            <div class="title">${notification.title}</div>
            <div class="message">${notification.message}</div>
            <div class="time">${Format.relativeTime(notification.timestamp || new Date())}</div>
        `;

        list.insertBefore(item, list.firstChild);

        // Update badge
        const currentCount = parseInt(badge.textContent) || 0;
        badge.textContent = currentCount + 1;

        // Mark as read on click
        item.addEventListener('click', () => {
            item.classList.remove('unread');
            const newCount = parseInt(badge.textContent) - 1;
            badge.textContent = newCount > 0 ? newCount : '';
        });
    }

    /**
     * Setup branch selector
     */
    setupBranchSelector() {
        const branchSelect = document.getElementById('branchSelect');

        // Restore saved branch
        const savedBranch = localStorage.getItem('selected_branch');
        if (savedBranch) {
            branchSelect.value = savedBranch;
            api.setBranch(savedBranch);
        }

        branchSelect.addEventListener('change', async () => {
            const branch = branchSelect.value;
            localStorage.setItem('selected_branch', branch);

            // Update API and WebSocket
            api.setBranch(branch);
            ws.changeBranch(branch);

            // Reload current page
            Toast.info(t('toast.branchChanged'), t('toast.branchSwitched', { name: branchSelect.options[branchSelect.selectedIndex].text }));
            await this.navigateTo(this.currentPage);
        });
    }

    /**
     * Update date display
     */
    updateDateDisplay() {
        const dateEl = document.getElementById('currentDate');
        const formatDate = () => {
            const now = new Date();
            dateEl.textContent = now.toLocaleDateString(I18N.dateLocale, {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'short'
            });
        };
        formatDate();
        setInterval(formatDate, 60000);
    }

    /**
     * Called when language is toggled — re-render current page
     */
    async onLanguageChange() {
        // Update page title
        const titleKey = `page.${this.currentPage}`;
        document.getElementById('pageTitle').textContent = t(titleKey);

        // Update date display locale
        this.updateDateDisplay();

        // Re-render current page with new language
        try {
            await this.pages[this.currentPage].init();
        } catch (error) {
            console.error('Failed to re-render page:', error);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new DashboardApp();
    window.dashboardApp = app;
    app.init();
});

// Add slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .grid-2 {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 20px;
    }
    .text-muted { color: var(--text-muted); }
    .text-center { text-align: center; }
    @media (max-width: 768px) {
        .grid-2 {
            grid-template-columns: 1fr;
        }
    }
`;
document.head.appendChild(style);
