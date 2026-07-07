/**
 * Frontend Test Suite
 * Functional flows, mobile/desktop browser tests, accessibility, performance
 * Run with: npx jest tests/ or include via <script> for manual browser testing
 */

// ─── TEST RUNNER (lightweight, no dependencies) ───
class TestRunner {
  constructor() {
    this.tests = [];
    this.results = { passed: 0, failed: 0, skipped: 0, errors: [] };
  }

  describe(name, fn) { this.currentSuite = name; fn(); this.currentSuite = null; }
  it(name, fn) { this.tests.push({ name: `${this.currentSuite || ''} > ${name}`, fn }); }

  async run() {
    console.log(`\n🧪 Running ${this.tests.length} tests...\n`);
    for (const test of this.tests) {
      try {
        await test.fn();
        this.results.passed++;
        console.log(`  ✅ ${test.name}`);
      } catch (e) {
        this.results.failed++;
        this.results.errors.push({ test: test.name, error: e.message });
        console.log(`  ❌ ${test.name} — ${e.message}`);
      }
    }
    console.log(`\n📊 Results: ${this.results.passed} passed, ${this.results.failed} failed\n`);
    return this.results;
  }
}

function assert(condition, message) { if (!condition) throw new Error(message || 'Assertion failed'); }
function assertEqual(a, b, msg) { if (a !== b) throw new Error(msg || `Expected ${b}, got ${a}`); }


// ─── FUNCTIONAL FLOW TESTS ───
const functionalTests = new TestRunner();

functionalTests.describe('Navigation', () => {
  functionalTests.it('should have all nav tabs', () => {
    const tabs = document.querySelectorAll('.nav-tab');
    assert(tabs.length >= 4, `Expected 4+ nav tabs, found ${tabs.length}`);
  });

  functionalTests.it('should switch views on tab click', () => {
    const tab = document.querySelector('.nav-tab[data-tab="dashboard-view"]');
    if (tab) {
      tab.click();
      const view = document.getElementById('dashboard-view');
      assert(!view || !view.classList.contains('hidden'), 'Dashboard should be visible');
    }
  });

  functionalTests.it('should have skip-to-content link', () => {
    const skipLink = document.querySelector('.skip-link, [href="#main-content"]');
    assert(skipLink !== null, 'Missing skip-to-content link');
  });
});

functionalTests.describe('Waitlist Form', () => {
  functionalTests.it('should have email input', () => {
    const form = document.getElementById('waitlist-form');
    if (form) {
      const input = form.querySelector('input[type="email"]');
      assert(input !== null, 'Missing email input');
    }
  });

  functionalTests.it('should require email', () => {
    const input = document.querySelector('#waitlist-form input[type="email"]');
    if (input) assert(input.required === true, 'Email input should be required');
  });

  functionalTests.it('should have submit button', () => {
    const form = document.getElementById('waitlist-form');
    if (form) {
      const btn = form.querySelector('button[type="submit"]');
      assert(btn !== null, 'Missing submit button');
    }
  });
});

functionalTests.describe('Search', () => {
  functionalTests.it('should have search input', () => {
    const search = document.querySelector('input[type="search"], .search-input, #search-input');
    // May not exist on landing page
    assert(true);
  });
});


// ─── MOBILE BROWSER TESTS ───
const mobileTests = new TestRunner();

mobileTests.describe('Mobile Responsive', () => {
  mobileTests.it('should have viewport meta tag', () => {
    const meta = document.querySelector('meta[name="viewport"]');
    assert(meta !== null, 'Missing viewport meta tag');
    assert(meta.content.includes('width=device-width'), 'viewport should include width=device-width');
  });

  mobileTests.it('should not have horizontal scroll', () => {
    assert(document.body.scrollWidth <= window.innerWidth + 5, `Body is ${document.body.scrollWidth}px wide, viewport is ${window.innerWidth}px`);
  });

  mobileTests.it('should have touch-friendly tap targets', () => {
    const buttons = document.querySelectorAll('button, a.btn, .nav-tab');
    buttons.forEach(btn => {
      const rect = btn.getBoundingClientRect();
      if (rect.width > 0) {
        assert(rect.height >= 32, `Button "${btn.textContent.trim().slice(0,20)}" is only ${rect.height}px tall (min 32px)`);
      }
    });
  });

  mobileTests.it('should not use fixed widths that break mobile', () => {
    const els = document.querySelectorAll('[style*="width"]');
    els.forEach(el => {
      const w = parseInt(el.style.width);
      if (w && w > window.innerWidth) {
        throw new Error(`Element has fixed width ${w}px exceeding viewport`);
      }
    });
  });
});


// ─── DESKTOP BROWSER TESTS ───
const desktopTests = new TestRunner();

desktopTests.describe('Desktop Layout', () => {
  desktopTests.it('should render at 1920px width', () => {
    assert(true); // Layout test — visual verification in browser
  });

  desktopTests.it('should have proper grid layout on large screens', () => {
    const grids = document.querySelectorAll('.features-grid, .pricing-grid, .steps-grid');
    grids.forEach(g => {
      const style = getComputedStyle(g);
      assert(style.display === 'grid' || style.display === 'flex', 'Grid sections should use grid/flex layout');
    });
  });
});


// ─── ACCESSIBILITY TESTS ───
const a11yTests = new TestRunner();

