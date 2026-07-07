// PreStocks App Orchestrator & State Coordinator
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

// Landing / App Page Toggle
window.showApp = function() {
  document.getElementById('landing-page').style.display = 'none';
  document.getElementById('app-page').style.display = 'flex';
};
window.showLanding = function() {
  document.getElementById('landing-page').style.display = 'block';
  document.getElementById('app-page').style.display = 'none';
};

// Application State
const appState = {
  currentPrices: {},
  priceHistories: {},
  activeSymbol: "NVDA",
  activeTimeframe: "1W",
  isHoveringChart: false
};

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
  // 1. Load data & initialize subsystems
  initStocksState();
  initPortfolio();
  initAcademy();
  setupPredictor();
  setupAcademyListeners();
  setupInfraView();

  // 2. Setup SPA view routing
  setupRouting();

  // 3. Setup dashboard inputs and order entries
  setupDashboardControls();

  // 4. Listen for academy virtual bonus events
  window.addEventListener("academyBonus", (e) => {
    const portfolio = getPortfolioState();
    portfolio.cash += e.detail.cashBonus;
    // Log transaction
    portfolio.transactions.unshift({
      id: "tx_bonus_" + Date.now(),
      type: "buy", // Highlight green
      symbol: "ACADEMY",
      shares: 0,
      price: 0,
      amount: e.detail.cashBonus,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    localStorage.setItem("prestocks_portfolio_state_v2", JSON.stringify(portfolio));
    
    // Play sound or show flash animation
    const headerNW = document.getElementById("header-net-worth");
    if (headerNW) {
      headerNW.style.color = "#ffcc00";
      setTimeout(() => { headerNW.style.color = ""; }, 2000);
    }
    
    updatePortfolioSummaryUI();
    renderRecentActivity();
  });

  // 5. Initial rendering
  renderTracksGrid();
  renderDashboard();
  renderRecentActivity();
  renderMarketsNews();

  // 6. Start real-time price ticking (every 3 seconds)
  setInterval(tickMarketPrices, 3000);
});

// Setup baseline stock prices and histories
async function initStocksState() {
  const isBackendActive = await refreshStockPrices();
  Object.keys(STOCKS).forEach(symbol => {
    const stock = STOCKS[symbol];
    appState.currentPrices[symbol] = isBackendActive ? stock.price : stock.basePrice;
    
    // Seed stock change percentages
    appState.currentPrices[symbol + "_changePct"] = isBackendActive ? stock.change_pct : (Math.random() - 0.45) * 3; // Initial offset

    // Pre-cache histories
    appState.priceHistories[symbol] = {
      '1D': generateHistory(symbol, '1D'),
      '1W': generateHistory(symbol, '1W'),
      '1M': generateHistory(symbol, '1M'),
      '1Y': generateHistory(symbol, '1Y')
    };
  });
}

// Router tabs logic
function setupRouting() {
  const tabs = document.querySelectorAll(".nav-tab");
  const views = document.querySelectorAll(".view-section");
  const logo = document.getElementById("logo-btn");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetView = tab.getAttribute("data-tab");
      
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      views.forEach(v => {
        if (v.id === targetView) {
          v.classList.add("active");
        } else {
          v.classList.remove("active");
        }
      });

      // Special re-draw triggers on switching
      if (targetView === "dashboard-view") {
        renderDashboard();
      } else if (targetView === "markets-view") {
        updateMarketsTabUI();
      } else if (targetView === "infra-view") {
        loadInfraData();
      }
    });
  });

  logo.addEventListener("click", () => {
    document.getElementById("nav-dashboard").click();
  });
}

