import { defineConfig } from "vite";

export default defineConfig({
  server: {
    proxy: {
      "/http-gateway": {
        target: "http://127.0.0.1:17081",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
