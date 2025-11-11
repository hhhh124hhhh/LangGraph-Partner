import React from 'react';

const VisualizationPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          数据可视化
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          LangGraph状态流程实时可视化
        </p>
      </div>

      <div className="card p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          可视化页面正在开发中...
        </p>
      </div>
    </div>
  );
};

export default VisualizationPage;