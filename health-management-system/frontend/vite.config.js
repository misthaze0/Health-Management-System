import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // 自动导入 Element Plus 组件
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: false // 禁用类型声明文件生成，提高启动速度
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: false // 禁用类型声明文件生成
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 19000,
    // 优化开发服务器性能
    hmr: {
      overlay: false // 禁用错误遮罩，提高性能
    },
    // 预编译依赖，加快页面加载
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'element-plus',
        'echarts',
        'vue-echarts',
        'dayjs',
        'axios'
      ]
    },
    proxy: {
      // 注意：顺序很重要，更具体的路径应该放在前面
      '/ai-service': {
        target: 'http://localhost:19002',  // AI服务端口与start-all.ps1配置一致
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai-service/, '')
      },

      '/api': {
        target: 'http://localhost:19001',  // 后端服务地址
        changeOrigin: true
        // 注意：不需要 rewrite，因为后端 context-path 也是 /api
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    // 启用代码压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 移除console
        drop_debugger: true // 移除debugger
      }
    },
    rollupOptions: {
      output: {
        // 代码分割策略
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts', 'vue-echarts'],
          'vendor': ['vue', 'vue-router', 'pinia', 'axios'],
          'utils': ['dayjs']
        },
        // 优化 chunk 文件名
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(assetInfo.name)) {
            return 'img/[name]-[hash][extname]'
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return 'fonts/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        }
      }
    }
  }
})
