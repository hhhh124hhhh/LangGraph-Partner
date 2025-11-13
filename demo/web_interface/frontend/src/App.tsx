import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from '@stores/index';
import { useWebSocketManager } from '@hooks/useWebSocketManager';

// 页面组件
import ChatPage from '@pages/ChatPage';
import SettingsPage from '@pages/SettingsPage';
// 新页面组件（稍后创建）
import KnowledgePage from '@pages/KnowledgePage';
import PersonaPage from '@pages/PersonaPage';
import MemoryPage from '@pages/MemoryPage';
import AnalyticsPage from '@pages/AnalyticsPage';
import AdvancedPage from '@pages/AdvancedPage';
import HelpPage from '@pages/HelpPage';
// 保留的旧页面（用于兼容）
import HomePage from '@pages/HomePage';
import DemoPage from '@pages/DemoPage';
import VisualizationPage from '@pages/VisualizationPage';
import ComparisonPage from '@pages/ComparisonPage';

// 布局组件
import AppLayout from '@components/Layout/AppLayout';

// 主题提供者
import { ThemeProvider } from '@components/ThemeProvider';

// 加载组件
import LoadingSpinner from '@components/LoadingSpinner';

const App: React.FC = () => {
  const { theme, user, setUser } = useAppStore();
  const {
    isConnected,
    connectionMode,
    connectionQuality,
    refreshConnection,
    getConnectionModeText,
    getConnectionModeIcon
  } = useWebSocketManager({
    autoConnect: true,
    showConnectionNotifications: true
  });

  // 初始化应用
  useEffect(() => {
    // 检查主题设置
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    } else if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', systemTheme);
    } else {
      document.documentElement.classList.toggle('dark', theme === 'dark');
    }

    // 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleThemeChange = () => {
      if (theme === 'system') {
        document.documentElement.classList.toggle('dark', mediaQuery.matches);
      }
    };

    mediaQuery.addEventListener('change', handleThemeChange);

    // 初始化用户信息（可以从本地存储或API获取）
    const initializeUser = async () => {
      try {
        // 这里可以调用API获取用户信息
        // const userInfo = await apiService.getUserInfo();
        // setUser(userInfo);

        // 临时模拟用户信息
        setUser({
          id: 'user_001',
          name: '演示用户',
          email: 'demo@aipartner.com',
          preferences: {
            language: 'zh-CN',
            timezone: 'Asia/Shanghai',
          },
        });
      } catch (error) {
        console.error('初始化用户信息失败:', error);
      }
    };

    initializeUser();

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [theme, setUser]);

  // 监听主题变化
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else if (theme === 'light') {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      localStorage.removeItem('theme');
    }
  }, [theme]);

  // 全局键盘快捷键
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + K 打开搜索
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        // 触发搜索功能
        console.log('打开搜索');
      }

      // Ctrl/Cmd + / 显示快捷键帮助
      if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        // 显示快捷键帮助
        console.log('显示快捷键帮助');
      }

      // Escape 关闭模态框或侧边栏
      if (event.key === 'Escape') {
        // 关闭模态框或侧边栏
        console.log('关闭模态框');
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // 如果用户信息还未加载，显示加载状态
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">正在初始化应用...</p>
        </div>
      </div>
    );
  }

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        {}
        <div className="fixed top-4 left-4 z-50 flex items-center space-x-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-xs text-gray-600 dark:text-gray-400">
            {isConnected ? '已连接' : '连接中...'}
          </span>
        </div>

        <AppLayout>
          <Routes>
            {/* 默认重定向到智能对话页面 */}
            <Route path="/" element={<Navigate to="/chat" replace />} />

            {/* 新的用户导向页面路由 */}
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/persona" element={<PersonaPage />} />
            <Route path="/memory" element={<MemoryPage />} />
            <Route path="/settings" element={<SettingsPage />} />

            {/* 辅助功能页面路由 */}
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/advanced" element={<AdvancedPage />} />
            <Route path="/help" element={<HelpPage />} />

            {/* 兼容旧路由 */}
            <Route path="/home" element={<Navigate to="/chat" replace />} />
            <Route path="/demo" element={<Navigate to="/advanced" replace />} />
            <Route path="/visualization" element={<Navigate to="/analytics" replace />} />
            <Route path="/comparison" element={<Navigate to="/advanced" replace />} />

            {/* 404 页面 */}
            <Route
              path="*"
              element={
                <div className="flex items-center justify-center min-h-[400px]">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                      404
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      页面未找到
                    </p>
                    <button
                      onClick={() => window.history.back()}
                      className="btn btn-primary"
                    >
                      返回
                    </button>
                  </div>
                </div>
              }
            />
          </Routes>
        </AppLayout>
      </div>
    </ThemeProvider>
  );
};

export default App;