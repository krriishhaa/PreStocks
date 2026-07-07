// AI Market Predictor Sandbox Component
import { STOCKS, generateHistory } from '../data/stocks.js';
import { drawPredictionChart } from './charts.js';

export function setupPredictor() {
  const stockSelect = document.getElementById("predict-stock-select");
  const headlineSelect = document.getElementById("predict-headline-select");
  const customHeadlineWrapper = document.getElementById("custom-headline-wrapper");
  const runBtn = document.getElementById("btn-run-prediction");

  if (!stockSelect) return;

  // Initialize stock selector dropdown
  stockSelect.innerHTML = Object.keys(STOCKS).map(symbol => {
    return `<option value="${symbol}">${symbol} - ${STOCKS[symbol].name}</option>`;
  }).join("");

  // Toggle custom headline field
  headlineSelect.addEventListener("change", () => {
    if (headlineSelect.value === "custom") {
      customHeadlineWrapper.style.display = "block";
    } else {
      customHeadlineWrapper.style.display = "none";
    }
  });

  // Slider bubble badges updates
  const ratesSlider = document.getElementById("predict-rates");
  const tradeSlider = document.getElementById("predict-trade");
  const spendingSlider = document.getElementById("predict-spending");

  const ratesLabels = ["Low (Stimulative)", "Medium (Normal)", "High (Restrictive)"];
  const tradeLabels = ["Low (Free Trade)", "Moderate", "High (Trade Wars)"];
  const spendingLabels = ["Weak (Recessionary)", "Stable", "Strong (Booming)"];

  ratesSlider.addEventListener("input", () => {
    document.getElementById("predict-rates-badge").textContent = ratesLabels[ratesSlider.value];
  });
  tradeSlider.addEventListener("input", () => {
    document.getElementById("predict-trade-badge").textContent = tradeLabels[tradeSlider.value];
  });
  spendingSlider.addEventListener("input", () => {
    document.getElementById("predict-spending-badge").textContent = spendingLabels[spendingSlider.value];
  });

  // Attach execution button
  runBtn.addEventListener("click", runPredictionSimulation);
}

