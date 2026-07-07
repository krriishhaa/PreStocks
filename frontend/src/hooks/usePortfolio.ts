import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "@/store/store";
import {
  addHolding,
  removeHolding,
  addTransaction,
  setCash,
  recalculateTotals,
} from "@/store/slices/portfolioSlice";
import { calculateCostBasis } from "@/utils/calculations";
import type { Holding, Transaction } from "@/types/portfolio";

export function usePortfolio() {
  const dispatch = useAppDispatch();
  const { portfolio, isLoading, error } = useAppSelector(
    (state) => state.portfolio
  );

  const buyStock = useCallback(
    (symbol: string, name: string, shares: number, price: number) => {
      const total = shares * price;
      if (total > portfolio.cashBalance) {
        throw new Error("Insufficient funds");
      }

      const existing = portfolio.holdings.find((h) => h.symbol === symbol);
      const newAvg = existing
        ? calculateCostBasis(existing.shares, existing.avgCost, shares, price)
        : price;

      const holding: Holding = {
        symbol,
        name,
        shares,
        avgCost: newAvg,
        currentPrice: price,
        totalValue: shares * price,
        totalReturn: 0,
        totalReturnPercent: 0,
        dayChange: 0,
        dayChangePercent: 0,
      };

      dispatch(addHolding(holding));
      dispatch(setCash(portfolio.cashBalance - total));

      const tx: Transaction = {
        id: `tx-${Date.now()}`,
        symbol,
        action: "buy",
        shares,
        price,
        total,
        timestamp: new Date().toISOString(),
        status: "filled",
      };
      dispatch(addTransaction(tx));
      dispatch(recalculateTotals());
    },
    [dispatch, portfolio]
  );

  const sellStock = useCallback(
    (symbol: string, shares: number, price: number) => {
      const existing = portfolio.holdings.find((h) => h.symbol === symbol);
      if (!existing || existing.shares < shares) {
        throw new Error("Insufficient shares");
      }

      const total = shares * price;

      if (existing.shares === shares) {
        dispatch(removeHolding(symbol));
      } else {
        const updatedHolding: Holding = {
          ...existing,
          shares: existing.shares - shares,
          totalValue: (existing.shares - shares) * price,
        };
        dispatch(removeHolding(symbol));
        dispatch(addHolding(updatedHolding));
      }

      dispatch(setCash(portfolio.cashBalance + total));

      const tx: Transaction = {
        id: `tx-${Date.now()}`,
        symbol,
        action: "sell",
        shares,
        price,
        total,
        timestamp: new Date().toISOString(),
        status: "filled",
      };
      dispatch(addTransaction(tx));
      dispatch(recalculateTotals());
    },
    [dispatch, portfolio]
  );

  return { portfolio, isLoading, error, buyStock, sellStock };
}
