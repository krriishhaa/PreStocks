import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/utils/api';

export function useApi<T>(key: string[], url: string, options?: { enabled?: boolean }) {
  return useQuery<T>({
    queryKey: key,
    queryFn: async () => {
      const response = await apiClient.get(url);
      return response.data;
    },
    enabled: options?.enabled,
  });
}

export function useApiMutation<TData, TVariables>(url: string, method: 'post' | 'put' | 'delete' = 'post') {
  const queryClient = useQueryClient();

  return useMutation<TData, Error, TVariables>({
    mutationFn: async (variables) => {
      const response = await apiClient[method](url, variables);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries();
    },
  });
}
