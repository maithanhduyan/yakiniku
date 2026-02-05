/**
 * API Client for Table Order App
 * REST API wrapper with authentication
 */

class APIClient {
    constructor() {
        this.baseUrl = CONFIG.API_BASE;
        this.branchCode = CONFIG.BRANCH_CODE;
    }
}
