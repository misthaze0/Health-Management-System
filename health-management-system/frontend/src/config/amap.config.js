/**
 * 高德地图API配置
 * 请替换为你自己的高德地图API密钥
 * 申请地址：https://lbs.amap.com/dev/key/app
 */

// 高德地图Web服务API密钥（用于IP定位、周边搜索等）
export const AMAP_KEY = 'b5fbc0bb334f28a9e9756cff38b5c60d'

// 高德地图JS API密钥（用于地图显示）
export const AMAP_JS_KEY = '20d2e407d975339dd6ca7423fc73a069'

// 高德地图API基础地址
export const AMAP_BASE_URL = 'https://restapi.amap.com/v3'

// 安全密钥（JS API需要）
export const AMAP_SECURITY_CONFIG = {
  securityJsCode: '4f5ba4af3eff3387cbae42729d327d08'
}

// 地图配置
export const MAP_CONFIG = {
  // 默认缩放级别
  zoom: 14,
  // 地图样式
  mapStyle: 'amap://styles/normal',
  // 搜索半径（米）
  searchRadius: 5000
}

/**
 * 检查API密钥是否已配置
 * @returns {boolean}
 */
export function isAmapKeyConfigured() {
  return AMAP_KEY && AMAP_KEY !== 'YOUR_AMAP_KEY_HERE'
}
