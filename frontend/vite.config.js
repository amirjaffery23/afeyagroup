//import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
//import vueJsx from '@vitejs/plugin-vue-jsx'
import path from 'path';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    build: {
        sourcemap: true, // Enable source maps for production builds
        chunkSizeWarningLimit: 1500, // Increase limit to 1.5 MB
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        port: 3000, // For the Docker container
        host: '0.0.0.0', // Allow external access
        proxy: {
            '/api': {
                target: 'http://backend:8000', // Backend URL
                changeOrigin: true,
                secure: false,
                rewrite: (path) => {
                    console.log(`Proxying ${path}`);
                    return path;
                }
            },
        },
    },
});