// Render Dashboard View (Chart, description, ordering details)
function renderDashboard() {
  const symbol = appState.activeSymbol;
  const stock = STOCKS[symbol];
  if (!stock) return;

  const currentPrice = appState.currentPrices[symbol];
  const changePct = appState.currentPrices[symbol + "_changePct"];
  const isPositive = changePct >= 0;

  // 1. Text elements
  document.getElementById("active-stock-name").textContent = stock.name;
  document.getElementById("active-stock-symbol").textContent = symbol;
  document.getElementById("active-stock-category").textContent = stock.category;
  
  if (!appState.isHoveringChart) {
    document.getElementById("active-stock-price").textContent = `$${currentPrice.toLocaleString([], {minimumFractionDigits:2, maximumFractionDigits:2})}`;
    const changeText = `${isPositive ? '+' : ''}${changePct.toFixed(2)}%`;
    const changeEl = document.getElementById("active-stock-change");
    changeEl.textContent = changeText;
    changeEl.className = `stock-change-percent ${isPositive ? 'positive' : 'negative'}`;
  }

  document.getElementById("active-stock-description").textContent = stock.desc;

  // 2. Sensitivity Meters
  const ratesVal = Math.round((stock.globalSensitivity.interestRates + 1) * 50); // Scale [-1,1] to [0,100]
  const tradeVal = Math.round((stock.globalSensitivity.tradeTensions + 1) * 50);
  const spendingVal = Math.round((stock.globalSensitivity.consumerSpending + 1) * 50);

  updateSensitivityMeter("rates", ratesVal, stock.globalSensitivity.interestRates);
  updateSensitivityMeter("trade", tradeVal, stock.globalSensitivity.tradeTensions);
  updateSensitivityMeter("spending", spendingVal, stock.globalSensitivity.consumerSpending);

  // 3. Order Panel Update
  document.getElementById("order-stock-symbol").textContent = symbol;
  document.getElementById("order-market-price").textContent = `$${currentPrice.toFixed(2)}`;
  updateEstimatedCost();

  // 4. Draw interactive chart
  const history = [...appState.priceHistories[symbol][appState.activeTimeframe]];
  
  // Update last element in history to match current live ticking price
  if (history.length > 0) {
    history[history.length - 1] = {
      price: currentPrice,
      label: history[history.length - 1].label
    };
  }

  const svg = document.getElementById("main-stock-svg");
  const wrapper = document.getElementById("main-chart-wrapper");
  const tooltip = document.getElementById("chart-tooltip");

  drawStockChart({
    svg,
    history,
    isPositive,
    wrapper,
    tooltip,
    onHover: (point) => {
      appState.isHoveringChart = true;
      document.getElementById("active-stock-price").textContent = `$${point.price.toLocaleString([], {minimumFractionDigits: 2})}`;
      const changeEl = document.getElementById("active-stock-change");
      // Calculate change relative to history start
      const startPrice = history[0].price;
      const hDiff = point.price - startPrice;
      const hPct = (hDiff / startPrice) * 100;
      changeEl.textContent = `${hPct >= 0 ? '+' : ''}${hPct.toFixed(2)}%`;
      changeEl.className = `stock-change-percent ${hPct >= 0 ? 'positive' : 'negative'}`;
    },
    onHoverLeave: () => {
      appState.isHoveringChart = false;
      // Re-trigger static render
      renderDashboard();
    }
  });

  // Update header and sidebar
  updatePortfolioSummaryUI();
  renderSidebar(appState.currentPrices, appState.activeSymbol, selectActiveStock);
}

function updateSensitivityMeter(type, val, raw) {
  const fill = document.getElementById(`sensitivity-${type}`);
  const txt = document.getElementById(`sensitivity-${type}-txt`);
  if (!fill || !txt) return;

  fill.style.width = `${val}%`;
  
  if (raw > 0.3) {
    txt.textContent = "Highly Positive";
    txt.style.color = "#00c805";
  } else if (raw > 0) {
    txt.textContent = "Mildly Positive";
    txt.style.color = "#bcf2be";
  } else if (raw < -0.3) {
    txt.textContent = "Highly Negative";
    txt.style.color = "#ff3b30";
  } else if (raw < 0) {
    txt.textContent = "Mildly Negative";
    txt.style.color = "#ffbaba";
  } else {
    txt.textContent = "Neutral / Unaffected";
    txt.style.color = "#8e9fae";
  }
}

// Select a new active stock
function selectActiveStock(symbol) {
  if (!STOCKS[symbol]) return;
  appState.activeSymbol = symbol;
  renderDashboard();
}

