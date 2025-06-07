// 自动生成的Vite配置覆盖
// 修改 config.yaml 后会自动更新

export const serverConfig = {
  host: '0.0.0.0',
  port: 8088,
  proxy: {
    '/api/v1': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
};
