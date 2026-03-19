import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

/**
 * 统一的登录状态检测Hook
 * 所有状态直接从userStore获取，确保单一数据源
 * @returns {Object} 登录状态和相关方法
 */
export function useAuth() {
  const userStore = useUserStore()

  // 使用computed从store获取状态，确保响应式更新
  const isLoggedIn = computed(() => userStore.isLoggedIn)
  const username = computed(() => userStore.username)
  const userInfo = computed(() => userStore.userInfo)

  // 检查登录状态方法
  const checkLoginStatus = () => {
    return userStore.isLoggedIn
  }

  return {
    isLoggedIn,
    username,
    userInfo,
    logout: userStore.logout,
    checkLoginStatus
  }
}
