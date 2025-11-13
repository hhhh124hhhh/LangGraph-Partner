import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, BookOpen, Brain, Heart, Star, TrendingUp, Users, Clock, Zap, Sparkles } from 'lucide-react';

import Button from '@components/Button';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const userFeatures = [
    {
      icon: MessageSquare,
      title: '智能对话',
      description: '个性化交流，深度理解你的需求，提供贴心建议和帮助',
      href: '/chat',
      color: 'primary',
      action: '开始对话'
    },
    {
      icon: BookOpen,
      title: '知识管理',
      description: '智能整理笔记，快速检索信息，让知识更有价值',
      href: '/settings',
      color: 'secondary',
      action: '管理笔记'
    },
    {
      icon: Brain,
      title: '画像配置',
      description: '个性化设置，AI越用越懂你，打造专属智能助手',
      href: '/settings',
      color: 'accent',
      action: '个性化设置'
    },
    {
      icon: Heart,
      title: '记忆功能',
      description: '对话记忆，连贯交流，让每次对话都更加贴心',
      href: '/chat',
      color: 'rose',
      action: '查看记忆'
    },
  ];

  const userStats = [
    { label: '对话满意度', value: '4.9/5', icon: Star },
    { label: '活跃用户', value: '10K+', icon: Users },
    { label: '日均对话', value: '50K+', icon: MessageSquare },
    { label: '响应速度', value: '<1秒', icon: Clock },
  ];

  return (
    <div className="space-y-8">
      {/* 英雄区域 - 重新设计为对话工作台 */}
      <div className="text-center py-12 bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-900 dark:to-gray-800 rounded-2xl">
        <div className="mb-4">
          <Sparkles className="w-12 h-12 text-primary-600 dark:text-primary-400 mx-auto" />
        </div>

        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-4">
          AI Partner
          <span className="block text-2xl md:text-3xl text-primary-600 dark:text-primary-400 mt-2">
            你的专属智能助手
          </span>
        </h1>

        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto mb-8">
          每一次对话都更懂你。智能对话、知识管理、个性化记忆，让AI成为你生活和工作的贴心伙伴。
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            size="lg"
            icon={<MessageSquare className="w-5 h-5" />}
            onClick={() => navigate('/chat')}
            className="transform hover:scale-105 transition-transform"
          >
            立即对话
          </Button>
          <Button
            variant="outline"
            size="lg"
            icon={<Brain className="w-5 h-5" />}
            onClick={() => navigate('/settings')}
          >
            个性化设置
          </Button>
        </div>

        <div className="mt-8 text-sm text-gray-500 dark:text-gray-400">
          ✨ 全新AI记忆功能，让对话更连贯自然
        </div>
      </div>

      {/* 核心功能 - 用户导向 */}
      <div>
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-4">
          为你而设计的智能体验
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
          不仅仅是聊天，更是贴心的AI伙伴。每一次互动都为你量身定制。
        </p>

        <div className="grid grid-responsive">
          {userFeatures.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="card p-6 hover:shadow-medium transition-all duration-300 cursor-pointer group"
                onClick={() => navigate(feature.href)}
              >
                <div
                  className={`w-14 h-14 bg-gradient-to-br from-${feature.color}-100 to-${feature.color}-50 dark:from-${feature.color}-900/20 dark:to-${feature.color}-900/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                >
                  <Icon className={`w-7 h-7 text-${feature.color}-600 dark:text-${feature.color}-400`} />
                </div>

                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>

                <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
                  {feature.description}
                </p>

                <Button variant="ghost" size="sm" className="group-hover:text-primary-600 dark:group-hover:text-primary-400">
                  {feature.action} →
                </Button>
              </div>
            );
          })}
        </div>
      </div>

      {/* 用户受益指标 */}
      <div className="bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-800 dark:to-gray-700 rounded-xl p-8">
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-8">
          用户说好才是真的好
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {userStats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="text-center">
                <div className="flex justify-center mb-3">
                  <div className="w-12 h-12 bg-white dark:bg-gray-800 rounded-xl flex items-center justify-center shadow-sm">
                    <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                </div>

                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
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

      {/* 技术亮点 - 作为差异化优势 */}
      <div className="bg-gray-50 dark:bg-gray-800/30 rounded-xl p-8">
        <div className="text-center mb-8">
          <Zap className="w-8 h-8 text-primary-600 dark:text-primary-400 mx-auto mb-3" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            AI Partner 独特优势
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            基于 LangGraph 的先进技术，为你带来更智能的对话体验
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              🧠 智能画像系统
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• 动态学习你的说话风格和偏好</li>
              <li>• 个性化推荐，越用越懂你</li>
              <li>• 上下文感知的贴心回应</li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              🕸️ 记忆网络
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• 记住重要的对话内容</li>
              <li>• 长期记忆让交流更连贯</li>
              <li>• 智能提取关键信息</li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              ⚡ LangGraph 引擎
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• 更智能的对话流程管理</li>
              <li>• 快速准确的响应处理</li>
              <li>• 稳定可靠的对话体验</li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              📚 知识管理
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• 智能整理和分类笔记</li>
              <li>• 快速检索相关信息</li>
              <li>• 知识图谱化展示</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 行动召唤 - 强调对话 */}
      <div className="text-center py-12 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl text-white">
        <h2 className="text-3xl font-bold mb-4">
          准备好开始对话了吗？
        </h2>

        <p className="text-lg mb-8 text-white/90">
          让AI Partner成为你的贴心伙伴，开启智能对话新体验
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            size="lg"
            variant="secondary"
            icon={<MessageSquare className="w-5 h-5" />}
            onClick={() => navigate('/chat')}
            className="bg-white text-primary-600 hover:bg-gray-100"
          >
            立即开始对话
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-white text-white hover:bg-white hover:text-primary-600"
            icon={<Brain className="w-5 h-5" />}
            onClick={() => navigate('/settings')}
          >
            个性化设置
          </Button>
        </div>

        <div className="mt-6 text-sm text-white/80">
          完全免费 · 无需注册 · 即时体验
        </div>
      </div>
    </div>
  );
};

export default HomePage;