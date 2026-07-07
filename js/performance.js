/**
 * PreStocks Performance Module
 * - Lazy loading (images + sections)
 * - Code splitting (dynamic imports)
 * - Infinite scrolling
 * - Virtualized tables/lists
 * - Intersection Observer patterns
 */

// ═══════════════════════════════════════════════════
// LAZY LOADING — Images & Sections
// ═══════════════════════════════════════════════════

const LazyLoader = {
  observer: null,

  init() {
    if (!('IntersectionObserver' in window)) return;

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const el = entry.target;
            if (el.tagName === 'IMG') {
              this.loadImage(el);
            } else if (el.dataset.lazySrc) {
              this.loadBackground(el);
            } else if (el.classList.contains('lazy-section')) {
              el.classList.add('loaded');
            }
            this.observer.unobserve(el);
          }
        });
      },
      { rootMargin: '200px 0px', threshold: 0.01 }
    );

    document.querySelectorAll('img[loading="lazy"], [data-lazy-src], .lazy-section').forEach(el => {
      this.observer.observe(el);
    });
  },

  loadImage(img) {
    const src = img.dataset.src || img.src;
    if (img.dataset.src) {
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
    }
    img.onload = () => img.classList.add('loaded');
    img.onerror = () => img.classList.add('error');
  },

  loadBackground(el) {
    el.style.backgroundImage = `url(${el.dataset.lazySrc})`;
    el.removeAttribute('data-lazy-src');
  }
};


// ═══════════════════════════════════════════════════
// CODE SPLITTING — Dynamic Module Loading
// ═══════════════════════════════════════════════════

const ModuleLoader = {
  loaded: new Set(),
  loading: new Map(),

  async load(modulePath) {
    if (this.loaded.has(modulePath)) {
      return;
    }
    if (this.loading.has(modulePath)) {
      return this.loading.get(modulePath);
    }

    const promise = import(modulePath).then(module => {
      this.loaded.add(modulePath);
      this.loading.delete(modulePath);
      return module;
    }).catch(err => {
      this.loading.delete(modulePath);
      console.error(`Failed to load module: ${modulePath}`, err);
      throw err;
    });

    this.loading.set(modulePath, promise);
    return promise;
  },

  async loadView(viewName) {
    const viewMap = {
      'dashboard-view': './components/charts.js',
      'learn-view': './components/academy.js',
      'predictor-view': './components/predictor.js',
      'markets-view': './components/markets.js',
      'infra-view': './components/infra.js',
    };

    const path = viewMap[viewName];
    if (path && !this.loaded.has(path)) {
      const container = document.getElementById(viewName);
      if (container) {
        container.innerHTML = `
          <div class="view-loading" role="status" aria-label="Loading content">
            <div class="spinner"></div>
            <span class="view-loading-text">Loading...</span>
          </div>
        `;
      }
      await this.load(path);
    }
  }
};


// ═══════════════════════════════════════════════════
// INFINITE SCROLLING
// ═══════════════════════════════════════════════════

class InfiniteScroll {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.loadMore = options.loadMore;
    this.threshold = options.threshold || 200;
    this.loading = false;
    this.hasMore = true;
    this.page = 1;

    this.trigger = document.createElement('div');
    this.trigger.className = 'infinite-scroll-trigger';
    this.trigger.setAttribute('aria-hidden', 'true');

    this.loader = document.createElement('div');
    this.loader.className = 'infinite-scroll-loader';
    this.loader.setAttribute('role', 'status');
    this.loader.setAttribute('aria-label', 'Loading more items');
    this.loader.innerHTML = '<div class="spinner"></div>';
    this.loader.style.display = 'none';

