/**
 * 数据可视化页面
 * 提供LangGraph状态流程的实时网络图可视化
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useAppStore } from '@stores/index';
import { useWebSocketManager } from '@hooks/useWebSocketManager';
import { ConnectionMode } from '@services/websocketManager';
import NetworkGraph, { NetworkNode, NetworkEdge } from '@components/Visualization/NetworkGraph';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { logger } from '@utils/logger';

// 模拟数据生成器
const generateMockNetworkData = (sessionId: string, complexity: 'simple' | 'medium' | 'complex' = 'medium') => {
  // 生成节点
  const nodes: NetworkNode[] = [];

  // 中心节点 - 用户
  nodes.push({
    id: 'user_center',
    label: '用户',
    type: 'user',
    data: { session_id: sessionId, importance: 10 }
  });

  // AI助手节点
  nodes.push({
    id: 'ai_assistant',
    label: 'AI Partner',
    type: 'assistant',
    data: { model: 'glm-4.6', capabilities: ['chat', 'memory', 'analysis'] }
  });

  // 上下文节点
  for (let i = 0; i < 3; i++) {
    nodes.push({
      id: `context_${i}`,
      label: `上下文 ${i + 1}`,
      type: 'context',
      data: {
        topic: ['工作', '学习', '生活'][i],
        weight: Math.random() * 10 + 5
      }
    });
  }

  // 记忆节点
  for (let i = 0; i < 4; i++) {
    nodes.push({
      id: `memory_${i}`,
      label: `记忆 ${i + 1}`,
      type: 'memory',
      data: {
        created: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        strength: Math.random() * 10 + 3
      }
    });
  }

  // 工具节点
  const tools = ['搜索', '计算', '天气', '翻译', '分析'];
  tools.forEach((tool, i) => {
    nodes.push({
      id: `tool_${i}`,
      label: tool,
      type: 'tool',
      data: { usage_count: Math.floor(Math.random() * 50) + 1 }
    });
  });

  // 数据节点
  for (let i = 0; i < 2; i++) {
    nodes.push({
      id: `data_${i}`,
      label: `数据 ${i + 1}`,
      type: 'data',
      data: { size: Math.floor(Math.random() * 1000) + 100 }
    });
  }

  // 生成边
  const edges: NetworkEdge[] = [];

  // 用户到AI的连接
  edges.push({
    id: 'user_ai',
    source: 'user_center',
    target: 'ai_assistant',
    type: 'response',
    weight: 10
  });

  // AI到上下文的连接
  for (let i = 0; i < 3; i++) {
    edges.push({
      id: `ai_context_${i}`,
      source: 'ai_assistant',
      target: `context_${i}`,
      type: 'context',
      weight: Math.random() * 8 + 2
    });
  }

  // AI到记忆的连接
  for (let i = 0; i < 4; i++) {
    edges.push({
      id: `ai_memory_${i}`,
      source: 'ai_assistant',
      target: `memory_${i}`,
      type: 'memory',
      weight: Math.random() * 6 + 1
    });
  }

  // AI到工具的连接
  for (let i = 0; i < Math.min(3, tools.length); i++) {
    edges.push({
      id: `ai_tool_${i}`,
      source: 'ai_assistant',
      target: `tool_${i}`,
      type: 'tool_call',
      weight: Math.random() * 7 + 1
    });
  }

  // 上下文之间的连接
  edges.push({
    id: 'context_0_1',
    source: 'context_0',
    target: 'context_1',
    type: 'data_flow',
    weight: 3
  });

  edges.push({
    id: 'context_1_2',
    source: 'context_1',
    target: 'context_2',
    type: 'data_flow',
    weight: 2
  });

  // 记忆之间的连接
  edges.push({
    id: 'memory_0_1',
    source: 'memory_0',
    target: 'memory_1',
    type: 'memory',
    weight: 4
  });

  return { nodes, edges };
};

const VisualizationPage: React.FC = () => {
  const { addNotification } = useAppStore();
  const { isConnected, connectionMode } = useWebSocketManager({
    autoConnect: true,
    showConnectionNotifications: true
  });

  // 状态管理
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('demo_session_001');
  const [networkData, setNetworkData] = useState<{ nodes: NetworkNode[], edges: NetworkEdge[] } | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [selectedComplexity, setSelectedComplexity] = useState<'simple' | 'medium' | 'complex'>('medium');

  // 统计信息
  const statistics = useMemo(() => {
    if (!networkData) return null;

    const nodeTypeCount = networkData.nodes.reduce((acc, node) => {
      acc[node.type] = (acc[node.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const edgeTypeCount = networkData.edges.reduce((acc, edge) => {
      acc[edge.type] = (acc[edge.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const totalWeight = networkData.edges.reduce((sum, edge) => sum + (edge.weight || 0), 0);

    return {
      totalNodes: networkData.nodes.length,
      totalEdges: networkData.edges.length,
      nodeTypeCount,
      edgeTypeCount,
      totalWeight,
      averageWeight: totalWeight / networkData.edges.length,
      sessions: 1,
      memorySize: Math.floor(Math.random() * 100) + 50
    };
  }, [networkData]);

  // 加载网络数据
  const loadNetworkData = useCallback(async () => {
    setLoading(true);
    try {
      logger.info('开始加载网络数据', 'VisualizationPage');

      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));

      // 生成模拟数据
      const mockData = generateMockNetworkData(sessionId, selectedComplexity);

      setNetworkData(mockData);

      addNotification({
        type: 'success',
        title: '数据加载成功',
        message: `已加载 ${mockData.nodes.length} 个节点和 ${mockData.edges.length} 条边`,
        duration: 3000
      });

      logger.info(`网络数据加载成功: ${mockData.nodes.length} 节点, ${mockData.edges.length} 边`, 'VisualizationPage');

    } catch (error) {
      logger.error('网络数据加载失败', 'VisualizationPage', error);
      addNotification({
        type: 'error',
        title: '加载失败',
        message: '无法加载网络数据，请稍后重试',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  }, [sessionId, selectedComplexity, addNotification]);

  // 自动刷新
  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(loadNetworkData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, loadNetworkData]);

  // 初始加载
  useEffect(() => {
    loadNetworkData();
  }, []);

  // 处理节点点击
  const handleNodeClick = useCallback((node: any) => {
    const nodeData = node.data();
    logger.info(`点击节点: ${nodeData.label}`, 'VisualizationPage');

    addNotification({
      type: 'info',
      title: '节点信息',
      message: `选中节点: ${nodeData.label} (类型: ${nodeData.type})`,
      duration: 2000
    });
  }, [addNotification]);

  // 处理边点击
  const handleEdgeClick = useCallback((edge: any) => {
    const edgeData = edge.data();
    logger.info(`点击边: ${edgeData.type}`, 'VisualizationPage');

    addNotification({
      type: 'info',
      title: '边信息',
      message: `选中边: ${edgeData.source} → ${edgeData.target} (类型: ${edgeData.type})`,
      duration: 2000
    });
  }, [addNotification]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        {/* 页面标题 */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            数据可视化
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            LangGraph状态流程实时网络图可视化
          </p>
          <div className="mt-2 flex items-center justify-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {connectionMode === ConnectionMode.WEBSOCKET ? '实时连接' : '模拟模式'}
              </span>
            </div>
          </div>
        </div>

        {/* 控制面板 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">控制面板</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* 会话控制 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                会话ID
              </label>
              <input
                type="text"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="输入会话ID"
              />
            </div>

            {/* 复杂度选择 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                网络复杂度
              </label>
              <select
                value={selectedComplexity}
                onChange={(e) => setSelectedComplexity(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="simple">简单</option>
                <option value="medium">中等</option>
                <option value="complex">复杂</option>
              </select>
            </div>

            {/* 自动刷新 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                自动刷新
              </label>
              <div className="flex space-x-2">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600"
                />
                <input
                  type="number"
                  value={refreshInterval / 1000}
                  onChange={(e) => setRefreshInterval(Number(e.target.value) * 1000)}
                  disabled={!autoRefresh}
                  className="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50"
                  min="1"
                  max="60"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">秒</span>
              </div>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex flex-wrap gap-3 mt-4">
            <Button
              onClick={loadNetworkData}
              disabled={loading}
              className="flex items-center space-x-2"
            >
              {loading && <LoadingSpinner size="sm" />}
              <span>{loading ? '加载中...' : '刷新数据'}</span>
            </Button>
          </div>
        </div>

        {/* 统计信息 */}
        {statistics && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">统计信息</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <div className="text-sm text-blue-600 dark:text-blue-400">总节点数</div>
                <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                  {statistics.totalNodes}
                </div>
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <div className="text-sm text-green-600 dark:text-green-400">总边数</div>
                <div className="text-2xl font-bold text-green-900 dark:text-green-100">
                  {statistics.totalEdges}
                </div>
              </div>

              <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                <div className="text-sm text-purple-600 dark:text-purple-400">会话数</div>
                <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                  {statistics.sessions}
                </div>
              </div>

              <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                <div className="text-sm text-orange-600 dark:text-orange-400">记忆大小</div>
                <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">
                  {statistics.memorySize}KB
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 网络图可视化 */}
        {networkData && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">网络图</h2>

              <NetworkGraph
                nodes={networkData.nodes}
                edges={networkData.edges}
                width={1200}
                height={600}
                layout="dagre"
                showControls={true}
                onNodeClick={handleNodeClick}
                onEdgeClick={handleEdgeClick}
              />
            </div>
          </div>
        )}

        {/* 空状态 */}
        {!networkData && !loading && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12 text-center">
            <div className="text-gray-500 dark:text-gray-400">
              <div className="text-lg mb-2">暂无数据</div>
              <div className="text-sm">点击"刷新数据"按钮开始可视化</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VisualizationPage;