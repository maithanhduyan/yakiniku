/**
 * Device Authentication Module
 * Handles QR code scanning, token auth, and session persistence.
 *
 * Flow:
 *   1. On app boot → check localStorage for saved session
 *   2. If session exists → POST /api/devices/session/validate → if valid, skip auth
 *   3. If no session → show auth screen (scan QR or enter code)
 *   4. On QR/code submit → POST /api/devices/auth → bind fingerprint + get session
 *   5. Session stored in localStorage for 1 year
 *   6. Dashboard can logout device → session invalidated
 */

const DeviceAuth = {
    // Storage keys
    STORAGE_KEY: 'yakiniku_device_session',

    // Device info resolved from auth
    deviceInfo: null,

    // ── Fingerprint ──
    /**
     * Generate a stable device fingerprint from browser properties.
     * SHA-256 not available in sync context, so we use a simple hash.
     */
    generateFingerprint() {
        const raw = [
            navigator.userAgent,
            navigator.language,
            screen.width + 'x' + screen.height,
            screen.colorDepth,
            Intl.DateTimeFormat().resolvedOptions().timeZone,
            navigator.hardwareConcurrency || 0,
        ].join('|');

        // Simple hash (DJB2)
        let hash = 5381;
        for (let i = 0; i < raw.length; i++) {
            hash = ((hash << 5) + hash + raw.charCodeAt(i)) >>> 0;
        }
        return hash.toString(16).padStart(8, '0') + '_' + btoa(raw).slice(0, 48).replace(/[^a-zA-Z0-9]/g, '');
    },

    // ── Session storage ──
    getSavedSession() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            return data ? JSON.parse(data) : null;
        } catch {
            return null;
        }
    },

    saveSession(data) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
            session_token: data.session_token,
            device_id: data.device_id,
            device_type: data.device_type,
            branch_code: data.branch_code,
            table_id: data.table_id,
            table_number: data.table_number,
            config: data.config,
            expires_at: data.session_expires_at || data.expires_at,
            fingerprint: this.generateFingerprint(),
            saved_at: new Date().toISOString(),
        }));
    },

    clearSession() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.deviceInfo = null;
    },

    // ── Validation ──
    async validateSavedSession() {
        const session = this.getSavedSession();
        if (!session || !session.session_token) return false;

        // Quick client-side expiry check
        if (session.expires_at && new Date(session.expires_at) < new Date()) {
            this.clearSession();
            return false;
        }

        // Fingerprint mismatch (device changed)
        const currentFP = this.generateFingerprint();
        if (session.fingerprint && session.fingerprint !== currentFP) {
            this.clearSession();
            return false;
        }

        // Server-side validation
        try {
            const resp = await fetch(`${CONFIG.API_URL}/devices/session/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_token: session.session_token,
                    device_fingerprint: currentFP,
                }),
            });

            if (!resp.ok) {
                this.clearSession();
                return false;
            }

            const result = await resp.json();

            if (result.valid) {
                this.deviceInfo = {
                    device_id: result.device_id,
                    device_type: result.device_type,
                    branch_code: result.branch_code,
                    table_id: result.table_id,
                    table_number: result.table_number,
                    config: result.config,
                };
                return true;
            }

            this.clearSession();
            return false;
        } catch (e) {
            // Network error — trust saved session (offline mode)
            console.warn('[DeviceAuth] Validation failed (offline?), trusting saved session:', e.message);
            this.deviceInfo = {
                device_id: session.device_id,
                device_type: session.device_type,
                branch_code: session.branch_code,
                table_id: session.table_id,
                table_number: session.table_number,
                config: session.config,
            };
            return true;
        }
    },

    // ── Auth by token (QR code or manual input) ──
    async authenticateWithToken(token) {
        const fingerprint = this.generateFingerprint();

        const resp = await fetch(`${CONFIG.API_URL}/devices/auth`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, device_fingerprint: fingerprint }),
        });

        if (!resp.ok) {
            throw new Error(`Server error: ${resp.status}`);
        }

        const result = await resp.json();

        if (!result.authorized) {
            throw new Error(result.message || t('auth.invalidToken'));
        }

        // Save session
        this.saveSession(result);

        this.deviceInfo = {
            device_id: result.device_id,
            device_type: result.device_type,
            branch_code: result.branch_code,
            table_id: result.table_id,
            table_number: result.table_number,
            config: result.config,
        };

        return result;
    },

    // ── Extract token from QR payload ──
    parseQRPayload(rawText) {
        try {
            const data = JSON.parse(rawText);
            if (data.token) return data.token;
        } catch {
            // Not JSON — treat raw text as token
        }
        // Plain token string
        return rawText.trim();
    },

    // ── UI Controller ──
    showAuthScreen() {
        document.getElementById('deviceAuthScreen').classList.remove('hidden');
        // Hide everything else behind auth
        const welcome = document.getElementById('welcomeScreen');
        const app = document.getElementById('appContainer');
        const loading = document.getElementById('loadingOverlay');
        if (welcome) welcome.classList.add('hidden');
        if (app) app.classList.add('hidden');
        if (loading) loading.classList.add('hidden');
        this.setupAuthUI();
    },

    hideAuthScreen() {
        document.getElementById('deviceAuthScreen').classList.add('hidden');
    },

    setupAuthUI() {
        const submitBtn = document.getElementById('authSubmitBtn');
        const codeInput = document.getElementById('authCodeInput');
        const scanBtn = document.getElementById('authScanBtn');

        // Submit with button
        submitBtn.addEventListener('click', () => this.handleManualAuth());

        // Submit with Enter
        codeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleManualAuth();
        });

        // Open QR scanner
        scanBtn.addEventListener('click', () => this.openQRScanner());

        // Close QR scanner
        document.getElementById('qrScannerClose')?.addEventListener('click', () => this.closeQRScanner());
    },

    async handleManualAuth() {
        const input = document.getElementById('authCodeInput');
        const token = input.value.trim();

        if (!token) {
            this.showError(t('auth.enterCode'));
            return;
        }

        await this.performAuth(token);
    },

    async performAuth(token) {
        this.hideError();
        this.showLoading(true);

        try {
            await this.authenticateWithToken(token);
            this.showLoading(false);
            this.hideAuthScreen();

            // Apply device config and proceed to app
            this.applyDeviceConfig();

        } catch (error) {
            this.showLoading(false);
            this.showError(error.message);
        }
    },

    applyDeviceConfig() {
        if (!this.deviceInfo) return;

        const info = this.deviceInfo;

        // Override table ID and branch code from device config
        if (info.table_id) {
            localStorage.setItem('table_id', info.table_id);
            window._RESOLVED_TABLE_ID = info.table_id;
        }
        if (info.table_number) {
            localStorage.setItem('table_number', info.table_number);
        }
        if (info.branch_code) {
            // Override CONFIG.BRANCH_CODE (not frozen yet at this point)
            window._DEVICE_BRANCH_CODE = info.branch_code;
        }
    },

    showError(message) {
        const el = document.getElementById('authError');
        const textEl = document.getElementById('authErrorText');
        if (el && textEl) {
            textEl.textContent = message;
            el.classList.remove('hidden');
        }
    },

    hideError() {
        const el = document.getElementById('authError');
        if (el) el.classList.add('hidden');
    },

    showLoading(show) {
        const el = document.getElementById('authLoading');
        if (el) {
            el.classList.toggle('hidden', !show);
        }
        // Disable/enable form
        const submitBtn = document.getElementById('authSubmitBtn');
        const codeInput = document.getElementById('authCodeInput');
        if (submitBtn) submitBtn.disabled = show;
        if (codeInput) codeInput.disabled = show;
    },

    // ── QR Scanner (BarcodeDetector + jsQR fallback) ──
    _scannerStream: null,
    _scannerRAF: null,
    _detector: null,
    _useJsQR: false,

    async openQRScanner() {
        const overlay = document.getElementById('qrScannerOverlay');
        const video = document.getElementById('qrVideo');
        if (!overlay || !video) return;

        overlay.classList.remove('hidden');

        // Try BarcodeDetector first (native on iOS 15.4+, Chrome 83+)
        if (!this._detector && 'BarcodeDetector' in window) {
            try {
                this._detector = new BarcodeDetector({ formats: ['qr_code'] });
                this._useJsQR = false;
            } catch { /* not supported */ }
        }

        // Fallback to jsQR library
        if (!this._detector && typeof jsQR === 'function') {
            this._useJsQR = true;
            console.log('[QR Scanner] Using jsQR fallback');
        }

        // Neither available
        if (!this._detector && !this._useJsQR) {
            this.closeQRScanner();
            this.showError(t('auth.cameraNotSupported'));
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
            });
            this._scannerStream = stream;
            video.srcObject = stream;
            video.setAttribute('playsinline', 'true');
            await video.play();

            // Start scan loop
            this._scanFrame(video);

        } catch (err) {
            console.error('[QR Scanner] Camera error:', err);
            this.closeQRScanner();
            this.showError(t('auth.cameraError'));
        }
    },

    async _scanFrame(video) {
        if (!this._scannerStream) return;

        if (video.readyState >= video.HAVE_ENOUGH_DATA) {
            try {
                let rawValue = null;

                if (this._useJsQR) {
                    // jsQR fallback: draw video frame to canvas and decode
                    const canvas = document.getElementById('qrCanvas');
                    const ctx = canvas.getContext('2d', { willReadFrequently: true });
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const code = jsQR(imageData.data, imageData.width, imageData.height, {
                        inversionAttempts: 'dontInvert',
                    });
                    if (code) rawValue = code.data;
                } else {
                    // Native BarcodeDetector
                    const codes = await this._detector.detect(video);
                    if (codes.length > 0) rawValue = codes[0].rawValue;
                }

                if (rawValue) {
                    this.closeQRScanner();
                    const token = this.parseQRPayload(rawValue);
                    this.performAuth(token);
                    return;
                }
            } catch { /* detection failed — try again next frame */ }
        }

        this._scannerRAF = requestAnimationFrame(() => this._scanFrame(video));
    },

    closeQRScanner() {
        const overlay = document.getElementById('qrScannerOverlay');
        if (overlay) overlay.classList.add('hidden');

        if (this._scannerRAF) {
            cancelAnimationFrame(this._scannerRAF);
            this._scannerRAF = null;
        }
        if (this._scannerStream) {
            this._scannerStream.getTracks().forEach(track => track.stop());
            this._scannerStream = null;
        }
        const video = document.getElementById('qrVideo');
        if (video) video.srcObject = null;
    },
};
