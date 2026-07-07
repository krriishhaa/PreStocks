import { useEffect, useCallback } from "react";
import { useAppDispatch, useAppSelector } from "@/store/store";
import {
  setFlags,
  setCompositeScore,
  setLoading,
  setError,
} from "@/store/slices/flagsSlice";
import api from "@/utils/api";
import type { RiskFlag, CompositeRiskScore } from "@/types/flags";

export function useFlagData(symbol?: string) {
  const dispatch = useAppDispatch();
  const { flags, compositeScores, isLoading, error } = useAppSelector(
    (state) => state.flags
  );

  const fetchFlags = useCallback(async () => {
    dispatch(setLoading(true));
    try {
      const data = await api.get<RiskFlag[]>("/flags");
      dispatch(setFlags(data));
    } catch (err: any) {
      dispatch(setError(err.message));
    }
  }, [dispatch]);

  const fetchCompositeScore = useCallback(
    async (ticker: string) => {
      try {
        const data = await api.get<CompositeRiskScore>(`/flags/${ticker}/composite`);
        dispatch(setCompositeScore(data));
      } catch (err: any) {
        dispatch(setError(err.message));
      }
    },
    [dispatch]
  );

  useEffect(() => {
    fetchFlags();
  }, [fetchFlags]);

  useEffect(() => {
    if (symbol) fetchCompositeScore(symbol);
  }, [symbol, fetchCompositeScore]);

  const symbolFlags = symbol
    ? flags.filter((f) => f.symbol === symbol)
    : flags;

  const compositeScore = symbol ? compositeScores[symbol] : undefined;

  return {
    flags: symbolFlags,
    compositeScore,
    allFlags: flags,
    isLoading,
    error,
    refetch: fetchFlags,
  };
}
