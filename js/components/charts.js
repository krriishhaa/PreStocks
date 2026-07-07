// Custom SVG Charting Component

/**
 * Draws a stock chart on the provided SVG element
 * @param {SVGElement} svg - The SVG DOM node
 * @param {Array} history - Array of {price, label} objects
 * @param {boolean} isPositive - Whether the price is up (green) or down (red)
 * @param {HTMLElement} wrapper - Container element for hover calculations
 * @param {HTMLElement} tooltip - Tooltip element to update
 * @param {Function} onHover - Callback when hovering over points: function(point)
 * @param {Function} onHoverLeave - Callback when pointer leaves: function()
 */
export function drawStockChart({
  svg,
  history,
  isPositive,
  wrapper,
  tooltip,
  onHover,
  onHoverLeave
}) {
  if (!svg || !history || history.length === 0) return;

  const width = 800;
  const height = 350;
  const paddingX = 10;
  const paddingY = 20;

  // Clear existing grid lines
  const gridGroup = svg.getElementById("chart-grid");
  if (gridGroup) gridGroup.innerHTML = "";

  // Get price bounds
  const prices = history.map(h => h.price);
  const maxPrice = Math.max(...prices);
  const minPrice = Math.min(...prices);
  const priceRange = maxPrice - minPrice || 1.0;

  // Calculate coordinates mapping function
  const getX = (index) => paddingX + (index / (history.length - 1)) * (width - 2 * paddingX);
  const getY = (price) => height - paddingY - ((price - minPrice) / priceRange) * (height - 2 * paddingY);

  // Generate gridlines (horizontal gridlines)
  const gridSteps = 4;
  for (let i = 0; i <= gridSteps; i++) {
    const ratio = i / gridSteps;
    const priceVal = minPrice + ratio * priceRange;
    const y = getY(priceVal);

    // Create horizontal gridline
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", paddingX);
    line.setAttribute("y1", y);
    line.setAttribute("x2", width - paddingX);
    line.setAttribute("y2", y);
    line.setAttribute("stroke", "#192229");
    line.setAttribute("stroke-width", "1");
    if (i > 0 && i < gridSteps) {
      line.setAttribute("stroke-dasharray", "4,4");
    }
    gridGroup.appendChild(line);

    // Create price label on right side
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", width - 5);
    text.setAttribute("y", y - 4);
    text.setAttribute("fill", "#5c6c7a");
    text.setAttribute("font-size", "10px");
    text.setAttribute("text-anchor", "end");
    text.textContent = `$${priceVal.toFixed(2)}`;
    gridGroup.appendChild(text);
  }

  // Generate line path
  let pathD = `M ${getX(0)} ${getY(history[0].price)}`;
  for (let i = 1; i < history.length; i++) {
    pathD += ` L ${getX(i)} ${getY(history[i].price)}`;
  }

  // Generate area path (shaded region under the line)
  const areaD = `${pathD} L ${getX(history.length - 1)} ${height} L ${getX(0)} ${height} Z`;

  // Update elements
  const linePath = svg.getElementById("chart-line-path");
  const areaPath = svg.getElementById("chart-area-path");

  if (linePath) {
    linePath.setAttribute("d", pathD);
    linePath.setAttribute("stroke", isPositive ? "#00c805" : "#ff3b30");
  }

  if (areaPath) {
    areaPath.setAttribute("d", areaD);
    areaPath.setAttribute("fill", isPositive ? "url(#chart-glow-gradient)" : "url(#chart-glow-gradient-red)");
  }

  // Setup Interactivity tracking nodes
  const trackLine = svg.getElementById("chart-interactive-line");
  const trackDot = svg.getElementById("chart-interactive-dot");

  if (trackDot) {
    trackDot.setAttribute("fill", isPositive ? "#00c805" : "#ff3b30");
  }

  // Event handlers
  const handleMouseMove = (e) => {
    const rect = wrapper.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const percentX = mouseX / rect.width;
    
    // Find closest index in history array
    let index = Math.round(percentX * (history.length - 1));
    index = Math.max(0, Math.min(history.length - 1, index));

    const point = history[index];
    const ptX = getX(index);
    const ptY = getY(point.price);

    // Position tracking lines & dots (converting back to wrapper scale)
    const renderX = (ptX / width) * rect.width;
    const renderY = (ptY / height) * rect.height;

    if (trackLine) {
      trackLine.setAttribute("x1", ptX);
      trackLine.setAttribute("x2", ptX);
      trackLine.style.display = "block";
    }

    if (trackDot) {
      trackDot.setAttribute("cx", ptX);
      trackDot.setAttribute("cy", ptY);
      trackDot.style.display = "block";
    }

    // Update Tooltip
    if (tooltip) {
      tooltip.style.display = "flex";
      // Position tooltip near the pointer but inside screen bounds
      let tooltipX = renderX + 15;
      let tooltipY = renderY - 45;

      if (tooltipX + 120 > rect.width) {
        tooltipX = renderX - 135;
      }
      if (tooltipY < 10) {
        tooltipY = renderY + 15;
      }

      tooltip.style.left = `${tooltipX}px`;
      tooltip.style.top = `${tooltipY}px`;

      const tDate = tooltip.querySelector("#tooltip-date");
      const tPrice = tooltip.querySelector("#tooltip-price");
      if (tDate) tDate.textContent = point.label;
      if (tPrice) tPrice.textContent = `$${point.price.toFixed(2)}`;
    }

    if (onHover) onHover(point);
  };

  const handleMouseLeave = () => {
    if (trackLine) trackLine.style.display = "none";
    if (trackDot) trackDot.style.display = "none";
    if (tooltip) tooltip.style.display = "none";
    if (onHoverLeave) onHoverLeave();
  };

  // Attach listeners (ensure we don't duplicate them)
  wrapper.removeEventListener("mousemove", wrapper._mousemoveHandler);
  wrapper.removeEventListener("mouseleave", wrapper._mouseleaveHandler);

  wrapper._mousemoveHandler = handleMouseMove;
  wrapper._mouseleaveHandler = handleMouseLeave;

  wrapper.addEventListener("mousemove", handleMouseMove);
  wrapper.addEventListener("mouseleave", handleMouseLeave);
}

