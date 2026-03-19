/**
 * 用户状态管理模块
 * 使用Pinia管理用户认证状态和信息
 *
 * @module stores/user
 * @author Health Management System
 * @since 1.0.0
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getUserInfo } from '@/api/user'
import { setToken, removeToken, getToken } from '@/utils/auth'

// localStorage key for role
const ROLE_KEY = 'health-management-role'

/**
 * 从localStorage获取角色
 */
const getRoleFromStorage = () => {
  return localStorage.getItem(ROLE_KEY) || ''
}

/**
 * 保存角色到localStorage
 */
const setRoleToStorage = (role) => {
  localStorage.setItem(ROLE_KEY, role)
}

/**
 * 从localStorage移除角色
 */
const removeRoleFromStorage = () => {
  localStorage.removeItem(ROLE_KEY)
}

/**
 * 用户状态Store
 * 提供用户登录、注册、信息获取和登出等功能
 */
export const useUserStore = defineStore('user', () => {
  // ==================== State ====================
  /**
   * JWT令牌
   * 从localStorage初始化，用于API认证
   */
  const token = ref(getToken() || '')

  /**
   * 用户信息对象
   * 包含用户基本资料、头像等
   */
  const userInfo = ref(null)

  /**
   * 用户角色列表
   * 用于权限控制
   */
  const roles = ref([])

  /**
   * 用户角色
   * 用于区分管理员和普通用户，从localStorage初始化
   */
  const role = ref(getRoleFromStorage())

  // ==================== Getters ====================
  /**
   * 是否已登录
   * 基于token是否存在计算
   */
  const isLoggedIn = computed(() => !!token.value)

  /**
   * 用户名
   * 从用户信息中获取，未登录时返回空字符串
   */
  const username = computed(() => userInfo.value?.username || '')

  /**
   * 是否为管理员
   * 基于role是否为admin计算
   */
  const isAdmin = computed(() => role.value === 'admin')

  // ==================== Actions ====================
  /**
   * 设置用户令牌
   * 同时更新state和localStorage
   *
   * @param {string} newToken - JWT令牌
   */
  const setUserToken = (newToken) => {
    token.value = newToken
    setToken(newToken)
  }

  /**
   * 设置用户信息
   *
   * @param {Object} info - 用户信息对象
   */
  const setUserInfo = (info) => {
    userInfo.value = info
    roles.value = info.roles || []
    // 保存角色信息到state和localStorage
    role.value = info.role || ''
    setRoleToStorage(info.role || '')
  }

  /**
   * 用户登录
   * 登录成功后自动获取用户信息
   *
   * @param {Object} loginForm - 登录表单 {username, password}
   * @returns {Promise<Object>} 登录结果
   * @throws {Error} 登录失败时抛出错误
   */
  const login = async (loginForm) => {
    try {
      const res = await loginApi(loginForm)
      setUserToken(res.token)
      // 如果后端返回用户信息，直接使用；否则获取用户信息
      if (res.user) {
        setUserInfo(res.user)
      } else {
        // 登录成功后获取用户信息，失败不阻断登录流程
        try {
          await fetchUserInfo()
        } catch (userInfoError) {
          console.warn('获取用户信息失败:', userInfoError)
          // 用户信息获取失败不影响登录，用户仍可使用基本功能
        }
      }
      return res
    } catch (error) {
      throw error
    }
  }

  /**
   * 用户注册
   *
   * @param {Object} registerForm - 注册表单
   * @returns {Promise<Object>} 注册结果
   * @throws {Error} 注册失败时抛出错误
   */
  const register = async (registerForm) => {
    try {
      const res = await registerApi(registerForm)
      return res
    } catch (error) {
      throw error
    }
  }

  /**
   * 获取当前用户信息
   * 用于页面刷新后恢复用户状态
   *
   * @returns {Promise<Object>} 用户信息
   * @throws {Error} 获取失败时抛出错误
   */
  const fetchUserInfo = async () => {
    try {
      const res = await getUserInfo()
      setUserInfo(res)
      return res
    } catch (error) {
      throw error
    }
  }

  /**
   * 用户登出
   * 清除所有用户状态和数据
   */
  const logout = () => {
    token.value = ''
    userInfo.value = null
    roles.value = []
    role.value = ''
    removeToken()
    removeRoleFromStorage()
  }

  // 暴露state、getters和actions
  return {
    // State
    token,
    userInfo,
    roles,
    role,
    // Getters
    isLoggedIn,
    username,
    isAdmin,
    // Actions
    login,
    register,
    fetchUserInfo,
    logout,
    setUserInfo
  }
})
