/**
 * Dashboard Notifications - Real-time SSE notifications
 */

class NotificationManager {
    constructor(branchCode = 'jinan') {
        this.branchCode = branchCode;
        this.eventSource = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;

        // Toast container
        this.createToastContainer();
    }

    createToastContainer() {
        if (document.getElementById('toast-container')) return;

        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }

    connect() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        const url = `/api/notifications/stream?branch_code=${this.branchCode}`;
        console.log('🔔 Connecting to notifications:', url);

        this.eventSource = new EventSource(url);

        this.eventSource.onopen = () => {
            console.log('🔔 Notification stream connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
        };

        this.eventSource.onmessage = (event) => {
            try {
                const notification = JSON.parse(event.data);
                this.handleNotification(notification);
            } catch (e) {
                console.warn('Failed to parse notification:', e);
            }
        };

        this.eventSource.addEventListener('connected', (event) => {
            console.log('🔔 SSE connected event received');
        });

        this.eventSource.onerror = (error) => {
            console.error('🔔 Notification stream error:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);

            // Attempt reconnect
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`🔔 Reconnecting... (attempt ${this.reconnectAttempts})`);
                setTimeout(() => this.connect(), this.reconnectDelay);
            }
        };
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            this.isConnected = false;
            console.log('🔔 Notification stream disconnected');
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('notification-status');
        if (indicator) {
            indicator.style.backgroundColor = connected ? '#22c55e' : '#ef4444';
            indicator.title = connected ? '通知接続中' : '通知切断';
        }
    }

    handleNotification(notification) {
        console.log('🔔 Received notification:', notification);

        // Play sound for important notifications
        if (notification.type === 'new_booking') {
            this.playSound();
        }

        // Show toast
        this.showToast(notification);

        // Handle specific notification types
        switch (notification.type) {
            case 'new_booking':
                this.handleNewBooking(notification);
                break;
            case 'booking_cancelled':
                this.handleBookingCancelled(notification);
                break;
            case 'booking_confirmed':
                this.handleBookingConfirmed(notification);
                break;
            case 'vip_arrived':
                this.handleVipArrived(notification);
                break;
        }
    }

    showToast(notification) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = 'notification-toast';

        // Determine color based on type
        let bgColor, borderColor;
        switch (notification.type) {
            case 'new_booking':
                bgColor = 'rgba(34, 197, 94, 0.15)';
                borderColor = '#22c55e';
                break;
            case 'booking_cancelled':
                bgColor = 'rgba(239, 68, 68, 0.15)';
                borderColor = '#ef4444';
                break;
            case 'booking_confirmed':
                bgColor = 'rgba(59, 130, 246, 0.15)';
                borderColor = '#3b82f6';
                break;
            case 'vip_arrived':
                bgColor = 'rgba(212, 175, 55, 0.15)';
                borderColor = '#d4af37';
                break;
            default:
                bgColor = 'rgba(107, 114, 128, 0.15)';
                borderColor = '#6b7280';
        }

        toast.style.cssText = `
            background-color: #252525;
            border-left: 4px solid ${borderColor};
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease-out;
            cursor: pointer;
        `;

        toast.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="font-weight: 600; margin-bottom: 0.25rem;">${notification.title}</div>
                    <div style="font-size: 0.875rem; color: #9ca3af;">${notification.message}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()"
                        style="background: none; border: none; color: #6b7280; cursor: pointer; font-size: 1.25rem; line-height: 1;">
                    ×
                </button>
            </div>
        `;

        // Click to navigate to booking detail
        if (notification.data?.booking_id) {
            toast.onclick = () => {
                window.location.href = `/admin/bookings?highlight=${notification.data.booking_id}`;
            };
        }

        container.appendChild(toast);

        // Auto remove after 8 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, 8000);
    }

    playSound() {
        // Create a simple beep sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 880; // A5 note
            oscillator.type = 'sine';
            gainNode.gain.value = 0.3;

            oscillator.start();

            // Fade out
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (e) {
            console.warn('Could not play notification sound:', e);
        }
    }

    handleNewBooking(notification) {
        // Could refresh the booking list via HTMX
        const bookingsList = document.getElementById('today-bookings');
        if (bookingsList && window.htmx) {
            htmx.trigger(bookingsList, 'refresh');
        }
    }

    handleBookingCancelled(notification) {
        // Update UI if booking is visible
    }

    handleBookingConfirmed(notification) {
        // Update UI if booking is visible
    }

    handleVipArrived(notification) {
        // Special handling for VIP
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    .notification-toast:hover {
        background-color: #2d2d2d !important;
    }
`;
document.head.appendChild(style);

// Auto-initialize on dashboard pages
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on a dashboard page
    if (window.location.pathname.startsWith('/admin')) {
        // Get branch code from page or default
        const branchSelect = document.querySelector('select[name="branch_code"]');
        const branchCode = branchSelect ? branchSelect.value : 'jinan';

        window.notificationManager = new NotificationManager(branchCode);
        window.notificationManager.connect();

        // Reconnect when page becomes visible again
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && !window.notificationManager.isConnected) {
                window.notificationManager.connect();
            }
        });
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.notificationManager) {
        window.notificationManager.disconnect();
    }
});
