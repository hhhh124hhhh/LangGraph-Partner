/**
 * 功能演示页面
 * 提供AI Partner核心功能的交互式演示
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useAppStore } from '@stores/index';
import { useWebSocketManager } from '@hooks/useWebSocketManager';
import { ConnectionMode } from '@services/websocketManager';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { logger } from '@utils/logger';

// 演示场景类型定义
interface DemoScenario {
  scenario_id: string;
  name: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration: string;
  features: string[];
  steps: DemoStep[];
  mock_data?: any;
}

interface DemoStep {
  step_id: string;
  name: string;
  description: string;
  type: 'input' | 'process' | 'output';
  content?: string;
  placeholder?: string;
  options?: string[];
}

interface DemoResult {
  run_id: string;
  scenario_id: string;
  status: 'running' | 'completed' | 'error';
  started_at: string;
  completed_at?: string;
  current_step: number;
  total_steps: number;
  steps: DemoStepResult[];
  metrics?: {
    response_time: number;
    tokens_used: number;
    accuracy: number;
  };
}

interface DemoStepResult {
  step_id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  input?: any;
  output?: any;
  error?: string;
  started_at?: string;
  completed_at?: string;
}

// 模拟演示场景数据
const MOCK_SCENARIOS: DemoScenario[] = [
  {
    scenario_id: 'smart_chat',
    name: '智能对话',
    description: '体验AI Partner的自然语言对话能力，支持上下文理解和多轮对话',
    category: '核心功能',
    difficulty: 'beginner',
    duration: '5-10分钟',
    features: ['自然语言理解', '上下文记忆', '多轮对话'],
    steps: [
      {
        step_id: 'greeting',
        name: '问候',
        description: '向AI Partner打招呼',
        type: 'input',
        placeholder: '请输入问候语，如：你好，AI Partner！'
      },
      {
        step_id: 'question',
        name: '提问',
        description: '询问AI Partner的功能',
        type: 'input',
        placeholder: '请输入问题，如：你能帮助我做什么？'
      },
      {
        step_id: 'response',
        name: 'AI回复',
        description: 'AI Partner的智能回复',
        type: 'output'
      }
    ]
  },
  {
    scenario_id: 'persona_match',
    name: '画像匹配',
    description: '体验用户画像与AI画像的智能匹配，实现个性化对话体验',
    category: '个性化',
    difficulty: 'intermediate',
    duration: '10-15分钟',
    features: ['用户画像分析', 'AI个性匹配', '兼容性评估'],
    steps: [
      {
        step_id: 'user_profile',
        name: '用户画像',
        description: '设置用户画像信息',
        type: 'input',
        placeholder: '描述您的性格特点、兴趣爱好等'
      },
      {
        step_id: 'ai_personality',
        name: 'AI个性',
        description: 'AI Partner根据用户画像调整个性',
        type: 'process'
      },
      {
        step_id: 'compatibility',
        name: '兼容性分析',
        description: '分析用户与AI的个性匹配度',
        type: 'output'
      }
    ]
  },
  {
    scenario_id: 'memory_network',
    name: '记忆网络',
    description: '探索AI Partner的长期记忆能力和知识关联网络',
    category: '智能记忆',
    difficulty: 'advanced',
    duration: '15-20分钟',
    features: ['长期记忆', '知识关联', '智能检索'],
    steps: [
      {
        step_id: 'memory_input',
        name: '信息输入',
        description: '向AI Partner提供需要记忆的信息',
        type: 'input',
        placeholder: '请输入需要AI记住的重要信息'
      },
      {
        step_id: 'association',
        name: '关联分析',
        description: 'AI分析信息间的关联关系',
        type: 'process'
      },
      {
        step_id: 'network_visualization',
        name: '记忆网络',
        description: '展示构建的记忆网络结构',
        type: 'output'
      }
    ]
  },
  {
    scenario_id: 'knowledge_retrieval',
    name: '知识检索',
    description: '体验AI Partner的知识库检索和智能问答能力',
    category: '知识管理',
    difficulty: 'intermediate',
    duration: '10-15分钟',
    features: ['语义搜索', '知识问答', '文档理解'],
    steps: [
      {
        step_id: 'query',
        name: '知识查询',
        description: '提出需要解答的问题',
        type: 'input',
        placeholder: '请输入您想了解的问题'
      },
      {
        step_id: 'search',
        name: '知识检索',
        description: 'AI在知识库中搜索相关信息',
        type: 'process'
      },
      {
        step_id: 'answer',
        name: '智能回答',
        description: '基于检索结果生成回答',
        type: 'output'
      }
    ]
  },
  {
    scenario_id: 'tool_integration',
    name: '工具集成',
    description: '演示AI Partner的工具调用能力，包括计算、搜索、翻译等',
    category: '工具调用',
    difficulty: 'advanced',
    duration: '15-20分钟',
    features: ['计算工具', '网络搜索', '语言翻译'],
    steps: [
      {
        step_id: 'task',
        name: '任务描述',
        description: '描述需要AI完成的任务',
        type: 'input',
        placeholder: '请描述需要完成的任务，如：帮我计算1+1等于几'
      },
      {
        step_id: 'tool_selection',
        name: '工具选择',
        description: 'AI分析任务并选择合适的工具',
        type: 'process'
      },
      {
        step_id: 'execution',
        name: '工具执行',
        description: '执行选定的工具并返回结果',
        type: 'output'
      }
    ]
  }
];

const DemoPage: React.FC = () => {
  const { addNotification } = useAppStore();
  const { isConnected, connectionMode } = useWebSocketManager({
    autoConnect: true,
    showConnectionNotifications: false
  });

  // 状态管理
  const [scenarios] = useState<DemoScenario[]>(MOCK_SCENARIOS);
  const [selectedScenario, setSelectedScenario] = useState<DemoScenario | null>(null);
  const [running, setRunning] = useState(false);
  const [currentResult, setCurrentResult] = useState<DemoResult | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [stepInputs, setStepInputs] = useState<Record<string, string>>({});
  const [completedScenarios, setCompletedScenarios] = useState<Set<string>>(new Set());

  // 运行演示场景
  const runScenario = useCallback(async (scenario: DemoScenario) => {
    setRunning(true);
    setSelectedScenario(scenario);
    setCurrentResult(null);
    setCurrentStep(0);
    setStepInputs({});

    try {
      logger.info(`开始运行演示场景: ${scenario.name}`, 'DemoPage');

      // 生成运行ID
      const runId = `demo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      // 初始化结果
      const result: DemoResult = {
        run_id: runId,
        scenario_id: scenario.scenario_id,
        status: 'running',
        started_at: new Date().toISOString(),
        current_step: 0,
        total_steps: scenario.steps.length,
        steps: scenario.steps.map(step => ({
          step_id: step.step_id,
          name: step.name,
          status: 'pending'
        }))
      };

      setCurrentResult(result);

      addNotification({
        type: 'info',
        title: '演示开始',
        message: `正在运行 "${scenario.name}" 演示`,
        duration: 3000
      });

      // 模拟逐步执行
      for (let i = 0; i < scenario.steps.length; i++) {
        const step = scenario.steps[i];

        // 更新当前步骤
        setCurrentStep(i);
        setCurrentResult(prev => prev ? {
          ...prev,
          current_step: i,
          steps: prev.steps.map((s, idx) =>
            idx === i ? { ...s, status: 'running', started_at: new Date().toISOString() } : s
          )
        } : null);

        // 等待用户输入（如果是输入步骤）
        if (step.type === 'input') {
          // 等待用户输入
          await new Promise<void>((resolve) => {
            const checkInput = () => {
              if (stepInputs[step.step_id]) {
                resolve();
              } else {
                setTimeout(checkInput, 100);
              }
            };
            setTimeout(checkInput, 500);
          });

          // 模拟处理输入
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else if (step.type === 'process') {
          // 模拟处理时间
          await new Promise(resolve => setTimeout(resolve, 2000));
        } else {
          // 输出步骤
          await new Promise(resolve => setTimeout(resolve, 1500));
        }

        // 生成步骤结果
        const stepResult = await generateStepResult(step, stepInputs[step.step_id]);

        // 更新步骤状态
        setCurrentResult(prev => prev ? {
          ...prev,
          steps: prev.steps.map((s, idx) =>
            idx === i ? {
              ...s,
              status: 'completed',
              completed_at: new Date().toISOString(),
              input: stepInputs[step.step_id],
              output: stepResult.output,
              error: stepResult.error
            } : s
          )
        } : null);
      }

      // 完成演示
      const finalResult = {
        ...result,
        status: 'completed' as const,
        completed_at: new Date().toISOString(),
        current_step: scenario.steps.length,
        metrics: {
          response_time: Math.random() * 2000 + 500,
          tokens_used: Math.floor(Math.random() * 1000 + 100),
          accuracy: Math.random() * 0.3 + 0.7 // 70-100%
        }
      };

      setCurrentResult(finalResult);
      setCompletedScenarios(prev => new Set([...prev, scenario.scenario_id]));

      addNotification({
        type: 'success',
        title: '演示完成',
        message: `"${scenario.name}" 演示运行成功`,
        duration: 5000
      });

      logger.info(`演示场景完成: ${scenario.name}`, 'DemoPage');

    } catch (error) {
      logger.error('演示运行失败', 'DemoPage', error);

      setCurrentResult(prev => prev ? {
        ...prev,
        status: 'error',
        completed_at: new Date().toISOString()
      } : null);

      addNotification({
        type: 'error',
        title: '演示失败',
        message: '运行演示时发生错误，请稍后重试',
        duration: 5000
      });
    } finally {
      setRunning(false);
    }
  }, [stepInputs, addNotification]);

  // 生成步骤结果
  const generateStepResult = async (step: DemoStep, input?: string) => {
    switch (step.type) {
      case 'input':
        return {
          output: `已接收输入: ${input}`,
          error: null
        };

      case 'process':
        return {
          output: generateProcessOutput(step.step_id, input),
          error: null
        };

      case 'output':
        return {
          output: generateOutputResult(step.step_id, input),
          error: null
        };

      default:
        return {
          output: '未知步骤类型',
          error: '不支持的步骤类型'
        };
    }
  };

  // 生成处理步骤的输出
  const generateProcessOutput = (stepId: string, input?: string) => {
    const outputs = {
      ai_personality: '🤖 正在分析用户画像...\n📊 匹配度计算中...\n✨ 个性化参数调整完成',
      association: '🔍 正在分析信息关联...\n🕸️ 构建知识网络...\n✅ 关联关系建立完成',
      search: '🔎 正在搜索知识库...\n📚 匹配相关文档...\n💡 生成检索结果',
      tool_selection: '🛠️ 分析任务需求...\n⚡ 选择最佳工具...\n🎯 工具匹配完成'
    };
    return outputs[stepId as keyof typeof outputs] || '处理中...';
  };

  // 生成输出步骤的结果
  const generateOutputResult = (stepId: string, input?: string) => {
    const outputs = {
      response: input
        ? `👋 您好！感谢您的问候！\n\n${input.includes('什么') ? '关于您的问题：' + input + '\n\n' : ''}我是AI Partner，一个智能对话助手。我可以帮助您：\n\n💬 自然语言对话\n🧠 记忆管理\n📚 知识检索\n🛠️ 工具调用\n🎯 个性化服务\n\n很高兴为您服务！有什么可以帮助您的吗？`
        : '👋 您好！我是AI Partner，很高兴为您服务！请告诉我您需要什么帮助。',

      compatibility: `🎭 个性匹配分析结果\n\n📊 匹配度：${(Math.random() * 30 + 70).toFixed(1)}%\n\n✅ 优势匹配：\n• 沟通风格协调\n• 兴趣爱好相似\n• 思维方式互补\n\n💡 优化建议：\n• 增加专业领域交流\n• 保持自然对话节奏\n• 分享更多个人见解`,

      network_visualization: `🕸️ 记忆网络构建完成\n\n📊 网络统计：\n• 节点数量：${Math.floor(Math.random() * 20 + 10)}\n• 连接关系：${Math.floor(Math.random() * 30 + 20)}\n• 网络密度：${(Math.random() * 0.5 + 0.3).toFixed(2)}\n\n🔗 关键关联：\n• 核心概念已识别\n• 语义链接已建立\n• 知识图谱已生成`,

      answer: input
        ? `💡 基于您的问题："${input}"\n\n📚 我为您找到了以下信息：\n\n• 核心答案：这是一个很好的问题，涉及到多个知识领域\n• 相关概念：包括基础理论、实际应用、最新发展等\n• 实用建议：建议您可以从以下几个方面深入了解\n\n📖 如需更详细的信息，请告诉我您的具体需求。`
        : '📚 知识库检索完成，请提供您想要了解的具体问题。',

      execution: '⚡ 工具执行完成\n\n📊 执行结果：\n• 计算精度：99.9%\n• 响应时间：1.2秒\n• 成功率：100%\n\n✅ 任务完成，结果已返回'
    };
    return outputs[stepId as keyof typeof outputs] || '处理完成';
  };

  // 处理步骤输入
  const handleStepInput = (stepId: string, value: string) => {
    setStepInputs(prev => ({ ...prev, [stepId]: value }));
  };

  // 继续到下一步
  const continueToNextStep = () => {
    if (selectedScenario && currentStep < selectedScenario.steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  // 重置演示
  const resetDemo = () => {
    setSelectedScenario(null);
    setCurrentResult(null);
    setCurrentStep(0);
    setStepInputs({});
  };

  // 获取难度颜色
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'advanced': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
      case 'running': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        {/* 页面标题 */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            功能演示
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            体验AI Partner的核心功能特性
          </p>
          <div className="mt-2 flex items-center justify-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {connectionMode === ConnectionMode.WEBSOCKET ? '实时模式' : '离线模式'}
              </span>
            </div>
          </div>
        </div>

        {/* 场景选择 */}
        {!selectedScenario && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarios.map((scenario) => (
              <div key={scenario.scenario_id} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {scenario.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {scenario.description}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(scenario.difficulty)}`}>
                      {scenario.difficulty === 'beginner' ? '初级' :
                       scenario.difficulty === 'intermediate' ? '中级' : '高级'}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                      {scenario.category}
                    </span>
                    {completedScenarios.has(scenario.scenario_id) && (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                        ✓ 已完成
                      </span>
                    )}
                  </div>

                  <div>
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                      ⏱️ {scenario.duration}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      <div className="font-medium mb-1">功能特性：</div>
                      <div className="space-y-1">
                        {scenario.features.map((feature, idx) => (
                          <div key={idx} className="flex items-center space-x-1">
                            <span className="text-green-500">•</span>
                            <span>{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={() => runScenario(scenario)}
                    disabled={running}
                    className="w-full"
                  >
                    {running ? <LoadingSpinner size="sm" /> : '开始演示'}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 演示进行中 */}
        {selectedScenario && currentResult && (
          <div className="space-y-6">
            {/* 演示头部 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    {selectedScenario.name}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    {selectedScenario.description}
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    步骤 {currentStep + 1} / {selectedScenario.steps.length}
                  </div>
                  <Button variant="secondary" onClick={resetDemo}>
                    退出演示
                  </Button>
                </div>
              </div>

              {/* 进度条 */}
              <div className="mt-4">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentStep + 1) / selectedScenario.steps.length) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* 当前步骤 */}
            {currentStep < selectedScenario.steps.length && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  步骤 {currentStep + 1}: {selectedScenario.steps[currentStep].name}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {selectedScenario.steps[currentStep].description}
                </p>

                {/* 输入步骤 */}
                {selectedScenario.steps[currentStep].type === 'input' && (
                  <div className="space-y-4">
                    <textarea
                      value={stepInputs[selectedScenario.steps[currentStep].step_id] || ''}
                      onChange={(e) => handleStepInput(selectedScenario.steps[currentStep].step_id, e.target.value)}
                      placeholder={selectedScenario.steps[currentStep].placeholder}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                      rows={4}
                    />
                    <Button
                      onClick={continueToNextStep}
                      disabled={!stepInputs[selectedScenario.steps[currentStep].step_id]}
                      className="w-full"
                    >
                      继续
                    </Button>
                  </div>
                )}

                {/* 处理步骤 */}
                {selectedScenario.steps[currentStep].type === 'process' && (
                  <div className="flex items-center justify-center py-8">
                    <LoadingSpinner size="lg" />
                    <span className="ml-3 text-gray-600 dark:text-gray-400">正在处理...</span>
                  </div>
                )}

                {/* 输出步骤 */}
                {selectedScenario.steps[currentStep].type === 'output' && (
                  <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <div className="whitespace-pre-wrap text-gray-900 dark:text-white">
                      {currentResult.steps[currentStep]?.output}
                    </div>
                    {currentStep < selectedScenario.steps.length - 1 && (
                      <Button onClick={continueToNextStep} className="mt-4">
                        下一步
                      </Button>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* 步骤列表 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">执行进度</h3>
              <div className="space-y-3">
                {currentResult.steps.map((step, idx) => (
                  <div key={step.step_id} className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full flex items-center justify-center ${getStatusColor(step.status)}`}>
                      {step.status === 'completed' && <span className="text-xs">✓</span>}
                      {step.status === 'running' && <LoadingSpinner size="sm" />}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {step.name}
                      </div>
                      {step.input && (
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          输入: {step.input}
                        </div>
                      )}
                      {step.output && (
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {step.output.length > 100 ? step.output.substring(0, 100) + '...' : step.output}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 演示结果 */}
            {currentResult.status === 'completed' && currentResult.metrics && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">演示统计</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <div className="text-sm text-blue-600 dark:text-blue-400">响应时间</div>
                    <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                      {currentResult.metrics.response_time.toFixed(0)}ms
                    </div>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                    <div className="text-sm text-green-600 dark:text-green-400">Token使用</div>
                    <div className="text-2xl font-bold text-green-900 dark:text-green-100">
                      {currentResult.metrics.tokens_used}
                    </div>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                    <div className="text-sm text-purple-600 dark:text-purple-400">准确率</div>
                    <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                      {(currentResult.metrics.accuracy * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex space-x-4">
                  <Button onClick={resetDemo}>
                    退出演示
                  </Button>
                  <Button variant="secondary" onClick={() => runScenario(selectedScenario)}>
                    重新运行
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DemoPage;