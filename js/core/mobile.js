/**
 * Mobile Optimization Module
 * Navigation, gestures, responsive layouts, offline mode, push notifications
 */

// ─── GESTURE HANDLER ───
export class GestureHandler {
  constructor(element) {
    this.el = typeof element === 'string' ? document.querySelector(element) : element;
    this.startX = 0;
    this.startY = 0;
    this.threshold = 50;
    this.handlers = {};
    if (this.el) this._init();
  }

  on(gesture, callback) { this.handlers[gesture] = callback; return this; }

  _init() {
    this.el.addEventListener('touchstart', (e) => {
      this.startX = e.touches[0].clientX;
      this.startY = e.touches[0].clientY;
    }, { passive: true });

    this.el.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - this.startX;
      const dy = e.changedTouches[0].clientY - this.startY;
      const absDx = Math.abs(dx);
      const absDy = Math.abs(dy);

      if (absDx < this.threshold && absDy < this.threshold) return;

      if (absDx > absDy) {
        this._emit(dx > 0 ? 'swipeRight' : 'swipeLeft');
      } else {
        this._emit(dy > 0 ? 'swipeDown' : 'swipeUp');
      }
    }, { passive: true });

    // Pull-to-refresh
    let pullStartY = 0;
    let pulling = false;
    this.el.addEventListener('touchstart', (e) => {
      if (this.el.scrollTop === 0) { pullStartY = e.touches[0].clientY; pulling = true; }
    }, { passive: true });

    this.el.addEventListener('touchmove', (e) => {
      if (!pulling) return;
      const dy = e.touches[0].clientY - pullStartY;
      if (dy > 80) { this._emit('pullToRefresh'); pulling = false; }
    }, { passive: true });

    this.el.addEventListener('touchend', () => { pulling = false; }, { passive: true });
  }

  _emit(gesture) { if (this.handlers[gesture]) this.handlers[gesture](); }
}


// ─── RESPONSIVE NAVIGATION ───
export class MobileNav {
  constructor() {
    this.currentTab = 'dashboard-view';
    this._setupHapticFeedback();
    this._setupSwipeNavigation();
  }

  _setupSwipeNavigation() {
    const main = document.querySelector('.app-body');
    if (!main) return;

    const gesture = new GestureHandler(main);
    const tabs = ['dashboard-view', 'company-view', 'markets-view', 'learn-view', 'predictor-view'];

    gesture.on('swipeLeft', () => {
      const idx = tabs.indexOf(this.currentTab);
      if (idx < tabs.length - 1) this._navigateTo(tabs[idx + 1]);
    });

    gesture.on('swipeRight', () => {
      const idx = tabs.indexOf(this.currentTab);
      if (idx > 0) this._navigateTo(tabs[idx - 1]);
    });

    gesture.on('pullToRefresh', () => {
      document.dispatchEvent(new CustomEvent('app:refresh'));
    });
  }

  _navigateTo(tabId) {
    this.currentTab = tabId;
    const tab = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
    if (tab) tab.click();
  }

  _setupHapticFeedback() {
    document.querySelectorAll('.mobile-nav-item, .btn').forEach(el => {
      el.addEventListener('touchstart', () => {
        if (navigator.vibrate) navigator.vibrate(10);
      }, { passive: true });
    });
  }
}


