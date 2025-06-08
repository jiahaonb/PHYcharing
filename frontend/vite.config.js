import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { resolve } from 'path'
import fs from 'fs'

// 尝试加载配置覆盖文件
let serverConfig = {
  host: '0.0.0.0',
  port: 3001,
  proxy: {
    '/api/v1': {
      target: 'http://0.0.0.0:8000',
      changeOrigin: true,
    }
  }
};

try {
  const overrideFile = resolve(__dirname, 'vite.config.override.js');
  if (fs.existsSync(overrideFile)) {
    const override = await import('./vite.config.override.js');
    serverConfig = override.serverConfig;
  }
} catch (e) {
  console.log('使用默认服务器配置');
}

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '');
  
  // 如果有环境变量配置，优先使用
  if (env.VITE_DEV_PORT) {
    serverConfig.port = parseInt(env.VITE_DEV_PORT);
  }
  if (env.VITE_DEV_HOST) {
    serverConfig.host = env.VITE_DEV_HOST;
  }
  if (env.VITE_API_PREFIX && env.VITE_API_BASE_URL) {
    serverConfig.proxy = {
      [env.VITE_API_PREFIX]: {
        target: env.VITE_API_BASE_URL,
        changeOrigin: true,
      }
    };
  }

  return {
    plugins: [
      vue(),
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    server: {
      ...serverConfig,
      strictPort: true, // 端口冲突时不自动切换
    }
  }
}) 