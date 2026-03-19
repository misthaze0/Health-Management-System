/**
 * 图片工具函数
 * 处理图片URL的拼接和转换
 */

// 上传文件URL前缀
// 注意：后端 server.servlet.context-path=/api，所以 /uploads/ 实际访问 /api/uploads/
const UPLOAD_URL_PREFIX = '/api/uploads/'

/**
 * 获取完整的图片URL
 * 将数据库中的相对路径转换为完整URL
 * 
 * 数据库路径格式: carousel/xxx.png
 * 完整URL格式: /api/uploads/carousel/xxx.png (开发环境使用相对路径，通过vite代理)
 * 
 * @param {string} url - 图片相对路径，如 carousel/xxx.png
 * @returns {string} 完整的图片URL
 */
export function getImageUrl(url) {
  if (!url) {
    console.log('[getImageUrl] url为空')
    return ''
  }

  // 如果已经是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    console.log('[getImageUrl] 已是完整URL:', url)
    return url
  }

  // 如果已经是 /api/uploads/ 开头的路径，直接返回
  if (url.startsWith('/api/uploads/')) {
    console.log('[getImageUrl] 已是完整路径:', url)
    return url
  }

  // 处理旧格式路径 /uploads/xxx/xxx.jpg -> 转换为 /api/uploads/xxx/xxx.jpg
  if (url.startsWith('/uploads/')) {
    const fullUrl = '/api' + url
    console.log('[getImageUrl] 旧格式路径转换:', url, '->', fullUrl)
    return fullUrl
  }

  // 拼接完整URL（使用相对路径，通过vite代理转发到后端）
  const fullUrl = UPLOAD_URL_PREFIX + url
  console.log('[getImageUrl] 原始路径:', url)
  console.log('[getImageUrl] 完整URL:', fullUrl)
  return fullUrl
}

/**
 * 获取轮播图图片URL
 * 
 * @param {string} imageUrl - 轮播图图片路径
 * @returns {string} 完整的图片URL
 */
export function getCarouselImageUrl(imageUrl) {
  return getImageUrl(imageUrl)
}

/**
 * 获取文章封面图片URL
 * 
 * @param {string} coverUrl - 封面图片路径
 * @returns {string} 完整的图片URL
 */
export function getArticleCoverUrl(coverUrl) {
  return getImageUrl(coverUrl)
}

/**
 * 获取用户头像URL
 * 
 * @param {string} avatarUrl - 头像路径
 * @returns {string} 完整的图片URL
 */
export function getAvatarUrl(avatarUrl) {
  return getImageUrl(avatarUrl)
}
