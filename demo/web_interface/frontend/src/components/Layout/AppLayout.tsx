import React, { ReactNode } from 'react';
import { Outlet } from 'react-router-dom';
import { useAppStore } from '@stores/index';
import { cn } from '@utils/index';

import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';

interface AppLayoutProps {
  children?: ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { sidebar_open } = useAppStore();

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* 侧边栏 */}
      <Sidebar />

      {/* 主内容区域 */}
      <div
        className={cn(
          'flex-1 flex flex-col transition-all duration-300 ease-in-out',
          sidebar_open ? 'ml-64' : 'ml-0 lg:ml-16'
        )}
      >
        {/* 顶部导航 */}
        <Header />

        {/* 页面内容 */}
        <main className="flex-1 overflow-auto">
          <div className="container-fluid p-4 md:p-6">
            {children || <Outlet />}
          </div>
        </main>

        {/* 底部 */}
        <Footer />
      </div>
    </div>
  );
};

export default AppLayout;