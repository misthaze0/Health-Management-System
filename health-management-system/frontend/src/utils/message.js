/**
 * 统一弹窗消息工具
 * 规范项目内所有弹窗样式和行为
 */
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

// 默认配置
const defaultConfig = {
  // 消息提示默认配置
  message: {
    duration: 3000,
    showClose: true,
    grouping: true
  },
  // 消息确认框默认配置
  messageBox: {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    closeOnClickModal: false,
    closeOnPressEscape: false
  },
  // 通知默认配置
  notification: {
    duration: 4500,
    showClose: true,
    position: 'top-right'
  }
}

/**
 * 成功消息
 * @param {string} message - 消息内容
 * @param {object} options - 配置选项
 */
export const showSuccess = (message, options = {}) => {
  return ElMessage.success({
    message,
    ...defaultConfig.message,
    ...options
  })
}

/**
 * 错误消息
 * @param {string} message - 消息内容
 * @param {object} options - 配置选项
 */
export const showError = (message, options = {}) => {
  return ElMessage.error({
    message,
    duration: 5000, // 错误消息显示更久
    ...defaultConfig.message,
    ...options
  })
}

/**
 * 警告消息
 * @param {string} message - 消息内容
 * @param {object} options - 配置选项
 */
export const showWarning = (message, options = {}) => {
  return ElMessage.warning({
    message,
    ...defaultConfig.message,
    ...options
  })
}

/**
 * 信息消息
 * @param {string} message - 消息内容
 * @param {object} options - 配置选项
 */
export const showInfo = (message, options = {}) => {
  return ElMessage.info({
    message,
    ...defaultConfig.message,
    ...options
  })
}

/**
 * 确认对话框
 * @param {string} message - 消息内容
 * @param {string} title - 标题
 * @param {object} options - 配置选项
 */
export const showConfirm = (message, title = '确认操作', options = {}) => {
  return ElMessageBox.confirm(
    message,
    title,
    {
      ...defaultConfig.messageBox,
      ...options
    }
  )
}

/**
 * 删除确认对话框（专用）
 * @param {string} itemName - 要删除的项目名称
 * @param {object} options - 配置选项
 */
export const showDeleteConfirm = (itemName = '该项', options = {}) => {
  return ElMessageBox.confirm(
    `确定要删除${itemName}吗？此操作不可恢复。`,
    '确认删除',
    {
      ...defaultConfig.messageBox,
      confirmButtonClass: 'el-button--danger',
      ...options
    }
  )
}

/**
 * 提示对话框
 * @param {string} message - 消息内容
 * @param {string} title - 标题
 * @param {object} options - 配置选项
 */
export const showAlert = (message, title = '提示', options = {}) => {
  return ElMessageBox.alert(
    message,
    title,
    {
      confirmButtonText: '确定',
      closeOnClickModal: true,
      closeOnPressEscape: true,
      ...options
    }
  )
}

/**
 * 通知消息
 * @param {string} title - 标题
 * @param {string} message - 消息内容
 * @param {string} type - 类型：success/warning/info/error
 * @param {object} options - 配置选项
 */
export const showNotification = (title, message, type = 'info', options = {}) => {
  return ElNotification({
    title,
    message,
    type,
    ...defaultConfig.notification,
    ...options
  })
}

/**
 * 成功通知
 * @param {string} title - 标题
 * @param {string} message - 消息内容
 * @param {object} options - 配置选项
 */
export const showSuccessNotification = (title, message, options = {}) => {
  return showNotification(title, message, 'success', options)
}

/**
 * 错误通知
 * @param {string} title - 标题
 * @param {string} message - 消息内容
 * @param {object} options - 配置选项
 */
export const showErrorNotification = (title, message, options = {}) => {
  return showNotification(title, message, 'error', { duration: 0, ...options })
}

/**
 * 关闭所有消息
 */
export const closeAllMessages = () => {
  ElMessage.closeAll()
}

/**
 * 关闭所有通知
 */
export const closeAllNotifications = () => {
  ElNotification.closeAll()
}

// 默认导出
export default {
  success: showSuccess,
  error: showError,
  warning: showWarning,
  info: showInfo,
  confirm: showConfirm,
  deleteConfirm: showDeleteConfirm,
  alert: showAlert,
  notify: showNotification,
  notifySuccess: showSuccessNotification,
  notifyError: showErrorNotification,
  closeAll: closeAllMessages,
  closeAllNotifications
}
