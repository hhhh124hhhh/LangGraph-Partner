import React from 'react';

const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          系统设置
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          配置系统参数和用户偏好
        </p>
      </div>

      <div className="card p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          设置页面正在开发中...
        </p>
      </div>
    </div>
  );
};

export default SettingsPage;