<template>
  <div class="physical-exam-container">
    <!-- 页面头部 - 仿健康管理看板风格 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">HEALTH EXAMINATION</div>
        <h1 class="hero-title">体检机构</h1>
        <p class="hero-subtitle">Medical Examination Centers</p>
        <div class="hero-desc">
          <p>发现优质体检机构，为健康保驾护航</p>
          <p>精准定位附近医疗资源，让健康管理更便捷</p>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-item">
          <span class="stat-value">{{ hospitalList.length }}</span>
          <span class="stat-label">合作机构</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ locationEnabled ? '附近' : '杭州' }}</span>
          <span class="stat-label">{{ locationEnabled ? '推荐' : '市内' }}</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value status-indicator" :class="{ active: locationEnabled }"></span>
          <span class="stat-label">{{ locationEnabled ? '已定位' : '未定位' }}</span>
        </div>
      </div>
    </section>

    <!-- 定位控制栏 -->
    <div class="location-bar">
      <div class="location-content">
        <div class="location-info">
          <div class="location-icon" :class="{ active: locationEnabled }">
            <el-icon :size="20"><MapLocation /></el-icon>
          </div>
          <div class="location-text">
            <span class="location-title">
              {{ locationEnabled ? '已开启定位' : '定位未开启' }}
            </span>
            <span class="location-desc">
              {{ locationEnabled ? `当前位置：${currentCity || '定位中...'}` : '默认展示杭州市内医院' }}
            </span>
          </div>
        </div>
        <div class="location-controls">
          <!-- 距离选择器 -->
          <div v-if="locationEnabled" class="distance-selector">
            <span class="distance-label">搜索范围：</span>
            <el-slider
              v-model="searchRadius"
              :min="1"
              :max="80"
              :step="1"
              :marks="{ 1: '1km', 20: '20km', 40: '40km', 60: '60km', 80: '80km' }"
              show-stops
              style="width: 200px"
            />
            <span class="distance-value">{{ searchRadius }}km</span>
            <el-button
              type="primary"
              size="small"
              :loading="loading"
              @click="confirmRadiusChange"
              class="confirm-btn"
            >
              <el-icon><Search /></el-icon>
              确认
            </el-button>
          </div>
          <el-button
            :type="locationEnabled ? 'success' : 'primary'"
            size="large"
            :loading="locationLoading"
            @click="toggleLocation"
            class="location-btn"
          >
            <el-icon v-if="!locationLoading"><Location /></el-icon>
            <span>{{ locationEnabled ? '关闭定位' : '开启定位' }}</span>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 高德地图区域（仅定位开启时显示） -->
    <div v-if="locationEnabled" class="map-section">
      <div class="map-container">
        <!-- 动态地图容器 -->
        <div id="amap-container" class="amap-container"></div>
        
        <!-- 地图标记说明 -->
        <div v-if="hospitalList.length > 0 && locationEnabled" class="map-legend">
          <div class="legend-item">
            <span class="legend-marker red">1</span>
            <span class="legend-text">您的位置</span>
          </div>
          <div class="legend-item">
            <span class="legend-marker blue">2</span>
            <span class="legend-text">附近医院</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 医院列表区域 -->
    <div class="hospitals-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><FirstAidKit /></el-icon>
          <span>{{ locationEnabled ? '附近医院' : '推荐医院' }}</span>
        </h2>
        <span v-if="locationEnabled && currentCity" class="location-tag">
          <el-icon><Location /></el-icon>
          {{ currentCity }}
        </span>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>

      <!-- 医院网格 -->
      <div v-else class="hospitals-grid">
        <div
          v-for="(hospital, index) in hospitalList"
          :key="hospital.id"
          class="hospital-card"
          @click="selectHospital(hospital)"
        >
          <!-- 医院图片 -->
          <div class="hospital-image">
            <img
              v-if="hospital.imageUrl || hospital.photos?.length > 0"
              :src="hospital.photos?.[0]?.url || getImageUrl(hospital.imageUrl)"
              :alt="hospital.name"
            />
            <div v-else class="hospital-image-placeholder">
              <el-icon :size="48"><FirstAidKit /></el-icon>
            </div>
            <!-- 序号标记 - 与地图标记对应（地图从2开始编号） -->
            <div v-if="locationEnabled" class="number-badge">
              {{ index + 2 }}
            </div>
            <!-- 距离标签 -->
            <div v-if="hospital.distance" class="distance-badge">
              <el-icon><Location /></el-icon>
              <span>{{ formatDistance(hospital.distance) }}</span>
            </div>
            <!-- 推荐标签 -->
            <div v-if="hospital.isRecommended" class="recommend-badge">
              <el-icon><StarFilled /></el-icon>
              <span>推荐</span>
            </div>
          </div>

          <!-- 医院信息 -->
          <div class="hospital-info">
            <div class="hospital-header">
              <h3 class="hospital-name">{{ hospital.name }}</h3>
              <div class="hospital-rating" v-if="hospital.rating">
                <el-icon><StarFilled /></el-icon>
                <span>{{ hospital.rating }}</span>
              </div>
            </div>

            <div class="hospital-tags" v-if="hospital.tags && hospital.tags.length > 0">
              <el-tag
                v-for="tag in hospital.tags"
                :key="tag"
                size="small"
                effect="light"
                round
              >
                {{ tag }}
              </el-tag>
            </div>
            <div class="hospital-tags" v-else-if="hospital.type">
              <el-tag size="small" effect="light" round>{{ hospital.type }}</el-tag>
            </div>

            <div class="hospital-address">
              <el-icon><Location /></el-icon>
              <span>{{ hospital.address }}</span>
            </div>

            <div class="hospital-features" v-if="hospital.features && hospital.features.length > 0">
              <div class="feature-item" v-for="feature in hospital.features" :key="feature">
                <el-icon><CircleCheck /></el-icon>
                <span>{{ feature }}</span>
              </div>
            </div>

            <div class="hospital-footer">
              <div class="contact-info" v-if="hospital.phone || hospital.tel">
                <el-icon><Phone /></el-icon>
                <span>{{ hospital.phone || hospital.tel }}</span>
              </div>
              <el-button type="primary" size="small" round>
                查看详情
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && hospitalList.length === 0" class="empty-state">
        <el-empty description="暂无医院信息">
          <template #image>
            <div class="custom-empty-icon">
              <el-icon :size="60" color="#dcdfe6"><FirstAidKit /></el-icon>
            </div>
          </template>
          <el-button type="primary" @click="resetLocation">
            重新定位
          </el-button>
        </el-empty>
      </div>
    </div>

    <!-- 医院详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="医院详情"
      width="700px"
      destroy-on-close
      class="hospital-detail-dialog"
    >
      <div v-if="selectedHospital" class="hospital-detail">
        <!-- 医院头部 -->
        <div class="detail-header">
          <div class="detail-image">
            <img
              v-if="selectedHospital.imageUrl || selectedHospital.photos?.length > 0"
              :src="selectedHospital.photos?.[0]?.url || getImageUrl(selectedHospital.imageUrl)"
              :alt="selectedHospital.name"
            />
            <div v-else class="detail-image-placeholder">
              <el-icon :size="48"><FirstAidKit /></el-icon>
            </div>
          </div>
          <div class="detail-info">
            <h3>{{ selectedHospital.name }}</h3>
            <div class="detail-rating" v-if="selectedHospital.rating">
              <el-rate
                :model-value="selectedHospital.rating"
                disabled
                show-score
                text-color="#ff9900"
              />
            </div>
            <div class="detail-address">
              <el-icon><Location /></el-icon>
              <span>{{ selectedHospital.address }}</span>
            </div>
            <div class="detail-phone" v-if="selectedHospital.phone || selectedHospital.tel">
              <el-icon><Phone /></el-icon>
              <span>{{ selectedHospital.phone || selectedHospital.tel }}</span>
            </div>
            <div class="detail-hours" v-if="selectedHospital.businessHours">
              <el-icon><Clock /></el-icon>
              <span>{{ selectedHospital.businessHours }}</span>
            </div>
          </div>
        </div>

        <!-- 医院介绍 -->
        <div class="detail-section">
          <h4>机构介绍</h4>
          <p>{{ selectedHospital.description || '暂无介绍' }}</p>
        </div>

        <!-- 体检套餐 -->
        <div class="detail-section" v-if="selectedHospital.packages && selectedHospital.packages.length > 0">
          <h4>体检套餐</h4>
          <div class="packages-list">
            <div
              v-for="pkg in selectedHospital.packages"
              :key="pkg.id"
              class="package-item"
            >
              <div class="package-info">
                <span class="package-name">{{ pkg.name }}</span>
                <span class="package-price">{{ pkg.price }}</span>
              </div>
              <el-button type="primary" link size="small">
                了解详情
              </el-button>
            </div>
          </div>
        </div>

        <!-- 营业时间 -->
        <div class="detail-section" v-if="selectedHospital.businessHours">
          <h4>营业时间</h4>
          <p>{{ selectedHospital.businessHours }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * PhysicalExam.vue - 体检机构页面
 * 集成高德地图API，支持定位后显示附近医院
 * 未开启定位时默认展示杭州市内医院
 */
import { ref, reactive, onMounted, computed } from 'vue'
import {
  MapLocation,
  Location,
  FirstAidKit,
  StarFilled,
  CircleCheck,
  Phone,
  Clock,
  Picture,
  Search
} from '@element-plus/icons-vue'
import { getImageUrl } from '@/utils/image'
import {
  searchNearbyHospitals,
  getCityByIP
} from '@/api/amap'
import { isAmapKeyConfigured, AMAP_SECURITY_CONFIG, AMAP_JS_KEY } from '@/config/amap.config'

// 从 localStorage 恢复定位状态
const savedLocation = localStorage.getItem('physicalExamLocation')
const parsedLocation = savedLocation ? JSON.parse(savedLocation) : null

// 定位状态
const locationEnabled = ref(parsedLocation?.enabled || false)
const locationLoading = ref(false)
const currentCity = ref(parsedLocation?.city || '')
const userLocation = reactive({
  lat: parsedLocation?.lat || null,
  lng: parsedLocation?.lng || null
})

// 搜索范围（公里）
const searchRadius = ref(parsedLocation?.radius || 5) // 默认5km

// 保存定位状态到 localStorage
const saveLocationState = () => {
  const state = {
    enabled: locationEnabled.value,
    lat: userLocation.lat,
    lng: userLocation.lng,
    city: currentCity.value,
    radius: searchRadius.value
  }
  localStorage.setItem('physicalExamLocation', JSON.stringify(state))
}

// 地图相关
const mapInstance = ref(null)
const mapMarkers = ref([])

// 医院列表
const hospitalList = ref([])
const loading = ref(false)

// 选中的医院
const selectedHospital = ref(null)
const detailDialogVisible = ref(false)

// 杭州市默认医院数据
const hangzhouHospitals = [
  {
    id: 1,
    name: '美年大健康体检中心（西湖分院）',
    address: '杭州市西湖区文三路168号',
    imageUrl: '',
    rating: 4.8,
    tags: ['三甲合作', '高端设备', '快速出报告'],
    features: ['专业医师团队', 'VIP服务', '免费早餐'],
    priceRange: '¥299-1299',
    isRecommended: true,
    description: '美年大健康是中国领先的专业健康体检机构，拥有先进的医疗设备和专业的医师团队。',
    phone: '0571-88888888',
    businessHours: '周一至周日 7:30-17:00',
    packages: [
      { id: 1, name: '基础体检套餐', price: '¥299' },
      { id: 2, name: '全面体检套餐', price: '¥599' },
      { id: 3, name: '高端体检套餐', price: '¥1299' }
    ]
  },
  {
    id: 2,
    name: '爱康国宾体检中心（钱江新城店）',
    address: '杭州市上城区钱江路200号',
    imageUrl: '',
    rating: 4.7,
    tags: ['连锁品牌', '环境优雅', '服务贴心'],
    features: ['一对一服务', '私密空间', '专家解读'],
    priceRange: '¥399-1599',
    isRecommended: true,
    description: '爱康国宾是中国领先的提供体检和就医服务的健康管理机构。',
    phone: '0571-88888889',
    businessHours: '周一至周六 8:00-16:00',
    packages: [
      { id: 1, name: '入职体检套餐', price: '¥199' },
      { id: 2, name: '健康体检套餐', price: '¥499' },
      { id: 3, name: '深度体检套餐', price: '¥1599' }
    ]
  },
  {
    id: 3,
    name: '慈铭体检中心（滨江分院）',
    address: '杭州市滨江区江南大道1000号',
    imageUrl: '',
    rating: 4.6,
    tags: ['专业体检', '设备先进', '交通便利'],
    features: ['免费停车', '报告邮寄', '健康档案'],
    priceRange: '¥259-999',
    description: '慈铭体检是中国体检行业的开创者，提供专业的健康体检服务。',
    phone: '0571-88888890',
    businessHours: '周一至周日 7:00-16:30',
    packages: [
      { id: 1, name: '常规体检套餐', price: '¥259' },
      { id: 2, name: '全面体检套餐', price: '¥599' },
      { id: 3, name: '老年人体检套餐', price: '¥999' }
    ]
  },
  {
    id: 4,
    name: '瑞慈体检中心（拱墅分院）',
    address: '杭州市拱墅区莫干山路500号',
    imageUrl: '',
    rating: 4.5,
    tags: ['高端体检', '精准检测', '舒适环境'],
    features: ['进口设备', '专家会诊', '健康管理'],
    priceRange: '¥499-1999',
    description: '瑞慈体检致力于为中高端人群提供高品质的健康体检服务。',
    phone: '0571-88888891',
    businessHours: '周一至周日 8:00-17:00',
    packages: [
      { id: 1, name: '标准体检套餐', price: '¥499' },
      { id: 2, name: '尊享体检套餐', price: '¥999' },
      { id: 3, name: '至尊体检套餐', price: '¥1999' }
    ]
  },
  {
    id: 5,
    name: '浙江省人民医院体检中心',
    address: '杭州市下城区上塘路158号',
    imageUrl: '',
    rating: 4.9,
    tags: ['公立医院', '权威认证', '医保定点'],
    features: ['三甲资质', '专家坐诊', '设备齐全'],
    priceRange: '¥199-899',
    isRecommended: true,
    description: '浙江省人民医院是浙江省最大的综合性三级甲等医院之一。',
    phone: '0571-88888892',
    businessHours: '周一至周五 7:30-11:30',
    packages: [
      { id: 1, name: '基础体检套餐', price: '¥199' },
      { id: 2, name: '常规体检套餐', price: '¥399' },
      { id: 3, name: '全面体检套餐', price: '¥899' }
    ]
  },
  {
    id: 6,
    name: '浙江大学医学院附属第一医院体检中心',
    address: '杭州市上城区庆春路79号',
    imageUrl: '',
    rating: 4.9,
    tags: ['顶级三甲', '科研实力', '权威可靠'],
    features: ['顶尖专家', '先进设备', '疑难会诊'],
    priceRange: '¥299-1299',
    description: '浙大一院是国家医学中心，拥有国内领先的医疗技术和设备。',
    phone: '0571-88888893',
    businessHours: '周一至周五 8:00-12:00',
    packages: [
      { id: 1, name: '入职体检', price: '¥299' },
      { id: 2, name: '健康体检', price: '¥599' },
      { id: 3, name: '深度体检', price: '¥1299' }
    ]
  }
]

// 加载医院列表
const loadHospitals = async () => {
  loading.value = true
  try {
    if (locationEnabled.value && userLocation.lat && userLocation.lng) {
      // 检查高德地图API密钥是否配置
      if (!isAmapKeyConfigured()) {
        ElMessage.warning('请先配置高德地图API密钥')
        hospitalList.value = [...hangzhouHospitals]
        return
      }
      
      // 使用高德地图API搜索附近医院（使用用户设置的距离）
      const location = `${userLocation.lng},${userLocation.lat}`
      const radiusInMeters = searchRadius.value * 1000 // 转换为米
      const hospitals = await searchNearbyHospitals(location, radiusInMeters)
      
      // 转换数据格式以适配UI
      hospitalList.value = hospitals.map((hospital, index) => ({
        ...hospital,
        id: hospital.id || `amap_${index}`,
        tags: hospital.type ? [hospital.type] : ['医疗机构'],
        features: ['专业医疗', '优质服务'],
        isRecommended: index < 3, // 前3个标记为推荐
        description: `${hospital.name}，${hospital.address}，距离您${formatDistance(hospital.distance)}`
      }))
      
      // 更新地图标记
      updateMapMarkers()
    } else {
      // 显示杭州市内医院
      hospitalList.value = [...hangzhouHospitals]
    }
  } catch (error) {
    console.error('加载医院列表失败:', error)
    ElMessage.error('获取附近医院失败，显示默认数据')
    hospitalList.value = [...hangzhouHospitals]
  } finally {
    loading.value = false
  }
}

// 确认距离变化并搜索
const confirmRadiusChange = async () => {
  if (locationEnabled.value && userLocation.lat && userLocation.lng) {
    ElMessage.info(`正在搜索 ${searchRadius.value}km 范围内的医院...`)
    await loadHospitals()
    // 保存搜索范围
    saveLocationState()
  }
}

// 根据搜索距离计算地图缩放级别
const getZoomByRadius = (radiusKm) => {
  // 距离越大，缩放级别越小（显示范围越大）
  if (radiusKm <= 1) return 15
  if (radiusKm <= 3) return 14
  if (radiusKm <= 5) return 13
  if (radiusKm <= 10) return 12
  if (radiusKm <= 20) return 11
  if (radiusKm <= 40) return 10
  if (radiusKm <= 60) return 9
  return 8 // 80km
}

// 初始化高德地图
const initMap = async () => {
  if (!userLocation.lat || !userLocation.lng) return

  // 等待DOM渲染完成
  setTimeout(async () => {
    const container = document.getElementById('amap-container')
    if (!container) return

    // 销毁旧地图实例
    if (mapInstance.value) {
      mapInstance.value.destroy()
      mapInstance.value = null
    }

    try {
      // 配置安全密钥
      window._AMapSecurityConfig = {
        securityJsCode: AMAP_SECURITY_CONFIG.securityJsCode
      }

      // 使用高德 Loader 加载地图
      const AMap = await window.AMapLoader.load({
        key: AMAP_JS_KEY,
        version: '2.0',
        plugins: []
      })

      // 创建新地图实例
      mapInstance.value = new AMap.Map('amap-container', {
        zoom: getZoomByRadius(searchRadius.value),
        center: [userLocation.lng, userLocation.lat]
      })

      // 更新标记
      updateMapMarkers()
    } catch (error) {
      console.error('地图加载失败:', error)
      ElMessage.error('地图加载失败，请检查网络连接')
    }
  }, 100)
}

// 创建用户位置标记的 SVG 图标
const createUserMarkerIcon = () => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="48" viewBox="0 0 36 48">
      <defs>
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.3"/>
        </filter>
      </defs>
      <path d="M18 0C8.06 0 0 8.06 0 18c0 13.5 18 30 18 30s18-16.5 18-30C36 8.06 27.94 0 18 0z" fill="#ff4d4f" filter="url(#shadow)"/>
      <circle cx="18" cy="18" r="8" fill="#fff"/>
      <circle cx="18" cy="18" r="5" fill="#ff4d4f"/>
    </svg>
  `
  return new AMap.Icon({
    image: 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg))),
    size: new AMap.Size(36, 48),
    imageSize: new AMap.Size(36, 48),
    anchor: 'center'
  })
}

// 创建医院标记的 SVG 图标
const createHospitalMarkerIcon = (number) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="40" viewBox="0 0 32 40">
      <defs>
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.3"/>
        </filter>
        <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:#1890ff;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#096dd9;stop-opacity:1" />
        </linearGradient>
      </defs>
      <path d="M16 0C7.16 0 0 7.16 0 16c0 12 16 24 16 24s16-12 16-24C32 7.16 24.84 0 16 0z" fill="url(#grad)" filter="url(#shadow)"/>
      <circle cx="16" cy="16" r="12" fill="#fff"/>
      <text x="16" y="21" text-anchor="middle" fill="#1890ff" font-size="14" font-weight="bold">${number}</text>
    </svg>
  `
  return new AMap.Icon({
    image: 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg))),
    size: new AMap.Size(32, 40),
    imageSize: new AMap.Size(32, 40),
    anchor: 'center'
  })
}

