import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAppStore } from '@stores/index';

interface ThemeContextType {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleTheme: () => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const { theme, setTheme: setAppTheme } = useAppStore();

  // 获取当前实际主题
  const getCurrentTheme = (): 'light' | 'dark' => {
    if (theme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return theme;
  };

  const isDark = getCurrentTheme() === 'dark';

  // 设置主题
  const setTheme = (newTheme: 'light' | 'dark' | 'system') => {
    setAppTheme(newTheme);
  };

  // 切换主题
  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark');
    } else if (theme === 'dark') {
      setTheme('light');
    } else {
      // system 模式下，切换到相反的主题
      const current = getCurrentTheme();
      setTheme(current === 'light' ? 'dark' : 'light');
    }
  };

  // 监听系统主题变化
  useEffect(() => {
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => {
        // 当系统主题变化时，会自动反映在DOM上
        document.documentElement.classList.toggle('dark', mediaQuery.matches);
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  // 应用主题到DOM
  useEffect(() => {
    const actualTheme = getCurrentTheme();
    document.documentElement.classList.toggle('dark', actualTheme === 'dark');

    // 设置meta标签
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', actualTheme === 'dark' ? '#1f2937' : '#ffffff');
    }
  }, [theme]);

  const value: ThemeContextType = {
    theme,
    setTheme,
    toggleTheme,
    isDark,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};