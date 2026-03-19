import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Element Plus 样式（组件通过自动导入）
import 'element-plus/dist/index.css'

// 按需引入图标 - 只注册实际使用的图标
import {
  // 布局相关
  FirstAidKit,
  DataLine,
  ChatDotRound,
  Document,
  Reading,
  Warning,
  User,
  Setting,
  Menu,
  ArrowDown,
  Grid,
  ArrowRight,
  Calendar,
  View,
  InfoFilled,
  Refresh,
  // AI医生
  Cpu,
  Search,
  Delete,
  Food,
  Basketball,
  Position,
  // 管理员
  Monitor,
  Picture,
  FullScreen,
  UserFilled,
  SwitchButton,
  Close,
  Clock,
  // 体检预约
  Location,
  // 健康管理
  TrendCharts,
  Moon,
  Lightning,
  Timer,
  // 报告分析
  // ...已有图标
} from '@element-plus/icons-vue'

// 全局样式
import './assets/main.css'

const app = createApp(App)

// 按需注册图标
const icons = {
  FirstAidKit,
  DataLine,
  ChatDotRound,
  Document,
  Reading,
  Warning,
  User,
  Setting,
  Menu,
  ArrowDown,
  Grid,
  ArrowRight,
  Calendar,
  View,
  InfoFilled,
  Refresh,
  Cpu,
  Search,
  Delete,
  Food,
  Basketball,
  Position,
  Monitor,
  Picture,
  FullScreen,
  UserFilled,
  SwitchButton,
  Close,
  Clock,
  Location,
  TrendCharts,
  Moon,
  Lightning,
  Timer,
}

for (const [key, component] of Object.entries(icons)) {
  app.component(key, component)
}

// 安装插件（按顺序）
app.use(createPinia())
app.use(router)

// 挂载应用
app.mount('#app')
