import React from 'react';

const PersonaPage: React.FC = () => {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-16">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            🧠 画像配置
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            个性化您的AI伙伴设置
          </p>
          <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-6">
            <p className="text-purple-800 dark:text-purple-200">
              此页面正在开发中，敬请期待...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonaPage;