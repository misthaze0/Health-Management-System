<template>
  <div class="layout-wrapper">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-container">
        <!-- Logo区域 -->
        <div class="logo-area" @click="goHome">
          <div class="logo-icon-wrapper">
            <el-icon size="28" :color="'var(--primary-color)'"><FirstAidKit /></el-icon>
          </div>
          <div class="logo-text-wrapper">
            <span class="logo-text">久物健康</span>
            <span class="logo-subtitle">JIUWU HEALTH</span>
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="nav-divider" v-show="!isMobile"></div>

        <!-- 顶部导航菜单 -->
        <nav class="top-nav" v-show="!isMobile">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            background-color="transparent"
            text-color="#ffffff"
            active-text-color="#1890ff"
            router
          >
            <el-menu-item index="/dashboard">
              <el-icon><DataLine /></el-icon>
              <span>首页</span>
            </el-menu-item>

            <el-menu-item index="/health">
              <el-icon><FirstAidKit /></el-icon>
              <span>健康管理</span>
            </el-menu-item>

            <el-menu-item index="/ai-doctor">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI健管师</span>
            </el-menu-item>

            <el-menu-item index="/physical-exam">
              <el-icon><Document /></el-icon>
              <span>体检管理</span>
            </el-menu-item>

            <el-menu-item index="/report">
              <el-icon><Reading /></el-icon>
              <span>报告解读</span>
            </el-menu-item>

            <el-menu-item index="/about">
              <el-icon><InfoFilled /></el-icon>
              <span>关于我们</span>
            </el-menu-item>
          </el-menu>
        </nav>

        <!-- 右侧用户信息 -->
        <div class="header-right">
          <!-- 已登录显示用户信息 -->
          <template v-if="isLoggedIn">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" :src="getAvatarUrl(userStore.userInfo?.avatar)" :icon="UserFilled" />
                <span class="username" v-show="!isMobile">{{ username || '用户' }}</span>
                <el-tag v-if="isAdmin" size="small" type="danger" class="admin-tag">管理员</el-tag>
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item v-if="isAdmin" command="admin">
                    <el-icon><Setting /></el-icon>管理中心
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <!-- 未登录显示登录/注册按钮 -->
          <template v-else>
            <div class="auth-buttons">
              <el-button type="primary" size="small" @click="goToLogin">登录</el-button>
              <el-button size="small" @click="goToRegister">注册</el-button>
            </div>
          </template>

          <!-- 移动端汉堡菜单按钮 -->
          <div v-if="isMobile" class="hamburger-menu" @click="toggleMobileMenu">
            <el-icon size="24"><Menu /></el-icon>
          </div>
        </div>
      </div>
    </header>

    <!-- 移动端侧边栏抽屉 -->
    <el-drawer
      v-model="mobileMenuVisible"
      direction="ltr"
      size="70%"
      :with-header="false"
      class="mobile-drawer"
    >
      <div class="mobile-sidebar">
        <div class="mobile-logo">
          <div class="logo-icon-wrapper">
            <el-icon size="28" :color="'var(--primary-color)'"><FirstAidKit /></el-icon>
          </div>
          <div class="logo-text-wrapper">
            <span class="logo-text">久物健康</span>
            <span class="logo-subtitle">JIUWU HEALTH</span>
          </div>
        </div>

        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#ffffff"
          text-color="var(--text-secondary)"
          active-text-color="var(--primary-color)"
          router
          @select="handleMobileMenuSelect"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <el-menu-item index="/health">
            <el-icon><FirstAidKit /></el-icon>
            <span>健康管理</span>
          </el-menu-item>

          <el-menu-item index="/ai-doctor">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI健管师</span>
          </el-menu-item>

          <el-menu-item index="/physical-exam">
            <el-icon><Document /></el-icon>
            <span>体检管理</span>
          </el-menu-item>

          <el-menu-item index="/report">
            <el-icon><Reading /></el-icon>
            <span>报告解读</span>
          </el-menu-item>

          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>

          <el-menu-item index="/about">
            <el-icon><InfoFilled /></el-icon>
            <span>关于我们</span>
          </el-menu-item>

          <el-menu-item v-if="isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>管理中心</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-drawer>

    <!-- 主内容区 -->
    <main class="main-content" :class="{ 'main-content-mobile': isMobile }">
      <router-view v-slot="{ Component }">
        <transition name="fade-transform" mode="out-in">
          <keep-alive :include="cachedViews">
            <component :is="Component" :key="route.fullPath" />
          </keep-alive>
        </transition>
      </router-view>
    </main>

    <!-- 页脚 - 关于页面不显示 -->
    <AppFooter v-if="!isAboutPage" />

    <!-- 回到顶部按钮 -->
    <BackToTop />
  </div>
</template>