// 更新地图标记
const updateMapMarkers = () => {
  if (!mapInstance.value || !userLocation.lat || !userLocation.lng) return

  // 清除旧标记
  mapMarkers.value.forEach(marker => marker.setMap(null))
  mapMarkers.value = []

  // 添加用户位置标记（红色定位图标）
  const userMarker = new AMap.Marker({
    position: [userLocation.lng, userLocation.lat],
    title: '您的位置',
    icon: createUserMarkerIcon(),
    offset: new AMap.Pixel(0, -24)
  })
  userMarker.setMap(mapInstance.value)
  mapMarkers.value.push(userMarker)

  // 添加医院标记（蓝色带数字图标）
  hospitalList.value.slice(0, 10).forEach((hospital, index) => {
    if (!hospital.location) return

    const [lng, lat] = hospital.location.split(',').map(Number)
    if (isNaN(lng) || isNaN(lat)) return

    const marker = new AMap.Marker({
      position: [lng, lat],
      title: hospital.name,
      icon: createHospitalMarkerIcon(index + 2),
      offset: new AMap.Pixel(0, -20)
    })

    // 点击标记显示信息窗口
    marker.on('click', () => {
      const infoWindow = new AMap.InfoWindow({
        content: `
          <div style="padding: 12px; max-width: 220px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h4 style="margin: 0 0 8px; font-size: 15px; color: #1f2937; font-weight: 600;">${hospital.name}</h4>
            <p style="margin: 0 0 6px; font-size: 13px; color: #6b7280; line-height: 1.5;">${hospital.address}</p>
            <p style="margin: 0; font-size: 13px; color: #1890ff; font-weight: 500;">📍 距离: ${formatDistance(hospital.distance)}</p>
          </div>
        `,
        offset: new AMap.Pixel(0, -40)
      })
      infoWindow.open(mapInstance.value, [lng, lat])
    })

    marker.setMap(mapInstance.value)
    mapMarkers.value.push(marker)
  })

  // 调整地图视野以显示所有标记
  if (mapMarkers.value.length > 1) {
    mapInstance.value.setFitView()
  }
}

