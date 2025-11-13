/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_WS_URL: string;
  // 可以添加其他环境变量的类型定义
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}