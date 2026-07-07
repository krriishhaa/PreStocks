// Virtual Portfolio Management Component

const STATE_KEY = "prestocks_portfolio_state_v2";

const DEFAULT_STATE = {
  cash: 10000.00,
  holdings: {}, // e.g. { "AAPL": { symbol: "AAPL", shares: 5, averagePrice: 175.50 } }
  transactions: [],
  watchlist: ["AAPL", "TSLA", "NVDA", "COIN", "SPY", "BTC"]
};

let state = { ...DEFAULT_STATE };

// Initialize state from local storage or default
export function initPortfolio() {
  const saved = localStorage.getItem(STATE_KEY);
  if (saved) {
    try {
      state = JSON.parse(saved);
      // Ensure essential fields exist
      if (state.cash === undefined) state.cash = DEFAULT_STATE.cash;
      if (!state.holdings) state.holdings = {};
      if (!state.transactions) state.transactions = [];
      if (!state.watchlist || state.watchlist.length === 0) state.watchlist = [...DEFAULT_STATE.watchlist];
    } catch (e) {
      console.error("Failed to parse portfolio state, resetting.", e);
      state = { ...DEFAULT_STATE };
      saveState();
    }
  } else {
    state = { ...DEFAULT_STATE };
    saveState();
  }
  return state;
}

export function getState() {
  return state;
}

function saveState() {
  localStorage.setItem(STATE_KEY, JSON.stringify(state));
}

// Calculate total portfolio net worth
export function getNetWorth(currentPrices) {
  let holdingsValue = 0;
  for (const symbol in state.holdings) {
    const price = currentPrices[symbol] || 0;
    holdingsValue += state.holdings[symbol].shares * price;
  }
  return state.cash + holdingsValue;
}

// Calculate percentage and dollar gains of portfolio
export function getPortfolioGains(currentPrices) {
  let currentVal = 0;
  let totalCost = 0;
  
  for (const symbol in state.holdings) {
    const h = state.holdings[symbol];
    const curPrice = currentPrices[symbol] || 0;
    currentVal += h.shares * curPrice;
    totalCost += h.shares * h.averagePrice;
  }

  // To make it look like a real brokerage account, we measure daily gains.
  // Since we don't track historical daily closes in a DB, we can estimate
  // daily returns based on the daily change of each stock in the portfolio.
  let dailyChangeDollar = 0;
  let previousDayValue = state.cash; // Cash doesn't change day-to-day

  for (const symbol in state.holdings) {
    const h = state.holdings[symbol];
    const curPrice = currentPrices[symbol] || 0;
    
    // Estimate daily return based on typical volatility, or simply stock's current daily change
    // Let's assume stock's daily change is proportional
    // For simplicity, we fetch the stock daily change from the master state in app.js
    // We will pass the dailyChangeDollar directly, or estimate:
    const changePct = currentPrices[symbol + "_changePct"] || 0.0;
    const prevPrice = curPrice / (1 + changePct / 100);
    const dayChange = (curPrice - prevPrice) * h.shares;
    dailyChangeDollar += dayChange;
    previousDayValue += prevPrice * h.shares;
  }

  const netWorth = state.cash + currentVal;
  const pctChange = previousDayValue > 0 ? (dailyChangeDollar / previousDayValue) * 100 : 0;

  return {
    dollarChange: dailyChangeDollar,
    pctChange: pctChange,
    netWorth: netWorth
  };
}

// Buy Stock
export function buyStock(symbol, shares, price) {
  shares = parseFloat(shares);
  if (isNaN(shares) || shares <= 0) {
    return { success: false, error: "Please enter a valid positive number of shares." };
  }

  const cost = shares * price;
  if (cost > state.cash) {
    return { success: false, error: `Insufficient cash buying power. Required: $${cost.toFixed(2)}, Available: $${state.cash.toFixed(2)}` };
  }

  // Execute buy
  state.cash -= cost;
  
  if (state.holdings[symbol]) {
    const holding = state.holdings[symbol];
    const totalShares = holding.shares + shares;
    const totalCost = (holding.shares * holding.averagePrice) + cost;
    holding.averagePrice = totalCost / totalShares;
    holding.shares = totalShares;
  } else {
    state.holdings[symbol] = {
      symbol: symbol,
      shares: shares,
      averagePrice: price
    };
  }

  // Log transaction
  state.transactions.unshift({
    id: "tx_" + Date.now(),
    type: "buy",
    symbol: symbol,
    shares: shares,
    price: price,
    amount: cost,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });

  saveState();
  return { success: true };
}

