/**
 * 记忆中心页面
 * 提供对话记忆的查看、搜索、管理功能
 */

import React, { useState, useEffect } from 'react';
import {
  Clock,
  MessageCircle,
  Brain,
  Search,
  Filter,
  Calendar,
  Tag,
  Trash2,
  Download,
  Eye,
  Archive,
  Star,
  TrendingUp,
  BarChart3,
  Heart,
  Zap
} from 'lucide-react';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { useAppStore } from '@stores/index';
import { cn, formatDateTime, truncateText } from '@utils/index';

interface MemorySession {
  id: string;
  title: string;
  summary: string;
  timestamp: string;
  message_count: number;
  duration_minutes: number;
  key_topics: string[];
  sentiment_score: number;
  importance_score: number;
  tags: string[];
  is_archived: boolean;
  is_favorite: boolean;
}

interface MemoryStats {
  total_sessions: number;
  total_messages: number;
  total_duration_hours: number;
  average_session_length: number;
  most_discussed_topics: { topic: string; count: number }[];
  sentiment_trend: { date: string; score: number }[];
  activity_heatmap: { date: string; count: number }[];
}

const MemoryPage: React.FC = () => {
  const { theme } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState<MemorySession[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'list' | 'grid' | 'timeline'>('list');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedSession, setSelectedSession] = useState<MemorySession | null>(null);
  const [showSessionDetail, setShowSessionDetail] = useState(false);

  // 过滤选项
  const [dateFilter, setDateFilter] = useState<'all' | 'today' | 'week' | 'month' | 'year'>('all');
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'neutral' | 'negative'>('all');
  const [importanceFilter, setImportanceFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    loadMemoryData();
  }, []);

  const loadMemoryData = async () => {
    setLoading(true);
    try {
      // TODO: 调用实际的API
      // const [sessionsData, statsData] = await Promise.all([
      //   apiService.getMemorySessions(),
      //   apiService.getMemoryStats()
      // ]);

      // 模拟数据
      const mockSessions: MemorySession[] = [
        {
          id: '1',
          title: '项目讨论 - AI功能规划',
          summary: '讨论了新功能的实现方案，包括用户画像配置和记忆管理系统的设计。重点讨论了技术架构和用户体验优化。',
          timestamp: '2025-11-13T10:30:00Z',
          message_count: 24,
          duration_minutes: 45,
          key_topics: ['AI功能', '用户体验', '技术架构', '项目规划'],
          sentiment_score: 0.8,
          importance_score: 0.9,
          tags: ['工作', '项目', 'AI'],
          is_archived: false,
          is_favorite: true
        },
        {
          id: '2',
          title: '学习交流 - LangGraph框架',
          summary: '深入学习了LangGraph框架的使用方法，包括状态图设计、节点实现和流程优化。还讨论了实际应用场景。',
          timestamp: '2025-11-12T14:15:00Z',
          message_count: 18,
          duration_minutes: 32,
          key_topics: ['LangGraph', '状态图', '节点设计', '流程优化'],
          sentiment_score: 0.6,
          importance_score: 0.7,
          tags: ['学习', '技术', 'LangGraph'],
          is_archived: false,
          is_favorite: false
        },
        {
          id: '3',
          title: '产品讨论 - 功能优化建议',
          summary: '收集了用户反馈，讨论了产品优化方向。主要关注界面改进、性能提升和新功能开发优先级。',
          timestamp: '2025-11-11T09:00:00Z',
          message_count: 31,
          duration_minutes: 58,
          key_topics: ['用户反馈', '界面优化', '性能提升', '功能规划'],
          sentiment_score: 0.7,
          importance_score: 0.8,
          tags: ['产品', '优化', '用户反馈'],
          is_archived: true,
          is_favorite: false
        }
      ];

      const mockStats: MemoryStats = {
        total_sessions: 156,
        total_messages: 2340,
        total_duration_hours: 48.5,
        average_session_length: 18.6,
        most_discussed_topics: [
          { topic: 'AI功能', count: 42 },
          { topic: '用户体验', count: 38 },
          { topic: '技术架构', count: 31 },
          { topic: '项目规划', count: 28 },
          { topic: '学习交流', count: 25 }
        ],
        sentiment_trend: [
          { date: '2025-11-13', score: 0.75 },
          { date: '2025-11-12', score: 0.68 },
          { date: '2025-11-11', score: 0.72 },
          { date: '2025-11-10', score: 0.65 }
        ],
        activity_heatmap: [
          { date: '2025-11-13', count: 3 },
          { date: '2025-11-12', count: 2 },
          { date: '2025-11-11', count: 4 },
          { date: '2025-11-10', count: 1 }
        ]
      };

      setSessions(mockSessions);
      setStats(mockStats);
    } catch (error) {
      console.error('加载记忆数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSessions = sessions.filter(session => {
    // 搜索过滤
    const matchesSearch = !searchQuery ||
      session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.key_topics.some(topic => topic.toLowerCase().includes(searchQuery.toLowerCase()));

    // 标签过滤
    const matchesTags = selectedTags.length === 0 ||
      selectedTags.some(tag => session.tags.includes(tag));

    // 日期过滤
    const sessionDate = new Date(session.timestamp);
    const now = new Date();
    const matchesDate = dateFilter === 'all' ||
      (dateFilter === 'today' && sessionDate.toDateString() === now.toDateString()) ||
      (dateFilter === 'week' && sessionDate >= new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)) ||
      (dateFilter === 'month' && sessionDate >= new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)) ||
      (dateFilter === 'year' && sessionDate >= new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000));

    // 情感过滤
    const matchesSentiment = sentimentFilter === 'all' ||
      (sentimentFilter === 'positive' && session.sentiment_score > 0.6) ||
      (sentimentFilter === 'neutral' && session.sentiment_score >= 0.4 && session.sentiment_score <= 0.6) ||
      (sentimentFilter === 'negative' && session.sentiment_score < 0.4);

    // 重要性过滤
    const matchesImportance = importanceFilter === 'all' ||
      (importanceFilter === 'high' && session.importance_score > 0.7) ||
      (importanceFilter === 'medium' && session.importance_score >= 0.4 && session.importance_score <= 0.7) ||
      (importanceFilter === 'low' && session.importance_score < 0.4);

    return matchesSearch && matchesTags && matchesDate && matchesSentiment && matchesImportance;
  });

  const toggleFavorite = (sessionId: string) => {
    setSessions(sessions.map(session =>
      session.id === sessionId
        ? { ...session, is_favorite: !session.is_favorite }
        : session
    ));
  };

  const toggleArchive = (sessionId: string) => {
    setSessions(sessions.map(session =>
      session.id === sessionId
        ? { ...session, is_archived: !session.is_archived }
        : session
    ));
  };

  const deleteSession = (sessionId: string) => {
    if (confirm('确定要删除这个会话记录吗？此操作不可撤销。')) {
      setSessions(sessions.filter(session => session.id !== sessionId));
    }
  };

  const exportSessions = () => {
    // TODO: 实现导出功能
    console.log('导出会话记录');
  };

  const getSentimentIcon = (score: number) => {
    if (score > 0.6) return <Heart className="w-4 h-4 text-green-500" />;
    if (score >= 0.4) return <MessageCircle className="w-4 h-4 text-yellow-500" />;
    return <MessageCircle className="w-4 h-4 text-red-500" />;
  };

  const getImportanceColor = (score: number) => {
    if (score > 0.7) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
    if (score >= 0.4) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
    return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
  };

  const allTags = Array.from(new Set(sessions.flatMap(session => session.tags)));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* 页面头部 */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Brain className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                记忆中心
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                查看和管理您的对话历史，洞察交流模式
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              icon={<Filter className="w-4 h-4" />}
            >
              过滤
            </Button>
            <Button
              variant="outline"
              onClick={exportSessions}
              icon={<Download className="w-4 h-4" />}
            >
              导出
            </Button>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">总会话数</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.total_sessions}
                </p>
              </div>
              <MessageCircle className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">总消息数</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.total_messages}
                </p>
              </div>
              <Zap className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">总时长</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.total_duration_hours.toFixed(1)}h
                </p>
              </div>
              <Clock className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">平均会话长度</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.average_session_length.toFixed(1)}min
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      )}

      {/* 搜索和过滤 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* 搜索框 */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="搜索会话内容、主题或标签..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* 视图切换 */}
          <div className="flex items-center gap-2 border border-gray-300 dark:border-gray-600 rounded-lg p-1">
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 rounded transition-colors',
                viewMode === 'list'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400'
              )}
            >
              <MessageCircle className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2 rounded transition-colors',
                viewMode === 'grid'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400'
              )}
            >
              <div className="w-4 h-4 grid grid-cols-2 gap-0.5">
                <div className="bg-current"></div>
                <div className="bg-current"></div>
                <div className="bg-current"></div>
                <div className="bg-current"></div>
              </div>
            </button>
            <button
              onClick={() => setViewMode('timeline')}
              className={cn(
                'p-2 rounded transition-colors',
                viewMode === 'timeline'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400'
              )}
            >
              <Clock className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 过滤器 */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* 日期过滤 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  日期范围
                </label>
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="all">全部时间</option>
                  <option value="today">今天</option>
                  <option value="week">最近一周</option>
                  <option value="month">最近一个月</option>
                  <option value="year">最近一年</option>
                </select>
              </div>

              {/* 情感过滤 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  情感倾向
                </label>
                <select
                  value={sentimentFilter}
                  onChange={(e) => setSentimentFilter(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="all">全部</option>
                  <option value="positive">积极</option>
                  <option value="neutral">中性</option>
                  <option value="negative">消极</option>
                </select>
              </div>

              {/* 重要性过滤 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  重要性
                </label>
                <select
                  value={importanceFilter}
                  onChange={(e) => setImportanceFilter(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="all">全部</option>
                  <option value="high">高</option>
                  <option value="medium">中</option>
                  <option value="low">低</option>
                </select>
              </div>

              {/* 标签过滤 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  标签
                </label>
                <select
                  multiple
                  value={selectedTags}
                  onChange={(e) => setSelectedTags(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {allTags.map(tag => (
                    <option key={tag} value={tag}>{tag}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 会话列表 */}
      <div className="space-y-4">
        {filteredSessions.map((session) => (
          <div
            key={session.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-medium transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {session.title}
                  </h3>
                  {session.is_favorite && (
                    <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  )}
                  {session.is_archived && (
                    <Archive className="w-4 h-4 text-gray-500" />
                  )}
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs font-medium',
                    getImportanceColor(session.importance_score)
                  )}>
                    {session.importance_score > 0.7 ? '重要' : session.importance_score >= 0.4 ? '一般' : '次要'}
                  </span>
                </div>

                <p className="text-gray-600 dark:text-gray-400 mb-3">
                  {truncateText(session.summary, 200)}
                </p>

                <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDateTime(session.timestamp, 'MM-DD HH:mm')}
                  </span>
                  <span className="flex items-center gap-1">
                    <MessageCircle className="w-4 h-4" />
                    {session.message_count} 消息
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {session.duration_minutes} 分钟
                  </span>
                  <span className="flex items-center gap-1">
                    {getSentimentIcon(session.sentiment_score)}
                    {(session.sentiment_score * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex flex-wrap gap-2">
                    {session.key_topics.slice(0, 3).map((topic, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-md text-xs"
                      >
                        {topic}
                      </span>
                    ))}
                    {session.key_topics.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-md text-xs">
                        +{session.key_topics.length - 3}
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {session.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-md text-xs"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 ml-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedSession(session);
                    setShowSessionDetail(true);
                  }}
                  icon={<Eye className="w-4 h-4" />}
                >
                  查看
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleFavorite(session.id)}
                  className={cn(
                    session.is_favorite ? 'text-yellow-500' : 'text-gray-500'
                  )}
                >
                  <Star className={cn("w-4 h-4", session.is_favorite && 'fill-current')} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleArchive(session.id)}
                  className="text-gray-500"
                >
                  <Archive className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteSession(session.id)}
                  className="text-red-500 hover:text-red-600"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 空状态 */}
      {filteredSessions.length === 0 && (
        <div className="text-center py-16">
          <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {searchQuery || selectedTags.length > 0 ? '没有找到匹配的会话' : '还没有任何会话记录'}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {searchQuery || selectedTags.length > 0 ? '尝试调整搜索条件' : '开始对话后，会话记录将显示在这里'}
          </p>
        </div>
      )}
    </div>
  );
};

export default MemoryPage;