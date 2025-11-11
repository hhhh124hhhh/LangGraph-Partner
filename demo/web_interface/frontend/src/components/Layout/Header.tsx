import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu, X, Bell, Settings, Search, User } from 'lucide-react';

import { useAppStore } from '@stores/index';
import { useTheme } from '@components/ThemeProvider';
import { cn } from '@utils/index';
import Button from '@components/Button';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebar_open, toggleSidebar, notifications, user } = useAppStore();
  const { toggleTheme, isDark } = useTheme();

  const unreadCount = notifications.filter(n => !n.read).length;

  const navigation = [
    { name: '首页', href: '/home', icon: '🏠' },
    { name: '演示', href: '/demo', icon: '🎭' },
    { name: '对话', href: '/chat', icon: '💬' },
    { name: '可视化', href: '/visualization', icon: '📊' },
    { name: '对比分析', href: '/comparison', icon: '⚡' },
    { name: '设置', href: '/settings', icon: '⚙️' },
  ];

  const handleNavigation = (href: string) => {
    navigate(href);
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
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* 左侧：移动端菜单按钮和标题 */}
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

          {/* 应用标题 */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AI</span>
            </div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white hidden sm:block">
              AI Partner
            </h1>
          </div>

          {/* 桌面端导航 */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <button
                  key={item.name}
                  onClick={() => handleNavigation(item.href)}
                  className={cn(
                    'nav-item flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                  )}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* 右侧：搜索、通知、用户菜单 */}
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

      {/* 移动端导航 */}
      <div className="md:hidden mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-1 overflow-x-auto">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <button
                key={item.name}
                onClick={() => handleNavigation(item.href)}
                className={cn(
                  'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap',
                  isActive
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                )}
              >
                <span>{item.icon}</span>
                <span>{item.name}</span>
              </button>
            );
          })}
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