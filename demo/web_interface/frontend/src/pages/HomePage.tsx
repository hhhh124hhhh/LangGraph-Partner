import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, MessageSquare, BarChart3, Zap, Star, TrendingUp, Users, Shield } from 'lucide-react';

import Button from '@components/Button';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: MessageSquare,
      title: '个性化对话',
      description: '基于用户画像的智能对话，提供精准的个性化体验',
      href: '/chat',
      color: 'primary',
    },
    {
      icon: BarChart3,
      title: '实时可视化',
      description: 'LangGraph状态流程实时展示，清晰了解AI思维过程',
      href: '/visualization',
      color: 'secondary',
    },
    {
      icon: Zap,
      title: '技术对比',
      description: '深度对比分析LangGraph与传统方案的差异和优势',
      href: '/comparison',
      color: 'accent',
    },
  ];

  const stats = [
    { label: '响应准确率', value: '98.5%', icon: TrendingUp },
    { label: '用户满意度', value: '4.9/5', icon: Star },
    { label: '活跃用户', value: '10K+', icon: Users },
    { label: '系统稳定性', value: '99.9%', icon: Shield },
  ];

  return (
    <div className="space-y-8">
      {/* 英雄区域 */}
      <div className="text-center py-12">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          AI Partner
          <span className="block text-2xl md:text-3xl text-primary-600 dark:text-primary-400 mt-2">
            基于 LangGraph 的智能体演示平台
          </span>
        </h1>

        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto mb-8">
          体验最先进的AI智能体技术，通过个性化的对话、实时的状态可视化和深度的技术对比，
          全面了解LangGraph在AI应用开发中的强大能力。
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            size="lg"
            icon={<Play className="w-5 h-5" />}
            onClick={() => navigate('/demo')}
          >
            开始演示
          </Button>
          <Button
            variant="outline"
            size="lg"
            icon={<MessageSquare className="w-5 h-5" />}
            onClick={() => navigate('/chat')}
          >
            立即对话
          </Button>
        </div>
      </div>

      {/* 核心功能 */}
      <div>
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
          核心功能展示
        </h2>

        <div className="grid grid-responsive">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="card p-6 hover:shadow-medium transition-shadow cursor-pointer"
                onClick={() => navigate(feature.href)}
              >
                <div
                  className={`w-12 h-12 bg-${feature.color}-100 dark:bg-${feature.color}-900/20 rounded-lg flex items-center justify-center mb-4`}
                >
                  <Icon className={`w-6 h-6 text-${feature.color}-600 dark:text-${feature.color}-400`} />
                </div>

                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>

                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {feature.description}
                </p>

                <Button variant="ghost" size="sm">
                  了解更多 →
                </Button>
              </div>
            );
          })}
        </div>
      </div>

      {/* 数据统计 */}
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-8">
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-8">
          平台数据
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="text-center">
                <div className="flex justify-center mb-2">
                  <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center">
                    <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  </div>
                </div>

                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                  {stat.value}
                </div>

                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 技术亮点 */}
      <div>
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-8">
          技术亮点
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="card p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              🧠 智能画像系统
            </h3>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>• 动态用户画像构建和更新</li>
              <li>• 多维度个性特征分析</li>
              <li>• 上下文感知的智能响应</li>
              <li>• 持续学习的对话优化</li>
            </ul>
          </div>

          <div className="card p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              ⚡ LangGraph 引擎
            </h3>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>• 状态机驱动的流程控制</li>
              <li>• 实时状态可视化展示</li>
              <li>• 灵活的工作流编排</li>
              <li>• 高并发处理能力</li>
            </ul>
          </div>

          <div className="card p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              🕸️ 记忆网络
            </h3>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>• 语义关联的知识图谱</li>
              <li>• 长期记忆管理</li>
              <li>• 智能知识检索</li>
              <li>• 上下文相关性分析</li>
            </ul>
          </div>

          <div className="card p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              📊 实时监控
            </h3>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>• 性能指标实时监控</li>
              <li>• 错误追踪和日志分析</li>
              <li>• 用户行为分析</li>
              <li>• 系统健康状态监控</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 行动召唤 */}
      <div className="text-center py-12 bg-gradient-primary rounded-xl text-white">
        <h2 className="text-3xl font-bold mb-4">
          准备好体验下一代AI智能体了吗？
        </h2>

        <p className="text-lg mb-8 text-white/90">
          立即开始演示，探索AI Partner的强大功能
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            size="lg"
            variant="secondary"
            icon={<Play className="w-5 h-5" />}
            onClick={() => navigate('/demo')}
          >
            开始探索
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-white text-white hover:bg-white hover:text-primary-600"
            onClick={() => navigate('/docs')}
          >
            查看文档
          </Button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;