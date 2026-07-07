import type { Holding } from "@/types/portfolio";

export function calculateTotalValue(holdings: Holding[], cash: number): number {
  return holdings.reduce((sum, h) => sum + h.totalValue, 0) + cash;
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
  return holdings.map((h) => ({
    symbol: h.symbol,
    percent: (h.totalValue / totalValue) * 100,
  }));
}

export function calculateDiversificationScore(holdings: Holding[]): number {
  if (holdings.length === 0) return 0;
  const total = holdings.reduce((s, h) => s + h.totalValue, 0);
  const weights = holdings.map((h) => h.totalValue / total);
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