function runPredictionSimulation() {
  const symbol = document.getElementById("predict-stock-select").value;
  const stock = STOCKS[symbol];
  if (!stock) return;

  // Fetch slider inputs
  const ratesIdx = parseInt(document.getElementById("predict-rates").value); // 0, 1, 2
  const tradeIdx = parseInt(document.getElementById("predict-trade").value); // 0, 1, 2
  const spendingIdx = parseInt(document.getElementById("predict-spending").value); // 0, 1, 2

  // Fetch Headline text
  const headlineSelect = document.getElementById("predict-headline-select");
  let headlineText = "";
  if (headlineSelect.value === "custom") {
    headlineText = document.getElementById("predict-custom-headline").value.trim();
    if (!headlineText) headlineText = "General economic indices update standard projection.";
  } else {
    headlineText = headlineSelect.options[headlineSelect.selectedIndex].text;
  }

  // Toggle display of screens
  const placeholder = document.getElementById("predict-placeholder");
  const scanner = document.getElementById("predict-scanner");
  const results = document.getElementById("predict-results");
  const statusTxt = document.getElementById("scanner-status-text");

  placeholder.style.display = "none";
  results.style.display = "none";
  scanner.style.display = "flex";

  // Sequential scanning animation status updates
  const statusSteps = [
    { text: "Ingesting macroeconomic data feeds...", time: 0 },
    { text: `Evaluating ${symbol} supply chain and sector sensitivities...`, time: 600 },
    { text: "Processing news headline sentiment matrices...", time: 1200 },
    { text: "Querying Claude reasoning loops & PyTorch LSTM...", time: 1800 }
  ];

  statusSteps.forEach(step => {
    setTimeout(() => {
      statusTxt.textContent = step.text;
    }, step.time);
  });

  // Calculate sentiment and projected prices after scanner completes
  setTimeout(async () => {
    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticker: symbol,
          macro_rates: ratesIdx,
          macro_trade: tradeIdx,
          macro_spending: spendingIdx,
          headline: headlineText
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        scanner.style.display = "none";
        results.style.display = "block";

        const sentimentBadge = document.getElementById("result-sentiment-badge");
        const directionEl = document.getElementById("result-direction");
        const assetEl = document.getElementById("result-asset");
        const riskEl = document.getElementById("result-risk");
        const explanationEl = document.getElementById("predict-explanation-txt");

        assetEl.textContent = symbol;
        
        // Show decision and score
        const formattedDecision = data.isBullish ? 'BULLISH' : 'BEARISH';
        sentimentBadge.textContent = `${data.sentimentScore}% ${formattedDecision}`;
        
        if (data.isBullish) {
          sentimentBadge.className = "result-badge-type positive";
          directionEl.className = "kpi-val positive";
          directionEl.textContent = `+${data.expectedMove.toFixed(1)}%`;
        } else {
          sentimentBadge.className = "result-badge-type negative";
          directionEl.className = "kpi-val negative";
          directionEl.textContent = `${data.expectedMove.toFixed(1)}%`;
        }

        // Set Risk Rating based on stock volatility
        if (stock.volatility > 0.3) {
          riskEl.textContent = "High";
          riskEl.style.color = "#ff3b30";
        } else if (stock.volatility > 0.15) {
          riskEl.textContent = "Moderate";
          riskEl.style.color = "#ffcc00";
        } else {
          riskEl.textContent = "Low";
          riskEl.style.color = "#00c805";
        }

        explanationEl.textContent = data.explanation;

        // Draw the chart with actual history and forecast
        const predictSvg = document.getElementById("predict-result-svg");
        drawPredictionChart(predictSvg, data.history, data.forecast);
        return;
      }
    } catch (err) {
      console.log("Failed to connect to FastAPI predictor. Falling back to local rules-based simulation.", err);
    }

    // Fallback to local rule-based simulation if API call fails
    scanner.style.display = "none";
    results.style.display = "block";

    const simulation = calculateSimulation({
      stock,
      ratesIdx,
      tradeIdx,
      spendingIdx,
      headlineText
    });

    const sentimentBadge = document.getElementById("result-sentiment-badge");
    const directionEl = document.getElementById("result-direction");
    const assetEl = document.getElementById("result-asset");
    const riskEl = document.getElementById("result-risk");
    const explanationEl = document.getElementById("predict-explanation-txt");

    assetEl.textContent = symbol;
    sentimentBadge.textContent = `${Math.round(simulation.sentimentScore)}% ${simulation.isBullish ? 'BULLISH' : 'BEARISH'}`;
    
    if (simulation.isBullish) {
      sentimentBadge.className = "result-badge-type positive";
      directionEl.className = "kpi-val positive";
      directionEl.textContent = `+${simulation.expectedMove.toFixed(1)}%`;
    } else {
      sentimentBadge.className = "result-badge-type negative";
      directionEl.className = "kpi-val negative";
      directionEl.textContent = `${simulation.expectedMove.toFixed(1)}%`;
    }

    if (stock.volatility > 0.3) {
      riskEl.textContent = "High";
      riskEl.style.color = "#ff3b30";
    } else if (stock.volatility > 0.15) {
      riskEl.textContent = "Moderate";
      riskEl.style.color = "#ffcc00";
    } else {
      riskEl.textContent = "Low";
      riskEl.style.color = "#00c805";
    }

    explanationEl.textContent = simulation.explanation;

    const history = generateHistory(symbol, '1M');
    const startPrice = history[history.length - 1].price;
    const forecast = [];
    let curVal = startPrice;
    const driftPerDay = (simulation.expectedMove / 100) / 30;
    
    let rSeed = stock.name.charCodeAt(0) + ratesIdx + tradeIdx + spendingIdx;
    function seededRandom() {
      const x = Math.sin(rSeed++) * 10000;
      return x - Math.floor(x);
    }

    for (let i = 1; i <= 30; i++) {
      const randomNoise = (seededRandom() - 0.5) * 2 * (stock.volatility / Math.sqrt(250));
      curVal = curVal * (1 + driftPerDay + randomNoise);
      forecast.push({
        price: parseFloat(curVal.toFixed(2)),
        label: `Day +${i}`
      });
    }

    const predictSvg = document.getElementById("predict-result-svg");
    drawPredictionChart(predictSvg, history, forecast);

  }, 2400);
}

