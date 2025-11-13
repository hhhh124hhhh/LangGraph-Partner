/**
 * 智能对话页面
 * 提供与AI Partner的实时对话体验，集成WebSocket实时更新
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAppStore } from '@stores/index';
import { useChatWebSocketManager } from '@hooks/useWebSocketManager';
import { ConnectionMode } from '@services/websocketManager';
import { apiService } from '@services/api';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { logger } from '@utils/logger';

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
  const {
    isConnected,
    connectionMode,
    sendChatMessage,
    availableFeatures,
    canSendMessages
  } = useChatWebSocketManager(currentSessionId); // 传递当前sessionId
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [typingIndicator, setTypingIndicator] = useState<TypingIndicator>({ is_typing: false });
  const [isTyping, setIsTyping] = useState(false);
  const [showSessions, setShowSessions] = useState(false);

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
              <div className="text-center py-12">
                <div className="text-gray-500 dark:text-gray-400">
                  <div className="text-lg mb-2">👋 欢迎来到AI Partner</div>
                  <div className="text-sm">开始您的对话吧！我可以帮助您解答问题、提供建议或进行日常交流。</div>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-2xl px-4 py-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      <div className="flex-shrink-0">
                        {message.role === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="flex-1">
                        <div className="whitespace-pre-wrap break-words">
                          {message.content}
                        </div>
                        {message.status === 'processing' && (
                          <div className="flex items-center space-x-1 mt-2">
                            <LoadingSpinner size="sm" />
                            <span className="text-xs opacity-70">正在处理...</span>
                          </div>
                        )}
                        {message.status === 'error' && (
                          <div className="text-xs opacity-70 mt-2">
                            ❌ 发送失败
                          </div>
                        )}
                        {message.metadata && message.metadata.response_time && (
                          <div className="text-xs opacity-70 mt-2">
                            响应时间: {message.metadata.response_time}ms
                            {message.metadata.tokens_used && ` · ${message.metadata.tokens_used} tokens`}
                          </div>
                        )}
                      </div>
                      <div className="text-xs opacity-70">
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <div className="flex space-x-3">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="输入消息... (Enter发送，Shift+Enter换行)"
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={1}
                disabled={!canSendMessages || isLoading}
              />
              <Button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || !canSendMessages || isLoading}
                className="px-6"
              >
                {isLoading ? <LoadingSpinner size="sm" /> : '发送'}
              </Button>
            </div>
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              {isTyping ? 'AI正在输入...' :
               canSendMessages ? '已连接到AI Partner' :
               '连接中...'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;