    if (this.container) {
      this.container.appendChild(this.loader);
      this.container.appendChild(this.trigger);
      this.setupObserver();
    }
  }

  setupObserver() {
    this.observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !this.loading && this.hasMore) {
          this.fetchNext();
        }
      },
      { rootMargin: `${this.threshold}px` }
    );
    this.observer.observe(this.trigger);
  }

  async fetchNext() {
    this.loading = true;
    this.loader.style.display = 'flex';

    try {
      const result = await this.loadMore(this.page);
      this.page++;

      if (!result || result.length === 0) {
        this.hasMore = false;
        this.observer.disconnect();
      }
    } catch (err) {
      console.error('Infinite scroll load failed:', err);
    } finally {
      this.loading = false;
      this.loader.style.display = 'none';
    }
  }

  reset() {
    this.page = 1;
    this.hasMore = true;
    this.loading = false;
    if (this.observer) {
      this.observer.observe(this.trigger);
    }
  }

  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
    this.trigger.remove();
    this.loader.remove();
  }
}


// ═══════════════════════════════════════════════════
// VIRTUALIZED LIST — Render only visible items
// ═══════════════════════════════════════════════════

class VirtualList {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.items = options.items || [];
    this.itemHeight = options.itemHeight || 56;
    this.renderItem = options.renderItem;
    this.overscan = options.overscan || 5;

    this.scrollTop = 0;
    this.containerHeight = 0;

    if (this.container) {
      this.container.classList.add('virtual-list');
      this.container.style.position = 'relative';
      this.container.setAttribute('role', 'list');
      this.container.setAttribute('aria-label', options.ariaLabel || 'Scrollable list');

      this.spacer = document.createElement('div');
      this.spacer.className = 'virtual-list-spacer';
      this.container.appendChild(this.spacer);

      this.container.addEventListener('scroll', this.onScroll.bind(this), { passive: true });
      this.render();

      this.resizeObserver = new ResizeObserver(() => {
        this.containerHeight = this.container.clientHeight;
        this.render();
      });
      this.resizeObserver.observe(this.container);
    }
  }

  onScroll() {
    const newScrollTop = this.container.scrollTop;
    if (Math.abs(newScrollTop - this.scrollTop) > this.itemHeight / 2) {
      this.scrollTop = newScrollTop;
      requestAnimationFrame(() => this.render());
    }
  }

  render() {
    if (!this.container || !this.renderItem) return;

    const totalHeight = this.items.length * this.itemHeight;
    this.spacer.style.height = `${totalHeight}px`;
    this.containerHeight = this.container.clientHeight;

    const startIdx = Math.max(0, Math.floor(this.scrollTop / this.itemHeight) - this.overscan);
    const endIdx = Math.min(
      this.items.length,
      Math.ceil((this.scrollTop + this.containerHeight) / this.itemHeight) + this.overscan
    );

    const existingItems = this.container.querySelectorAll('.virtual-list-item');
    existingItems.forEach(el => el.remove());

    const fragment = document.createDocumentFragment();
    for (let i = startIdx; i < endIdx; i++) {
      const el = document.createElement('div');
      el.className = 'virtual-list-item';
      el.style.top = `${i * this.itemHeight}px`;
      el.style.height = `${this.itemHeight}px`;
      el.setAttribute('role', 'listitem');
      el.setAttribute('aria-setsize', String(this.items.length));
      el.setAttribute('aria-posinset', String(i + 1));
      el.innerHTML = this.renderItem(this.items[i], i);
      fragment.appendChild(el);
    }
    this.container.appendChild(fragment);
  }

  setItems(items) {
    this.items = items;
    this.render();
  }

  destroy() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    this.container.removeEventListener('scroll', this.onScroll);
  }
}


// ═══════════════════════════════════════════════════
// KEYBOARD NAVIGATION
// ═══════════════════════════════════════════════════

