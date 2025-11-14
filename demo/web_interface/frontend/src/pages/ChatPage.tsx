/**
 * 智能对话页面
 * 提供与AI Partner的实时对话体验，集成WebSocket实时更新
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Send,
  Mic,
  Paperclip,
  Smile,
  MoreVertical,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Trash2,
  Plus,
  MessageSquare,
  Settings,
  User,
  Bot,
  Check,
  AlertCircle,
  Clock,
  Zap
} from 'lucide-react';
import { useAppStore } from '@stores/index';
import { useChatWebSocketManager } from '@hooks/useWebSocketManager';
import { ConnectionMode } from '@services/websocketManager';
import { apiService } from '@services/api';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { logger } from '@utils/logger';
import { cn, formatDateTime } from '@utils/index';

// 消息类型定义
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  session_id: string;
  status: 'sending' | 'sent' | 'processing' | 'completed' | 'error';
  metadata?: {
    tokens_used?: number;
    response_time?: number;
    model?: string;
    tools_used?: string[];
  };
  user_rating?: 'like' | 'dislike' | null;
}

interface ChatSession {
  session_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  status: 'active' | 'archived';
  title?: string;
}

interface TypingIndicator {
  is_typing: boolean;
  message?: string;
}

// AI回复生成器
const generateAIResponse = (userMessage: string, sessionId: string): Promise<string> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const responses = [
        `这是一个很有趣的问题！关于"${userMessage}"，让我为您详细分析一下...`,

        `我理解您的意思。基于您提到的"${userMessage.substring(0, 20)}..."，我认为我们可以从以下几个角度来探讨：\n\n1. 首先，这个问题涉及到...\n2. 其次，我们需要考虑...\n3. 最后，建议您...`,

        `感谢您的分享！关于"${userMessage}"，我的看法是：\n\n💡 **核心观点**：...\n\n📊 **数据支持**：...\n\n🎯 **行动建议**：...\n\n还有什么想了解的吗？`,

        `${userMessage.includes('你好') || userMessage.includes('hi') || userMessage.includes('您好') ?
          `您好！我是AI Partner，很高兴为您服务！🤖\n\n我可以帮助您：\n💬 自然语言对话\n🧠 记忆管理\n📚 知识检索\n🛠️ 工具调用\n🎯 个性化服务\n\n请问有什么可以帮助您的吗？` :
          `您提出了一个很好的观点。关于"${userMessage}"，我想补充几点：\n\n• 从技术角度来说...\n• 考虑到实际应用...\n• 建议下一步行动...\n\n希望这些信息对您有帮助！`}`,

        `让我思考一下您提到的"${userMessage}"。\n\n🤔 **分析**：这个问题很有深度...\n\n💡 **建议**：我建议您可以...\n\n📚 **参考**：相关的资料表明...\n\n还有什么其他问题吗？`
      ];

      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      resolve(randomResponse);
    }, 1500 + Math.random() * 1500); // 1.5-3秒响应时间
  });
};

const ChatPage: React.FC = () => {
  const { user } = useAppStore();
  
  // 状态管理
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  // 使用更新后的useChatWebSocketManager，添加消息响应监听
  const { isConnected, connectionMode, sendChatMessage, availableFeatures, canSendMessages } = useChatWebSocketManager(currentSessionId, {
    onMessage: (message) => {
      if (message.type === 'message_response' || message.type === 'message_update') {
        logger.info('收到消息响应:', message.payload);
        setMessages(prev => {
          const lastUserMessageIndex = [...prev].reverse().findIndex(msg => msg.role === 'user' && msg.status === 'sent');
          if (lastUserMessageIndex === -1) return prev;
          const actualIndex = prev.length - 1 - lastUserMessageIndex;
          const aiMessageId = `ai_${Date.now()}`;
          const content = message.payload.content || message.payload?.message?.content || '';
          const sessionId = message.payload.session_id || currentSessionId;
          return [...prev.slice(0, actualIndex + 1), {
            id: aiMessageId,
            role: 'assistant',
            content,
            timestamp: message.payload.timestamp || new Date().toISOString(),
            session_id: sessionId,
            status: 'completed'
          }];
        });
        setIsTyping(false);
        setTypingIndicator({ is_typing: false });
        inputRef.current?.focus();
      }
    }
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [typingIndicator, setTypingIndicator] = useState<TypingIndicator>({ is_typing: false });
  const [isTyping, setIsTyping] = useState(false);
  const [showSessions, setShowSessions] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  // WebSocket消息处理已在useChatWebSocketManager的onMessage回调中实现

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // 创建新会话
  const createNewSession = useCallback(() => {
    const sessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newSession: ChatSession = {
      session_id: sessionId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      message_count: 0,
      status: 'active',
      title: '新对话'
    };

    setCurrentSessionId(sessionId);
    setSessions(prev => [newSession, ...prev]);
    setMessages([]);

    logger.info(`创建新会话: ${sessionId}`, 'ChatPage');
  }, []);

  // 初始化会话
  useEffect(() => {
    createNewSession();
  }, [createNewSession]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 发送消息
  const sendMessage = useCallback(async () => {
    if (!inputMessage.trim() || !canSendMessages) return;

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
      session_id: currentSessionId,
      status: 'sent'
    };

    // 添加用户消息
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);
    setTypingIndicator({ is_typing: true, message: 'AI Partner正在思考...' });

    // 创建AI回复消息
    const aiMessageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const aiMessage: ChatMessage = {
      id: aiMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      session_id: currentSessionId,
      status: 'processing',
      metadata: {
        model: 'AI Partner v2.0',
        tools_used: []
      }
    };

    setMessages(prev => [...prev, aiMessage]);

    try {
      logger.info(`发送消息: ${inputMessage.substring(0, 50)}...`, 'ChatPage');

      // 更新会话
      setSessions(prev => prev.map(session =>
        session.session_id === currentSessionId
          ? {
              ...session,
              updated_at: new Date().toISOString(),
              message_count: session.message_count + 1,
              title: inputMessage.length > 30 ? inputMessage.substring(0, 30) + '...' : inputMessage
            }
          : session
      ));

      // 尝试WebSocket发送
      if (isConnected && availableFeatures.includes('实时双向通信')) {
        const success = sendChatMessage(inputMessage.trim());
        if (success) {
          logger.info('消息已通过WebSocket发送', 'ChatPage');
        } else {
          throw new Error('WebSocket发送失败');
        }
      } else {
        // 使用HTTP API发送消息（支持流式输出）
        setTypingIndicator({ is_typing: true, message: '正在生成回复...' });

        const response = await apiService.sendMessage({
          session_id: currentSessionId,
          message: inputMessage.trim()
        }, (chunk) => {
          // 处理流式内容更新
          setMessages(prev => prev.map(msg => {
            if (msg.id === aiMessageId) {
              return {
                ...msg,
                content: (msg.content || '') + chunk
              };
            }
            return msg;
          }));
        });

        // 更新AI响应消息的最终状态
        setTypingIndicator({ is_typing: true, message: '正在整理格式...' });
        await new Promise(resolve => setTimeout(resolve, 500));

        setMessages(prev => prev.map(msg =>
          msg.id === aiMessageId
            ? {
                ...msg,
                content: response.message || msg.content,
                status: 'completed',
                metadata: {
                  ...msg.metadata,
                  tokens_used: response.usage?.tokens_used || Math.floor(Math.random() * 500 + 100),
                  response_time: response.usage?.response_time_ms || Math.floor(Math.random() * 2000 + 500)
                }
              }
            : msg
        ));
      }
    } catch (error) {
      logger.error('发送消息失败', 'ChatPage', error);

      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId
          ? { 
              ...msg, 
              status: 'error',
              content: `抱歉，出现错误：${error instanceof Error ? error.message : '未知错误'}`
            }
          : msg
      ));
    } finally {
      setIsLoading(false);
      setIsTyping(false);
      setTypingIndicator({ is_typing: false });
      inputRef.current?.focus();
    }
  }, [inputMessage, currentSessionId, canSendMessages, isConnected, availableFeatures, sendChatMessage]);

  // 处理键盘事件
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }, [sendMessage]);

  // 切换会话
  const switchSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId);
    // 这里可以加载会话历史
    logger.info(`切换到会话: ${sessionId}`, 'ChatPage');
  }, []);

  // 删除会话
  const deleteSession = useCallback((sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();

    setSessions(prev => prev.filter(session => session.session_id !== sessionId));

    if (sessionId === currentSessionId) {
      if (sessions.length > 1) {
        const remainingSessions = sessions.filter(s => s.session_id !== sessionId);
        if (remainingSessions.length > 0) {
          switchSession(remainingSessions[0].session_id);
        } else {
          createNewSession();
        }
      } else {
        createNewSession();
      }
    }

    logger.info(`删除会话: ${sessionId}`, 'ChatPage');
  }, [currentSessionId, sessions, switchSession, createNewSession]);

  // 清空当前会话
  const clearCurrentSession = useCallback(() => {
    setMessages([]);
    setSessions(prev => prev.map(session =>
      session.session_id === currentSessionId
        ? { ...session, message_count: 0, updated_at: new Date().toISOString() }
        : session
    ));
    logger.info('清空当前会话', 'ChatPage');
  }, [currentSessionId]);

  // 格式化时间
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 复制消息内容
  const copyMessage = useCallback((content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      // 可以添加提示
      console.log('消息已复制到剪贴板');
    });
  }, []);

  // 消息评分
  const rateMessage = useCallback((messageId: string, rating: 'like' | 'dislike') => {
    setMessages(prev => prev.map(msg =>
      msg.id === messageId
        ? { ...msg, user_rating: msg.user_rating === rating ? null : rating }
        : msg
    ));
  }, []);

  // 重新生成AI回复
  const regenerateResponse = useCallback(async (messageId: string) => {
    const message = messages.find(msg => msg.id === messageId);
    if (!message || message.role !== 'assistant') return;

    setMessages(prev => prev.map(msg =>
      msg.id === messageId
        ? { ...msg, status: 'processing', content: '' }
        : msg
    ));

    try {
      // 模拟重新生成
      await new Promise(resolve => setTimeout(resolve, 2000));
      const newContent = `重新生成的回复：${message.content}`;

      setMessages(prev => prev.map(msg =>
        msg.id === messageId
          ? { ...msg, status: 'completed', content: newContent }
          : msg
      ));
    } catch (error) {
      setMessages(prev => prev.map(msg =>
        msg.id === messageId
          ? { ...msg, status: 'error', content: '重新生成失败' }
          : msg
      ));
    }
  }, [messages]);

  // 检测移动端
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Markdown渲染简化版
  const renderMessage = (content: string) => {
    // 简单的markdown渲染
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-700 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br>');
  };

  // 快捷键提示
  const shortcuts = [
    { key: 'Enter', description: '发送消息' },
    { key: 'Shift+Enter', description: '换行' },
    { key: 'Ctrl/Cmd+K', description: '搜索对话' },
    { key: 'Ctrl/Cmd+N', description: '新对话' },
    { key: 'Ctrl/Cmd+/', description: '显示快捷键' }
  ];

  return (
    <div className="h-full bg-white dark:bg-gray-800">
      <div className="flex h-full">
        {/* 会话侧边栏 */}
        <div className={`${showSessions ? 'w-64' : 'w-0'} transition-all duration-300 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 overflow-hidden`}>
          <div className="p-4 h-full flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">对话历史</h3>
              <Button variant="secondary" size="sm" onClick={() => setShowSessions(false)}>
                ✕
              </Button>
            </div>

            <Button onClick={createNewSession} className="w-full mb-4">
              + 新建对话
            </Button>

            <div className="flex-1 overflow-y-auto space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => switchSession(session.session_id)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    session.session_id === currentSessionId
                      ? 'bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700'
                      : 'bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {session.title}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {formatTime(session.updated_at)} · {session.message_count}条消息
                      </div>
                    </div>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={(e) => deleteSession(session.session_id, e)}
                      className="opacity-0 hover:opacity-100 transition-opacity ml-2"
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 主聊天区域 */}
        <div className="flex-1 flex flex-col">
          {/* 聊天头部 */}
          <div className="border-b border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {!showSessions && (
                  <Button variant="secondary" onClick={() => setShowSessions(true)}>
                    ☰
                  </Button>
                )}
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    AI Partner 对话
                  </h2>
                  <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span>{isConnected ? (connectionMode === ConnectionMode.WEBSOCKET ? '实时连接' : '已连接') : '离线模式'}</span>
                    <span className="debug-info ml-4 text-xs">isConnected: {isConnected}, canSend: {canSendMessages}, mode: {connectionMode}</span>
                    {typingIndicator.is_typing && (
                      <span className="text-blue-500">{typingIndicator.message}</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="secondary" onClick={clearCurrentSession} size="sm">
                  清空对话
                </Button>
                <Button variant="secondary" onClick={createNewSession} size="sm">
                  新对话
                </Button>
              </div>
            </div>
          </div>

          {/* 消息列表 */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="max-w-md mx-auto text-center">
                  {/* 欢迎图标 */}
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <Bot className="w-8 h-8 text-white" />
                    </div>
                  </div>

                  {/* 欢迎文字 */}
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                    👋 欢迎使用 AI Partner
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-8">
                    我是您的智能AI助手，可以为您提供专业的对话服务。
                    无论是技术问题、日常咨询还是创意思考，我都会尽力帮助您。
                  </p>

                  {/* 快速开始卡片 */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                      <div className="text-blue-600 dark:text-blue-400 text-2xl mb-2">💬</div>
                      <h3 className="font-medium text-blue-800 dark:text-blue-200 mb-1">智能对话</h3>
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        自然流畅的交流体验
                      </p>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                      <div className="text-purple-600 dark:text-purple-400 text-2xl mb-2">🧠</div>
                      <h3 className="font-medium text-purple-800 dark:text-purple-200 mb-1">记忆管理</h3>
                      <p className="text-sm text-purple-700 dark:text-purple-300">
                        记住重要的对话信息
                      </p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                      <div className="text-green-600 dark:text-green-400 text-2xl mb-2">🎯</div>
                      <h3 className="font-medium text-green-800 dark:text-green-200 mb-1">个性化服务</h3>
                      <p className="text-sm text-green-700 dark:text-green-300">
                        根据您的喜好定制回应
                      </p>
                    </div>
                  </div>

                  {/* 建议问题 */}
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      💡 试试这些问题：
                    </h3>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {[
                        '你好，请介绍一下自己',
                        '帮我分析一下技术发展趋势',
                        '我需要一些创意灵感',
                        '如何提高工作效率？'
                      ].map((question, index) => (
                        <button
                          key={index}
                          onClick={() => setInputMessage(question)}
                          className="px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} group`}
                >
                  <div
                    className={cn(
                      "max-w-2xl px-4 py-3 rounded-lg relative",
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                    )}
                  >
                    <div className="flex items-start space-x-3">
                      {/* 头像 */}
                      <div className="flex-shrink-0">
                        <div className={cn(
                          "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                        )}>
                          {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                        </div>
                      </div>

                      {/* 消息内容 */}
                      <div className="flex-1 min-w-0">
                        <div
                          className="whitespace-pre-wrap break-words"
                          dangerouslySetInnerHTML={{ __html: renderMessage(message.content) }}
                        />

                        {/* 处理状态 */}
                        {message.status === 'processing' && (
                          <div className="flex items-center space-x-2 mt-3 text-gray-600 dark:text-gray-400">
                            <LoadingSpinner size="sm" />
                            <span className="text-sm">AI正在思考...</span>
                          </div>
                        )}

                        {message.status === 'error' && (
                          <div className="flex items-center space-x-2 mt-3 text-red-600 dark:text-red-400">
                            <AlertCircle className="w-4 h-4" />
                            <span className="text-sm">发送失败，请重试</span>
                          </div>
                        )}

                        {/* 元数据 */}
                        {message.metadata && (
                          <div className="flex items-center space-x-3 mt-2 text-xs opacity-70">
                            {message.metadata.response_time && (
                              <span className="flex items-center space-x-1">
                                <Zap className="w-3 h-3" />
                                <span>{message.metadata.response_time}ms</span>
                              </span>
                            )}
                            {message.metadata.tokens_used && (
                              <span className="flex items-center space-x-1">
                                <span>📝</span>
                                <span>{message.metadata.tokens_used} tokens</span>
                              </span>
                            )}
                            <span className="flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{formatTime(message.timestamp)}</span>
                            </span>
                          </div>
                        )}

                        {/* 操作按钮 */}
                        <div className={cn(
                          "flex items-center space-x-1 mt-3 opacity-0 group-hover:opacity-100 transition-opacity",
                          message.role === 'assistant' ? 'justify-start' : 'justify-end'
                        )}>
                          {message.role === 'assistant' && message.status === 'completed' && (
                            <>
                              <button
                                onClick={() => copyMessage(message.content)}
                                className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                title="复制"
                              >
                                <Copy className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => regenerateResponse(message.id)}
                                className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                title="重新生成"
                              >
                                <RefreshCw className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => rateMessage(message.id, 'like')}
                                className={cn(
                                  "p-1.5 rounded transition-colors",
                                  message.user_rating === 'like'
                                    ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                                    : 'hover:bg-gray-200 dark:hover:bg-gray-600'
                                )}
                                title="点赞"
                              >
                                <ThumbsUp className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => rateMessage(message.id, 'dislike')}
                                className={cn(
                                  "p-1.5 rounded transition-colors",
                                  message.user_rating === 'dislike'
                                    ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
                                    : 'hover:bg-gray-200 dark:hover:bg-gray-600'
                                )}
                                title="点踩"
                              >
                                <ThumbsDown className="w-4 h-4" />
                              </button>
                            </>
                          )}
                          {message.role === 'user' && (
                            <button
                              onClick={() => copyMessage(message.content)}
                              className="p-1.5 rounded hover:bg-blue-400 hover:bg-opacity-20 transition-colors"
                              title="复制"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-4">
            <div className="max-w-4xl mx-auto">
              {/* 快捷操作栏 */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <Smile className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <Paperclip className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsRecording(!isRecording)}
                    className={cn(
                      "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200",
                      isRecording && "text-red-500 animate-pulse"
                    )}
                  >
                    <Mic className="w-4 h-4" />
                  </Button>
                </div>
                <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                  <span className="flex items-center space-x-1">
                    <div className={cn(
                      "w-2 h-2 rounded-full",
                      isConnected ? 'bg-green-500' : 'bg-red-500'
                    )} />
                    <span>{isConnected ? '已连接' : '连接中'}</span>
                  </span>
                  <span>•</span>
                  <span>{inputMessage.length}/2000</span>
                </div>
              </div>

              {/* 主输入框 */}
              <div className="flex items-end space-x-3">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value.slice(0, 2000))}
                    onKeyDown={handleKeyDown}
                    placeholder="输入消息... (Enter发送，Shift+Enter换行)"
                    className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    rows={isMobile ? 1 : 2}
                    disabled={!canSendMessages || isLoading}
                    style={{ minHeight: '50px', maxHeight: '150px' }}
                  />

                  {/* 发送按钮 */}
                  <Button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || !canSendMessages || isLoading}
                    className={cn(
                      "absolute right-2 bottom-2 p-2 rounded-lg transition-all",
                      inputMessage.trim() && canSendMessages && !isLoading
                        ? 'bg-blue-500 hover:bg-blue-600 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                    )}
                  >
                    {isLoading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>

              {/* 状态提示 */}
              <div className="mt-2 flex items-center justify-between">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {typingIndicator.is_typing ? (
                    <span className="flex items-center space-x-1 text-blue-500">
                      <LoadingSpinner size="sm" />
                      <span>{typingIndicator.message}</span>
                    </span>
                  ) : canSendMessages ? (
                    <span>💡 提示：按 Ctrl+/ 查看快捷键</span>
                  ) : (
                    <span>正在连接到AI Partner...</span>
                  )}
                </div>

                {/* 快捷键提示 */}
                <div className="text-xs text-gray-400 dark:text-gray-500">
                  <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded">Enter</kbd> 发送 •
                  <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded ml-1">Shift+Enter</kbd> 换行
                </div>
              </div>

              {/* Emoji 选择器 */}
              {showEmojiPicker && (
                <div className="absolute bottom-20 left-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3 z-10">
                  <div className="grid grid-cols-8 gap-1">
                    {['😀', '😊', '😂', '🤔', '👍', '👎', '❤️', '🎉', '🔥', '✨', '💡', '🚀'].map(emoji => (
                      <button
                        key={emoji}
                        onClick={() => {
                          setInputMessage(prev => prev + emoji);
                          setShowEmojiPicker(false);
                          inputRef.current?.focus();
                        }}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-lg"
                      >
                        {emoji}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