// Setup order panels & timeframe clicks
function setupDashboardControls() {
  // Timeframes
  const tfBtns = document.querySelectorAll(".timeframe-btn");
  tfBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tfBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      appState.activeTimeframe = btn.getAttribute("data-timeframe");
      renderDashboard();
    });
  });

  // Order Type selector (Buy vs Sell)
  const buyTab = document.getElementById("order-tab-buy");
  const sellTab = document.getElementById("order-tab-sell");
  const submitBtn = document.getElementById("btn-submit-order");

  buyTab.addEventListener("click", () => {
    buyTab.classList.add("active");
    sellTab.classList.remove("active");
    submitBtn.textContent = "Buy Shares";
    submitBtn.classList.remove("sell-state");
    submitBtn.setAttribute("data-action", "buy");
    document.getElementById("order-error-box").style.display = "none";
  });

  sellTab.addEventListener("click", () => {
    sellTab.classList.add("active");
    buyTab.classList.remove("active");
    submitBtn.textContent = "Sell Shares";
    submitBtn.classList.add("sell-state");
    submitBtn.setAttribute("data-action", "sell");
    document.getElementById("order-error-box").style.display = "none";
  });

  // Shares quantity typing calculates total cost
  const qtyInput = document.getElementById("order-quantity");
  qtyInput.addEventListener("input", updateEstimatedCost);

  // Submit Order
  submitBtn.addEventListener("click", () => {
    const action = submitBtn.getAttribute("data-action") || "buy";
    const symbol = appState.activeSymbol;
    const qty = parseFloat(qtyInput.value);
    const price = appState.currentPrices[symbol];
    const errorBox = document.getElementById("order-error-box");

    errorBox.style.display = "none";

    let result;
    if (action === "buy") {
      result = buyStock(symbol, qty, price);
    } else {
      result = sellStock(symbol, qty, price);
    }

    if (result.success) {
      // Clear input
      qtyInput.value = "";
      updateEstimatedCost();
      renderDashboard();
      renderRecentActivity();
      
      // micro-animation flashing border of order card
      const orderCard = document.querySelector(".order-card");
      const flashColor = action === "buy" ? "rgba(0, 200, 5, 0.3)" : "rgba(255, 59, 48, 0.3)";
      orderCard.style.boxShadow = `0 0 20px ${flashColor}`;
      setTimeout(() => { orderCard.style.boxShadow = ""; }, 1000);
    } else {
      errorBox.textContent = result.error;
      errorBox.style.display = "block";
    }
  });
}

