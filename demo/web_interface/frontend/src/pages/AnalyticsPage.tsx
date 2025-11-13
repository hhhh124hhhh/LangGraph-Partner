import React from 'react';

const AnalyticsPage: React.FC = () => {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-16">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            📊 使用分析
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            查看您的使用统计和分析数据
          </p>
          <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-6">
            <p className="text-orange-800 dark:text-orange-200">
              此页面正在开发中，敬请期待...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;