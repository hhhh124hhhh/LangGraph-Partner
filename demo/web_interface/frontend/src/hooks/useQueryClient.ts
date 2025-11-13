import { QueryClient, QueryClientConfig } from '@tanstack/react-query';

// React Query 配置
const queryConfig: QueryClientConfig = {
  defaultOptions: {
    queries: {
      // 5分钟缓存时间
      staleTime: 5 * 60 * 1000,
      // 重试配置
      retry: (failureCount, error) => {
        // 4xx 错误不重试
        if (error && typeof error === 'object' && 'status' in error) {
          const status = error.status as number;
          if (status >= 400 && status < 500) {
            return false;
          }
        }
        // 最多重试2次
        return failureCount < 2;
      },
      // 重试延迟
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // 窗口聚焦时是否重新获取
      refetchOnWindowFocus: false,
      // 网络重连时是否重新获取
      refetchOnReconnect: true,
    },
    mutations: {
      // 变更重试配置
      retry: 1,
      retryDelay: 1000,
    },
  },
};

export const queryClient = new QueryClient(queryConfig);

export default queryClient;