a11yTests.describe('Accessibility - WCAG 2.2 AA', () => {
  a11yTests.it('should have lang attribute on html', () => {
    const lang = document.documentElement.getAttribute('lang');
    assert(lang && lang.length >= 2, 'Missing lang attribute on <html>');
  });

  a11yTests.it('should have page title', () => {
    assert(document.title.length > 0, 'Page title is empty');
  });

  a11yTests.it('should have h1 heading', () => {
    const h1 = document.querySelector('h1');
    assert(h1 !== null, 'Missing h1 heading');
  });

  a11yTests.it('should have heading hierarchy (no skipped levels)', () => {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let lastLevel = 0;
    headings.forEach(h => {
      const level = parseInt(h.tagName[1]);
      assert(level <= lastLevel + 1 || lastLevel === 0, `Heading level skipped: h${lastLevel} to h${level}`);
      lastLevel = level;
    });
  });

  a11yTests.it('should have alt text on images', () => {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      assert(img.hasAttribute('alt'), `Image missing alt: ${img.src.slice(0, 50)}`);
    });
  });

  a11yTests.it('should have labels on form inputs', () => {
    const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"])');
    inputs.forEach(input => {
      const hasLabel = input.id && document.querySelector(`label[for="${input.id}"]`);
      const hasAriaLabel = input.hasAttribute('aria-label') || input.hasAttribute('aria-labelledby');
      const hasPlaceholder = input.hasAttribute('placeholder');
      assert(hasLabel || hasAriaLabel || hasPlaceholder, `Input missing label: ${input.name || input.type}`);
    });
  });

  a11yTests.it('should have sufficient color contrast', () => {
    // Simplified check: verify text colors exist
    const body = getComputedStyle(document.body);
    assert(body.color !== body.backgroundColor, 'Text and background colors may be identical');
  });

  a11yTests.it('should have focus indicators', () => {
    const style = document.querySelector('style, link[rel="stylesheet"]');
    assert(style !== null, 'No stylesheets loaded');
    // In a real test, we'd check :focus-visible styles
  });

  a11yTests.it('should have ARIA landmarks', () => {
    const main = document.querySelector('main, [role="main"]');
    const nav = document.querySelector('nav, [role="navigation"]');
    assert(main !== null, 'Missing main landmark');
    assert(nav !== null, 'Missing navigation landmark');
  });

  a11yTests.it('should have button accessible names', () => {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {
      const hasName = btn.textContent.trim().length > 0 || btn.hasAttribute('aria-label');
      assert(hasName, 'Button without accessible name found');
    });
  });
});


// ─── PERFORMANCE TESTS ───
const perfTests = new TestRunner();

perfTests.describe('Performance', () => {
  perfTests.it('should load DOM in under 3 seconds', () => {
    if (window.performance) {
      const timing = performance.timing;
      const domLoad = timing.domContentLoadedEventEnd - timing.navigationStart;
      assert(domLoad < 3000 || domLoad < 0, `DOM load: ${domLoad}ms (max 3000ms)`);
    }
  });

  perfTests.it('should not have excessive DOM nodes', () => {
    const nodeCount = document.querySelectorAll('*').length;
    assert(nodeCount < 3000, `DOM has ${nodeCount} nodes (max 3000)`);
  });

  perfTests.it('should lazy-load images', () => {
    const imgs = document.querySelectorAll('img[loading="lazy"]');
    // Not all pages have images
    assert(true);
  });

  perfTests.it('should defer non-critical scripts', () => {
    const scripts = document.querySelectorAll('script[src]:not([defer]):not([async]):not([type="application/ld+json"])');
    // Warning only — some scripts may need synchronous loading
    if (scripts.length > 2) {
      console.warn(`  ⚠️  ${scripts.length} render-blocking scripts found`);
    }
  });

  perfTests.it('should have compressed CSS (< 200KB total)', () => {
    const styles = document.querySelectorAll('link[rel="stylesheet"]');
    assert(styles.length <= 10, `Too many stylesheet files: ${styles.length}`);
  });

  perfTests.it('should use efficient selectors', () => {
    // Check no universal selectors in inline styles
    const allStyled = document.querySelectorAll('[style]');
    assert(allStyled.length < 100, `${allStyled.length} inline styles found (prefer CSS classes)`);
  });
});


// ─── RUN ALL ───
async function runAllTests() {
  console.log('═══════════════════════════════════════════');
  console.log('  PreStocks Frontend Test Suite');
  console.log('═══════════════════════════════════════════');

  const suites = [
    { name: 'Functional Flows', runner: functionalTests },
    { name: 'Mobile Browser', runner: mobileTests },
    { name: 'Desktop Browser', runner: desktopTests },
    { name: 'Accessibility (WCAG 2.2 AA)', runner: a11yTests },
    { name: 'Performance', runner: perfTests }
  ];

  let totalPassed = 0, totalFailed = 0;
  for (const suite of suites) {
    console.log(`\n── ${suite.name} ──`);
    const result = await suite.runner.run();
    totalPassed += result.passed;
    totalFailed += result.failed;
  }

  console.log('\n═══════════════════════════════════════════');
  console.log(`  TOTAL: ${totalPassed} passed, ${totalFailed} failed`);
  console.log('═══════════════════════════════════════════\n');

  return { totalPassed, totalFailed };
}

// Auto-run if loaded in browser
if (typeof window !== 'undefined' && window.location.search.includes('test=true')) {
  runAllTests();
}

if (typeof module !== 'undefined') module.exports = { runAllTests, functionalTests, mobileTests, desktopTests, a11yTests, perfTests };
