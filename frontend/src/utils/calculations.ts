import type { Holding } from "@/types/portfolio";

export function calculateTotalValue(holdings: Holding[], cash: number): number {
  return holdings.reduce((sum, h) => sum + h.market_value, 0) + cash;
}

export function calculateReturn(current: number, cost: number): number {
  return current - cost;
}

export function calculateReturnPercent(current: number, cost: number): number {
  if (cost === 0) return 0;
  return ((current - cost) / cost) * 100;
}

export function calculatePortfolioAllocation(
  holdings: Holding[],
  totalValue: number
): { symbol: string; percent: number }[] {
  if (totalValue === 0) return holdings.map((h) => ({ symbol: h.symbol, percent: 0 }));
  return holdings.map((h) => ({
    symbol: h.symbol,
    percent: (h.market_value / totalValue) * 100,
  }));
}

export function calculateDiversificationScore(holdings: Holding[]): number {
  if (holdings.length === 0) return 0;
  const total = holdings.reduce((s, h) => s + h.market_value, 0);
  if (total === 0) return 0;
  const weights = holdings.map((h) => h.market_value / total);
  const hhi = weights.reduce((s, w) => s + w * w, 0);
  return Math.round((1 - hhi) * 100);
}

export function calculateCostBasis(
  existingShares: number,
  existingAvg: number,
  newShares: number,
  newPrice: number
): number {
  const totalShares = existingShares + newShares;
  if (totalShares === 0) return 0;
  return (existingShares * existingAvg + newShares * newPrice) / totalShares;
}
