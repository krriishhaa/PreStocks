import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/utils/api";

// ─── Search ───
export function useSearch(query: string, options?: { type?: string; limit?: number }) {
  return useQuery({
    queryKey: ["search", query, options],
    queryFn: async () => {
      const res = await api.get("/search/", { params: { q: query, ...options } });
      return res.data;
    },
    enabled: query.length >= 1,
  });
}

export function useSemanticSearch(query: string) {
  return useQuery({
    queryKey: ["search", "semantic", query],
    queryFn: async () => {
      const res = await api.get("/search/semantic", { params: { q: query } });
      return res.data;
    },
    enabled: query.length >= 3,
  });
}

export function useTrending() {
  return useQuery({
    queryKey: ["trending"],
    queryFn: async () => {
      const res = await api.get("/search/trending");
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

// ─── Companies ───
export function useCompany(id: number) {
  return useQuery({
    queryKey: ["company", id],
    queryFn: async () => {
      const res = await api.get(`/companies/${id}`);
      return res.data;
    },
    enabled: !!id,
  });
}

export function useCompanyFundamentals(id: number) {
  return useQuery({
    queryKey: ["company", id, "fundamentals"],
    queryFn: async () => {
      const res = await api.get(`/companies/${id}/fundamentals`);
      return res.data;
    },
    enabled: !!id,
  });
}

export function useCompanyRiskFlags(id: number) {
  return useQuery({
    queryKey: ["company", id, "risk-flags"],
    queryFn: async () => {
      const res = await api.get(`/companies/${id}/risk-flags`);
      return res.data;
    },
    enabled: !!id,
  });
}

// ─── Portfolio ───
export function usePortfolioSummary() {
  return useQuery({
    queryKey: ["portfolio", "summary"],
    queryFn: async () => {
      const res = await api.get("/portfolio/summary");
      return res.data;
    },
  });
}

export function useExecuteTrade() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (trade: { company_id: number; action: string; quantity: number; price: number }) => {
      const res = await api.post("/portfolio/trade", trade);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
    },
  });
}

// ─── AI ───
export function useAIResearch(companyName: string) {
  return useQuery({
    queryKey: ["ai", "research", companyName],
    queryFn: async () => {
      const res = await api.post("/ai/research", { company_name: companyName });
      return res.data;
    },
    enabled: false, // manual trigger
  });
}

export function usePortfolioAdvice() {
  return useQuery({
    queryKey: ["ai", "portfolio-advice"],
    queryFn: async () => {
      const res = await api.post("/ai/portfolio-advice");
      return res.data;
    },
    enabled: false,
  });
}

// ─── News ───
export function useNews(limit = 10) {
  return useQuery({
    queryKey: ["news", limit],
    queryFn: async () => {
      const res = await api.get("/news/", { params: { limit } });
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

// ─── Watchlists ───
export function useWatchlists() {
  return useQuery({
    queryKey: ["watchlists"],
    queryFn: async () => {
      const res = await api.get("/watchlists/");
      return res.data;
    },
  });
}

export function useAddToWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ watchlistId, companyId }: { watchlistId: number; companyId: number }) => {
      const res = await api.post(`/watchlists/${watchlistId}/items`, { company_id: companyId });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlists"] });
    },
  });
}

// ─── Notifications ───
export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      const res = await api.get("/notifications/");
      return res.data;
    },
    refetchInterval: 30 * 1000,
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: async () => {
      const res = await api.get("/notifications/unread-count");
      return res.data.count;
    },
    refetchInterval: 30 * 1000,
  });
}