// ─── OFFLINE MODE ───
export class OfflineManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.pendingActions = [];
    this._init();
  }

  _init() {
    window.addEventListener('online', () => { this.isOnline = true; this._syncPending(); this._showStatus('Back online'); });
    window.addEventListener('offline', () => { this.isOnline = false; this._showStatus('You are offline'); });
    this._registerServiceWorker();
  }

  cacheData(key, data) {
    try { localStorage.setItem(`ps_cache_${key}`, JSON.stringify({ data, timestamp: Date.now() })); }
    catch (e) { console.warn('Cache storage full'); }
  }

  getCachedData(key, maxAgeMs = 300000) {
    try {
      const raw = localStorage.getItem(`ps_cache_${key}`);
      if (!raw) return null;
      const { data, timestamp } = JSON.parse(raw);
      if (Date.now() - timestamp > maxAgeMs) return null;
      return data;
    } catch { return null; }
  }

  queueAction(action) {
    this.pendingActions.push({ ...action, timestamp: Date.now() });
    localStorage.setItem('ps_pending_actions', JSON.stringify(this.pendingActions));
  }

  _syncPending() {
    const pending = JSON.parse(localStorage.getItem('ps_pending_actions') || '[]');
    if (!pending.length) return;
    pending.forEach(action => {
      fetch(action.url, { method: action.method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(action.body) })
        .catch(() => {});
    });
    localStorage.removeItem('ps_pending_actions');
    this.pendingActions = [];
  }

  _showStatus(message) {
    const banner = document.createElement('div');
    banner.className = `offline-banner ${this.isOnline ? 'online' : 'offline'}`;
    banner.textContent = message;
    banner.setAttribute('role', 'alert');
    document.body.prepend(banner);
    setTimeout(() => banner.remove(), 3000);
  }

  _registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  }
}


// ─── PUSH NOTIFICATIONS ───
export class PushNotifications {
  constructor() {
    this.permission = Notification.permission;
  }

  async requestPermission() {
    if (!('Notification' in window)) return false;
    const result = await Notification.requestPermission();
    this.permission = result;
    return result === 'granted';
  }

  async subscribe(userId) {
    if (this.permission !== 'granted') {
      const granted = await this.requestPermission();
      if (!granted) return null;
    }

    if (!('serviceWorker' in navigator)) return null;

    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: this._urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
    });

    // Send subscription to backend
    await fetch('/api/notifications/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, subscription })
    }).catch(() => {});

    return subscription;
  }

  showLocal(title, options = {}) {
    if (this.permission !== 'granted') return;
    new Notification(title, {
      icon: '/favicon.ico',
      badge: '/badge.png',
      vibrate: [200, 100, 200],
      ...options
    });
  }

  _urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));
  }
}


// ─── RESPONSIVE LAYOUT MANAGER ───
export class ResponsiveLayout {
  constructor() {
    this.breakpoint = this._getCurrentBreakpoint();
    this._init();
  }

  _init() {
    window.addEventListener('resize', this._debounce(() => {
      const newBp = this._getCurrentBreakpoint();
      if (newBp !== this.breakpoint) {
        this.breakpoint = newBp;
        document.dispatchEvent(new CustomEvent('breakpointChange', { detail: { breakpoint: newBp } }));
        this._adjustLayout(newBp);
      }
    }, 150));

    this._adjustLayout(this.breakpoint);
  }

  _getCurrentBreakpoint() {
    const w = window.innerWidth;
    if (w < 600) return 'mobile';
    if (w < 1024) return 'tablet';
    if (w < 1440) return 'desktop';
    return 'ultrawide';
  }

  _adjustLayout(bp) {
    document.body.setAttribute('data-breakpoint', bp);

    const sidebar = document.querySelector('.sidebar-panel');
    const mobileNav = document.querySelector('.mobile-nav');
    const headerNav = document.querySelector('.header-nav');

    if (bp === 'mobile') {
      if (sidebar) sidebar.style.display = 'none';
      if (mobileNav) mobileNav.style.display = 'block';
      if (headerNav) headerNav.style.display = 'none';
    } else {
      if (sidebar) sidebar.style.display = '';
      if (mobileNav) mobileNav.style.display = bp === 'tablet' ? 'block' : 'none';
      if (headerNav) headerNav.style.display = '';
    }
  }

  _debounce(fn, ms) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
  }
}


// ─── INIT ───
export function initMobile() {
  const nav = new MobileNav();
  const offline = new OfflineManager();
  const responsive = new ResponsiveLayout();
  const push = new PushNotifications();
  return { nav, offline, responsive, push };
}
