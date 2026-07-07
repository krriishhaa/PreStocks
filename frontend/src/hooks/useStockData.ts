import { useEffect, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useAppDispatch } from "@/store/store";
import { updatePrice, recalculateTotals } from "@/store/slices/portfolioSlice";
import { WS_URL } from "@/config/constants";
import api from "@/utils/api";
import type { Stock, StockQuote, PricePoint } from "@/types/stock";

let socket: Socket | null = null;

export function useStockData(symbol?: string) {
  const dispatch = useAppDispatch();
  const [stock, setStock] = useState<Stock | null>(null);
  const [history, setHistory] = useState<PricePoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchStock = useCallback(
    async (ticker: string) => {
      setIsLoading(true);
      try {
        const data = await api.get<Stock>(`/stocks/${ticker}`);
        setStock(data);
      } catch {
        setStock(null);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const fetchHistory = useCallback(
    async (ticker: string, timeframe = "1M") => {
      try {
        const data = await api.get<PricePoint[]>(`/stocks/${ticker}/history`, {
          params: { timeframe },
        });
        setHistory(data);
      } catch {
        setHistory([]);
      }
    },
    []
  );

  const subscribe = useCallback(
    (symbols: string[]) => {
      if (!socket) {
        socket = io(WS_URL, { transports: ["websocket"] });
      }
      socket.emit("subscribe", { symbols });
      socket.on("price_update", (data: StockQuote) => {
        dispatch(
          updatePrice({
            symbol: data.symbol,
            price: data.price,
            change: data.change,
            changePercent: data.changePercent,
          })
        );
        dispatch(recalculateTotals());
        if (data.symbol === symbol) {
          setStock((prev) =>
            prev ? { ...prev, price: data.price, change: data.change, changePercent: data.changePercent } : prev
          );
        }
      });
    },
    [dispatch, symbol]
  );

  const unsubscribe = useCallback(() => {
    if (socket) {
      socket.disconnect();
      socket = null;
    }
  }, []);

  useEffect(() => {
    if (symbol) {
      fetchStock(symbol);
      fetchHistory(symbol);
    }
  }, [symbol, fetchStock, fetchHistory]);

  return { stock, history, isLoading, fetchStock, fetchHistory, subscribe, unsubscribe };
}
