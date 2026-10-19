import { defineConfig, loadEnv } from 'vite';

const defaultApiUrl = 'https://br-noisy-unit-b84wai0k-feedback.compute.c-14.us-east-1.aws.neon.tech/';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const adminToken = env.FEEDBACK_ADMIN_TOKEN;
  if (!adminToken) {
    throw new Error('FEEDBACK_ADMIN_TOKEN is missing. Add it to feedback-dashboard/.env.local.');
  }

  return {
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      proxy: {
        '/api/submissions': {
          target: env.FEEDBACK_API_URL || defaultApiUrl,
          changeOrigin: true,
          rewrite: () => '/',
          configure(proxy) {
            proxy.on('proxyReq', (proxyRequest) => {
              proxyRequest.setHeader('authorization', `Bearer ${adminToken}`);
            });
          },
        },
        '/api/changelog': {
          target: env.FEEDBACK_API_URL || defaultApiUrl,
          changeOrigin: true,
          rewrite: () => '/changelog',
          configure(proxy) {
            proxy.on('proxyReq', (proxyRequest) => {
              proxyRequest.setHeader('authorization', `Bearer ${adminToken}`);
            });
          },
        },
      },
    },
  };
});