// 切换定位
const toggleLocation = async () => {
  if (locationEnabled.value) {
    // 关闭定位
    locationEnabled.value = false
    userLocation.lat = null
    userLocation.lng = null
    currentCity.value = ''
    // 销毁地图实例
    if (mapInstance.value) {
      mapInstance.value.destroy()
      mapInstance.value = null
    }
    // 保存状态
    saveLocationState()
    ElMessage.info('已关闭定位，展示杭州市内医院')
    await loadHospitals()
  } else {
    // 开启定位
    locationLoading.value = true
    try {
      // 获取浏览器地理位置
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          timeout: 10000,
          enableHighAccuracy: true
        })
      })

      userLocation.lat = position.coords.latitude
      userLocation.lng = position.coords.longitude
      locationEnabled.value = true

      // 获取城市信息
      try {
        const cityInfo = await getCityByIP()
        currentCity.value = cityInfo.city || '当前城市'
      } catch (e) {
        currentCity.value = '当前位置'
      }

      // 保存状态
      saveLocationState()

      ElMessage.success('定位成功，展示附近医院')
      await loadHospitals()
      // 初始化地图
      initMap()
    } catch (error) {
      console.error('定位失败:', error)
      ElMessage.warning('定位失败，展示杭州市内医院')
      locationEnabled.value = false
      await loadHospitals()
    } finally {
      locationLoading.value = false
    }
  }
}

