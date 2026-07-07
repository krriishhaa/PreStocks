// PreStocks App — Main Orchestrator
import { STOCKS, generateHistory, refreshStockPrices } from './data/stocks.js';
import { drawStockChart } from './components/charts.js';
import {
  initPortfolio,
  getState as getPortfolioState,
  buyStock,
  sellStock,
  getPortfolioGains,
  renderSidebar,
  renderRecentActivity
} from './components/portfolio.js';
import {
  initAcademy,
  renderTracksGrid,
  setupAcademyListeners
} from './components/academy.js';
import { setupPredictor } from './components/predictor.js';

// ─── Globals ───
window.showApp = function () {
  document.getElementById('landing-page').style.display = 'none';
  document.getElementById('app-page').style.display = 'flex';
};
window.showLanding = function () {
  document.getElementById('landing-page').style.display = 'block';
  document.getElementById('app-page').style.display = 'none';
};

const appState = {
  currentPrices: {},
  priceHistories: {},
  activeSymbol: 'NVDA',
  activeTimeframe: '1W',
  isHoveringChart: false
};

// ─── Init ───
document.addEventListener('DOMContentLoaded', () => {
  initStocksState();
  initPortfolio();
  initAcademy();
  setupPredictor();
  setupAcademyListeners();

  setupRouting();
  setupDashboardControls();
  setupCompanyPageTabs();
  setupInteractiveDemo();

  window.addEventListener('academyBonus', (e) => {
    const portfolio = getPortfolioState();
    portfolio.cash += e.detail.cashBonus;
    portfolio.transactions.unshift({
      id: 'tx_bonus_' + Date.now(), type: 'buy', symbol: 'ACADEMY',
      shares: 0, price: 0, amount: e.detail.cashBonus,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    localStorage.setItem('prestocks_portfolio_state_v2', JSON.stringify(portfolio));
    updatePortfolioSummaryUI();
    renderRecentActivity();
  });

  renderTracksGrid();
  renderDashboard();
  renderRecentActivity();

  setInterval(tickMarketPrices, 3000);
});

// ─── Stock state ───
async function initStocksState() {
  const isBackendActive = await refreshStockPrices();
  Object.keys(STOCKS).forEach(symbol => {
    const stock = STOCKS[symbol];
    appState.currentPrices[symbol] = isBackendActive ? stock.price : stock.basePrice;
    appState.currentPrices[symbol + '_changePct'] = isBackendActive ? stock.change_pct : (Math.random() - 0.45) * 3;
    appState.priceHistories[symbol] = {
      '1D': generateHistory(symbol, '1D'),
      '1W': generateHistory(symbol, '1W'),
      '1M': generateHistory(symbol, '1M'),
      '3M': generateHistory(symbol, '1M'),
      '1Y': generateHistory(symbol, '1Y')
    };
  });
}

// ─── SPA Routing ───
function setupRouting() {
  const tabs = document.querySelectorAll('.nav-tab');
  const views = document.querySelectorAll('.view-section');
  const logo = document.getElementById('logo-btn');
  const mobileTabs = document.querySelectorAll('.mobile-nav-item');

  function switchView(targetView) {
    tabs.forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
    mobileTabs.forEach(m => m.classList.remove('active'));
    views.forEach(v => v.classList.toggle('active', v.id === targetView));

    const matchedTab = document.querySelector(`.nav-tab[data-tab="${targetView}"]`);
    if (matchedTab) { matchedTab.classList.add('active'); matchedTab.setAttribute('aria-selected', 'true'); }
    const matchedMobile = document.querySelector(`.mobile-nav-item[data-tab="${targetView}"]`);
    if (matchedMobile) matchedMobile.classList.add('active');

    if (targetView === 'dashboard-view') renderDashboard();
  }

  tabs.forEach(tab => tab.addEventListener('click', () => switchView(tab.getAttribute('data-tab'))));
  mobileTabs.forEach(tab => tab.addEventListener('click', () => switchView(tab.getAttribute('data-tab'))));

  if (logo) logo.addEventListener('click', () => switchView('dashboard-view'));
}

// ─── Dashboard Render ───
function renderDashboard() {
  const symbol = appState.activeSymbol;
  const stock = STOCKS[symbol];
  if (!stock) return;

  const currentPrice = appState.currentPrices[symbol];
  const changePct = appState.currentPrices[symbol + '_changePct'] || 0;
  const isPositive = changePct >= 0;

  const nameEl = document.getElementById('active-stock-name');
  const symbolEl = document.getElementById('active-stock-symbol');
  const catEl = document.getElementById('active-stock-category');
  const priceEl = document.getElementById('active-stock-price');
  const changeEl = document.getElementById('active-stock-change');

  if (nameEl) nameEl.textContent = stock.name;
  if (symbolEl) symbolEl.textContent = symbol;
  if (catEl) catEl.textContent = stock.category;

  if (!appState.isHoveringChart && priceEl) {
    priceEl.textContent = `$${currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (changeEl) {
      changeEl.textContent = `${isPositive ? '+' : ''}${changePct.toFixed(2)}%`;
      changeEl.className = `stock-change-percent ${isPositive ? 'price-up' : 'price-down'}`;
    }
  }

  // Trade widget
  const tradePriceEl = document.getElementById('trade-market-price');
  if (tradePriceEl) tradePriceEl.textContent = `$${currentPrice.toFixed(2)}`;
  const tradeBtn = document.getElementById('btn-execute-trade');
  if (tradeBtn) {
    const action = document.getElementById('btn-buy')?.classList.contains('active-buy') ? 'Buy' : 'Sell';
    tradeBtn.textContent = `${action} ${symbol}`;
  }
  updateEstimatedCost();

  // Chart
  const history = [...(appState.priceHistories[symbol]?.[appState.activeTimeframe] || [])];
  if (history.length > 0) history[history.length - 1] = { price: currentPrice, label: history[history.length - 1].label };

  const svg = document.getElementById('main-stock-svg');
  const wrapper = document.getElementById('main-chart-wrapper');
  if (svg && wrapper) {
    drawStockChart({
      svg, history, isPositive, wrapper, tooltip: null,
      onHover: (point) => {
        appState.isHoveringChart = true;
        if (priceEl) priceEl.textContent = `$${point.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
      },
      onHoverLeave: () => { appState.isHoveringChart = false; renderDashboard(); }
    });
  }

  updatePortfolioSummaryUI();
}

