/**
 * API Client for Dashboard
 * REST API wrapper with authentication
 */
class APIClient {
    constructor() {
        this.baseUrl = CONFIG.API_URL;
        this.branchCode = CONFIG.DEFAULT_BRANCH;
    }

    /**
     * Set branch code for requests
     */
    setBranch(branchCode) {
        this.branchCode = branchCode;
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const headers = {
            'Content-Type': 'application/json',
            'X-Branch-Code': this.branchCode,
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new APIError(response.status, error.detail || 'Request failed');
            }

            // Return null for 204 No Content
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError(0, error.message || 'Network error');
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                searchParams.append(key, value);
            }
        });

        const queryString = searchParams.toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;

        return this.request(url, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * PATCH request
     */
    async patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // ============================================
    // Bookings API
    // ============================================

    async getBookings(params = {}) {
        return this.get('/api/bookings', {
            branch_code: this.branchCode,
            ...params
        });
    }

    async getBooking(id) {
        return this.get(`/api/bookings/${id}`);
    }

    async createBooking(data) {
        return this.post('/api/bookings', {
            branch_code: this.branchCode,
            ...data
        });
    }

    async updateBooking(id, data) {
        return this.patch(`/api/bookings/${id}`, data);
    }

    async cancelBooking(id) {
        return this.patch(`/api/bookings/${id}`, { status: 'cancelled' });
    }

    async confirmBooking(id) {
        return this.patch(`/api/bookings/${id}`, { status: 'confirmed' });
    }

    // ============================================
    // Tables API
    // ============================================

    async getTables(params = {}) {
        return this.get('/api/tables', {
            branch_code: this.branchCode,
            ...params
        });
    }

    async getTable(id) {
        return this.get(`/api/tables/${id}`);
    }

    async updateTableStatus(id, status) {
        return this.patch(`/api/tables/${id}`, { status });
    }

    async assignTable(bookingId, tableId) {
        return this.post(`/api/bookings/${bookingId}/assign-table`, {
            table_id: tableId
        });
    }

    // ============================================
    // Customers API
    // ============================================

    async getCustomers(params = {}) {
        return this.get('/api/customers', {
            branch_code: this.branchCode,
            ...params
        });
    }

    async getCustomer(id) {
        return this.get(`/api/customers/${id}`);
    }

    async searchCustomers(query) {
        return this.get('/api/customers/search', { q: query });
    }

    async getCustomerPreferences(customerId) {
        return this.get(`/api/customers/${customerId}/preferences`);
    }

    // ============================================
    // Dashboard Stats API
    // ============================================

    async getDashboardStats() {
        return this.get('/api/dashboard/stats', {
            branch_code: this.branchCode
        });
    }

    async getTodayBookings() {
        const today = new Date().toISOString().split('T')[0];
        return this.get('/api/bookings', {
            branch_code: this.branchCode,
            date: today
        });
    }

    // ============================================
    // Devices API
    // ============================================

    async getDevices(params = {}) {
        return this.get('/api/devices/', {
            branch_code: this.branchCode,
            ...params
        });
    }

    async getDevice(id) {
        return this.get(`/api/devices/${id}`);
    }

    async createDevice(data) {
        return this.post('/api/devices/', data);
    }

    async updateDevice(id, data) {
        return this.patch(`/api/devices/${id}`, data);
    }

    async deleteDevice(id) {
        return this.delete(`/api/devices/${id}`);
    }

    async regenerateDeviceToken(id) {
        return this.post(`/api/devices/${id}/regenerate-token`, {});
    }

    async logoutDevice(id) {
        return this.post(`/api/devices/${id}/logout`, {});
    }
}

/**
 * API Error class
 */
class APIError extends Error {
    constructor(status, message) {
        super(message);
        this.name = 'APIError';
        this.status = status;
    }
}

// Create singleton instance
const api = new APIClient();
