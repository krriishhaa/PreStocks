/**
 * Data Visualization Components
 * Heatmaps, Treemaps, Line/Area charts, Funding timelines,
 * Valuation history, Ownership charts, Sector comparisons
 */

// ─── HEATMAP ───
export class Heatmap {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.options = { cellSize: 40, colorScale: ['#10B981', '#F59E0B', '#EF4444'], gap: 2, ...options };
  }

  render(data) {
    if (!this.container) return;
    const { cellSize, gap, colorScale } = this.options;
    const rows = data.length;
    const cols = data[0]?.length || 0;
    const width = cols * (cellSize + gap);
    const height = rows * (cellSize + gap);

    let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" class="viz-heatmap">`;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const val = data[r][c]?.value ?? 0;
        const norm = Math.max(0, Math.min(1, (val + 1) / 2));
        const color = this._interpolateColor(norm, colorScale);
        const x = c * (cellSize + gap);
        const y = r * (cellSize + gap);
        const label = data[r][c]?.label || '';
        svg += `<rect x="${x}" y="${y}" width="${cellSize}" height="${cellSize}" fill="${color}" rx="4">
          <title>${label}: ${(val * 100).toFixed(1)}%</title></rect>`;
        if (cellSize >= 30) {
          svg += `<text x="${x + cellSize / 2}" y="${y + cellSize / 2 + 4}" text-anchor="middle" font-size="10" fill="#fff">${label}</text>`;
        }
      }
    }
    svg += '</svg>';
    this.container.innerHTML = svg;
  }

  _interpolateColor(t, colors) {
    if (t <= 0.5) {
      return colors[0];
    } else if (t <= 0.75) {
      return colors[1];
    }
    return colors[2];
  }
}

// ─── TREEMAP ───
export class Treemap {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.options = { width: 600, height: 400, padding: 2, ...options };
  }

  render(data) {
    if (!this.container) return;
    const { width, height, padding } = this.options;
    const total = data.reduce((sum, d) => sum + d.value, 0);
    const sorted = [...data].sort((a, b) => b.value - a.value);

    let html = `<div class="viz-treemap" style="width:${width}px;height:${height}px;position:relative">`;
    let x = 0, y = 0, remainingWidth = width, remainingHeight = height;
    let remaining = [...sorted];

    const rects = this._squarify(remaining, { x: 0, y: 0, w: width, h: height }, total);
    for (const rect of rects) {
      const pct = ((rect.item.value / total) * 100).toFixed(1);
      const color = rect.item.color || this._sectorColor(rect.item.label);
      html += `<div class="treemap-cell" style="position:absolute;left:${rect.x + padding}px;top:${rect.y + padding}px;width:${Math.max(0, rect.w - padding * 2)}px;height:${Math.max(0, rect.h - padding * 2)}px;background:${color};border-radius:6px;padding:8px;overflow:hidden;color:#fff;font-size:12px">
        <strong>${rect.item.label}</strong><br><span style="opacity:0.8">${pct}%</span>
      </div>`;
    }
    html += '</div>';
    this.container.innerHTML = html;
  }

  _squarify(items, rect, total) {
    const rects = [];
    let { x, y, w, h } = rect;
    for (const item of items) {
      const ratio = item.value / total;
      if (w >= h) {
        const itemW = w * ratio;
        rects.push({ x, y, w: Math.min(itemW, w), h, item });
        x += itemW;
        w -= itemW;
      } else {
        const itemH = h * ratio;
        rects.push({ x, y, w, h: Math.min(itemH, h), item });
        y += itemH;
        h -= itemH;
      }
    }
    return rects;
  }

  _sectorColor(label) {
    const colors = { Technology: '#3B82F6', Healthcare: '#10B981', Finance: '#8B5CF6', Energy: '#F59E0B', Consumer: '#EC4899', Industrial: '#6366F1' };
    return colors[label] || '#64748B';
  }
}

// ─── LINE CHART ───
export class LineChart {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.options = { width: 700, height: 300, color: '#1E40AF', fillOpacity: 0.1, showDots: false, ...options };
  }

  render(data, labels = []) {
    if (!this.container || !data.length) return;
    const { width, height, color, fillOpacity, showDots } = this.options;
    const padding = { top: 20, right: 20, bottom: 30, left: 50 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    const points = data.map((v, i) => ({
      x: padding.left + (i / (data.length - 1)) * chartW,
      y: padding.top + chartH - ((v - min) / range) * chartH
    }));

    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
    const areaD = pathD + ` L${points[points.length - 1].x},${padding.top + chartH} L${points[0].x},${padding.top + chartH} Z`;

    let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" class="viz-line-chart">`;
    svg += `<path d="${areaD}" fill="${color}" opacity="${fillOpacity}"/>`;
    svg += `<path d="${pathD}" fill="none" stroke="${color}" stroke-width="2"/>`;

    if (showDots) {
      for (const p of points) {
        svg += `<circle cx="${p.x}" cy="${p.y}" r="3" fill="${color}"/>`;
      }
    }

    // Y-axis labels
    for (let i = 0; i <= 4; i++) {
      const val = min + (range * i / 4);
      const y = padding.top + chartH - (i / 4) * chartH;
      svg += `<text x="${padding.left - 8}" y="${y + 4}" text-anchor="end" font-size="10" fill="#94A3B8">${this._formatNum(val)}</text>`;
      svg += `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#E2E8F0" stroke-dasharray="4,4"/>`;
    }

    svg += '</svg>';
    this.container.innerHTML = svg;
  }

  _formatNum(n) {
    if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(1) + 'B';
    if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return n.toFixed(0);
  }
}