// ─── Dashboard Controls ───
function setupDashboardControls() {
  // Timeframes
  document.querySelectorAll('.timeframe-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.activeTimeframe = btn.getAttribute('data-timeframe');
      renderDashboard();
    });
  });

  // Buy/Sell toggle
  const buyBtn = document.getElementById('btn-buy');
  const sellBtn = document.getElementById('btn-sell');
  if (buyBtn && sellBtn) {
    buyBtn.addEventListener('click', () => { buyBtn.classList.add('active-buy'); sellBtn.classList.remove('active-sell'); renderDashboard(); });
    sellBtn.addEventListener('click', () => { sellBtn.classList.add('active-sell'); buyBtn.classList.remove('active-buy'); renderDashboard(); });
  }

  // Shares input
  const sharesInput = document.getElementById('trade-shares');
  if (sharesInput) sharesInput.addEventListener('input', updateEstimatedCost);

  // Execute trade
  const executeBtn = document.getElementById('btn-execute-trade');
  if (executeBtn) {
    executeBtn.addEventListener('click', () => {
      const isBuy = document.getElementById('btn-buy')?.classList.contains('active-buy');
      const symbol = appState.activeSymbol;
      const qty = parseFloat(document.getElementById('trade-shares')?.value) || 0;
      const price = appState.currentPrices[symbol];

      if (qty <= 0) { showToast('Enter a valid quantity', 'error'); return; }

      const result = isBuy ? buyStock(symbol, qty, price) : sellStock(symbol, qty, price);
      if (result.success) {
        document.getElementById('trade-shares').value = '';
        updateEstimatedCost();
        renderDashboard();
        renderRecentActivity();
        showToast(`${isBuy ? 'Bought' : 'Sold'} ${qty} ${symbol} @ $${price.toFixed(2)}`, 'success');
      } else {
        showToast(result.error, 'error');
      }
    });
  }
}

function updateEstimatedCost() {
  const qty = parseFloat(document.getElementById('trade-shares')?.value) || 0;
  const price = appState.currentPrices[appState.activeSymbol] || 0;
  const el = document.getElementById('trade-est-cost');
  if (el) el.textContent = `$${(qty * price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function updatePortfolioSummaryUI() {
  const portfolio = getPortfolioState();
  const gains = getPortfolioGains(appState.currentPrices);
  const nwEl = document.getElementById('header-net-worth');
  const returnEl = document.getElementById('header-daily-return');
  if (nwEl) nwEl.textContent = `$${gains.netWorth.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (returnEl) {
    const isPos = gains.dollarChange >= 0;
    returnEl.className = `metric-value ${isPos ? 'positive' : 'negative'}`;
    returnEl.textContent = `${isPos ? '+' : ''}$${gains.dollarChange.toFixed(2)}`;
  }
}

// ─── Company Page Tabs ───
function setupCompanyPageTabs() {
  const tabs = document.querySelectorAll('.company-tab');
  const contents = document.querySelectorAll('.company-tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const target = tab.getAttribute('data-ctab');
      contents.forEach(c => c.classList.toggle('active', c.id === `ctab-${target}`));
    });
  });
}

