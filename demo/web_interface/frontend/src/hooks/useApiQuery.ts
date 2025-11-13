import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@services/index';
import {
  LangGraphState,
  MemoryNetwork,
  KnowledgeSearchRequest,
  KnowledgeSearchResponse,
  DemoScenario,
  ComparisonRequest,
  ComparisonResponse,
  PersonaUpdateRequest,
} from '@typesdef/index';

// 查询键工厂
export const queryKeys = {
  // 对话相关
  chatState: (sessionId: string) => ['chat', 'state', sessionId] as const,

  // 记忆网络相关
  memoryNetwork: (sessionId: string) => ['memory', 'network', sessionId] as const,

  // 知识检索相关
  knowledgeSearch: (request: KnowledgeSearchRequest) => ['knowledge', 'search', request] as const,

  // 演示相关
  demoScenarios: () => ['demo', 'scenarios'] as const,

  // 对比分析相关
  comparison: (request: ComparisonRequest) => ['comparison', 'analyze', request] as const,

  // 通用查询
  health: () => ['health'] as const,
} as const;

// 对话状态查询
export const useChatStateQuery = (sessionId: string) => {
  return useQuery({
    queryKey: queryKeys.chatState(sessionId),
    queryFn: () => apiService.getChatState(sessionId),
    enabled: !!sessionId,
    refetchInterval: 5000, // 每5秒刷新一次
    staleTime: 1000, // 1秒内数据被认为是新鲜的
  });
};

// 记忆网络查询
export const useMemoryNetworkQuery = (sessionId: string) => {
  return useQuery({
    queryKey: queryKeys.memoryNetwork(sessionId),
    queryFn: () => apiService.getMemoryNetwork(sessionId),
    enabled: !!sessionId,
    staleTime: 30000, // 30秒内数据被认为是新鲜的
  });
};

// 知识检索查询
export const useKnowledgeSearchQuery = (request: KnowledgeSearchRequest, enabled = true) => {
  return useQuery({
    queryKey: queryKeys.knowledgeSearch(request),
    queryFn: () => apiService.searchKnowledge(request),
    enabled: enabled && !!request.query,
    staleTime: 60000, // 1分钟内数据被认为是新鲜的
  });
};

// 演示场景查询
export const useDemoScenariosQuery = () => {
  return useQuery({
    queryKey: queryKeys.demoScenarios(),
    queryFn: () => apiService.getDemoScenarios(),
    staleTime: 10 * 60 * 1000, // 10分钟内数据被认为是新鲜的
  });
};

// 对比分析查询
export const useComparisonQuery = (request: ComparisonRequest, enabled = true) => {
  return useQuery({
    queryKey: queryKeys.comparison(request),
    queryFn: () => apiService.analyzeComparison(request),
    enabled: enabled && !!request.session_id,
    staleTime: 5 * 60 * 1000, // 5分钟内数据被认为是新鲜的
  });
};

// 健康检查查询
export const useHealthQuery = () => {
  return useQuery({
    queryKey: queryKeys.health(),
    queryFn: () => apiService.healthCheck(),
    refetchInterval: 30000, // 每30秒检查一次
    retry: 3,
  });
};

// 变更相关hooks

// 画像更新变更
export const usePersonaUpdateMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PersonaUpdateRequest) => apiService.updatePersona(request),
    onSuccess: () => {
      // 更新相关的查询缓存
      queryClient.invalidateQueries({ queryKey: ['chat'] });
    },
    onError: (error) => {
      console.error('[Mutation] Persona update failed:', error);
    },
  });
};

// 知识检索变更
export const useKnowledgeSearchMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: KnowledgeSearchRequest) => apiService.searchKnowledge(request),
    onSuccess: (data, variables) => {
      // 更新缓存
      queryClient.setQueryData(
        queryKeys.knowledgeSearch(variables),
        data
      );
    },
    onError: (error) => {
      console.error('[Mutation] Knowledge search failed:', error);
    },
  });
};

// 对比分析变更
export const useComparisonMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ComparisonRequest) => apiService.analyzeComparison(request),
    onSuccess: (data, variables) => {
      // 更新缓存
      queryClient.setQueryData(
        queryKeys.comparison(variables),
        data
      );
    },
    onError: (error) => {
      console.error('[Mutation] Comparison analysis failed:', error);
    },
  });
};

// 通用工具hooks

// 无效化所有查询
export const useInvalidateAllQueries = () => {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries();
  };
};

// 预取数据
export const usePrefetchData = () => {
  const queryClient = useQueryClient();

  const prefetchChatState = (sessionId: string) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.chatState(sessionId),
      queryFn: () => apiService.getChatState(sessionId),
      staleTime: 1000,
    });
  };

  const prefetchMemoryNetwork = (sessionId: string) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.memoryNetwork(sessionId),
      queryFn: () => apiService.getMemoryNetwork(sessionId),
      staleTime: 30000,
    });
  };

  const prefetchDemoScenarios = () => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.demoScenarios(),
      queryFn: () => apiService.getDemoScenarios(),
      staleTime: 10 * 60 * 1000,
    });
  };

  return {
    prefetchChatState,
    prefetchMemoryNetwork,
    prefetchDemoScenarios,
  };
};

// 乐观更新工具
export const useOptimisticUpdate = () => {
  const queryClient = useQueryClient();

  const updateChatStateOptimistically = (sessionId: string, newData: Partial<LangGraphState>) => {
    queryClient.setQueryData(
      queryKeys.chatState(sessionId),
      (old: LangGraphState | undefined) => {
        if (!old) return old;
        return { ...old, ...newData };
      }
    );
  };

  const updateMemoryNetworkOptimistically = (sessionId: string, newData: Partial<MemoryNetwork>) => {
    queryClient.setQueryData(
      queryKeys.memoryNetwork(sessionId),
      (old: MemoryNetwork | undefined) => {
        if (!old) return old;
        return { ...old, ...newData };
      }
    );
  };

  return {
    updateChatStateOptimistically,
    updateMemoryNetworkOptimistically,
  };
};