// 重置定位
const resetLocation = () => {
  locationEnabled.value = false
  userLocation.lat = null
  userLocation.lng = null
  currentCity.value = ''
  // 销毁地图实例
  if (mapInstance.value) {
    mapInstance.value.destroy()
    mapInstance.value = null
  }
  loadHospitals()
}

// 选择医院
const selectHospital = (hospital) => {
  selectedHospital.value = hospital
  detailDialogVisible.value = true
}

// 格式化距离
const formatDistance = (distance) => {
  if (!distance && distance !== 0) return ''
  if (distance < 1000) {
    return `${Math.round(distance)}m`
  }
  return `${(distance / 1000).toFixed(1)}km`
}

onMounted(() => {
  // 如果有保存的定位状态，恢复定位
  if (locationEnabled.value && userLocation.lat && userLocation.lng) {
    loadHospitals().then(() => {
      // 延迟初始化地图，确保DOM已渲染
      setTimeout(() => {
        initMap()
      }, 200)
    })
  } else {
    // 默认加载杭州市内医院
    loadHospitals()
  }
})
</script>

<style scoped lang="scss">
// 设计系统变量
.physical-exam-container {
  --primary-color: #1890ff;
  --primary-light: #40a9ff;
  --primary-lighter: #69c0ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #ff4d4f;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --border-color: #e5e7eb;
  --card-radius: 16px;
  --card-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  --card-shadow-hover: 0 8px 24px rgba(24, 144, 255, 0.12);

  padding: 20px;
  background: var(--bg-secondary);
  min-height: calc(100vh - 84px);
}

