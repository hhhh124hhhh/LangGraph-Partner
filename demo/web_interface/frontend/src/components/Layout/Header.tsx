import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu, X, Bell, Settings, Search, User, Home } from 'lucide-react';

import { useAppStore } from '@stores/index';
import { useTheme } from '@components/ThemeProvider';
import { cn } from '@utils/index';
import Button from '@components/Button';
import Breadcrumb from './Breadcrumb';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebar_open, toggleSidebar, notifications, user } = useAppStore();
  const { toggleTheme, isDark } = useTheme();

  const unreadCount = notifications.filter(n => !n.read).length;

  // 获取页面标题
  const getPageTitle = () => {
    const pathMap: Record<string, string> = {
      '/chat': '智能对话',
      '/knowledge': '知识库',
      '/persona': '画像配置',
      '/memory': '记忆中心',
      '/settings': '设置',
      '/analytics': '使用分析',
      '/advanced': '高级功能',
      '/help': '使用帮助',
    };
    const normalizedPath = location.pathname.replace(/\/$/, '');
    return pathMap[normalizedPath] || 'AI Partner';
  };

  const handleQuickHome = () => {
    navigate('/chat');
  };

  const handleSearch = () => {
    // 实现搜索功能
    console.log('打开搜索');
  };

  const handleNotifications = () => {
    // 显示通知面板
    console.log('显示通知面板');
  };

  const handleUserMenu = () => {
    // 显示用户菜单
    console.log('显示用户菜单');
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between">
          {/* 左侧：移动端菜单按钮和页面信息 */}
          <div className="flex items-center space-x-4">
            {/* 移动端菜单按钮 */}
            <button
              onClick={toggleSidebar}
              className="lg:hidden p-2 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {sidebar_open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            {/* 桌面端侧边栏切换 */}
            <button
              onClick={toggleSidebar}
              className="hidden lg:block p-2 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* 应用标识和页面信息 */}
            <div className="flex items-center space-x-3">
              {/* Logo按钮 - 点击返回对话页面 */}
              <button
                onClick={handleQuickHome}
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="返回智能对话"
              >
                <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AI</span>
                </div>
                <div className="hidden sm:block text-left">
                  <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                    AI Partner
                  </h1>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {getPageTitle()}
                  </p>
                </div>
              </button>

              {/* 面包屑导航 */}
              <div className="hidden lg:block">
                <Breadcrumb />
              </div>

              {/* 移动端页面标题 */}
              <div className="lg:hidden sm:block">
                <Breadcrumb />
              </div>
            </div>
          </div>

          {/* 右侧：搜索、主题切换、通知、用户菜单 */}
          <div className="flex items-center space-x-2">
            {/* 搜索按钮 */}
            <button
              onClick={handleSearch}
              className="p-2 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="搜索 (Ctrl+K)"
            >
              <Search className="w-5 h-5" />
            </button>

            {/* 主题切换 */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title={isDark ? '切换到亮色主题' : '切换到暗色主题'}
            >
              {isDark ? '🌙' : '☀️'}
            </button>

            {/* 通知按钮 */}
            <div className="relative">
              <button
                onClick={handleNotifications}
                className="p-2 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative"
                title="通知"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                )}
              </button>
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </div>

            {/* 用户菜单 */}
            <div className="relative">
              <button
                onClick={handleUserMenu}
                className="flex items-center space-x-2 p-2 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="用户菜单"
              >
                <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-medium">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
                <ChevronDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

// ChevronDown 图标组件
const ChevronDown: React.FC<{ className?: string }> = ({ className = '' }) => (
  <svg className={`w-4 h-4 ${className}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

export default Header;