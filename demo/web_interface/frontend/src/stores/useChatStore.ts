import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { ChatMessage, ChatRequest, ChatResponse, Persona, LangGraphState } from '@typesdef/index';

// 移除自定义的PersistedChatState类型，使用Zustand的默认类型

export interface ChatState {
  // 会话管理
  sessions: Array<{
    id: string;
    title: string;
    messages: ChatMessage[];
    created_at: string;
    updated_at: string;
    persona: Persona | null;
  }>;

  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;

  // 实时状态
  langGraphState: LangGraphState | null;
  isStreaming: boolean;
  streamingContent: string;

  // 输入状态
  inputMessage: string;
  inputHistory: string[];
  historyIndex: number;

  // Actions
  createSession: (title?: string) => string;
  switchSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void;
  sendMessage: (request: ChatRequest) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setLangGraphState: (state: LangGraphState | null) => void;
  setStreaming: (isStreaming: boolean, content?: string) => void;
  appendStreamingContent: (content: string) => void;
  setInputMessage: (message: string) => void;
  addToHistory: (message: string) => void;
  navigateHistory: (direction: 'up' | 'down') => void;
  clearCurrentSession: () => void;
  clearAllSessions: () => void;
}

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
      // 初始状态
      sessions: [],
      currentSessionId: null,
      isLoading: false,
      error: null,
      langGraphState: null,
      isStreaming: false,
      streamingContent: '',
      inputMessage: '',
      inputHistory: [],
      historyIndex: -1,

      // Actions
      createSession: (title = '新对话') => {
        const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const newSession = {
          id: sessionId,
          title,
          messages: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          persona: null,
        };

        set((state) => ({
          sessions: [newSession, ...state.sessions],
          currentSessionId: sessionId,
          inputMessage: '',
          inputHistory: [],
          historyIndex: -1,
        }));

        return sessionId;
      },

      switchSession: (sessionId) => {
        set({
          currentSessionId: sessionId,
          inputMessage: '',
          historyIndex: -1,
        });
      },

      deleteSession: (sessionId) => {
        set((state) => {
          const newSessions = state.sessions.filter(s => s.id !== sessionId);
          const newCurrentId = state.currentSessionId === sessionId
            ? (newSessions.length > 0 ? newSessions[0].id : null)
            : state.currentSessionId;

          return {
            sessions: newSessions,
            currentSessionId: newCurrentId,
          };
        });
      },

      updateSessionTitle: (sessionId, title) => {
        set((state) => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? { ...session, title, updated_at: new Date().toISOString() }
              : session
          ),
        }));
      },

      addMessage: (message) => {
        set((state) => {
          if (!state.currentSessionId) return state;

          const updatedSessions = state.sessions.map(session =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  messages: [...session.messages, message],
                  updated_at: new Date().toISOString(),
                }
              : session
          );

          return { sessions: updatedSessions };
        });
      },

      updateMessage: (messageId, updates) => {
        set((state) => ({
          sessions: state.sessions.map(session =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  messages: session.messages.map(msg =>
                    msg.id === messageId ? { ...msg, ...updates } : msg
                  ),
                  updated_at: new Date().toISOString(),
                }
              : session
          ),
        }));
      },

      sendMessage: async (request) => {
        const state = get();
        if (!state.currentSessionId) {
          state.createSession();
        }

        // 添加用户消息
        const userMessage: ChatMessage = {
          id: `msg_${Date.now()}_user`,
          role: 'user',
          content: request.message,
          timestamp: new Date().toISOString(),
          session_id: state.currentSessionId || '',
        };

        get().addMessage(userMessage);
        get().setLoading(true);
        get().setError(null);
        get().setStreaming(true);

        try {
          // 这里会调用API服务
          const { apiService } = await import('@services/index');
          const response = await apiService.sendMessage({
            ...request,
            session_id: state.currentSessionId!,
          });

          // 添加助手消息
          const assistantMessage: ChatMessage = {
            id: `msg_${Date.now()}_assistant`,
            role: 'assistant',
            content: response.message,
            timestamp: new Date().toISOString(),
            session_id: state.currentSessionId!,
            metadata: {
              persona_influence: response.persona_response.applied_traits.join(', '),
              confidence: response.persona_response.confidence_score,
              related_memories: response.state_info.execution_path,
            },
          };

          get().addMessage(assistantMessage);
          get().setLangGraphState(response.state_info as any);

        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '发送消息失败';
          get().setError(errorMessage);

          // 添加错误消息
          const errorChatMessage: ChatMessage = {
            id: `msg_${Date.now()}_error`,
            role: 'assistant',
            content: `抱歉，出现错误：${errorMessage}`,
            timestamp: new Date().toISOString(),
            session_id: state.currentSessionId!,
          };

          get().addMessage(errorChatMessage);
        } finally {
          get().setLoading(false);
          get().setStreaming(false);
        }
      },

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      setLangGraphState: (state) => set({ langGraphState: state }),

      setStreaming: (isStreaming, content = '') => set({
        isStreaming,
        streamingContent: content,
      }),

      appendStreamingContent: (content) => set((state) => ({
        streamingContent: state.streamingContent + content,
      })),

      setInputMessage: (message) => set({ inputMessage: message }),

      addToHistory: (message) => set((state) => ({
        inputHistory: [message, ...state.inputHistory.slice(0, 49)], // 保留最近50条
        historyIndex: -1,
      })),

      navigateHistory: (direction) => {
        const state = get();
        const { inputHistory, historyIndex, inputMessage } = state;

        if (direction === 'up') {
          // 向上浏览历史记录
          if (historyIndex < inputHistory.length - 1) {
            const newIndex = historyIndex + 1;
            set({
              inputMessage: inputHistory[newIndex],
              historyIndex: newIndex,
            });
          }
        } else {
          // 向下浏览历史记录
          if (historyIndex > 0) {
            const newIndex = historyIndex - 1;
            set({
              inputMessage: inputHistory[newIndex],
              historyIndex: newIndex,
            });
          } else if (historyIndex === 0) {
            // 回到当前输入
            set({
              inputMessage: inputMessage,
              historyIndex: -1,
            });
          }
        }
      },

      clearCurrentSession: () => {
        const state = get();
        if (!state.currentSessionId) return;

        set((prevState) => ({
          sessions: prevState.sessions.map(session =>
            session.id === state.currentSessionId
              ? { ...session, messages: [], updated_at: new Date().toISOString() }
              : session
          ),
        }));
      },

      clearAllSessions: () => set({
        sessions: [],
        currentSessionId: null,
        inputMessage: '',
        inputHistory: [],
        historyIndex: -1,
      }),
    }),
    {
      name: 'chat-store',
      storage: {
        getItem: (name) => {
          const item = localStorage.getItem(name);
          return item ? JSON.parse(item) : null;
        },
        setItem: (name, value) => {
          localStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name) => {
          localStorage.removeItem(name);
        },
      },
      // 使用默认的partialize行为，持久化整个状态
    })
  )
);