// Hero Section - 仿健康管理看板风格
.hero-section {
  margin: -20px -20px 24px;
  padding: 60px 40px 50px;
  text-align: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 20% 80%, rgba(24, 144, 255, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(54, 207, 201, 0.15) 0%, transparent 50%);
    pointer-events: none;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-block;
  font-size: 12px;
  letter-spacing: 3px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 16px;
  padding: 6px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.05);
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  margin-bottom: 16px;
  text-transform: uppercase;
}

.hero-desc {
  max-width: 500px;
  margin: 0 auto 32px;

  p {
    font-size: 14px;
    line-height: 1.8;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 4px;
  }
}

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  position: relative;
  z-index: 1;
  margin-top: 32px;

  .stat-item {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 80px;

    .stat-value {
      font-size: 36px;
      font-weight: 700;
      color: #fff;
      line-height: 1;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 36px;
    }

    .stat-label {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.6);
      letter-spacing: 1px;
      line-height: 1;
      margin-top: 8px;
    }

    // 状态指示器 - 呼吸灯效果
    .status-indicator {
      display: inline-block;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #ff4d4f !important;
      box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.7);
      animation: breathe-red 2s ease-in-out infinite;
      -webkit-background-clip: unset !important;
      -webkit-text-fill-color: unset !important;
      background-clip: unset !important;
      flex-shrink: 0;

      &.active {
        background: #52c41a !important;
        box-shadow: 0 0 0 0 rgba(82, 196, 26, 0.7);
        animation: breathe-green 2s ease-in-out infinite;
      }
    }
  }

  // 红色呼吸灯动画
  @keyframes breathe-red {
    0% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.7);
    }
    50% {
      transform: scale(1.1);
      box-shadow: 0 0 0 10px rgba(255, 77, 79, 0);
    }
    100% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(255, 77, 79, 0);
    }
  }

  // 绿色呼吸灯动画
  @keyframes breathe-green {
    0% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(82, 196, 26, 0.7);
    }
    50% {
      transform: scale(1.1);
      box-shadow: 0 0 0 10px rgba(82, 196, 26, 0);
    }
    100% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(82, 196, 26, 0);
    }
  }

  .stat-divider {
    width: 1px;
    height: 50px;
    background: linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
  }
}

