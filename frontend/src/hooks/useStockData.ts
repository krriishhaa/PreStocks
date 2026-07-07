import { useState, useEffect } from "react";
import { useAppDispatch } from "@/store/store";
import { api } from "@/utils/api";
import type { Stock, PricePoint } from "@/types/stock";

export function useStockData(symbol: string) {
  const [stock, setStock] = useState<Stock | null>(null);
  const [priceHistory, setPriceHistory] = useState<PricePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;

    const fetchStock = async () => {
      setLoading(true);
      try {
        const { data } = await api.get<Stock>(`/stocks/${symbol}`);
        setStock(data);
      } catch (err: any) {
        setError(err.message);
      }
    };

    const fetchHistory = async () => {
      try {
        const { data } = await api.get<PricePoint[]>(`/stocks/${symbol}/history`);
        setPriceHistory(data);
      } catch {
        // Non-critical
      } finally {
        setLoading(false);
      }
    };

    fetchStock();
    fetchHistory();
  }, [symbol]);

  return { stock, priceHistory, loading, isLoading: loading, error };
}