// ─── Interactive Demo ───
function setupInteractiveDemo() {
  const input = document.getElementById('demo-search');
  if (!input) return;
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') runDemoAnalysis(); });
}

window.runDemoAnalysis = function () {
  const input = document.getElementById('demo-search');
  const result = document.getElementById('demo-result');
  if (!input || !result) return;

  const query = input.value.trim();
  if (!query) return;

  result.innerHTML = `<div style="text-align:center;padding:var(--space-4);color:var(--text-secondary)"><div class="skeleton-loader" style="width:100%;height:16px;margin-bottom:12px"></div><div class="skeleton-loader" style="width:80%;height:16px;margin-bottom:12px"></div><div class="skeleton-loader" style="width:60%;height:16px"></div></div>`;

  setTimeout(() => {
    const companyName = query.charAt(0).toUpperCase() + query.slice(1);
    result.innerHTML = `
      <div class="demo-result-content">
        <div style="display:flex;align-items:center;gap:var(--space-3);margin-bottom:var(--space-4)">
          <div style="width:40px;height:40px;border-radius:var(--radius-lg);background:var(--bg-tertiary);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--color-primary)">${companyName.slice(0, 2).toUpperCase()}</div>
          <div><strong>${companyName}</strong><br><span class="text-sm text-secondary">AI Risk Analysis</span></div>
        </div>
        <div style="display:flex;flex-direction:column;gap:var(--space-3)">
          <div class="mockup-risk-flag"><div class="risk-flag-indicator high"></div><div><div class="text-sm font-semibold">Volatility Flag — High</div><div class="text-xs text-secondary">30-day realized vol exceeds 2x sector median</div></div></div>
          <div class="mockup-risk-flag"><div class="risk-flag-indicator medium"></div><div><div class="text-sm font-semibold">Valuation Flag — Moderate</div><div class="text-xs text-secondary">P/E ratio in 75th percentile of historical range</div></div></div>
          <div class="mockup-risk-flag"><div class="risk-flag-indicator low"></div><div><div class="text-sm font-semibold">Financial Health — Good</div><div class="text-xs text-secondary">Strong balance sheet with net cash position</div></div></div>
        </div>
        <div style="margin-top:var(--space-4);padding:var(--space-3);background:var(--color-primary-surface);border-radius:var(--radius-md);font-size:var(--font-size-sm);color:var(--color-primary)">
          <strong>AI Summary:</strong> ${companyName} shows elevated short-term volatility but strong fundamentals. Consider the position size relative to your portfolio and ensure proper diversification.
        </div>
      </div>`;
  }, 1200);
};

// ─── Price Ticking ───
async function tickMarketPrices() {
  const isBackendActive = await refreshStockPrices();
  Object.keys(STOCKS).forEach(symbol => {
    const stock = STOCKS[symbol];
    let nextPrice, changePct;
    if (isBackendActive) {
      nextPrice = stock.price;
      changePct = stock.change_pct;
    } else {
      const curPrice = appState.currentPrices[symbol] || stock.basePrice;
      const step = (Math.random() - 0.485) * 2 * stock.volatility * 0.15;
      nextPrice = curPrice * (1 + step);
      changePct = ((nextPrice - stock.basePrice) / stock.basePrice) * 100;
    }
    appState.currentPrices[symbol] = nextPrice;
    appState.currentPrices[symbol + '_changePct'] = changePct;
  });

  const activeTab = document.querySelector('.nav-tab.active');
  if (activeTab?.getAttribute('data-tab') === 'dashboard-view') {
    renderDashboard();
  } else {
    updatePortfolioSummaryUI();
  }
}

// ─── Toast Notification ───
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.setAttribute('role', 'alert');
  container.appendChild(toast);
  setTimeout(() => toast.classList.add('toast-show'), 10);
  setTimeout(() => { toast.classList.remove('toast-show'); setTimeout(() => toast.remove(), 300); }, 3500);
}

function selectActiveStock(symbol) {
  if (!STOCKS[symbol]) return;
  appState.activeSymbol = symbol;
  renderDashboard();
}
