import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  MessageCircle,
  Database,
  Sparkles,
  Clock,
  Settings,
  BarChart3,
  Wrench,
  HelpCircle,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';

import { useAppStore } from '@stores/index';
import { cn } from '@utils/index';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebar_open, active_panel } = useAppStore();

  const navigation = [
    {
      name: '智能对话',
      href: '/chat',
      icon: MessageCircle,
      description: '与AI伙伴开始个性化对话',
    },
    {
      name: '知识库',
      href: '/knowledge',
      icon: Database,
      description: '管理笔记和知识内容',
    },
    {
      name: '画像配置',
      href: '/persona',
      icon: Sparkles,
      description: '个性化AI伙伴设置',
    },
    {
      name: '记忆中心',
      href: '/memory',
      icon: Clock,
      description: '查看和管理对话记忆',
    },
    {
      name: '设置',
      href: '/settings',
      icon: Settings,
      description: '系统配置和偏好设置',
    },
  ];

  const secondaryNavigation = [
    {
      name: '使用分析',
      href: '/analytics',
      icon: BarChart3,
      description: '查看使用统计和分析',
    },
    {
      name: '高级功能',
      href: '/advanced',
      icon: Wrench,
      description: '专业功能和技术设置',
    },
    {
      name: '使用帮助',
      href: '/help',
      icon: HelpCircle,
      description: '获取使用指南和支持',
    },
  ];

  const handleNavigation = (href: string) => {
    navigate(href);
  };

  return (
    <>
      {/* 移动端遮罩 */}
      {sidebar_open && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => useAppStore.getState().toggleSidebar()}
        />
      )}

      {/* 侧边栏 */}
      <div
        className={cn(
          'fixed left-0 top-0 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ease-in-out z-50',
          sidebar_open ? 'w-64' : 'w-0 lg:w-16',
          'overflow-hidden flex flex-col'
        )}
      >
        {/* 侧边栏头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          {sidebar_open && (
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">AI</span>
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">
                  AI Partner
                </h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  个性化AI对话伙伴
                </p>
              </div>
            </div>
          )}

          <button
            onClick={() => useAppStore.getState().toggleSidebar()}
            className="p-2 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {sidebar_open ? (
              <ChevronDown className="w-5 h-5 transform -rotate-90" />
            ) : (
              <ChevronRight className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* 主导航 */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            {sidebar_open && (
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                核心功能
              </h3>
            )}

            <nav className="space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;

                return (
                  <button
                    key={item.name}
                    onClick={() => handleNavigation(item.href)}
                    className={cn(
                      'w-full flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors group',
                      isActive
                        ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    )}
                    title={!sidebar_open ? item.name : undefined}
                  >
                    <Icon className="w-5 h-5 flex-shrink-0" />
                    {sidebar_open && (
                      <div className="ml-3 text-left">
                        <div className="font-medium">{item.name}</div>
                        {!sidebar_open && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {item.description}
                          </div>
                        )}
                      </div>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* 二级导航 */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            {sidebar_open && (
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                辅助功能
              </h3>
            )}

            <nav className="space-y-1">
              {secondaryNavigation.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;

                return (
                  <button
                    key={item.name}
                    onClick={() => handleNavigation(item.href)}
                    className={cn(
                      'w-full flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors group',
                      isActive
                        ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    )}
                    title={!sidebar_open ? item.name : undefined}
                  >
                    <Icon className="w-5 h-5 flex-shrink-0" />
                    {sidebar_open && (
                      <span className="ml-3">{item.name}</span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* 侧边栏底部 */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          {sidebar_open ? (
            <div className="space-y-3">
              {/* 连接状态 */}
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  系统运行正常
                </span>
              </div>

              {/* 版本信息 */}
              <div className="text-xs text-gray-500 dark:text-gray-400">
                版本: v1.0.0
              </div>
            </div>
          ) : (
            <div className="flex justify-center">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;