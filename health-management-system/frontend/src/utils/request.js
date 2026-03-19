/**
 * HTTP请求工具模块
 * 基于axios封装，提供统一的请求拦截、响应处理和错误处理
 *
 * @module utils/request
 * @author Health Management System
 * @since 1.0.0
 */

import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { getToken } from './auth'

/**
 * 创建axios实例
 * 配置基础URL、超时时间和默认请求头
 */
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 * 在请求发送前自动添加JWT Token到请求头
 */
service.interceptors.request.use(
  (config) => {
    console.log('[DEBUG Request] ==================== 请求开始 ====================')
    console.log('[DEBUG Request] URL:', config.url)
    console.log('[DEBUG Request] Method:', config.method)
    console.log('[DEBUG Request] BaseURL:', config.baseURL)
    console.log('[DEBUG Request] 完整URL:', (config.baseURL || '') + config.url)

    const token = getToken()
    console.log('[DEBUG Request] Token存在:', !!token)
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
      console.log('[DEBUG Request] Token已添加到请求头')
    } else {
      console.log('[DEBUG Request] 警告: Token不存在')
    }

    console.log('[DEBUG Request] 请求头:', config.headers)
    console.log('[DEBUG Request] 请求数据:', config.data)
    console.log('[DEBUG Request] ==================== 请求结束 ====================')

    return config
  },
  (error) => {
    console.error('[DEBUG Request] 请求拦截器错误:', error)
    ElMessage.error('请求发送失败，请检查网络连接')
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 处理响应数据和错误状态
 * - 成功响应：直接返回数据
 * - 业务错误：显示错误消息
 * - HTTP错误：根据状态码进行不同处理
 */
service.interceptors.response.use(
  /**
   * 处理成功响应
   * @param {Object} response - axios响应对象
   * @returns {any} 响应数据
   */
  (response) => {
    const res = response.data

    // 如果响应成功（code为200或0）
    if (res.code === 200 || res.code === 0) {
      return res.data
    }

    // 处理业务错误
    const errorMsg = res.message || '请求失败'
    ElMessage.error(errorMsg)
    return Promise.reject(new Error(errorMsg))
  },
  /**
   * 处理错误响应
   * @param {Object} error - 错误对象
   * @returns {Promise} 拒绝的Promise
   */
  (error) => {
    const { response, config } = error

    // 打印详细错误信息到控制台
    console.error('[Request] ==================== 请求错误开始 ====================')
    console.error('[Request] 请求URL:', config?.url)
    console.error('[Request] 请求方法:', config?.method)
    console.error('[Request] 错误类型:', error.name)
    console.error('[Request] 错误信息:', error.message)

    if (response) {
      console.error('[Request] HTTP状态码:', response.status)
      console.error('[Request] 响应数据:', response.data)
      console.error('[Request] 响应头:', response.headers)
    } else if (error.request) {
      console.error('[Request] 请求已发送但未收到响应')
      console.error('[Request] 请求对象:', error.request)
    }
    console.error('[Request] ==================== 请求错误结束 ====================')

    if (response) {
      const errorMsg = response.data?.message || ''
      const url = config?.url || '未知接口'

      // 根据HTTP状态码进行不同处理
      switch (response.status) {
        case 401:
          // 未授权，Token过期或无效
          ElMessageBox.alert(
            `登录已过期，请重新登录<br><small>接口: ${url}</small>`,
            '登录过期',
            {
              confirmButtonText: '去登录',
              type: 'warning',
              dangerouslyUseHTMLString: true,
              callback: () => {
                const userStore = useUserStore()
                userStore.logout()
                window.location.href = '/login'
              }
            }
          )
          break
        case 403:
          // 禁止访问，权限不足
          ElMessageBox.alert(
            `没有权限访问该资源<br><small>接口: ${url}</small>`,
            '权限不足',
            {
              confirmButtonText: '确定',
              type: 'error',
              dangerouslyUseHTMLString: true
            }
          )
          break
        case 404:
          // 资源不存在
          ElMessage.error(`请求的资源不存在: ${url}`)
          break
        case 500:
          // 服务器内部错误
          ElMessageBox.alert(
            `服务器内部错误<br><small>接口: ${url}<br>错误: ${errorMsg}</small>`,
            '服务器错误',
            {
              confirmButtonText: '确定',
              type: 'error',
              dangerouslyUseHTMLString: true
            }
          )
          break
        default:
          ElMessage.error(`请求失败: ${errorMsg || '未知错误'}`)
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应（网络错误）
      ElMessageBox.alert(
        '无法连接到服务器，请检查:<br>1. 网络连接是否正常<br>2. 后端服务是否启动',
        '网络错误',
        {
          confirmButtonText: '确定',
          type: 'error',
          dangerouslyUseHTMLString: true
        }
      )
    } else {
      // 请求配置错误
      ElMessage.error(`请求配置错误: ${error.message}`)
    }

    return Promise.reject(error)
  }
)

export default service