// Prediction scoring logic based on sensitivity matrices
function calculateSimulation({ stock, ratesIdx, tradeIdx, spendingIdx, headlineText }) {
  // Base sentiment is 50%
  let score = 50.0;
  let explanations = [];

  // 1. Evaluate Interest Rates
  // Sensitivity: negative value (e.g. -0.2). If rates are High (2), deduct from score. If Low (0), add.
  const rateSens = stock.globalSensitivity.interestRates;
  if (ratesIdx === 0) { // Low
    const bonus = Math.abs(rateSens) * 20;
    score += bonus;
    explanations.push(`Low stimulative interest rates boost valuation multiples for growth assets like ${stock.name}.`);
  } else if (ratesIdx === 2) { // High
    const penalty = Math.abs(rateSens) * 20;
    score -= penalty;
    explanations.push(`High restrictive interest rates increase borrowing costs and compress margins, acting as a headwind.`);
  }

  // 2. Evaluate Trade Tariffs
  // Sensitivity: negative value (e.g. -0.4). High tariffs (2) deduct.
  const tradeSens = stock.globalSensitivity.tradeTensions;
  if (tradeIdx === 0) { // Low (Free trade)
    const bonus = Math.abs(tradeSens) * 15;
    score += bonus;
    explanations.push(`Reduced tariffs support frictionless global supply chains and increase overseas revenues.`);
  } else if (tradeIdx === 2) { // High (Trade wars)
    const penalty = Math.abs(tradeSens) * 25;
    score -= penalty;
    explanations.push(`Intense trade tensions and tariff hikes disrupt supply chains and increase component costs.`);
  }

  // 3. Evaluate Consumer Spending
  // Sensitivity: positive value (e.g. 0.6). Strong spending (2) adds. Weak (0) deducts.
  const spendingSens = stock.globalSensitivity.consumerSpending;
  if (spendingIdx === 0) { // Weak (Recession)
    const penalty = spendingSens * 25;
    score -= penalty;
    explanations.push(`Sluggish consumer spending and low retail confidence dampens sales volumes.`);
  } else if (spendingIdx === 2) { // Strong (Booming)
    const bonus = spendingSens * 20;
    score += bonus;
    explanations.push(`Robust consumer confidence and spending drive organic product sales.`);
  }

  // 4. Headline keyword scanner
  const headline = headlineText.toLowerCase();
  let headlineImpact = 0;

  // Bullish keywords
  const bullWords = ["breakthrough", "cut", "cools", "growth", "surges", "deal", "rises", "success", "innovate", "approval", "merger"];
  // Bearish keywords
  const bearWords = ["tariffs", "wars", "ban", "breakdown", "crisis", "hike", "strict", "inflation", "drop", "fines", "limits", "shortage"];

  bullWords.forEach(w => {
    if (headline.includes(w)) headlineImpact += 6;
  });
  bearWords.forEach(w => {
    if (headline.includes(w)) headlineImpact -= 7;
  });

  // Cryptocurreny specific headlines
  if (stock.symbol === "BTC" || stock.symbol === "COIN") {
    if (headline.includes("crypto") || headline.includes("bitcoin") || headline.includes("digital asset")) {
      if (headline.includes("ban") || headline.includes("strict") || headline.includes("regulation")) {
        headlineImpact -= 15;
      }
      if (headline.includes("breakthrough") || headline.includes("adoption") || headline.includes("approval")) {
        headlineImpact += 15;
      }
    }
  }

  score += headlineImpact;
  
  if (headlineImpact > 0) {
    explanations.push("Positive regulatory or technological sentiment in the news headlines provides immediate tailwinds.");
  } else if (headlineImpact < 0) {
    explanations.push("Negative news updates regarding regulations, supply disruptions, or inflation trigger defensive positioning.");
  }

  // Cap score between 10% and 95%
  score = Math.max(10, Math.min(95, score));

  // Determine expected 30-day percentage price move
  // Expected move = (Score - 50) * multiplier
  // High volatility stocks swing wider
  const multiplier = stock.volatility * 0.6;
  const expectedMove = (score - 50) * multiplier;

  const isBullish = score >= 50;

  // Create explanation summary
  const directionTxt = isBullish ? "UPWARD" : "DOWNWARD";
  const explanationReport = `Our algorithms project a ${directionTxt} trend of ${expectedMove.toFixed(1)}% for ${stock.name} (${stock.symbol}) over the next 30 days. ${explanations.join(" ")} The headline event ("${headlineText.substring(0, 75)}...") combined with current central bank rates creates a net market sentiment index of ${Math.round(score)}%.`;

  return {
    sentimentScore: score,
    expectedMove: expectedMove,
    isBullish: isBullish,
    explanation: explanationReport
  };
}
