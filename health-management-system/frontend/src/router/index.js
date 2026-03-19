import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getToken } from '@/utils/auth'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { ElLoading } from 'element-plus'

// 预加载布局组件
import Layout from '@/views/layout/index.vue'
import AdminLayout from '@/views/admin/AdminLayout.vue'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '数据概览', icon: 'DataLine', public: true }
      },
      {
        path: '/health',
        name: 'Health',
        component: () => import('@/views/health/index.vue'),
        meta: { title: '健康管理', icon: 'FirstAidKit' }
      },
      {
        path: '/ai-doctor',
        name: 'AIDoctor',
        component: () => import('@/views/ai-doctor/index.vue'),
        meta: { title: 'AI健管师', icon: 'ChatDotRound' }
      },
      {
        path: '/physical-exam',
        name: 'PhysicalExam',
        component: () => import('@/views/physical-exam/index.vue'),
        meta: { title: '体检管理', icon: 'Document' }
      },
      {
        path: '/report',
        name: 'Report',
        component: () => import('@/views/report/index.vue'),
        meta: { title: '报告解读', icon: 'Reading' }
      },
      {
        path: '/report/pdf/:id',
        name: 'PdfViewer',
        component: () => import('@/views/report/PdfViewer.vue'),
        meta: { title: 'PDF预览' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心', icon: 'User' }
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('@/views/about/index.vue'),
        meta: { title: '关于我们', icon: 'InfoFilled', public: true }
      }
    ]
  },
  // 文章列表页 - 公开访问
  {
    path: '/articles',
    component: Layout,
    meta: { title: '健康资讯', public: true },
    children: [
      {
        path: '',
        name: 'ArticleList',
        component: () => import('@/views/article/ArticleList.vue'),
        meta: { title: '健康资讯', public: true }
      }
    ]
  },
  // 文章详情页 - 公开访问，使用Layout布局
  {
    path: '/article/:id',
    component: Layout,
    meta: { title: '文章详情', public: true },
    children: [
      {
        path: '',
        name: 'ArticleDetail',
        component: () => import('@/views/article/ArticleDetail.vue'),
        meta: { title: '文章详情', public: true }
      }
    ]
  },
  // 管理员后台路由
  {
    path: '/admin',
    name: 'Admin',
    component: AdminLayout,
    redirect: '/admin/articles',
    meta: { title: '管理后台' },
    children: [
      {
        path: '/admin/articles',
        name: 'AdminArticles',
        component: () => import('@/views/admin/AdminArticles.vue'),
        meta: { title: '文章管理', activeMenu: '/admin/articles' }
      },
      {
        path: '/admin/articles/edit/:id?',
        name: 'AdminArticleEdit',
        component: () => import('@/views/admin/AdminArticleEdit.vue'),
        meta: { title: '编辑文章', activeMenu: '/admin/articles' }
      },
      {
        path: '/admin/carousel',
        name: 'AdminCarousel',
        component: () => import('@/views/admin/AdminCarousel.vue'),
        meta: { title: '轮播图管理', activeMenu: '/admin/carousel' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue')
  },
  {
    path: '/logout',
    name: 'Logout',
    component: {
      beforeRouteEnter(to, from, next) {
        // 动态导入并执行登出
        import('@/stores/user').then(({ useUserStore }) => {
          useUserStore().logout()
        })
        next('/login')
      }
    },
    meta: { public: true }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 滚动行为：切换路由时平滑滚动到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      // 返回历史记录时恢复位置
      return savedPosition
    }
    if (to.hash) {
      // 锚点跳转
      return { el: to.hash, behavior: 'smooth' }
    }
    // 默认滚动到顶部
    return { top: 0, behavior: 'smooth' }
  }
})

// 全局加载实例
let loadingInstance = null

// 路由守卫：登录验证 + 加载指示器
router.beforeEach((to, from, next) => {
  // 只在初始加载时显示加载指示器，路由切换时不显示
  // 避免切换页面时的白屏闪烁
  if (!loadingInstance && !from.name) {
    loadingInstance = ElLoading.service({
      lock: false,
      text: '加载中...',
      background: 'rgba(255, 255, 255, 0.3)',
      target: 'body'
    })
  }

  const hasToken = getToken()

  // 未登录且访问非公开页面，弹出提示框后跳转到登录页
  if (!to.meta.public && !hasToken) {
    // 关闭加载指示器
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }

    // 保存当前尝试访问的页面路径到 localStorage
    localStorage.setItem('redirectPath', to.fullPath)

    ElMessageBox.confirm(
      '请先登录后再访问此页面',
      '提示',
      {
        confirmButtonText: '去登录',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    )
      .then(() => {
        // 用户点击确认，跳转到登录页
        next('/login')
      })
      .catch(() => {
        // 用户点击取消，留在当前页面或跳转到首页
        if (from.path !== '/') {
          next(false)
        } else {
          next('/dashboard')
        }
      })
    return
  }

  // 已登录且访问登录页，重定向到首页
  if (to.path === '/login' && hasToken) {
    next('/dashboard')
    return
  }

  next()
})

// 路由加载完成
router.afterEach(() => {
  // 延迟关闭加载指示器，确保组件完全渲染
  setTimeout(() => {
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
  }, 100)
})

// 路由错误处理
router.onError((error) => {
  console.error('路由加载失败:', error)
  // 关闭加载指示器
  if (loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
})

export default router
