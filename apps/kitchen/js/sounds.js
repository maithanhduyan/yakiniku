/**
 * Kitchen Sound System — Gentle Audio Feedback
 * Web Audio API synthesized sounds — no audio files needed.
 *
 * Design principle: 温かい (warm) — sounds a kitchen team hears
 * hundreds of times a day should feel natural, not alarming.
 *
 * Available sounds:
 *   🔔  newOrder   — Soft bell ding (two-tone chime)
 *   ✅  complete   — Gentle positive confirmation
 *   ❌  cancel     — Subtle low acknowledgment
 *   📋  notify     — Light tap for general notifications
 */

class KitchenSounds {
    constructor() {
        this._ctx = null;
        this._enabled = true;
        this._volume = 0.35;  // Default volume (0–1), kept low for comfort
    }

    /**
     * Lazy-init AudioContext (must happen after user gesture on iOS/Chrome)
     */
    _getContext() {
        if (!this._ctx) {
            this._ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
        // Resume if suspended (autoplay policy)
        if (this._ctx.state === 'suspended') {
            this._ctx.resume();
        }
        return this._ctx;
    }

    /** Master enable / disable */
    get enabled() { return this._enabled; }
    set enabled(v) { this._enabled = !!v; }

    /** Volume 0–1 */
    get volume() { return this._volume; }
    set volume(v) { this._volume = Math.max(0, Math.min(1, v)); }

    // ================================================================
    //  Sound Recipes
    // ================================================================

    /**
     * 🔔 New Order — Warm two-tone bell chime
     * Two soft sine tones a fifth apart, gentle attack, slow fade.
     * Inspired by Japanese wind chimes (風鈴).
     */
    newOrder() {
        if (!this._enabled) return;
        const ctx = this._getContext();
        const now = ctx.currentTime;
        const vol = this._volume;

        // --- Tone 1: Root note (E5 ~659 Hz) ---
        this._bell(ctx, now, 659.25, vol * 0.5, 0.8);

        // --- Tone 2: Fifth above (B5 ~987 Hz), slightly delayed ---
        this._bell(ctx, now + 0.12, 987.77, vol * 0.35, 0.6);

        // --- Subtle shimmer overtone ---
        this._bell(ctx, now + 0.05, 1318.5, vol * 0.1, 0.4);
    }

    /**
     * ✅ Item Complete — Soft upward chime (positive feeling)
     * Quick ascending two-note phrase.
     */
    complete() {
        if (!this._enabled) return;
        const ctx = this._getContext();
        const now = ctx.currentTime;
        const vol = this._volume;

        // G5 → C6 (perfect fourth up — sounds resolved & happy)
        this._tone(ctx, now, 783.99, vol * 0.3, 0.25, 'sine');
        this._tone(ctx, now + 0.1, 1046.50, vol * 0.25, 0.35, 'sine');
    }

    /**
     * ❌ Cancel — Subtle low acknowledgment
     * Single muted tone, not alarming.
     */
    cancel() {
        if (!this._enabled) return;
        const ctx = this._getContext();
        const now = ctx.currentTime;
        const vol = this._volume;

        // Low C4 with quick fade — a quiet "ok, noted"
        this._tone(ctx, now, 261.63, vol * 0.2, 0.3, 'triangle');
    }

    /**
     * 📋 Notify — Light tap for general notifications
     * Very brief, like a soft woodblock tap.
     */
    notify() {
        if (!this._enabled) return;
        const ctx = this._getContext();
        const now = ctx.currentTime;
        const vol = this._volume;

        this._tone(ctx, now, 1200, vol * 0.15, 0.08, 'sine');
        this._tone(ctx, now, 600, vol * 0.1, 0.12, 'triangle');
    }

    // ================================================================
    //  Primitives
    // ================================================================

    /**
     * Bell-like tone: sine + harmonics with exponential decay
     * Mimics a small bell / wind chime resonance.
     */
    _bell(ctx, startTime, freq, volume, duration) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, startTime);

        // Gentle attack → smooth exponential decay
        gain.gain.setValueAtTime(0, startTime);
        gain.gain.linearRampToValueAtTime(volume, startTime + 0.015);   // 15ms attack
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + duration + 0.05);
    }

    /**
     * Simple tone with envelope
     */
    _tone(ctx, startTime, freq, volume, duration, type = 'sine') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, startTime);

        // Soft attack → decay
        gain.gain.setValueAtTime(0, startTime);
        gain.gain.linearRampToValueAtTime(volume, startTime + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + duration + 0.05);
    }
}

// Singleton
const Sounds = new KitchenSounds();
