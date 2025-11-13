import React from 'react';

const HelpPage: React.FC = () => {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-16">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            📖 使用帮助
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            获取使用指南和技术支持
          </p>
          <div className="bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-800 rounded-lg p-6">
            <p className="text-teal-800 dark:text-teal-200">
              此页面正在开发中，敬请期待...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpPage;