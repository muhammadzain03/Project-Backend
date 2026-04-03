import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig} from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  envDir: path.resolve(__dirname, '..'),
  server: {
    proxy: {
      '/auth': { target: 'http://127.0.0.1:5000', changeOrigin: true },
      '/user': { target: 'http://127.0.0.1:5000', changeOrigin: true },
    },
  },
});
