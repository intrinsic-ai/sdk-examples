import {defineConfig, loadEnv} from 'vite';

export default defineConfig(({mode}) => {
  // Load env vars (e.g. from command line or .env file)
  const env = loadEnv(mode, process.cwd(), '');

  const TARGET_URL = env.HMI_SERVER_URL;
  const AUTH_TOKEN = env.HMI_AUTH_TOKEN;

  if (!TARGET_URL || !AUTH_TOKEN) {
    console.error('\nERROR: Env variables Missing');
    console.error('   You must set HMI_SERVER_URL and HMI_AUTH_TOKEN.');
    console.error(
      '   Example: HMI_SERVER_URL=https://... HMI_AUTH_TOKEN=... npm run dev\n',
    );
    process.exit(1);
  }

  console.log(`\nHMI SETUP:`);
  console.log(`   Target: ${TARGET_URL}`);
  console.log(`   Status: Authenticated Proxy Active\n`);

  return {
    server: {
      proxy: {
        '/http-gateway': {
          target: TARGET_URL,
          changeOrigin: true,
          secure: true, // Required for https
          configure: (proxy) => {
            proxy.on('proxyReq', (proxyReq) => {
              if (AUTH_TOKEN) {
                proxyReq.setHeader('Cookie', `auth-proxy=${AUTH_TOKEN}`);
              }
            });
          },
        },
      },
    },
  };
});
