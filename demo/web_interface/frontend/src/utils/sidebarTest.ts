/**
 * 导航栏重构验证脚本
 * 用于验证新的用户导向导航结构
 */

// 新的导航结构
export const newNavigationStructure = {
  mainNavigation: [
    {
      name: '智能对话',
      href: '/chat',
      icon: 'MessageCircle',
      description: '与AI伙伴开始个性化对话',
      priority: 1,
    },
    {
      name: '知识库',
      href: '/knowledge',
      icon: 'Database',
      description: '管理笔记和知识内容',
      priority: 2,
    },
    {
      name: '画像配置',
      href: '/persona',
      icon: 'Brain',
      description: '个性化AI伙伴设置',
      priority: 3,
    },
    {
      name: '记忆中心',
      href: '/memory',
      icon: 'Clock',
      description: '查看和管理对话记忆',
      priority: 4,
    },
    {
      name: '设置',
      href: '/settings',
      icon: 'Settings',
      description: '系统配置和偏好设置',
      priority: 5,
    },
  ],
  secondaryNavigation: [
    {
      name: '使用分析',
      href: '/analytics',
      icon: 'BarChart3',
      description: '查看使用统计和分析',
      priority: 1,
    },
    {
      name: '高级功能',
      href: '/advanced',
      icon: 'Wrench',
      description: '专业功能和技术设置',
      priority: 2,
    },
    {
      name: '使用帮助',
      href: '/help',
      icon: 'HelpCircle',
      description: '获取使用指南和支持',
      priority: 3,
    },
  ],
};

// 旧的导航结构（用于对比）
export const oldNavigationStructure = {
  mainNavigation: [
    {
      name: '首页概览',
      href: '/home',
      description: '查看系统概览和快速入口',
    },
    {
      name: '功能演示',
      href: '/demo',
      description: '体验AI Partner核心功能',
    },
    {
      name: '智能对话',
      href: '/chat',
      description: '与AI进行个性化对话',
    },
    {
      name: '数据可视化',
      href: '/visualization',
      description: '查看LangGraph状态流程',
    },
    {
      name: '对比分析',
      href: '/comparison',
      description: 'LangGraph vs Coze技术对比',
    },
    {
      name: '系统设置',
      href: '/settings',
      description: '配置系统参数和偏好',
    },
  ],
  secondaryNavigation: [
    {
      name: '用户社区',
      href: '/community',
      description: '与其他用户交流',
    },
    {
      name: '使用文档',
      href: '/docs',
      description: '查看详细文档',
    },
    {
      name: '帮助中心',
      href: '/help',
      description: '获取帮助和支持',
    },
  ],
};

// 重构改进验证
export const improvements = {
  userOrientation: {
    before: '技术演示导向，如"功能演示"、"数据可视化"',
    after: '用户日常使用导向，如"智能对话"、"知识库"',
    impact: '提高用户友好度和使用频率',
  },
  terminology: {
    before: '技术术语较多，如"LangGraph状态流程"',
    after: '简化表述，如"使用统计和分析"',
    impact: '降低用户理解门槛',
  },
  priority: {
    before: '首页概览优先，核心功能排后',
    after: '智能对话设为核心，放在第一位',
    impact: '突出主要使用场景',
  },
  structure: {
    before: '功能分类不够清晰',
    after: '明确区分"核心功能"和"辅助功能"',
    impact: '更好的信息架构',
  },
};

// 路由映射验证
export const routeMappings = {
  new: {
    '/chat': 'ChatPage',
    '/knowledge': 'KnowledgePage',
    '/persona': 'PersonaPage',
    '/memory': 'MemoryPage',
    '/settings': 'SettingsPage',
    '/analytics': 'AnalyticsPage',
    '/advanced': 'AdvancedPage',
    '/help': 'HelpPage',
  },
  redirects: {
    '/home': '/chat',
    '/demo': '/advanced',
    '/visualization': '/analytics',
    '/comparison': '/advanced',
  },
};

export default {
  newNavigationStructure,
  oldNavigationStructure,
  improvements,
  routeMappings,
};