<script setup>
/**
 * 顶部导航栏布局组件
 * 将侧边导航改为顶部导航，更适合现代Web应用
 */
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useUserStore } from '@/stores/user'
import { getAvatarUrl } from '@/utils/image'
import AppFooter from '@/components/AppFooter.vue'
import BackToTop from '@/components/BackToTop.vue'
import {
  UserFilled,
  ArrowDown,
  FirstAidKit,
  DataLine,
  ChatDotRound,
  Document,
  Reading,
  User,
  Menu,
  Setting,
  SwitchButton,
  HomeFilled,
  Histogram,
  List,
  Bell,
  InfoFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { isLoggedIn, username, logout } = useAuth()

// 获取用户store以检查管理员权限
const userStore = useUserStore()
const isAdmin = computed(() => userStore.isAdmin)

// 响应式状态
const isMobile = ref(false)
const mobileMenuVisible = ref(false)

// 需要缓存的页面组件名称列表
const cachedViews = ref(['Dashboard', 'Health', 'AIDoctor', 'PhysicalExam', 'Report'])

// 当前激活的菜单项
const activeMenu = computed(() => route.path)

// 判断是否关于页面（关于页面不显示footer）
const isAboutPage = computed(() => route.path === '/about')

// 检测屏幕尺寸
const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 768
}

// 切换移动端菜单
const toggleMobileMenu = () => {
  mobileMenuVisible.value = !mobileMenuVisible.value
}

// 移动端菜单选择后关闭抽屉
const handleMobileMenuSelect = () => {
  mobileMenuVisible.value = false
}

// 返回首页
const goHome = () => {
  router.push('/dashboard')
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/login?tab=register')
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'admin') {
    router.push('/admin')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      logout()
      ElMessage.success('退出成功')
      router.push('/login')
    })
  }
}

// 监听窗口大小变化
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)

  // 如果已登录，异步获取用户信息（不阻塞渲染）
  if (isLoggedIn.value) {
    // 使用 setTimeout 将请求放到下一个事件循环，避免阻塞渲染
    setTimeout(() => {
      userStore.fetchUserInfo().catch(error => {
        console.error('获取用户信息失败:', error)
      })
    }, 0)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})
</script>

<style scoped>
/* CSS变量定义 */
:root {
  --primary-color: #1890ff;
  --text-primary: #333333;
  --text-secondary: #666666;
}

/* 布局容器 */
.layout-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 - 黑色背景 */
.top-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 60px;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo区域 - 现代化样式 */
.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo-area:hover {
  opacity: 0.85;
}

/* Logo图标包装器 - 添加渐变背景装饰 */
.logo-icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.1) 0%, rgba(24, 144, 255, 0.05) 100%);
  transition: transform 0.3s ease;
}

.logo-area:hover .logo-icon-wrapper {
  transform: scale(1.05);
}

.logo-text-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.logo-text {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.5px;
  line-height: 1.2;
}

.logo-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 10px;
  font-weight: 400;
  letter-spacing: 1px;
  margin-top: 2px;
}

/* 分隔线 */
.nav-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 15px;
}

/* 顶部导航菜单 - 透明背景 */
.top-nav {
  flex: 1;
  margin: 0 10px;
}

.top-nav :deep(.el-menu) {
  border-bottom: none;
  background-color: transparent !important;
}

.top-nav :deep(.el-menu-item) {
  height: 60px;
  line-height: 60px;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.85) !important;
}

/* 导航菜单悬停效果 - 背景高亮 + 文字变白 */
.top-nav :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
  border-radius: 8px 8px 0 0;
}

/* 导航菜单激活状态 - 底部蓝色边框 + 背景高亮 */
.top-nav :deep(.el-menu-item.is-active) {
  background: rgba(24, 144, 255, 0.15) !important;
  border-bottom: 2px solid #1890ff;
  color: #1890ff !important;
}

/* 右侧区域 */
.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 用户信息 - 黑色导航栏适配 */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.3s;
  color: #ffffff;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.username {
  font-size: 14px;
  color: #ffffff;
  font-weight: 500;
}

.admin-tag {
  margin-left: 4px;
}

/* 登录/注册按钮 */
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 汉堡菜单按钮 - 黑色导航栏适配 */
.hamburger-menu {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
  color: #ffffff;
}

.hamburger-menu:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

/* 移动端侧边栏抽屉 - 白色背景 */
.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  background-color: #ffffff;
}

.mobile-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mobile-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--text-primary, #333333);
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #f0f0f0;
  background-color: #ffffff;
}

.mobile-logo .logo-text {
  font-size: 16px;
  color: var(--text-primary, #333333);
}

/* 移动端菜单样式 */
.mobile-sidebar :deep(.el-menu) {
  border-right: none;
}

.mobile-sidebar :deep(.el-menu-item) {
  color: var(--text-secondary, #666666);
  transition: all 0.3s ease;
}

.mobile-sidebar :deep(.el-menu-item:hover) {
  background-color: rgba(24, 144, 255, 0.05) !important;
  color: var(--primary-color, #1890ff) !important;
}

.mobile-sidebar :deep(.el-menu-item.is-active) {
  background-color: rgba(24, 144, 255, 0.08) !important;
  color: var(--primary-color, #1890ff) !important;
  border-right: 3px solid var(--primary-color, #1890ff);
}

/* 主内容区 - 更新背景色和padding */
.main-content {
  flex: 1;
  background-color: #f5f7fa;
  padding: 24px;
  margin-top: 60px;
  min-height: calc(100vh - 60px);
}

.main-content-mobile {
  padding: 16px;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .header-container {
    padding: 0 15px;
  }

  .logo-text {
    font-size: 16px;
  }

  .main-content {
    padding: 12px;
  }
}

@media screen and (max-width: 1024px) {
  .top-nav {
    margin: 0 10px;
  }

  .top-nav :deep(.el-menu-item) {
    padding: 0 12px;
    font-size: 13px;
  }
}
</style>
