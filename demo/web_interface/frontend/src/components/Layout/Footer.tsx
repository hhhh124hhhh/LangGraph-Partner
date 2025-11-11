import React from 'react';
import { Github, ExternalLink, Heart } from 'lucide-react';
import { useAppStore } from '@stores/index';

const Footer: React.FC = () => {
  const { user } = useAppStore();

  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
        {/* 左侧：状态信息 */}
        <div className="flex items-center space-x-4">
          <span>
            {user ? `欢迎, ${user.name}` : '未登录'}
          </span>
          <span className="hidden sm:inline">
            LangGraph v1.0.0
          </span>
        </div>

        {/* 右侧：链接和版权 */}
        <div className="flex items-center space-x-4">
          <a
            href="https://github.com/langchain-ai/langgraph"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
          >
            <Github className="w-4 h-4" />
            <span className="hidden sm:inline">GitHub</span>
          </a>

          <a
            href="https://python.langchain.com/docs/langgraph"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            <span className="hidden sm:inline">文档</span>
          </a>

          <div className="flex items-center space-x-1">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-red-500" />
            <span>by AI Partner Team</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;