const KeyboardNav = {
  init() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav-active');
      }
    });
    document.addEventListener('mousedown', () => {
      document.body.classList.remove('keyboard-nav-active');
    });

    this.setupArrowNavigation();
    this.setupEscapeClose();
    this.setupShortcuts();
  },

  setupArrowNavigation() {
    document.addEventListener('keydown', (e) => {
      const target = e.target;

      if (target.matches('.nav-tab, .mobile-nav-item, .timeframe-btn')) {
        const parent = target.parentElement;
        const siblings = [...parent.querySelectorAll(target.tagName.toLowerCase() + ':not([disabled])')];
        const idx = siblings.indexOf(target);

        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
          e.preventDefault();
          const next = siblings[(idx + 1) % siblings.length];
          next.focus();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
          e.preventDefault();
          const prev = siblings[(idx - 1 + siblings.length) % siblings.length];
          prev.focus();
        } else if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          target.click();
        }
      }
    });
  },

  setupEscapeClose() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal-backdrop.active');
        if (activeModal) {
          activeModal.classList.remove('active');
          const trigger = document.querySelector('[data-modal-trigger]');
          if (trigger) trigger.focus();
        }

        const activeDropdown = document.querySelector('.dropdown.active');
        if (activeDropdown) {
          activeDropdown.classList.remove('active');
          activeDropdown.querySelector('button')?.focus();
        }
      }
    });
  },

  setupShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (e.target.matches('input, textarea, select')) return;

      const shortcuts = {
        '/': () => document.querySelector('.search-bar-input')?.focus(),
        '1': () => switchTab('dashboard-view'),
        '2': () => switchTab('learn-view'),
        '3': () => switchTab('predictor-view'),
        '4': () => switchTab('markets-view'),
      };

      if (shortcuts[e.key] && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        shortcuts[e.key]();
      }
    });
  }
};


// ═══════════════════════════════════════════════════
// ACCESSIBILITY HELPERS
// ═══════════════════════════════════════════════════

const A11y = {
  announcements: null,

  init() {
    this.announcements = document.createElement('div');
    this.announcements.setAttribute('aria-live', 'polite');
    this.announcements.setAttribute('aria-atomic', 'true');
    this.announcements.className = 'sr-only';
    this.announcements.id = 'a11y-announcements';
    document.body.appendChild(this.announcements);
  },

  announce(message, priority = 'polite') {
    if (!this.announcements) this.init();
    this.announcements.setAttribute('aria-live', priority);
    this.announcements.textContent = '';
    requestAnimationFrame(() => {
      this.announcements.textContent = message;
    });
  },

  trapFocus(element) {
    const focusable = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    const handler = (e) => {
      if (e.key !== 'Tab') return;
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    element.addEventListener('keydown', handler);
    first?.focus();
    return () => element.removeEventListener('keydown', handler);
  }
};


// ═══════════════════════════════════════════════════
// PERFORMANCE MONITORING
// ═══════════════════════════════════════════════════

const PerfMonitor = {
  marks: {},

  init() {
    if ('PerformanceObserver' in window) {
      const lcp = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const last = entries[entries.length - 1];
        this.marks.lcp = last.startTime;
      });
      lcp.observe({ type: 'largest-contentful-paint', buffered: true });

      const cls = new PerformanceObserver((list) => {
        let clsValue = 0;
        list.getEntries().forEach(entry => {
          if (!entry.hadRecentInput) clsValue += entry.value;
        });
        this.marks.cls = clsValue;
      });
      cls.observe({ type: 'layout-shift', buffered: true });
    }

    window.addEventListener('load', () => {
      requestIdleCallback(() => {
        const nav = performance.getEntriesByType('navigation')[0];
        if (nav) {
          this.marks.ttfb = nav.responseStart;
          this.marks.fcp = performance.getEntriesByName('first-contentful-paint')[0]?.startTime;
          this.marks.domReady = nav.domContentLoadedEventEnd;
          this.marks.load = nav.loadEventEnd;
        }
      });
    });
  },

  getMetrics() {
    return { ...this.marks };
  }
};


// ═══════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════

function initPerformance() {
  LazyLoader.init();
  KeyboardNav.init();
  A11y.init();
  PerfMonitor.init();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPerformance);
} else {
  initPerformance();
}

export { LazyLoader, ModuleLoader, InfiniteScroll, VirtualList, KeyboardNav, A11y, PerfMonitor };