function updateEstimatedCost() {
  const qty = parseFloat(document.getElementById("order-quantity").value) || 0;
  const price = appState.currentPrices[appState.activeSymbol] || 0;
  const estCost = qty * price;
  document.getElementById("order-estimated-cost").textContent = `$${estCost.toLocaleString([], {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

// Update Top header metrics
function updatePortfolioSummaryUI() {
  const portfolio = getPortfolioState();
  const gains = getPortfolioGains(appState.currentPrices);

  const nwEl = document.getElementById("header-net-worth");
  const cashEl = document.getElementById("header-cash");
  const returnEl = document.getElementById("header-daily-return");
  const orderCashEl = document.getElementById("order-cash-txt");

  if (nwEl) nwEl.textContent = `$${gains.netWorth.toLocaleString([], {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  if (cashEl) cashEl.textContent = `$${portfolio.cash.toLocaleString([], {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  if (orderCashEl) orderCashEl.textContent = `$${portfolio.cash.toLocaleString([], {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  
  if (returnEl) {
    const isPositive = gains.dollarChange >= 0;
    returnEl.className = `metric-value ${isPositive ? 'positive' : 'negative'}`;
    returnEl.textContent = `${isPositive ? '+' : ''}$${gains.dollarChange.toFixed(2)} (${isPositive ? '+' : ''}${gains.pctChange.toFixed(2)}%)`;
  }
}


// Real-time market tick generator
async function tickMarketPrices() {
  const isBackendActive = await refreshStockPrices();
  Object.keys(STOCKS).forEach(symbol => {
    const stock = STOCKS[symbol];
    let nextPrice;
    let changePct;

    if (isBackendActive) {
      nextPrice = stock.price;
      changePct = stock.change_pct;
    } else {
      const curPrice = appState.currentPrices[symbol] || stock.basePrice;
      const maxChange = stock.volatility * 0.15; // Ticking scale factor
      const stepChange = (Math.random() - 0.485) * 2 * maxChange;
      nextPrice = curPrice * (1 + stepChange);
      changePct = ((nextPrice - stock.basePrice) / stock.basePrice) * 100;
    }
    
    appState.currentPrices[symbol] = nextPrice;
    appState.currentPrices[symbol + "_changePct"] = changePct;

    // Tick the history cache 1D to reflect real-time pricing updates
    const d1Hist = appState.priceHistories[symbol]['1D'];
    if (d1Hist && d1Hist.length > 0) {
      d1Hist[d1Hist.length - 1] = {
        price: nextPrice,
        label: d1Hist[d1Hist.length - 1].label
      };
    }
  });

  // Re-render dashboard active elements (only if active tab is dashboard)
  const activeTab = document.querySelector(".nav-tab.active");
  if (activeTab && activeTab.getAttribute("data-tab") === "dashboard-view") {
    renderDashboard();
  } else {
    // If not on dashboard view, we still need to update global stats and sidebar watchlists
    updatePortfolioSummaryUI();
    renderSidebar(appState.currentPrices, appState.activeSymbol, selectActiveStock);
  }

  // Update Global Markets tickers and Heatmap (if on Markets view)
  if (activeTab && activeTab.getAttribute("data-tab") === "markets-view") {
    updateMarketsTabUI();
  }
}


// ================= GLOBAL MARKETS VIEW UI UPDATES =================
function updateMarketsTabUI() {
  // Update Tickers
  const tickerData = [
    { id: "spy", symbol: "SPY" },
    { id: "aapl", symbol: "AAPL" },
    { id: "nvda", symbol: "NVDA" },
    { id: "btc", symbol: "BTC" }
  ];

  tickerData.forEach(tick => {
    const valEl = document.getElementById(`market-${tick.id}-val`);
    const chgEl = document.getElementById(`market-${tick.id}-chg`);
    
    if (valEl && chgEl) {
      const price = appState.currentPrices[tick.symbol];
      const chg = appState.currentPrices[tick.symbol + "_changePct"];
      const isPositive = chg >= 0;

      valEl.textContent = `$${price.toLocaleString([], {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      chgEl.textContent = `${isPositive ? '+' : ''}${chg.toFixed(2)}%`;
      
      const parent = valEl.parentElement;
      parent.className = `ticker-pill ${isPositive ? 'positive' : 'negative'}`;
    }
  });

  // Update Heatmap Sectors
  updateSectorHeatmapBox("semis", "NVDA");
  updateSectorHeatmapBox("ai", "PLTR");
  updateSectorHeatmapBox("space", "RKLB");
  updateSectorHeatmapBox("lunar", "LUNR");
}

function updateSectorHeatmapBox(id, stockSymbol) {
  const box = document.getElementById(`heatmap-${id}`);
  const chgEl = document.getElementById(`heatmap-${id}-chg`);
  if (!box || !chgEl) return;

  const chg = appState.currentPrices[stockSymbol + "_changePct"] || 0.0;
  const isPositive = chg >= 0;

  chgEl.textContent = `${isPositive ? '+' : ''}${chg.toFixed(2)}%`;
  box.className = `heatmap-box ${isPositive ? 'positive' : 'negative'}`;
}

// Standard news feed items loading
function renderMarketsNews() {
  const feed = document.getElementById("markets-news-feed");
  if (!feed) return;

  const newsItems = [
    {
      source: "Macro Journal",
      tag: "bullish",
      title: "Federal Reserve hints at rate stability, signaling rate cuts by late Autumn",
      desc: "Following a cooling Consumer Price Index, Fed officials indicated interest rate cycles may have reached their peak, fostering strong bullish runs on growth assets."
    },
    {
      source: "Global Supply Wire",
      tag: "bearish",
      title: "Tariff increases proposed on rare earth materials essential for chip development",
      desc: "Trade negotiators raise warning signs over silicon and lithium imports, sparking volatility in semiconductor stocks like NVIDIA and automotive lines."
    },
    {
      source: "Decentralized Digest",
      tag: "neutral",
      title: "SEC approves broad regulatory guidelines for global staking providers",
      desc: "Strict compliance updates have been proposed for institutional crypto providers, stabilizing Coinbase and Bitcoin swings in a tight range."
    },
    {
      source: "Retail Monitor",
      tag: "bullish",
      title: "Consumer spending index exceeds forecasts, showing robust holiday order books",
      desc: "Household balance sheets remain resilient despite interest rate pressures, feeding demand for high-end consumer hardware and tech integrations."
    }
  ];

  feed.innerHTML = newsItems.map(item => {
    return `
      <div class="news-card-item">
        <div class="news-meta">
          <span class="news-source">${item.source}</span>
          <span class="news-tag ${item.tag}">${item.tag}</span>
        </div>
        <h4>${item.title}</h4>
        <p>${item.desc}</p>
      </div>
    `;
  }).join("");
}

// ================= DATA INFRA VIEW =================
function setupInfraView() {
  const refreshBtn = document.getElementById("infra-refresh-btn");
  const runBtn = document.getElementById("infra-run-btn");
  if (!refreshBtn || !runBtn) return;

  refreshBtn.addEventListener("click", () => {
    loadInfraData();
  });

  runBtn.addEventListener("click", async () => {
    const msg = document.getElementById("infra-run-msg");
    msg.textContent = "Running ETL...";
    try {
      const res = await fetch("http://127.0.0.1:8000/infra/run-nightly", { method: "POST" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to trigger ETL run.");
      }
      const successCount = (data.runs || []).filter(r => r.status === "success" || r.status === "partial_success").length;
      msg.textContent = `Triggered ${data.runs.length} pipelines, healthy: ${successCount}.`;
      loadInfraData();
    } catch (err) {
      msg.textContent = `ETL run failed: ${err.message}`;
    }
  });
}

async function loadInfraData() {
  const envEl = document.getElementById("infra-env");
  const healthyEl = document.getElementById("infra-healthy");
  const dbEl = document.getElementById("infra-db");
  const tbody = document.getElementById("infra-runs-body");
  const alertMetaEl = document.getElementById("infra-alerting-meta");
  if (!envEl || !healthyEl || !dbEl || !tbody || !alertMetaEl) return;

  try {
    const [statusRes, runsRes] = await Promise.all([
      fetch("http://127.0.0.1:8000/infra/status"),
      fetch("http://127.0.0.1:8000/infra/runs?limit=20"),
    ]);

    if (!statusRes.ok || !runsRes.ok) {
      throw new Error("Backend infra endpoints unavailable");
    }

    const status = await statusRes.json();
    const runs = await runsRes.json();

    envEl.textContent = status.environment || "development";
    healthyEl.textContent = `${status.pipelines_healthy || 0}/${status.pipelines_total || 0}`;
    dbEl.textContent = status.database || "-";
    const alerting = status.alerting || {};
    alertMetaEl.textContent =
      `Retries: ${alerting.max_attempts || 0} (backoff ${alerting.backoff_seconds || 0}s), ` +
      `Slack alerts: ${alerting.slack_enabled ? "on" : "off"}, ` +
      `Email alerts: ${alerting.email_enabled ? "on" : "off"}`;

    if (!runs.length) {
      tbody.innerHTML = `<tr><td colspan="6">No ETL runs yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = runs.map(run => {
      const statusClass = run.status === "success" ? "positive" : run.status === "partial_success" ? "neutral" : "negative";
      return `
        <tr>
          <td>${run.pipeline_name}</td>
          <td><span class="infra-status-pill ${statusClass}">${run.status}</span></td>
          <td>${run.records_pulled ?? 0}</td>
          <td>${run.records_valid ?? 0}</td>
          <td>${run.records_stored ?? 0}</td>
          <td>${run.run_date || "-"}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    envEl.textContent = "offline";
    healthyEl.textContent = "0/0";
    dbEl.textContent = "-";
    alertMetaEl.textContent = "Alerting metadata unavailable.";
    tbody.innerHTML = `<tr><td colspan="6">Unable to load infra data: ${err.message}</td></tr>`;
  }
}