/**
 * Draws a prediction forecast chart showing solid history followed by a dashed prediction line.
 * @param {SVGElement} svg - The Prediction SVG DOM node
 * @param {Array} history - Historical price points [{price, label}]
 * @param {Array} forecast - Future price points [{price, label}]
 */
export function drawPredictionChart(svg, history, forecast) {
  if (!svg || !history || history.length === 0 || !forecast || forecast.length === 0) return;

  const width = 400;
  const height = 150;
  const paddingX = 10;
  const paddingY = 15;

  // Clear existing grid
  const gridGroup = svg.getElementById("predict-grid");
  if (gridGroup) gridGroup.innerHTML = "";

  const allPrices = [...history.map(h => h.price), ...forecast.map(f => f.price)];
  const maxPrice = Math.max(...allPrices);
  const minPrice = Math.min(...allPrices);
  const priceRange = maxPrice - minPrice || 1.0;

  const totalPoints = history.length + forecast.length;
  
  const getX = (index) => paddingX + (index / (totalPoints - 1)) * (width - 2 * paddingX);
  const getY = (price) => height - paddingY - ((price - minPrice) / priceRange) * (height - 2 * paddingY);

  // Gridlines
  const gridSteps = 3;
  for (let i = 0; i <= gridSteps; i++) {
    const ratio = i / gridSteps;
    const priceVal = minPrice + ratio * priceRange;
    const y = getY(priceVal);

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", paddingX);
    line.setAttribute("y1", y);
    line.setAttribute("x2", width - paddingX);
    line.setAttribute("y2", y);
    line.setAttribute("stroke", "#1e2930");
    line.setAttribute("stroke-width", "1");
    if (i > 0 && i < gridSteps) {
      line.setAttribute("stroke-dasharray", "3,3");
    }
    gridGroup.appendChild(line);

    // Label
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", width - 5);
    text.setAttribute("y", y - 3);
    text.setAttribute("fill", "#5c6c7a");
    text.setAttribute("font-size", "9px");
    text.setAttribute("text-anchor", "end");
    text.textContent = `$${priceVal.toFixed(2)}`;
    gridGroup.appendChild(text);
  }

  // Draw History Path
  let histD = `M ${getX(0)} ${getY(history[0].price)}`;
  for (let i = 1; i < history.length; i++) {
    histD += ` L ${getX(i)} ${getY(history[i].price)}`;
  }
  const histPath = svg.getElementById("predict-historical-path");
  if (histPath) {
    histPath.setAttribute("d", histD);
  }

  // Draw Forecast Path starting from the last history point
  const lastHistIdx = history.length - 1;
  const lastHistPt = history[lastHistIdx];
  
  let foreD = `M ${getX(lastHistIdx)} ${getY(lastHistPt.price)}`;
  for (let i = 0; i < forecast.length; i++) {
    foreD += ` L ${getX(lastHistIdx + 1 + i)} ${getY(forecast[i].price)}`;
  }
  
  const forePath = svg.getElementById("predict-forecast-path");
  const isForecastUp = forecast[forecast.length - 1].price >= lastHistPt.price;

  if (forePath) {
    forePath.setAttribute("d", foreD);
    forePath.setAttribute("stroke", isForecastUp ? "#00c805" : "#ff3b30");
  }

  // Position breakpoint dot (where history connects to forecast)
  const bpDot = svg.getElementById("predict-breakpoint-dot");
  if (bpDot) {
    bpDot.setAttribute("cx", getX(lastHistIdx));
    bpDot.setAttribute("cy", getY(lastHistPt.price));
    bpDot.setAttribute("fill", isForecastUp ? "#00c805" : "#ff3b30");
  }
}
