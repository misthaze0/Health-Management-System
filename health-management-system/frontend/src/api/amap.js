import axios from 'axios'
import { AMAP_KEY, AMAP_BASE_URL } from '@/config/amap.config'

// 创建axios实例用于高德地图API
const amapService = axios.create({
  baseURL: AMAP_BASE_URL,
  timeout: 10000
})

/**
 * IP定位 - 获取用户当前城市
 * @returns {Promise<Object>} 城市信息
 */
export function getCityByIP() {
  return amapService.get('/ip', {
    params: {
      key: AMAP_KEY
    }
  }).then(res => {
    if (res.data.status === '1') {
      return {
        province: res.data.province,
        city: res.data.city,
        adcode: res.data.adcode,
        rectangle: res.data.rectangle // 矩形区域坐标
      }
    }
    throw new Error(res.data.info || 'IP定位失败')
  })
}

/**
 * 周边搜索 - 搜索附近的医院（筛选正规医院和体检中心）
 * @param {string} location - 经纬度，格式："经度,纬度"
 * @param {number} radius - 搜索半径（米），默认5000
 * @param {number} page - 页码，默认1
 * @param {number} offset - 每页数量，默认20
 * @returns {Promise<Array>} 医院列表
 */
export function searchNearbyHospitals(location, radius = 5000, page = 1, offset = 20) {
  return amapService.get('/place/around', {
    params: {
      key: AMAP_KEY,
      location: location,
      radius: radius,
      keywords: '医院|体检中心|体检|人民医院|附属医院|中心医院|第一医院|第二医院|第三医院|中医院|妇幼保健院|专科医院',
      types: '090100|090101|090102|090200|090201|090202|090203|090204|090205|090206|090207', // 综合医院、专科医院等
      offset: offset,
      page: page,
      extensions: 'all' // 返回详细信息
    }
  }).then(res => {
    if (res.data.status === '1') {
      // 筛选正规医院：过滤掉小诊所、卫生室、卫生所等
      const validTypes = ['医院', '综合医院', '专科医院', '中医医院', '妇幼保健院', '体检中心']
      
      // 排除的关键词（小诊所、卫生室等）
      const excludeKeywords = ['诊所', '卫生室', '卫生所', '卫生中心', '社区卫生', '村卫生室', '医务室', '门诊部', '门诊']
      
      const filteredPois = res.data.pois.filter(poi => {
        // 检查类型是否匹配
        const typeMatch = validTypes.some(type => poi.type?.includes(type))
        
        // 检查名称是否包含医院或体检相关关键词
        const nameMatch = /医院|体检|医疗中心|health|hospital/i.test(poi.name)
        
        // 检查是否包含排除关键词（排除小诊所等）
        const hasExcludeKeyword = excludeKeywords.some(keyword => 
          poi.name?.includes(keyword) || poi.type?.includes(keyword)
        )
        
        // 只保留正规医院，排除小诊所等
        return (typeMatch || nameMatch) && !hasExcludeKeyword
      })
      
      return filteredPois.map(poi => ({
        id: poi.id,
        name: poi.name,
        address: poi.address,
        location: poi.location, // 经纬度
        tel: poi.tel,
        type: poi.type,
        distance: parseInt(poi.distance), // 距离（米）
        rating: parseFloat(poi.biz_ext?.rating) || 4.0, // 评分
        photos: poi.photos || [], // 图片
        businessHours: poi.biz_ext?.open_time || '营业时间未知',
        website: poi.website,
        pcode: poi.pcode,
        citycode: poi.citycode,
        adcode: poi.adcode
      }))
    }
    throw new Error(res.data.info || '搜索附近医院失败')
  })
}

/**
 * 获取静态地图图片URL
 * @param {string} location - 中心点经纬度
 * @param {Array} hospitals - 医院列表
 * @param {number} zoom - 缩放级别
 * @param {string} size - 图片尺寸，默认"800*400"
 * @returns {string} 静态地图图片URL
 */
export function getStaticMapUrl(location, hospitals = [], zoom = 14, size = '800*400') {
  const baseUrl = 'https://restapi.amap.com/v3/staticmap'
  
  // 构建标记参数 - 最多5个标记（1个用户+4个医院）避免URL过长
  const markers = []
  
  // 用户位置 - 红色标记，标签为1
  markers.push(`large,0xFF0000,1:${location}`)
  
  // 医院位置 - 蓝色标记，标签从2开始，最多4个
  hospitals.slice(0, 4).forEach((h, i) => {
    if (h.location && typeof h.location === 'string') {
      markers.push(`large,0x0000FF,${i + 2}:${h.location}`)
    }
  })
  
  const markersParam = markers.join('|')
  
  // 构建URL
  const params = []
  params.push(`key=${AMAP_KEY}`)
  params.push(`location=${location}`)
  params.push(`zoom=${zoom}`)
  params.push(`size=${size}`)
  params.push(`scale=2`)
  
  if (markersParam) {
    params.push(`markers=${markersParam}`)
  }
  
  const url = `${baseUrl}?${params.join('&')}`
  console.log('静态地图URL:', url)
  return url
}

/**
 * 地理编码 - 地址转坐标
 * @param {string} address - 地址
 * @param {string} city - 城市
 * @returns {Promise<Object>} 坐标信息
 */
export function geocode(address, city = '') {
  return amapService.get('/geocode/geo', {
    params: {
      key: AMAP_KEY,
      address: address,
      city: city
    }
  }).then(res => {
    if (res.data.status === '1' && res.data.geocodes.length > 0) {
      const geo = res.data.geocodes[0]
      return {
        location: geo.location,
        province: geo.province,
        city: geo.city,
        district: geo.district,
        formattedAddress: geo.formatted_address
      }
    }
    throw new Error('地理编码失败')
  })
}

/**
 * 逆地理编码 - 坐标转地址
 * @param {string} location - 经纬度
 * @returns {Promise<Object>} 地址信息
 */
export function regeocode(location) {
  return amapService.get('/geocode/regeo', {
    params: {
      key: AMAP_KEY,
      location: location,
      extensions: 'all'
    }
  }).then(res => {
    if (res.data.status === '1') {
      const regeo = res.data.regeocode
      return {
        formattedAddress: regeo.formatted_address,
        province: regeo.addressComponent.province,
        city: regeo.addressComponent.city,
        district: regeo.addressComponent.district,
        street: regeo.addressComponent.street,
        address: regeo.addressComponent.address
      }
    }
    throw new Error('逆地理编码失败')
  })
}

/**
 * 获取地点详情
 * @param {string} id - 地点ID
 * @returns {Promise<Object>} 地点详情
 */
export function getPlaceDetail(id) {
  return amapService.get('/place/detail', {
    params: {
      key: AMAP_KEY,
      id: id
    }
  }).then(res => {
    if (res.data.status === '1' && res.data.pois.length > 0) {
      const poi = res.data.pois[0]
      return {
        id: poi.id,
        name: poi.name,
        address: poi.address,
        location: poi.location,
        tel: poi.tel,
        type: poi.type,
        photos: poi.photos || [],
        rating: parseFloat(poi.biz_ext?.rating) || 4.0,
        businessHours: poi.biz_ext?.open_time || '营业时间未知',
        website: poi.website,
        description: poi.indoor_map ? '支持室内地图' : ''
      }
    }
    throw new Error('获取地点详情失败')
  })
}
