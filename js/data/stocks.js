// Stock Profiles and Price History Generator

export const STOCKS = {
  NVDA: {
    symbol: "NVDA",
    name: "NVIDIA Corporation",
    category: "Semiconductors",
    icon: "🤖",
    desc: "NVIDIA Corporation focuses on personal computer graphics, graphics processing units, and also AI solutions. It is the leading provider of chips powering the global AI revolution.",
    basePrice: 120.50,
    price: 120.50,
    change: 0.0,
    change_pct: 0.0,
    volatility: 0.28,
    globalSensitivity: {
      interestRates: -0.1,
      tradeTensions: -0.6,
      consumerSpending: 0.3
    }
  },
  PLTR: {
    symbol: "PLTR",
    name: "Palantir Technologies Inc.",
    category: "Software / AI",
    icon: "🔮",
    desc: "Palantir Technologies builds software platforms for big data analytics. Its platforms are heavily utilized by defense agencies and enterprise customers for operations.",
    basePrice: 25.30,
    price: 25.30,
    change: 0.0,
    change_pct: 0.0,
    volatility: 0.32,
    globalSensitivity: {
      interestRates: -0.3,
      tradeTensions: -0.2,
      consumerSpending: 0.4
    }
  },
  RKLB: {
    symbol: "RKLB",
    name: "Rocket Lab USA Inc.",
    category: "Aerospace / Defense",
    icon: "🚀",
    desc: "Rocket Lab is an end-to-end space company. It delivers launch services, spacecraft manufacture, satellite components, and on-orbit management solutions.",
    basePrice: 4.80,
    price: 4.80,
    change: 0.0,
    change_pct: 0.0,
    volatility: 0.40,
    globalSensitivity: {
      interestRates: -0.5,
      tradeTensions: -0.3,
      consumerSpending: 0.3
    }
  },
  LUNR: {
    symbol: "LUNR",
    name: "Intuitive Machines Inc.",
    category: "Aerospace / Space Exploration",
    icon: "🌙",
    desc: "Intuitive Machines is an American space exploration company focused on lunar landers, lunar surface operations, orbital services, and space communications.",
    basePrice: 5.20,
    price: 5.20,
    change: 0.0,
    change_pct: 0.0,
    volatility: 0.55,
    globalSensitivity: {
      interestRates: -0.6,
      tradeTensions: -0.2,
      consumerSpending: 0.2
    }
  }
};

// Refresh stock prices from the FastAPI backend if running
export async function refreshStockPrices() {
  try {
    const res = await fetch("http://localhost:8000/stocks");
    if (res.ok) {
      const data = await res.json();
      for (const symbol in data) {
        if (STOCKS[symbol]) {
          STOCKS[symbol].price = data[symbol].price;
          STOCKS[symbol].change = data[symbol].change;
          STOCKS[symbol].change_pct = data[symbol].change_pct;
        }
      }
      return true;
    }
  } catch (e) {
    console.log("FastAPI backend not running or reachable. Using simulated ticks.");
  }
  return false;
}

// Generates deterministic random walk for stock price history so that the charts are nice and consistent
// rangeType can be: '1D' (24 points), '1W' (35 points), '1M' (30 points), '1Y' (250 points)
export function generateHistory(stock, rangeType) {
  const spec = STOCKS[stock.symbol || stock];
  if (!spec) return [];

  let points = 30;
  switch (rangeType) {
    case '1D': points = 24; break;
    case '1W': points = 35; break;
    case '1M': points = 30; break;
    case '1Y': points = 250; break;
    default: points = 30;
  }

  // LCG pseudo-random generator with seed
  let seed = 0;
  for (let i = 0; i < spec.name.length; i++) {
    seed += spec.name.charCodeAt(i);
  }
  for (let i = 0; i < rangeType.length; i++) {
    seed += rangeType.charCodeAt(i) * 10;
  }

  function seededRandom() {
    const x = Math.sin(seed++) * 10000;
    return x - Math.floor(x);
  }

  const history = [];
  let currentPrice = spec.price || spec.basePrice;

  const rawPrices = new Array(points);
  rawPrices[points - 1] = currentPrice;

  const stepVolatility = spec.volatility / Math.sqrt(points);
  // Default annualized trend
  const trendFactor = spec.symbol === "NVDA" ? 0.25 : spec.symbol === "PLTR" ? 0.20 : 0.15;
  const stepTrend = trendFactor / points;

  for (let i = points - 2; i >= 0; i--) {
    const changePercent = stepTrend + (seededRandom() - 0.48) * 2 * stepVolatility;
    currentPrice = currentPrice / (1 + changePercent);
    rawPrices[i] = currentPrice;
  }

  const now = new Date();
  for (let i = 0; i < points; i++) {
    let dateStr = "";
    if (rangeType === '1D') {
      const h = new Date(now.getTime() - (points - 1 - i) * 60 * 60 * 1000);
      dateStr = h.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      const d = new Date(now.getTime() - (points - 1 - i) * 24 * 60 * 60 * 1000);
      dateStr = d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }

    history.push({
      price: parseFloat(rawPrices[i].toFixed(2)),
      label: dateStr
    });
  }

  return history;
}
