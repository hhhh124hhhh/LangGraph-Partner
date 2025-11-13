import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { cn } from '@utils/index';

interface BreadcrumbItem {
  name: string;
  href?: string;
}

const Breadcrumb: React.FC = () => {
  const location = useLocation();

  // 路径到面包屑的映射
  const pathMap: Record<string, BreadcrumbItem[]> = {
    '/chat': [{ name: '智能对话', href: '/chat' }],
    '/knowledge': [{ name: '知识库', href: '/knowledge' }],
    '/persona': [{ name: '画像配置', href: '/persona' }],
    '/memory': [{ name: '记忆中心', href: '/memory' }],
    '/settings': [{ name: '设置', href: '/settings' }],
    '/analytics': [{ name: '使用分析', href: '/analytics' }],
    '/advanced': [{ name: '高级功能', href: '/advanced' }],
    '/help': [{ name: '使用帮助', href: '/help' }],
  };

  // 获取当前路径的面包屑
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const normalizedPath = location.pathname.replace(/\/$/, '');
    return pathMap[normalizedPath] || [{ name: '未知页面' }];
  };

  const breadcrumbs = getBreadcrumbs();

  if (breadcrumbs.length <= 1) {
    return null; // 只有一个页面时不显示面包屑
  }

  // 移动端简化显示
  if (typeof window !== 'undefined' && window.innerWidth < 1024) {
    const lastItem = breadcrumbs[breadcrumbs.length - 1];
    return (
      <nav className="text-sm text-gray-600 dark:text-gray-400">
        <span className="font-medium text-gray-900 dark:text-gray-100">
          {lastItem.name}
        </span>
      </nav>
    );
  }

  return (
    <nav className="flex items-center space-x-1 text-sm text-gray-600 dark:text-gray-400">
      {breadcrumbs.map((item, index) => {
        const isLast = index === breadcrumbs.length - 1;

        return (
          <React.Fragment key={index}>
            {index > 0 && (
              <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-600" />
            )}

            {item.href && !isLast ? (
              <Link
                to={item.href}
                className="hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
              >
                {item.name}
              </Link>
            ) : (
              <span
                className={cn(
                  'font-medium',
                  isLast ? 'text-gray-900 dark:text-gray-100' : ''
                )}
              >
                {item.name}
              </span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export default Breadcrumb;