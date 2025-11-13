/**
 * 网络图可视化组件
 * 基于Cytoscape.js实现的交互式网络图
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape';
import { useAppStore } from '@stores/index';
import { logger } from '@utils/logger';

// 布局样式
import dagre from 'cytoscape-dagre';
import cola from 'cytoscape-cola';
import fcose from 'cytoscape-fcose';

// 注册扩展
cytoscape.use(dagre);
cytoscape.use(cola);
cytoscape.use(fcose);

export interface NetworkNode {
  id: string;
  label: string;
  type: 'user' | 'assistant' | 'context' | 'tool' | 'memory' | 'data';
  data?: any;
  position?: { x: number; y: number };
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  type: 'response' | 'context' | 'memory' | 'data_flow' | 'tool_call';
  weight?: number;
  data?: any;
}

export interface NetworkGraphProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  width?: number;
  height?: number;
  layout?: string;
  showControls?: boolean;
  onNodeClick?: (node: NodeSingular) => void;
  onEdgeClick?: (edge: EdgeSingular) => void;
  onDataUpdate?: (nodes: NetworkNode[], edges: NetworkEdge[]) => void;
}

interface GraphStyles {
  node: {
    [key: string]: any;
  };
  edge: {
    [key: string]: any;
  };
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({
  nodes,
  edges,
  width = 800,
  height = 600,
  layout = 'dagre',
  showControls = true,
  onNodeClick,
  onEdgeClick,
  onDataUpdate
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<NodeSingular | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<EdgeSingular | null>(null);
  const [currentLayout, setCurrentLayout] = useState(layout);
  const { addNotification } = useAppStore();

  // 节点样式配置
  const getNodeStyle = useCallback((type: string): any => {
    const baseStyle = {
      width: 60,
      height: 60,
      shape: 'ellipse',
      label: 'data(label)',
      fontSize: 12,
      fontWeight: 'bold',
      textVerticalAlign: 'center',
      textHAlign: 'center',
      color: '#ffffff',
      borderWidth: 2,
      borderColor: '#ffffff',
      overlayOpacity: 0,
      zIndex: 10
    };

    const typeStyles = {
      user: {
        backgroundColor: '#3b82f6',
        shape: 'round-rectangle',
        width: 80,
        height: 50
      },
      assistant: {
        backgroundColor: '#10b981',
        shape: 'hexagon',
        width: 70,
        height: 70
      },
      context: {
        backgroundColor: '#f59e0b',
        shape: 'diamond',
        width: 60,
        height: 60
      },
      tool: {
        backgroundColor: '#8b5cf6',
        shape: 'rectangle',
        width: 100,
        height: 40
      },
      memory: {
        backgroundColor: '#ef4444',
        shape: 'triangle',
        width: 50,
        height: 50
      },
      data: {
        backgroundColor: '#6b7280',
        shape: 'square',
        width: 55,
        height: 55
      }
    };

    return { ...baseStyle, ...typeStyles[type as keyof typeof typeStyles] };
  }, []);

  // 边样式配置
  const getEdgeStyle = useCallback((type: string): any => {
    const baseStyle = {
      width: 2,
      lineColor: '#94a3b8',
      targetArrowColor: '#94a3b8',
      targetArrowShape: 'triangle',
      curveStyle: 'bezier',
      overlayOpacity: 0,
      zIndex: 1
    };

    const typeStyles = {
      response: {
        lineColor: '#3b82f6',
        targetArrowColor: '#3b82f6',
        width: 3
      },
      context: {
        lineColor: '#f59e0b',
        targetArrowColor: '#f59e0b',
        width: 2,
        lineStyle: 'dashed'
      },
      memory: {
        lineColor: '#ef4444',
        targetArrowColor: '#ef4444',
        width: 2,
        lineStyle: 'dotted'
      },
      data_flow: {
        lineColor: '#6b7280',
        targetArrowColor: '#6b7280',
        width: 1
      },
      tool_call: {
        lineColor: '#8b5cf6',
        targetArrowColor: '#8b5cf6',
        width: 2,
        lineStyle: 'dashed'
      }
    };

    return { ...baseStyle, ...typeStyles[type as keyof typeof typeStyles] };
  }, []);

  // 布局配置
  const getLayoutOptions = useCallback((layoutType: string): any => {
    const layouts = {
      dagre: {
        name: 'dagre',
        rankDir: 'TB',
        align: 'UL',
        rankSep: 100,
        nodeSep: 50,
        edgeSep: 10,
        animate: true,
        animationDuration: 1000
      },
      cola: {
        name: 'cola',
        animate: true,
        animationDuration: 1000,
        fit: true,
        nodeSpacing: 50,
        edgeLength: 100
      },
      fcose: {
        name: 'fcose',
        animate: true,
        animationDuration: 1000,
        quality: 'default',
        nodeOverlap: 20,
        idealEdgeLength: 100,
        edgeElasticity: 0.45,
        nestingFactor: 0.1
      },
      concentric: {
        name: 'concentric',
        animate: true,
        animationDuration: 1000,
        concentric: (node: any) => node.degree(),
        minNodeSpacing: 50
      },
      grid: {
        name: 'grid',
        animate: true,
        animationDuration: 1000,
        rows: 3,
        cols: 4,
        fit: true,
        nodeSpacing: 100
      },
      random: {
        name: 'random',
        animate: true,
        animationDuration: 1000,
        fit: true
      }
    };

    return layouts[layoutType as keyof typeof layouts] || layouts.dagre;
  }, []);

  // 初始化Cytoscape
  useEffect(() => {
    if (!containerRef.current || cyRef.current) return;

    try {
      logger.info('初始化网络图', 'NetworkGraph');

      // 创建Cytoscape实例
      const cy = cytoscape({
        container: containerRef.current,
        elements: [
          ...nodes.map(node => ({
            data: {
              id: node.id,
              label: node.label,
              type: node.type,
              ...node.data
            },
            position: node.position
          })),
          ...edges.map(edge => ({
            data: {
              id: edge.id,
              source: edge.source,
              target: edge.target,
              type: edge.type,
              weight: edge.weight || 1,
              ...edge.data
            }
          }))
        ],
        style: [
          {
            selector: 'node',
            style: {
              backgroundColor: '#3b82f6',
              width: 60,
              height: 60,
              shape: 'ellipse',
              label: 'data(label)',
              fontSize: 12,
              fontWeight: 'bold',
              textVerticalAlign: 'center',
              textHAlign: 'center',
              color: '#ffffff',
              borderWidth: 2,
              borderColor: '#ffffff'
            } as any
          },
          {
            selector: 'edge',
            style: {
              width: 2,
              lineColor: '#94a3b8',
              targetArrowColor: '#94a3b8',
              targetArrowShape: 'triangle',
              curveStyle: 'bezier'
            } as any
          }
        ],
        layout: getLayoutOptions(currentLayout),
        minZoom: 0.1,
        maxZoom: 3,
        wheelSensitivity: 0.2,
        boxSelectionEnabled: false,
        autoungrabify: false,
        autolock: false,
        autounselectify: false
      });

      cyRef.current = cy;

      // 应用节点样式
      cy.nodes().forEach(node => {
        const nodeType = node.data('type');
        node.style(getNodeStyle(nodeType));
      });

      // 应用边样式
      cy.edges().forEach(edge => {
        const edgeType = edge.data('type');
        edge.style(getEdgeStyle(edgeType));
      });

      // 事件监听
      cy.on('tap', 'node', (event) => {
        const node = event.target;
        setSelectedNode(node);
        setSelectedEdge(null);

        logger.info(`点击节点: ${node.data('label')}`, 'NetworkGraph');

        if (onNodeClick) {
          onNodeClick(node);
        }
      });

      cy.on('tap', 'edge', (event) => {
        const edge = event.target;
        setSelectedEdge(edge);
        setSelectedNode(null);

        logger.info(`点击边: ${edge.data('type')}`, 'NetworkGraph');

        if (onEdgeClick) {
          onEdgeClick(edge);
        }
      });

      cy.on('tap', (event) => {
        if (event.target === cy) {
          setSelectedNode(null);
          setSelectedEdge(null);
        }
      });

      // 双击节点展开/收缩
      cy.on('dblclick', 'node', (event) => {
        const node = event.target;
        const connectedEdges = node.connectedEdges();
        const connectedNodes = connectedEdges.connectedNodes();

        // 切换邻居节点的显示/隐藏
        connectedNodes.forEach(connectedNode => {
          if (connectedNode !== node) {
            const isVisible = connectedNode.visible();
            connectedNode.style('display', isVisible ? 'none' : 'element');
            connectedNode.connectedEdges().forEach(edge => {
              edge.style('display', isVisible ? 'none' : 'element');
            });
          }
        });
      });

      logger.info('网络图初始化完成', 'NetworkGraph');

    } catch (error) {
      logger.error('网络图初始化失败', 'NetworkGraph', error);
      addNotification({
        type: 'error',
        title: '可视化错误',
        message: '网络图初始化失败',
        duration: 5000
      });
    }

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [nodes, edges, currentLayout, getNodeStyle, getEdgeStyle, getLayoutOptions, onNodeClick, onEdgeClick, addNotification]);

  // 更新布局
  const changeLayout = useCallback((newLayout: string) => {
    if (!cyRef.current) return;

    try {
      setCurrentLayout(newLayout);
      cyRef.current.layout(getLayoutOptions(newLayout)).run();

      logger.info(`切换布局: ${newLayout}`, 'NetworkGraph');

      addNotification({
        type: 'success',
        title: '布局更新',
        message: `已切换到 ${newLayout} 布局`,
        duration: 2000
      });
    } catch (error) {
      logger.error('布局切换失败', 'NetworkGraph', error);
    }
  }, [getLayoutOptions, addNotification]);

  // 导出图片
  const exportImage = useCallback((format: 'png' | 'jpg' | 'svg' = 'png') => {
    if (!cyRef.current) return;

    try {
      const dataUrl = cyRef.current.png({
        output: 'base64uri',
        bg: 'white',
        full: true,
        scale: 2
      });

      // 创建下载链接
      const link = document.createElement('a');
      link.download = `network-graph-${Date.now()}.${format}`;
      link.href = dataUrl;
      link.click();

      logger.info(`导出图片: ${format}`, 'NetworkGraph');

      addNotification({
        type: 'success',
        title: '导出成功',
        message: `网络图已导出为 ${format} 格式`,
        duration: 3000
      });
    } catch (error) {
      logger.error('图片导出失败', 'NetworkGraph', error);

      addNotification({
        type: 'error',
        title: '导出失败',
        message: '图片导出时发生错误',
        duration: 5000
      });
    }
  }, [addNotification]);

  // 重置视图
  const resetView = useCallback(() => {
    if (!cyRef.current) return;

    cyRef.current.fit(undefined, 50);

    logger.info('重置视图', 'NetworkGraph');
  }, []);

  // 适应视图
  const fitView = useCallback(() => {
    if (!cyRef.current) return;

    cyRef.current.fit(undefined, 50);

    logger.info('适应视图', 'NetworkGraph');
  }, []);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* 控制面板 */}
      {showControls && (
        <div className="border-b border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900">
          <div className="flex flex-wrap items-center gap-4">
            {/* 布局选择 */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                布局:
              </label>
              <select
                value={currentLayout}
                onChange={(e) => changeLayout(e.target.value)}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-sm"
              >
                <option value="dagre">分层布局</option>
                <option value="cola">力导向布局</option>
                <option value="fcose">F-Cose布局</option>
                <option value="concentric">同心圆布局</option>
                <option value="grid">网格布局</option>
                <option value="random">随机布局</option>
              </select>
            </div>

            {/* 视图控制 */}
            <div className="flex items-center gap-2">
              <button
                onClick={fitView}
                className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm"
              >
                适应视图
              </button>
              <button
                onClick={resetView}
                className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors text-sm"
              >
                重置视图
              </button>
            </div>

            {/* 导出功能 */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => exportImage('png')}
                className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 transition-colors text-sm"
              >
                导出PNG
              </button>
              <button
                onClick={() => exportImage('svg')}
                className="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors text-sm"
              >
                导出SVG
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 图形容器 */}
      <div
        ref={containerRef}
        style={{ width, height }}
        className="bg-gray-100 dark:bg-gray-900"
      />

      {/* 信息面板 */}
      {(selectedNode || selectedEdge) && (
        <div className="absolute bottom-4 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 max-w-xs">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
            {selectedNode ? '节点信息' : '边信息'}
          </h3>

          {selectedNode && (
            <div className="space-y-1 text-sm">
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">ID:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedNode.data('id')}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">标签:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedNode.data('label')}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">类型:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedNode.data('type')}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">连接数:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedNode.degree()}</span>
              </div>
            </div>
          )}

          {selectedEdge && (
            <div className="space-y-1 text-sm">
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">ID:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedEdge.data('id')}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">源:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedEdge.source().data('label')}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">目标:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedEdge.target().data('label')}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">类型:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedEdge.data('type')}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600 dark:text-gray-400">权重:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedEdge.data('weight')}</span>
              </div>
            </div>
          )}

          <button
            onClick={() => {
              setSelectedNode(null);
              setSelectedEdge(null);
            }}
            className="mt-3 w-full px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm"
          >
            关闭
          </button>
        </div>
      )}

      {/* 统计信息 */}
      <div className="absolute top-4 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3">
        <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
          <div>节点: {nodes.length}</div>
          <div>边: {edges.length}</div>
          <div>布局: {currentLayout}</div>
        </div>
      </div>
    </div>
  );
};

export default NetworkGraph;