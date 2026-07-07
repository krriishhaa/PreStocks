import { useAppDispatch, useAppSelector } from "@/store/store";
import { fetchPortfolio, fetchTrades } from "@/store/slices/portfolioSlice";
import { api } from "@/utils/api";

export function usePortfolio() {
  const dispatch = useAppDispatch();
  const { data: portfolio, trades, loading, error } = useAppSelector((state) => state.portfolio);

  const refresh = () => {
    dispatch(fetchPortfolio());
    dispatch(fetchTrades());
  };

  const executeTrade = async (trade: { symbol: string; company_name?: string; side: string; shares: number; price: number }) => {
    const { data } = await api.post("/portfolio/trades", trade);
    dispatch(fetchPortfolio());
    dispatch(fetchTrades());
    return data;
  };

  const buyStock = async (symbol: string, nameOrShares: string | number, sharesOrPrice?: number, priceArg?: number) => {
    const shares = typeof nameOrShares === "number" ? nameOrShares : sharesOrPrice!;
    const price = typeof nameOrShares === "number" ? sharesOrPrice! : priceArg!;
    const company_name = typeof nameOrShares === "string" ? nameOrShares : undefined;
    return executeTrade({ symbol, company_name, side: "buy", shares, price });
  };

  const sellStock = async (symbol: string, shares: number, price: number) => {
    return executeTrade({ symbol, side: "sell", shares, price });
  };

  return {
    portfolio,
    holdings: portfolio?.holdings ?? [],
    trades,
    loading,
    error,
    refresh,
    executeTrade,
    buyStock,
    sellStock,
  };
}
