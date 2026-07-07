import { useAppDispatch, useAppSelector } from "@/store/store";
import { setPortfolio, setHoldings, addTransaction, setLoading, setError } from "@/store/slices/portfolioSlice";
import { api } from "@/utils/api";
import type { Holding, Transaction } from "@/types/portfolio";

export function usePortfolio() {
  const dispatch = useAppDispatch();
  const { portfolio, holdings, loading, error } = useAppSelector((state) => state.portfolio);

  const fetchPortfolio = async () => {
    dispatch(setLoading(true));
    try {
      const { data } = await api.get("/portfolio/summary");
      dispatch(setPortfolio(data));
    } catch (err: any) {
      dispatch(setError(err.message));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const executeTrade = async (trade: { company_id: number; action: string; quantity: number; price: number }) => {
    try {
      const { data } = await api.post("/portfolio/trade", trade);
      dispatch(addTransaction(data));
      await fetchPortfolio();
      return data;
    } catch (err: any) {
      dispatch(setError(err.message));
      throw err;
    }
  };

  const buyStock = async (symbol: string, nameOrShares: string | number, sharesOrPrice?: number, priceArg?: number) => {
    const shares = typeof nameOrShares === 'number' ? nameOrShares : sharesOrPrice!;
    const price = typeof nameOrShares === 'number' ? sharesOrPrice! : priceArg!;
    return executeTrade({ company_id: 0, action: "buy", quantity: shares, price });
  };

  const sellStock = async (symbol: string, shares: number, price: number) => {
    return executeTrade({ company_id: 0, action: "sell", quantity: shares, price });
  };

  return {
    portfolio,
    holdings,
    loading,
    error,
    fetchPortfolio,
    executeTrade,
    buyStock,
    sellStock,
  };
}