// 定位控制栏
.location-bar {
  margin-bottom: 24px;

  .location-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-primary);
    padding: 20px 24px;
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
  }

  .location-info {
    display: flex;
    align-items: center;
    gap: 16px;

    .location-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: var(--bg-secondary);
      color: var(--text-tertiary);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;

      &.active {
        background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
        color: var(--primary-color);
      }
    }

    .location-text {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .location-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }

      .location-desc {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }
  }

  .location-controls {
    display: flex;
    align-items: center;
    gap: 20px;

    .distance-selector {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 16px;
      background: var(--bg-secondary);
      border-radius: 8px;

      .distance-label {
        font-size: 14px;
        color: var(--text-secondary);
        white-space: nowrap;
      }

      .distance-value {
        font-size: 14px;
        font-weight: 600;
        color: var(--primary-color);
        min-width: 45px;
        text-align: right;
      }

      .confirm-btn {
        margin-left: 8px;
        padding: 6px 12px;
        font-size: 13px;

        .el-icon {
          margin-right: 4px;
          font-size: 12px;
        }
      }

      :deep(.el-slider) {
        .el-slider__runway {
          background-color: var(--border-color);
        }

        .el-slider__bar {
          background-color: var(--primary-color);
        }

        .el-slider__button {
          border-color: var(--primary-color);
        }

        .el-slider__marks-text {
          font-size: 12px;
          color: var(--text-tertiary);
        }
      }
    }
  }

  .location-btn {
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;

    .el-icon {
      margin-right: 6px;
    }
  }
}