// ─── AREA CHART ───
export class AreaChart extends LineChart {
  constructor(container, options = {}) {
    super(container, { ...options, fillOpacity: 0.2 });
  }
}

// ─── FUNDING TIMELINE ───
export class FundingTimeline {
  constructor(container) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
  }

  render(rounds) {
    if (!this.container || !rounds.length) return;
    let html = '<div class="viz-funding-timeline">';
    for (const round of rounds) {
      const amount = round.amount_usd ? `$${(round.amount_usd / 1e6).toFixed(0)}M` : 'Undisclosed';
      const valuation = round.post_money_valuation ? `$${(round.post_money_valuation / 1e9).toFixed(1)}B` : '';
      html += `<div class="funding-node">
        <div class="funding-dot" style="background:${this._stageColor(round.stage)}"></div>
        <div class="funding-details">
          <div class="funding-stage">${round.stage || round.round_name || 'Round'}</div>
          <div class="funding-amount">${amount}</div>
          ${valuation ? `<div class="funding-valuation">Valuation: ${valuation}</div>` : ''}
          <div class="funding-date">${round.announced_date || ''}</div>
          ${round.lead_investor ? `<div class="funding-lead">Lead: ${round.lead_investor}</div>` : ''}
        </div>
      </div>`;
    }
    html += '</div>';
    this.container.innerHTML = html;
  }

  _stageColor(stage) {
    const map = { seed: '#10B981', series_a: '#3B82F6', series_b: '#6366F1', series_c: '#8B5CF6', series_d: '#A855F7', ipo: '#F59E0B' };
    return map[stage] || '#64748B';
  }
}

// ─── VALUATION HISTORY CHART ───
export class ValuationHistory {
  constructor(container) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.chart = new LineChart(container, { color: '#8B5CF6', fillOpacity: 0.15, showDots: true });
  }

  render(valuations) {
    const values = valuations.map(v => v.valuation_usd || v.market_cap || 0);
    this.chart.render(values);
  }
}

// ─── OWNERSHIP/PIE CHART ───
export class OwnershipChart {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.options = { size: 200, ...options };
  }

  render(slices) {
    if (!this.container || !slices.length) return;
    const { size } = this.options;
    const cx = size / 2, cy = size / 2, r = size / 2 - 10;
    const total = slices.reduce((s, d) => s + d.value, 0);
    const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6366F1', '#64748B'];

    let svg = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" class="viz-ownership">`;
    let startAngle = -Math.PI / 2;

    slices.forEach((slice, i) => {
      const angle = (slice.value / total) * 2 * Math.PI;
      const endAngle = startAngle + angle;
      const x1 = cx + r * Math.cos(startAngle);
      const y1 = cy + r * Math.sin(startAngle);
      const x2 = cx + r * Math.cos(endAngle);
      const y2 = cy + r * Math.sin(endAngle);
      const largeArc = angle > Math.PI ? 1 : 0;
      const color = slice.color || colors[i % colors.length];

      svg += `<path d="M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${largeArc} 1 ${x2},${y2} Z" fill="${color}">
        <title>${slice.label}: ${((slice.value / total) * 100).toFixed(1)}%</title></path>`;
      startAngle = endAngle;
    });

    svg += `<circle cx="${cx}" cy="${cy}" r="${r * 0.55}" fill="white"/></svg>`;

    let legend = '<div class="viz-legend">';
    slices.forEach((s, i) => {
      const color = s.color || colors[i % colors.length];
      legend += `<div class="legend-item"><span class="legend-dot" style="background:${color}"></span>${s.label} (${((s.value / total) * 100).toFixed(0)}%)</div>`;
    });
    legend += '</div>';

    this.container.innerHTML = `<div class="viz-ownership-wrapper">${svg}${legend}</div>`;
  }
}

// ─── SECTOR COMPARISON BAR CHART ───
export class SectorComparison {
  constructor(container) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
  }

  render(sectors) {
    if (!this.container || !sectors.length) return;
    const max = Math.max(...sectors.map(s => s.value));

    let html = '<div class="viz-sector-comparison">';
    for (const sector of sectors) {
      const pct = (sector.value / max) * 100;
      const change = sector.change || 0;
      const changeClass = change >= 0 ? 'positive' : 'negative';
      html += `<div class="sector-bar-row">
        <div class="sector-bar-label">${sector.label}</div>
        <div class="sector-bar-track"><div class="sector-bar-fill" style="width:${pct}%;background:${sector.color || '#3B82F6'}"></div></div>
        <div class="sector-bar-value ${changeClass}">${change >= 0 ? '+' : ''}${change.toFixed(1)}%</div>
      </div>`;
    }
    html += '</div>';
    this.container.innerHTML = html;
  }
}