// Sell Stock
export function sellStock(symbol, shares, price) {
  shares = parseFloat(shares);
  if (isNaN(shares) || shares <= 0) {
    return { success: false, error: "Please enter a valid positive number of shares." };
  }

  const holding = state.holdings[symbol];
  if (!holding || holding.shares < shares) {
    const owned = holding ? holding.shares.toFixed(4) : "0";
    return { success: false, error: `Insufficient shares. You only own ${owned} shares of ${symbol}.` };
  }

  // Execute sell
  const revenue = shares * price;
  state.cash += revenue;
  holding.shares -= shares;

  if (holding.shares < 0.0001) {
    delete state.holdings[symbol];
  }

  // Log transaction
  state.transactions.unshift({
    id: "tx_" + Date.now(),
    type: "sell",
    symbol: symbol,
    shares: shares,
    price: price,
    amount: revenue,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });

  saveState();
  return { success: true };
}

// Render the entire Watchlist & Holdings on the right sidebar
export function renderSidebar(currentPrices, activeSymbol, onSelectStock) {
  const watchlistContainer = document.getElementById("watchlist-list");
  const holdingsContainer = document.getElementById("holdings-list");

  if (!watchlistContainer || !holdingsContainer) return;

  // Render Holdings
  holdingsContainer.innerHTML = "";
  const ownedSymbols = Object.keys(state.holdings);
  
  if (ownedSymbols.length === 0) {
    holdingsContainer.innerHTML = '<div class="empty-list-placeholder">No assets owned.</div>';
  } else {
    ownedSymbols.forEach(symbol => {
      const h = state.holdings[symbol];
      const curPrice = currentPrices[symbol] || h.averagePrice;
      const totalValue = h.shares * curPrice;
      const profitLoss = (curPrice - h.averagePrice) * h.shares;
      const profitLossPct = (curPrice - h.averagePrice) / h.averagePrice * 100;
      const isPositive = profitLoss >= 0;

      const item = document.createElement("div");
      item.className = `watchlist-item ${symbol === activeSymbol ? 'active' : ''}`;
      item.innerHTML = `
        <div class="item-left">
          <span class="item-symbol">${symbol}</span>
          <span class="item-name">${h.shares.toFixed(3)} Shares</span>
          <span class="item-holdings-badge">Avg: $${h.averagePrice.toFixed(2)}</span>
        </div>
        <div class="item-right">
          <span class="item-price">$${totalValue.toFixed(2)}</span>
          <span class="item-badge ${isPositive ? 'positive' : 'negative'}">
            ${isPositive ? '+' : ''}${profitLossPct.toFixed(1)}%
          </span>
        </div>
      `;
      item.addEventListener("click", () => onSelectStock(symbol));
      holdingsContainer.appendChild(item);
    });
  }

  // Render Watchlist
  watchlistContainer.innerHTML = "";
  state.watchlist.forEach(symbol => {
    const price = currentPrices[symbol] || 0;
    const changePct = currentPrices[symbol + "_changePct"] || 0.0;
    const isPositive = changePct >= 0;

    const item = document.createElement("div");
    item.className = `watchlist-item ${symbol === activeSymbol ? 'active' : ''}`;
    item.innerHTML = `
      <div class="item-left">
        <span class="item-symbol">${symbol}</span>
        <span class="item-name">${symbol === 'BTC' ? 'Cryptocurrency' : 'Equity'}</span>
      </div>
      <div class="item-right">
        <span class="item-price">$${price.toLocaleString([], {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
        <span class="item-badge ${isPositive ? 'positive' : 'negative'}">
          ${isPositive ? '+' : ''}${changePct.toFixed(2)}%
        </span>
      </div>
    `;
    item.addEventListener("click", () => onSelectStock(symbol));
    watchlistContainer.appendChild(item);
  });
}

// Render Recent Transactions list
export function renderRecentActivity() {
  const list = document.getElementById("recent-transactions-list");
  if (!list) return;

  if (state.transactions.length === 0) {
    list.innerHTML = '<div class="empty-transactions">No transactions yet. Buy some stock to start investing!</div>';
    return;
  }

  list.innerHTML = state.transactions.slice(0, 10).map(t => {
    return `
      <div class="transaction-log-item">
        <div class="trans-left">
          <span class="trans-action-badge ${t.type}">${t.type}</span>
          <span class="trans-stock">${t.symbol}</span>
        </div>
        <div class="trans-right">
          <span class="trans-amount">$${t.amount.toFixed(2)}</span>
          <span class="trans-details">${t.shares.toFixed(3)} @ $${t.price.toFixed(2)}</span>
        </div>
      </div>
    `;
  }).join("");
}