// 地图区域
.map-section {
  margin-bottom: 24px;

  .map-container {
    background: var(--bg-primary);
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
    overflow: hidden;
    position: relative;

    .amap-container {
      width: 100%;
      height: 400px;
    }

    .map-loading,
    .map-error {
      height: 400px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: var(--text-tertiary);
      gap: 12px;

      p {
        margin: 0;
        font-size: 14px;
      }
    }

    .map-legend {
      position: absolute;
      bottom: 16px;
      left: 16px;
      background: rgba(255, 255, 255, 0.95);
      padding: 12px 16px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      display: flex;
      gap: 20px;

      .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: var(--text-secondary);

        .legend-marker {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
          font-size: 11px;
          font-weight: 600;

          &.red {
            background: #ff4d4f;
          }

          &.blue {
            background: #1890ff;
          }
        }
      }
    }
  }
}

// 医院列表区域
.hospitals-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;

      .el-icon {
        color: var(--primary-color);
      }
    }

    .location-tag {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: var(--bg-primary);
      border-radius: 20px;
      font-size: 13px;
      color: var(--text-secondary);
      box-shadow: var(--card-shadow);

      .el-icon {
        color: var(--primary-color);
      }
    }
  }

  .loading-state {
    background: var(--bg-primary);
    padding: 40px;
    border-radius: var(--card-radius);
    box-shadow: var(--card-shadow);
  }
}

// 医院网格
.hospitals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

