<template>
  <!-- 管理员后台布局组件 -->
  <div class="admin-layout">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <!-- Logo区域 -->
      <div class="logo">
        <el-icon class="logo-icon"><Monitor /></el-icon>
        <span v-show="!isCollapsed" class="logo-text">管理后台</span>
      </div>

      <!-- 菜单区域 -->
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        router
        class="admin-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <!-- 文章管理菜单 -->
        <el-menu-item index="/admin/articles">
          <el-icon><Document /></el-icon>
          <template #title>
            <span>文章管理</span>
          </template>
        </el-menu-item>

        <!-- 轮播图管理菜单 -->
        <el-menu-item index="/admin/carousel">
          <el-icon><Picture /></el-icon>
          <template #title>
            <span>轮播图管理</span>
          </template>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 右侧主内容区 -->
    <div class="main-container" :class="{ collapsed: isCollapsed }">
      <!-- 顶部导航栏 -->
      <header class="header">
        <!-- 折叠按钮 -->
        <div class="collapse-btn" @click="toggleSidebar">
          <el-icon>
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>

        <!-- 面包屑导航 -->
        <el-breadcrumb class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/admin' }">管理后台</el-breadcrumb-item>
          <el-breadcrumb-item v-if="currentRoute.meta?.title">
            {{ currentRoute.meta.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <!-- 右侧操作区 -->
        <div class="header-right">
          <!-- 返回首页按钮 -->
          <el-tooltip content="返回首页" placement="bottom">
            <div class="action-btn" @click="goToHome">
              <el-icon><HomeFilled /></el-icon>
            </div>
          </el-tooltip>

          <!-- 全屏按钮 -->
          <el-tooltip content="全屏" placement="bottom">
            <div class="action-btn" @click="toggleFullscreen">
              <el-icon><FullScreen /></el-icon>
            </div>
          </el-tooltip>

          <!-- 管理员信息下拉菜单 -->
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-info">
              <el-avatar :size="32" :src="userInfo.avatar">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <span class="username">{{ userInfo.username || '管理员' }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区域 -->
      <main class="content">
        <!-- 子路由内容 -->
        <div class="page-content">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
/**
 * AdminLayout.vue - 管理员后台布局组件
 * 提供侧边栏菜单、顶部导航栏和子路由内容区域
 */
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  Monitor,
  Document,
  Picture,
  Fold,
  Expand,
  FullScreen,
  UserFilled,
  ArrowDown,
  User,
  Setting,
  SwitchButton,
  HomeFilled
} from '@element-plus/icons-vue'

// 路由实例
const route = useRoute()
const router = useRouter()

// 用户状态管理
const userStore = useUserStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 当前激活的菜单项
const activeMenu = computed(() => {
  const { meta, path } = route
  if (meta?.activeMenu) {
    return meta.activeMenu
  }
  return path
})

// 当前路由信息
const currentRoute = computed(() => route)

// 管理员信息
const userInfo = computed(() => userStore.userInfo || {})

/**
 * 切换侧边栏折叠状态
 */
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

/**
 * 返回首页
 */
const goToHome = () => {
  router.push('/dashboard')
}

/**
 * 切换全屏模式
 */
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      ElMessage.warning(`进入全屏失败: ${err.message}`)
    })
  } else {
    document.exitFullscreen()
  }
}

/**
 * 处理下拉菜单命令
 * @param {string} command - 命令名称
 */
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
      break
    case 'logout':
      handleLogout()
      break
  }
}

/**
 * 处理退出登录
 */
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    })
    .catch(() => {})
}

// 组件挂载时初始化
onMounted(() => {
  // 从本地存储读取侧边栏状态
  const sidebarStatus = localStorage.getItem('adminSidebarCollapsed')
  if (sidebarStatus !== null) {
    isCollapsed.value = sidebarStatus === 'true'
  }
})

// 监听侧边栏状态变化，保存到本地存储
watch(isCollapsed, (val) => {
  localStorage.setItem('adminSidebarCollapsed', String(val))
})
</script>

<style scoped>
/* 布局容器 */
.admin-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 210px;
  height: 100%;
  background-color: #304156;
  transition: width 0.3s;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: 64px;
}

/* Logo区域 */
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background-color: #2b3649;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  font-size: 24px;
  margin-right: 12px;
}

.logo-text {
  white-space: nowrap;
}

.sidebar.collapsed .logo-icon {
  margin-right: 0;
}

/* 菜单样式 */
.admin-menu {
  border-right: none;
  height: calc(100% - 60px);
}

.admin-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

.admin-menu :deep(.el-menu-item:hover) {
  background-color: #263445 !important;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background-color: #263445 !important;
}

/* 主内容区 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-left 0.3s;
}

/* 顶部导航栏 */
.header {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

/* 折叠按钮 */
.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  cursor: pointer;
  font-size: 20px;
  color: #606266;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: #409EFF;
}

/* 面包屑导航 */
.breadcrumb {
  margin-left: 15px;
  flex: 1;
}

/* 右侧操作区 */
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 操作按钮 */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  cursor: pointer;
  font-size: 18px;
  color: #606266;
  transition: color 0.3s;
}

.action-btn:hover {
  color: #409EFF;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #606266;
}

.dropdown-icon {
  font-size: 12px;
  color: #909399;
}

/* 内容区域 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
  overflow: hidden;
}

/* 页面内容 */
.page-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 下拉菜单图标样式 */
:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }

  .main-container {
    margin-left: 0;
  }

  .username {
    display: none;
  }
}
</style>
