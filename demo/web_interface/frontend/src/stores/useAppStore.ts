import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { devtools } from 'zustand/middleware';
import { UIState, Notification, LangGraphState, MemoryNetwork, DemoScenario } from '@types/index';

interface AppState extends UIState {
  // 用户相关
  user: {
    id: string;
    name: string;
    email: string;
    preferences: Record<string, any>;
  } | null;

  // 当前会话
  currentSession: {
    id: string;
    title: string;
    started_at: string;
  } | null;

  // 实时数据状态
  realtimeData: {
    langGraphState: LangGraphState | null;
    memoryNetwork: MemoryNetwork | null;
    lastUpdate: string;
  };

  // 演示相关
  demo: {
    activeScenario: DemoScenario | null;
    currentStep: number;
    completedSteps: string[];
    progress: number;
  };

  // 应用设置
  settings: {
    autoSave: boolean;
    notifications: boolean;
    soundEffects: boolean;
    compactMode: boolean;
    showAdvanced: boolean;
  };

  // Actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setActivePanel: (panel: string) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  setUser: (user: AppState['user']) => void;
  setCurrentSession: (session: AppState['currentSession']) => void;
  updateRealtimeData: (data: Partial<AppState['realtimeData']>) => void;
  setActiveScenario: (scenario: DemoScenario | null) => void;
  setCurrentStep: (step: number) => void;
  markStepCompleted: (stepId: string) => void;
  updateDemoProgress: (progress: number) => void;
  updateSettings: (settings: Partial<AppState['settings']>) => void;
  setLoading: (key: string, loading: boolean) => void;
  setGlobalLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // 初始状态
        theme: 'system',
        sidebar_open: true,
        active_panel: 'chat',
        notifications: [],
        loading: {
          global: false,
          components: {},
        },
        user: null,
        currentSession: null,
        realtimeData: {
          langGraphState: null,
          memoryNetwork: null,
          lastUpdate: new Date().toISOString(),
        },
        demo: {
          activeScenario: null,
          currentStep: 0,
          completedSteps: [],
          progress: 0,
        },
        settings: {
          autoSave: true,
          notifications: true,
          soundEffects: false,
          compactMode: false,
          showAdvanced: false,
        },

        // Actions
        setTheme: (theme) => set({ theme }),

        toggleSidebar: () => set((state) => ({ sidebar_open: !state.sidebar_open })),

        setSidebarOpen: (open) => set({ sidebar_open: open }),

        setActivePanel: (panel) => set({ active_panel: panel }),

        addNotification: (notification) => {
          const id = `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          const newNotification: Notification = {
            ...notification,
            id,
            timestamp: new Date().toISOString(),
            read: false,
          };

          set((state) => ({
            notifications: [newNotification, ...state.notifications].slice(0, 50), // 最多保留50条
          }));

          // 自动标记为已读（5秒后）
          setTimeout(() => {
            get().markNotificationRead(id);
          }, 5000);
        },

        markNotificationRead: (id) =>
          set((state) => ({
            notifications: state.notifications.map((n) =>
              n.id === id ? { ...n, read: true } : n
            ),
          })),

        clearNotifications: () => set({ notifications: [] }),

        setUser: (user) => set({ user }),

        setCurrentSession: (session) => set({ currentSession: session }),

        updateRealtimeData: (data) =>
          set((state) => ({
            realtimeData: {
              ...state.realtimeData,
              ...data,
              lastUpdate: new Date().toISOString(),
            },
          })),

        setActiveScenario: (scenario) =>
          set((state) => ({
            demo: {
              ...state.demo,
              activeScenario: scenario,
              currentStep: scenario ? 0 : state.demo.currentStep,
              progress: scenario ? 0 : state.demo.progress,
              completedSteps: scenario ? [] : state.demo.completedSteps,
            },
          })),

        setCurrentStep: (step) =>
          set((state) => ({
            demo: {
              ...state.demo,
              currentStep: step,
            },
          })),

        markStepCompleted: (stepId) =>
          set((state) => ({
            demo: {
              ...state.demo,
              completedSteps: [...state.demo.completedSteps, stepId],
            },
          })),

        updateDemoProgress: (progress) =>
          set((state) => ({
            demo: {
              ...state.demo,
              progress,
            },
          })),

        updateSettings: (newSettings) =>
          set((state) => ({
            settings: {
              ...state.settings,
              ...newSettings,
            },
          })),

        setLoading: (key, loading) =>
          set((state) => ({
            loading: {
              ...state.loading,
              components: {
                ...state.loading.components,
                [key]: loading,
              },
            },
          })),

        setGlobalLoading: (loading) =>
          set((state) => ({
            loading: {
              ...state.loading,
              global: loading,
            },
          })),
      }),
      {
        name: 'ai-partner-app-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebar_open: state.sidebar_open,
          settings: state.settings,
          user: state.user,
        }),
      }
    ),
    {
      name: 'app-store',
    }
  )
);