// 医院卡片
.hospital-card {
  background: var(--bg-primary);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;

  &:hover {
    box-shadow: var(--card-shadow-hover);
    transform: translateY(-4px);
    border-color: var(--primary-lighter);
  }

  // 医院图片
  .hospital-image {
    position: relative;
    height: 200px;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }

    &:hover img {
      transform: scale(1.05);
    }

    .hospital-image-placeholder {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--primary-color);
    }

    // 序号标记
    .number-badge {
      position: absolute;
      top: 12px;
      left: 12px;
      width: 28px;
      height: 28px;
      background: #1890ff;
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 600;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    // 距离标签
    .distance-badge {
      position: absolute;
      top: 12px;
      right: 12px;
      background: rgba(0, 0, 0, 0.7);
      color: #fff;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    // 推荐标签
    .recommend-badge {
      position: absolute;
      bottom: 12px;
      right: 12px;
      background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
      color: #fff;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  // 医院信息
  .hospital-info {
    padding: 20px;

    .hospital-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;

      .hospital-name {
        font-size: 17px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        flex: 1;
        line-height: 1.4;
      }

      .hospital-rating {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #ff9900;
        font-size: 14px;
        font-weight: 600;
        flex-shrink: 0;
        margin-left: 8px;

        .el-icon {
          font-size: 16px;
        }
      }
    }

    .hospital-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;

      .el-tag {
        border-radius: 12px;
      }
    }

    .hospital-address {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 12px;

      .el-icon {
        color: var(--primary-color);
        flex-shrink: 0;
      }

      span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .hospital-features {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border-color);

      .feature-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: var(--text-secondary);

        .el-icon {
          color: var(--success-color);
          font-size: 14px;
        }
      }
    }

    .hospital-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .contact-info {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: var(--text-secondary);

        .el-icon {
          color: var(--primary-color);
        }
      }
    }
  }
}

// 空状态
.empty-state {
  padding: 60px 0;
  background: var(--bg-primary);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);

  .custom-empty-icon {
    margin-bottom: 16px;
  }
}

// 医院详情对话框
.hospital-detail-dialog {
  :deep(.el-dialog__header) {
    padding: 24px 24px 16px;
    border-bottom: 1px solid var(--border-color);

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }
}

.hospital-detail {
  .detail-header {
    display: flex;
    gap: 20px;
    margin-bottom: 24px;

    .detail-image {
      width: 200px;
      height: 150px;
      border-radius: 12px;
      overflow: hidden;
      flex-shrink: 0;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .detail-image-placeholder {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-color);
      }
    }

    .detail-info {
      flex: 1;

      h3 {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 12px;
      }

      .detail-rating {
        margin-bottom: 12px;
      }

      .detail-address,
      .detail-phone,
      .detail-hours {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: var(--text-secondary);
        margin-bottom: 8px;

        .el-icon {
          color: var(--primary-color);
        }
      }
    }
  }

  .detail-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    h4 {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 12px;
      padding-left: 12px;
      border-left: 3px solid var(--primary-color);
    }

    p {
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.8;
      margin: 0;
    }

    .packages-list {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .package-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background: var(--bg-secondary);
        border-radius: 8px;

        .package-info {
          display: flex;
          align-items: center;
          gap: 16px;

          .package-name {
            font-size: 14px;
            color: var(--text-primary);
          }

          .package-price {
            font-size: 16px;
            font-weight: 600;
            color: var(--primary-color);
          }
        }
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .physical-exam-container {
    padding: 12px;
  }

  .hero-section {
    margin: -12px -12px 20px;
    padding: 40px 20px 32px;

    .hero-title {
      font-size: 32px;
      letter-spacing: 2px;
    }

    .hero-subtitle {
      font-size: 14px;
    }

    .hero-desc {
      p {
        font-size: 13px;
      }
    }

    .hero-stats {
      gap: 24px;

      .stat-item {
        .stat-value {
          font-size: 28px;
        }

        .stat-label {
          font-size: 12px;
        }
      }

      .stat-divider {
        height: 40px;
      }
    }
  }

  .location-bar {
    .location-content {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
    }

    .location-btn {
      width: 100%;
    }
  }

  .map-section {
    .map-container {
      .static-map,
      .map-loading,
      .map-error {
        height: 250px;
      }

      .map-legend {
        position: relative;
        bottom: auto;
        left: auto;
        margin: 12px;
      }
    }
  }

  .hospitals-grid {
    grid-template-columns: 1fr;
  }

  .hospital-detail {
    .detail-header {
      flex-direction: column;

      .detail-image {
        width: 100%;
        height: 200px;
      }
    }
  }
}
</style>
