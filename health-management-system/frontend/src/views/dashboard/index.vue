<template>
  <div class="dashboard-container">
    <!-- 1. Hero 轮播区域 -->
    <section class="hero-section animate-fade-in">
      <el-skeleton :rows="3" animated v-if="loading && carouselItems.length === 0" />
      <div v-else-if="carouselItems.length > 0" class="hero-carousel">
        <el-carousel
          height="42.86vw"
          :interval="5000"
          arrow="always"
          trigger="click"
        >
          <el-carousel-item
            v-for="(item, index) in carouselItems"
            :key="index"
          >
            <div class="carousel-item" :style="{ backgroundImage: `url(${getImageUrl(item.image)})` }">
              <div class="hero-overlay"></div>
              <div class="hero-content">
                <h1 class="hero-title">{{ item.title }}</h1>
                <p class="hero-subtitle">{{ item.description }}</p>
              </div>
              <!-- 装饰元素 -->
              <div class="hero-decoration">
                <div class="decoration-circle circle-1"></div>
                <div class="decoration-circle circle-2"></div>
                <div class="decoration-circle circle-3"></div>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
      <!-- 默认静态 Banner（无轮播数据时显示） -->
      <div v-else class="hero-banner">
        <div class="hero-overlay"></div>
        <div class="hero-content">
          <h1 class="hero-title">智慧健康管理平台</h1>
          <p class="hero-subtitle">基于Kimi AI技术，为您提供个性化、专业化的健康管理服务</p>
          <div class="hero-actions">
            <el-button type="primary" size="large" class="hero-btn-primary" @click="handlePrimaryAction">
              立即体验
            </el-button>
            <el-button size="large" class="hero-btn-secondary" @click="handleSecondaryAction">
              了解更多
            </el-button>
          </div>
        </div>
        <!-- 装饰元素 -->
        <div class="hero-decoration">
          <div class="decoration-circle circle-1"></div>
          <div class="decoration-circle circle-2"></div>
          <div class="decoration-circle circle-3"></div>
        </div>
      </div>
    </section>

    <!-- 2. 统计数据展示区域 - 简约数字设计 -->
    <section class="stats-section animate-slide-up delay-1">
      <div class="stats-container">
        <div class="stats-header">
          <span class="section-tag">DATA</span>
          <h2 class="section-title">数据见证实力</h2>
        </div>
        <div class="stats-divider"></div>
        <div class="stats-grid-minimal">
          <div v-for="(stat, index) in statistics" :key="index" class="stat-item-minimal">
            <div class="stat-number-minimal">{{ stat.value }}</div>
            <div class="stat-label-minimal">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 3. 核心功能区域 - 卡片式设计 -->
    <section class="features-section animate-slide-up delay-2">
      <div class="features-header">
        <span class="section-tag">SERVICES</span>
        <h2 class="section-title">核心服务</h2>
        <p class="section-desc">为不同场景提供专业健康管理解决方案</p>
      </div>
      <div class="features-grid">
        <div
          v-for="(feature, index) in features"
          :key="index"
          class="feature-card"
          :class="{ 'feature-card-large': index === 0 }"
          @click="navigateTo(feature.path)"
        >
          <div class="feature-number">0{{ index + 1 }}</div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
          <div class="feature-arrow">
            <span>了解更多</span>
            <div class="arrow-line"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. 快速入口区域 - 深色背景 -->
    <section class="quick-links-section-dark animate-slide-up delay-3">
      <div class="quick-links-container-dark">
        <!-- 左侧：快速入口 -->
        <div class="quick-links-left">
          <div class="quick-links-header-dark">
            <span class="section-tag light">QUICK ACCESS</span>
            <h2 class="section-title light">快速入口</h2>
          </div>
          <div class="quick-links-list-dark">
            <div
              v-for="(entry, index) in quickEntries"
              :key="index"
              class="quick-link-item-dark"
              @click="navigateTo(entry.path)"
            >
              <div class="quick-link-content-dark">
                <h4>{{ entry.label }}</h4>
                <p>{{ entry.description }}</p>
              </div>
              <div class="quick-link-arrow-dark">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </div>
            </div>
          </div>
        </div>


      </div>
    </section>

    <!-- 5. 健康资讯区域 - 混合布局 -->
    <section class="articles-section animate-slide-up delay-4">
      <div class="articles-header">
        <span class="section-tag">ARTICLES</span>
        <h2 class="section-title">健康资讯</h2>
        <p class="section-desc">获取最新健康知识</p>
        <el-button type="primary" text class="view-more-btn" @click="viewMoreArticles">
          查看更多 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
      <!-- 加载骨架屏 -->
      <div v-if="loading" class="articles-mixed-grid">
        <div v-for="n in 4" :key="n" class="article-featured-skeleton">
          <el-skeleton animated>
            <template #template>
              <el-skeleton-item variant="image" style="width: 100%; height: 200px; border-radius: 16px" />
              <div style="padding: 16px 0">
                <el-skeleton-item variant="h3" style="width: 60%" />
                <div style="margin-top: 12px">
                  <el-skeleton-item variant="text" style="width: 100%" />
                  <el-skeleton-item variant="text" style="width: 70%; margin-top: 8px" />
                </div>
              </div>
            </template>
          </el-skeleton>
        </div>
      </div>
      <!-- 空状态 -->
      <el-empty
        v-else-if="healthArticles.length === 0"
        description="暂无健康知识文章"
        :image-size="120"
      />
      <div v-else class="articles-mixed-container">
        <!-- 有封面的文章 - 网格卡片布局 -->
        <div v-if="articlesWithCover.length > 0" class="articles-grid-section">
          <div class="articles-grid">
            <div
              v-for="(article, index) in articlesWithCover"
              :key="'cover-' + index"
              class="article-card-with-cover"
              @click="readArticle(article)"
            >
              <div class="article-cover-wrapper">
                <img :src="getImageUrl(article.imageUrl)" :alt="article.title" class="article-cover-img" />
                <div class="article-cover-overlay">
                  <el-tag size="small" effect="dark" class="article-cover-tag">{{ article.tag }}</el-tag>
                </div>
              </div>
              <div class="article-cover-content">
                <h4 class="article-cover-title">{{ article.title }}</h4>
                <p class="article-cover-summary">{{ article.summary }}</p>
                <div class="article-cover-meta">
                  <span class="article-cover-date">
                    <el-icon><Calendar /></el-icon>
                    {{ article.date }}
                  </span>
                  <span class="article-cover-views">
                    <el-icon><View /></el-icon>
                    {{ article.views }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 无封面的文章 - 胶囊列表布局 -->
        <div v-if="articlesWithoutCover.length > 0" class="articles-capsule-section">
          <div class="capsule-section-header">
            <span class="capsule-section-label">更多资讯</span>
          </div>
          <div class="articles-capsule-list">
            <div
              v-for="(article, index) in articlesWithoutCover"
              :key="'nocover-' + index"
              class="article-capsule"
              @click="readArticle(article)"
            >
              <div class="capsule-content">
                <div class="capsule-main">
                  <el-tag size="small" :type="article.tagType" class="capsule-tag">{{ article.tag }}</el-tag>
                  <h4 class="capsule-title">{{ article.title }}</h4>
                  <p class="capsule-summary">{{ article.summary }}</p>
                </div>
                <div class="capsule-meta">
                  <span class="capsule-date">{{ article.date }}</span>
                  <div class="capsule-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. 优势展示区域 - 深色背景横向滚动 -->
    <section class="why-us-section animate-slide-up delay-5">
      <div class="why-us-header-dark">
        <span class="section-tag light">WHY CHOOSE US</span>
        <h2 class="section-title light">为什么选择我们</h2>
        <p class="why-us-subtitle">专业 · 智能 · 安全 · 高效</p>
        <p class="why-us-subtitle-en">Professional · Intelligent · Secure · Efficient</p>
      </div>
      <div class="why-us-scroll-container">
        <div class="why-us-scroll-wrapper">
          <!-- 第一组卡片 -->
          <div v-for="(item, index) in whyUsFeatures" :key="'first-' + index" class="why-us-card">
            <div class="why-us-card-number">{{ String(index + 1).padStart(2, '0') }}</div>
            <div class="why-us-card-content">
              <h4 class="why-us-card-title">{{ item.title }}</h4>
              <span class="why-us-card-title-en">{{ item.titleEn }}</span>
              <p class="why-us-card-desc">{{ item.desc }}</p>
              <span class="why-us-card-desc-en">{{ item.descEn }}</span>
            </div>
          </div>
          <!-- 第二组卡片（复制实现无缝滚动） -->
          <div v-for="(item, index) in whyUsFeatures" :key="'second-' + index" class="why-us-card">
            <div class="why-us-card-number">{{ String(index + 1).padStart(2, '0') }}</div>
            <div class="why-us-card-content">
              <h4 class="why-us-card-title">{{ item.title }}</h4>
              <span class="why-us-card-title-en">{{ item.titleEn }}</span>
              <p class="why-us-card-desc">{{ item.desc }}</p>
              <span class="why-us-card-desc-en">{{ item.descEn }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
/**
 * Dashboard 首页组件
 * @description 智慧健康管理平台首页，包含Hero区域、统计数据、解决方案、快速入口、健康资讯、优势展示和CTA区域
 */

defineOptions({
  name: 'Dashboard'
})

import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getImageUrl } from '@/utils/image'
import AuroraBackground from '@/components/AuroraBackground.vue'

import {
  ArrowRight,
  Calendar,
  View,
  User,
  OfficeBuilding,
  Location,
  Clock,
  FirstAidKit,
  ChatDotRound,
  Document,
  Warning,
  Apple,
  Moon,
  Watermelon,
  Sunrise,
  Trophy,
  Grid,
  Pointer,
  Reading,
  Cpu,
  UserFilled,
  Lock,
  Service,
  TrendCharts,
  Histogram,
  DataLine,
  Monitor,
  Sunny,
  Cloudy,
  Pouring,
  InfoFilled,
  WindPower
} from '@element-plus/icons-vue'
import { getArticles, getCarousel } from '@/api/article'

const router = useRouter()
const { isLoggedIn } = useAuth()

// ==================== 数据定义 ====================

// 统计数据 - 统一蓝白渐变色调
const statistics = ref([
  {
    value: '300万+',
    label: '服务用户',
    icon: 'User',
    color: '#1890ff'
  },
  {
    value: '500+',
    label: '合作机构',
    icon: 'OfficeBuilding',
    color: '#40a9ff'
  },
  {
    value: '320个',
    label: '覆盖城市',
    icon: 'Location',
    color: '#69c0ff'
  },
  {
    value: '15年',
    label: '行业经验',
    icon: 'Clock',
    color: '#91d5ff'
  }
])

// 核心功能数据 - 简约设计
const features = ref([
  {
    title: '个人健康管理',
    description: '日常健康监测与预警，为您提供个性化的健康建议和风险评估',
    path: '/health'
  },
  {
    title: 'AI智能问诊',
    description: '7×24小时在线健康咨询，基于大模型的智能诊断服务',
    path: '/ai-doctor'
  },
  {
    title: '体检报告管理',
    description: '体检报告智能解读，一键生成个性化健康建议',
    path: '/physical-exam'
  },
  {
    title: '健康资讯中心',
    description: '汇集最新健康科普文章，助您掌握健康知识',
    path: '/articles'
  }
])

// 为什么选择我们 - 中英文对照
const whyUsFeatures = ref([
  { title: 'AI智能分析', titleEn: 'AI-Powered Analytics', desc: '基于大模型的精准健康评估', descEn: 'Precision health assessment powered by LLM' },
  { title: '专业团队', titleEn: 'Expert Team', desc: '千名健康专家在线支持', descEn: 'Thousands of health experts at your service' },
  { title: '数据安全', titleEn: 'Data Security', desc: '银行级加密保护隐私', descEn: 'Bank-grade encryption for privacy protection' },
  { title: '全天候服务', titleEn: '24/7 Service', desc: '7×24小时健康监测', descEn: 'Round-the-clock health monitoring' },
  { title: '个性方案', titleEn: 'Personalized Plans', desc: '量身定制健康管理方案', descEn: 'Tailored health management solutions' },
  { title: '智能预警', titleEn: 'Smart Alerts', desc: '实时监测风险预警', descEn: 'Real-time risk monitoring & alerts' },
  { title: '全周期管理', titleEn: 'Lifecycle Care', desc: '覆盖全生命周期健康', descEn: 'Full lifecycle health coverage' },
  { title: '科技赋能', titleEn: 'Tech Enabled', desc: '前沿科技驱动健康', descEn: 'Cutting-edge technology for wellness' }
])

// 快速入口数据 - 简约列表设计
const quickEntries = ref([
  {
    label: '健康管理',
    description: '多维健康数据看板',
    path: '/health'
  },
  {
    label: 'AI健管师',
    description: '智能健康咨询服务',
    path: '/ai-doctor'
  },
  {
    label: '体检管理',
    description: '预约与查看体检报告',
    path: '/physical-exam'
  },
  {
    label: '报告解读',
    description: '专业报告分析建议',
    path: '/report'
  },
  {
    label: '健康资讯',
    description: '最新健康科普文章',
    path: '/articles'
  },
  {
    label: '个人中心',
    description: '管理个人信息设置',
    path: '/profile'
  }
])



// 轮播图数据 - 从后端API获取
const carouselItems = ref([])

// 天气数据
const weatherData = ref(null)

// 天气健康建议映射
const weatherHealthTips = {
  '晴': '天气晴朗，适合户外活动。注意防晒，多喝水，保持充足水分。',
  '多云': '天气舒适，适合运动。建议进行户外散步或慢跑，增强体质。',
  '阴': '天气阴沉，注意调节心情。可以进行室内运动，保持心情愉悦。',
  '小雨': '有小雨，出门记得带伞。路面湿滑，注意行走安全。',
  '中雨': '降雨明显，建议减少外出。注意保暖，避免着凉感冒。',
  '大雨': '雨势较大，尽量待在室内。注意防潮，保持室内通风。',
  '雷阵雨': '雷雨天气，注意安全。避免在空旷地带活动，关闭电器。',
  '雪': '下雪天气，注意保暖防滑。减少外出，多喝热水。',
  '雾霾': '空气质量较差，减少户外活动。外出请佩戴口罩，开启空气净化器。'
}

// 根据天气获取健康建议
const weatherHealthTip = computed(() => {
  if (!weatherData.value) return ''
  const type = weatherData.value.type
  return weatherHealthTips[type] || '注意天气变化，保持健康生活方式。'
})

// 当前时间
const currentTime = computed(() => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

// 当前日期
const currentDate = computed(() => {
  const now = new Date()
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const dayName = days[now.getDay()]
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const date = String(now.getDate()).padStart(2, '0')
  return `周${dayName} ${month}-${date}`
})

// AQI等级计算
const aqiLevel = computed(() => {
  if (!weatherData.value) return '良'
  const aqi = weatherData.value.aqi || 85
  if (aqi <= 50) return '优'
  if (aqi <= 100) return '良'
  if (aqi <= 150) return '轻度污染'
  if (aqi <= 200) return '中度污染'
  return '重度污染'
})

// AQI等级样式类
const aqiLevelClass = computed(() => {
  if (!weatherData.value) return 'aqi-good'
  const aqi = weatherData.value.aqi || 85
  if (aqi <= 50) return 'aqi-excellent'
  if (aqi <= 100) return 'aqi-good'
  if (aqi <= 150) return 'aqi-light'
  if (aqi <= 200) return 'aqi-moderate'
  return 'aqi-heavy'
})

// AQI百分比
const aqiPercent = computed(() => {
  if (!weatherData.value) return 50
  const aqi = weatherData.value.aqi || 85
  return Math.min((aqi / 200) * 100, 100)
})

// 运动指数
const sportIndex = computed(() => {
  if (!weatherData.value) return '适宜'
  const type = weatherData.value.type
  if (['晴', '多云'].includes(type)) return '适宜'
  if (['阴', '小雨'].includes(type)) return '较适宜'
  return '不宜'
})

// 穿衣指数
const clothingIndex = computed(() => {
  if (!weatherData.value) return '舒适'
  const temp = weatherData.value.temperature
  if (temp >= 28) return '炎热'
  if (temp >= 24) return '热'
  if (temp >= 20) return '舒适'
  if (temp >= 15) return '凉爽'
  if (temp >= 10) return '冷'
  return '寒冷'
})

// 健康知识文章数据 - 从后端API获取
const healthArticles = ref([])

// 加载状态
const loading = ref(false)

// ==================== 计算属性 ====================

// 有封面的文章
const articlesWithCover = computed(() => {
  return healthArticles.value.filter(article => article.imageUrl)
})

// 无封面的文章
const articlesWithoutCover = computed(() => {
  return healthArticles.value.filter(article => !article.imageUrl)
})

// ==================== 轮播图方法 ====================

// ==================== 方法定义 ====================

/**
 * 处理主按钮点击 - 立即体验
 */
const handlePrimaryAction = () => {
  if (isLoggedIn.value) {
    router.push('/ai-doctor')
  } else {
    router.push('/login')
  }
}

/**
 * 处理次按钮点击 - 了解更多
 */
const handleSecondaryAction = () => {
  // 滚动到解决方案区域
  const solutionsSection = document.querySelector('.solutions-section')
  if (solutionsSection) {
    solutionsSection.scrollIntoView({ behavior: 'smooth' })
  }
}

/**
 * 处理注册按钮点击
 */
const handleRegister = () => {
  router.push('/register')
}

/**
 * 导航到指定路径
 * @param {string} path - 目标路径
 */
const navigateTo = (path) => {
  router.push(path)
}

/**
 * 查看更多文章
 */
const viewMoreArticles = () => {
  router.push('/articles')
}

/**
 * 阅读文章
 * @param {Object} article - 文章对象
 */
const readArticle = (article) => {
  router.push(`/article/${article.id}`)
}

/**
 * 从API加载数据
 */
const loadData = async () => {
  loading.value = true
  carouselItems.value = []
  healthArticles.value = []

  try {
    // 并行加载轮播图和文章列表
    const [carouselRes, articlesRes] = await Promise.all([
      getCarousel().catch(err => {
        console.error('加载轮播图失败:', err)
        return []
      }),
      getArticles().catch(err => {
        console.error('加载文章失败:', err)
        return { data: [] }
      })
    ])

    // 处理轮播图数据 - 适配后端 Carousel 实体类字段
    if (carouselRes && Array.isArray(carouselRes) && carouselRes.length > 0) {
      carouselItems.value = carouselRes.map(item => ({
        id: item.id,
        title: item.title,
        description: item.content,
        image: item.imageUrl
      }))
    }

    // 处理文章列表数据 - 随机选取9个
    if (articlesRes && Array.isArray(articlesRes) && articlesRes.length > 0) {
      // 随机打乱数组并取前9个
      const shuffled = [...articlesRes].sort(() => Math.random() - 0.5)
      const randomArticles = shuffled.slice(0, 9)

      healthArticles.value = randomArticles.map(item => ({
        id: item.id,
        title: item.title,
        summary: item.summary,
        tag: item.tag || '健康知识',
        tagType: item.tagType || 'primary',
        date: item.createTime ? item.createTime.split(' ')[0] : '2024-01-01',
        views: item.views || 0,
        icon: item.icon || 'Document',
        gradient: item.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        imageUrl: item.imageUrl
      }))
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

/**
 * 加载天气数据
 */
const loadWeatherData = async () => {
  // 模拟天气数据（实际项目中应该调用天气API）
  // 这里使用模拟数据演示效果
  setTimeout(() => {
    weatherData.value = {
      city: '北京',
      temperature: 22,
      type: '晴',
      windDirection: '东南风',
      windPower: '2级',
      humidity: 45,
      aqi: 85,
      visibility: '10km'
    }
  }, 500)
}

// ==================== 生命周期钩子 ====================

onMounted(() => {
  // 延迟加载数据，确保页面先渲染
  setTimeout(() => {
    loadData()
    loadWeatherData()
  }, 0)
})
</script>

<style scoped lang="scss">
// ==================== CSS 变量定义 ====================
:root {
  --primary-color: #1890ff;
  --primary-gradient: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --border-radius: 16px;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

// ==================== 主容器 ====================
.dashboard-container {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

// ==================== 动画效果 ====================
.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out;
}

.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
.delay-3 { animation-delay: 0.3s; }
.delay-4 { animation-delay: 0.4s; }
.delay-5 { animation-delay: 0.5s; }
.delay-6 { animation-delay: 0.6s; }

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 悬浮效果 - 简约风格
.hover-lift {
  transition: box-shadow 0.2s ease;
  cursor: pointer;

  &:hover {
    box-shadow: var(--shadow-md);
  }
}

// ==================== 1. Hero 轮播区域 ====================
.hero-section {
  margin-bottom: 48px;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-top: -24px;
  position: relative;
  overflow: hidden;
}

// 极光背景
.hero-aurora-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

// 轮播图容器
.hero-carousel {
  width: 100%;
  overflow: hidden;

  :deep(.el-carousel) {
    width: 100%;

    .el-carousel__container {
      width: 100%;
    }

    .el-carousel__arrow {
      background: rgba(255, 255, 255, 0.9);
      border: none;
      color: var(--primary-color);
      font-size: 20px;
      width: 44px;
      height: 44px;
      transition: background var(--transition-normal), box-shadow var(--transition-normal);

      &:hover {
        background: white;
        box-shadow: var(--shadow-md);
      }
    }

    .el-carousel__indicators {
      bottom: 20px;

      .el-carousel__indicator {
        padding: 0 6px;

        .el-carousel__button {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.5);
          transition: all var(--transition-normal);
        }

        &.is-active .el-carousel__button {
          background: white;
          width: 30px;
          border-radius: 5px;
        }
      }
    }
  }
}

// 轮播项样式
.carousel-item {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 80px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.hero-banner {
  position: relative;
  height: 42.86vw;
  max-height: 600px;
  border-radius: var(--border-radius);
  overflow: hidden;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.95) 0%, rgba(54, 207, 201, 0.9) 100%);
  display: flex;
  align-items: center;
  padding: 0 80px;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 600px;
  color: white;
  text-align: center;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 20px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 18px;
  margin: 0 auto 32px;
  opacity: 0.95;
  line-height: 1.6;
  max-width: 500px;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-btn-primary {
  background: white;
  border: none;
  color: #1890ff;
  font-weight: 600;
  padding: 12px 32px;
  font-size: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.9;
  }
}

.hero-btn-secondary {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.8);
  color: white;
  font-weight: 600;
  padding: 12px 32px;
  font-size: 16px;
  transition: background 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
  }
}

// Hero 装饰元素
.hero-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -50px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: 50px;
  right: 100px;
  animation-delay: -2s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 250px;
  animation-delay: -4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-20px) scale(1.05);
  }
}

// ==================== 通用标题样式 ====================
.section-tag {
  font-size: 12px;
  font-weight: 600;
  color: #1890ff;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 12px;
  display: block;
}

.section-title {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.section-desc {
  font-size: 16px;
  color: #666;
  margin-top: 8px;
}

// 深色背景下的标题样式
.section-tag.light {
  color: rgba(255, 255, 255, 0.5);
}

.section-title.light {
  color: white;
}

.section-desc.light {
  color: rgba(255, 255, 255, 0.6);
}

// ==================== 2. 统计数据展示区域 - 深色背景 ====================
.stats-section {
  margin-bottom: 64px;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-top: -48px;
  position: relative;
  z-index: 10;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.stats-container {
  padding: 48px 80px;
  color: white;
  max-width: 1400px;
  margin: 0 auto;
}

.stats-header {
  text-align: center;
  margin-bottom: 32px;
}

.stats-header .section-tag {
  color: rgba(255, 255, 255, 0.5);
}

.stats-header .section-title {
  color: white;
  font-size: 28px;
}

.stats-divider {
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #1890ff, #36cfc9);
  margin: 0 auto 40px;
  border-radius: 2px;
}

.stats-grid-minimal {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 48px;
}

.stat-item-minimal {
  text-align: center;
}

.stat-number-minimal {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label-minimal {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
}

// ==================== 3. 核心功能区域 - 卡片式设计 ====================
.features-section {
  margin-bottom: 64px;
  padding: 0 20px;
}

.features-header {
  text-align: center;
  margin-bottom: 48px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.feature-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #1890ff, #36cfc9);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-card-large {
  grid-column: span 2;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
}

.feature-card-large .feature-title {
  color: white;
}

.feature-card-large .feature-desc {
  color: rgba(255, 255, 255, 0.7);
}

.feature-number {
  font-size: 14px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 16px;
  letter-spacing: 2px;
}

.feature-card-large .feature-number {
  color: #36cfc9;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 24px;
}

.feature-arrow {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #1890ff;
  font-weight: 500;
}

.arrow-line {
  width: 24px;
  height: 1px;
  background: #1890ff;
  transition: width 0.3s ease;
}

.feature-card:hover .arrow-line {
  width: 40px;
}

// ==================== 4. 快速入口区域 - 深色背景全屏 ====================
.quick-links-section-dark {
  margin-bottom: 64px;
  padding: 64px 0;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
}

.quick-links-container-dark {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: center;
}

.quick-links-left {
  width: 100%;
  max-width: 800px;
}

.quick-links-header-dark {
  margin-bottom: 24px;
}

.quick-links-list-dark {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.quick-link-item-dark {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.quick-link-item-dark:last-child {
  border-bottom: none;
}

.quick-link-item-dark:hover {
  background: rgba(255, 255, 255, 0.1);
  padding-left: 40px;
}

.quick-link-content-dark h4 {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}

.quick-link-content-dark p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.quick-link-arrow-dark {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.quick-link-arrow-dark svg {
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.quick-link-item-dark:hover .quick-link-arrow-dark {
  background: #1890ff;
  border-color: #1890ff;
}

.quick-link-item-dark:hover .quick-link-arrow-dark svg {
  color: white;
  transform: translateX(2px);
}

.entry-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 24px 16px;
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.entry-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.entry-label {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.entry-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

// ==================== 5. 健康资讯区域 - 混合布局 ====================
.articles-section {
  margin-bottom: 64px;
  padding: 0 20px;
}

.articles-header {
  text-align: center;
  margin-bottom: 48px;
  position: relative;
}

.view-more-btn {
  margin-top: 16px;
  font-size: 14px;

  &:hover {
    .el-icon--right {
      transform: translateX(4px);
    }
  }

  .el-icon--right {
    transition: transform 0.3s ease;
  }
}

// 混合容器
.articles-mixed-container {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

// 骨架屏网格
.articles-mixed-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;

  @media (max-width: 992px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 576px) {
    grid-template-columns: 1fr;
  }
}

.article-featured-skeleton {
  background: white;
  border-radius: 16px;
  padding: 16px;
}

// ===== 有封面的文章 - 网格卡片布局 =====
.articles-grid-section {
  width: 100%;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;

  @media (max-width: 992px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 576px) {
    grid-template-columns: 1fr;
  }
}

// 有封面的卡片样式
.article-card-with-cover {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  }
}

.article-cover-wrapper {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.article-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;

  .article-card-with-cover:hover & {
    transform: scale(1.05);
  }
}

.article-cover-overlay {
  position: absolute;
  top: 12px;
  left: 12px;
}

.article-cover-tag {
  background: rgba(0, 0, 0, 0.6) !important;
  border: none !important;
  backdrop-filter: blur(4px);
}

.article-cover-content {
  padding: 20px;
}

.article-cover-title {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-cover-summary {
  font-size: 13px;
  color: #666;
  margin: 0 0 16px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-cover-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #9ca3af;

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

// ===== 无封面的文章 - 胶囊列表布局 =====
.articles-capsule-section {
  width: 100%;
}

.capsule-section-header {
  margin-bottom: 20px;
}

.capsule-section-label {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  padding-left: 12px;
  border-left: 3px solid #1890ff;
}

.articles-capsule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

// 胶囊卡片样式
.article-capsule {
  background: white;
  border-radius: 50px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    border-color: #e0e0e0;
    transform: translateX(4px);
  }
}

.capsule-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  gap: 16px;
}

.capsule-main {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.capsule-tag {
  flex-shrink: 0;
}

.capsule-title {
  font-size: 15px;
  font-weight: 500;
  color: #1a1a2e;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.capsule-summary {
  display: none;
}

.capsule-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.capsule-date {
  font-size: 12px;
  color: #9ca3af;
  white-space: nowrap;
}

.capsule-arrow {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  .el-icon {
    font-size: 14px;
    color: #999;
    transition: all 0.3s ease;
  }

  .article-capsule:hover & {
    background: #1890ff;

    .el-icon {
      color: white;
      transform: translateX(2px);
    }
  }
}

// 响应式：小屏幕下胶囊卡片调整
@media (max-width: 768px) {
  .capsule-content {
    flex-direction: column;
    align-items: flex-start;
    padding: 16px 20px;
    border-radius: 16px;
  }

  .article-capsule {
    border-radius: 16px;
  }

  .capsule-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .capsule-title {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .capsule-summary {
    display: block;
    font-size: 13px;
    color: #666;
    margin: 0;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .capsule-meta {
    width: 100%;
    justify-content: space-between;
  }
}

// ==================== 6. 优势展示区域 ====================
.advantages-section {
  margin-bottom: 48px;
  padding: 0 20px;
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

// ==================== 7. 为什么选择我们 - 深色背景横向滚动 ====================
.why-us-section {
  margin-bottom: 64px;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  background: linear-gradient(135deg, #0a0a1a 0%, #121228 50%, #0d1525 100%);
  padding: 80px 0 100px;
  overflow: hidden;
  position: relative;
}

.why-us-header-dark {
  text-align: center;
  margin-bottom: 56px;
  padding: 0 20px;
  position: relative;
  z-index: 1;

  .section-tag.light {
    color: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    letter-spacing: 3px;
    margin-bottom: 16px;
    display: block;
  }

  .section-title.light {
    color: white;
    margin-bottom: 16px;
    font-size: 36px;
    font-weight: 700;
  }
}

.why-us-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
  font-weight: 500;
  letter-spacing: 4px;
}

.why-us-subtitle-en {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 2px;
  font-weight: 400;
}

.why-us-scroll-container {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 20px 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
  position: relative;
  z-index: 1;

  &::-webkit-scrollbar {
    display: none;
  }
}

.why-us-scroll-wrapper {
  display: flex;
  gap: 24px;
  padding: 0 80px;
  width: max-content;
  animation: scrollLeft 25s linear infinite;
}

@keyframes scrollLeft {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.why-us-card {
  flex-shrink: 0;
  width: 320px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 32px;
  text-align: left;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.35);
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  }
}

.why-us-card-number {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 20px;
  letter-spacing: 2px;
}

.why-us-card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.why-us-card-title {
  font-size: 22px;
  font-weight: 600;
  color: white;
  margin: 0;
  line-height: 1.3;
}

.why-us-card-title-en {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.why-us-card-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  margin: 0;
}

.why-us-card-desc-en {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.5;
  font-style: italic;
}

// ==================== 响应式布局 ====================
@media (max-width: 1200px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .feature-card-large {
    grid-column: span 2;
  }

  .quick-links-container {
    grid-template-columns: 1fr;
  }

  .quick-links-header {
    position: static;
    text-align: center;
  }

  .why-us-content {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .why-us-main {
    padding-right: 0;
    border-right: none;
    border-bottom: 1px solid #e8e8e8;
    padding-bottom: 32px;
  }
}

@media (max-width: 992px) {
  .hero-banner {
    height: 42.86vw;
    padding: 0 40px;
  }

  .hero-title {
    font-size: 36px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .stats-container {
    padding: 40px 32px;
  }

  .stats-grid-minimal {
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 0;
  }

  .hero-banner {
    height: 42.86vw;
    min-height: 200px;
    padding: 0 24px;
    text-align: center;
  }

  .hero-content {
    max-width: 100%;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-subtitle {
    font-size: 14px;
    max-width: 100%;
  }

  .hero-actions {
    flex-direction: column;
    gap: 12px;
  }

  .hero-btn-primary,
  .hero-btn-secondary {
    width: 100%;
    padding: 12px 24px;
  }

  .stats-container {
    padding: 32px 24px;
    border-radius: 16px;
  }

  .stats-grid-minimal {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .stat-number-minimal {
    font-size: 32px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .feature-card-large {
    grid-column: span 1;
  }

  .quick-link-item {
    padding: 16px 20px;
  }

  .why-us-container {
    padding: 32px 24px;
  }

  .why-us-lead {
    font-size: 20px;
  }

  .advantages-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .cta-content {
    padding: 40px 24px;
  }

  .cta-title {
    font-size: 24px;
  }

  .cta-subtitle {
    font-size: 14px;
  }

  .section-header {
    flex-direction: column;
    gap: 12px;
  }

  .stats-section,
  .solutions-section,
  .quick-entry-section,
  .articles-section,
  .advantages-section,
  .cta-section {
    padding: 0 12px;
    margin-bottom: 32px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-entry-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero-decoration,
  .cta-decoration {
    display: none;
  }
}

// ==================== 减少动画偏好支持 ====================
@media (prefers-reduced-motion: reduce) {
  .animate-fade-in,
  .animate-slide-up,
  .delay-1,
  .delay-2,
  .delay-3,
  .delay-4,
  .delay-5,
  .delay-6 {
    animation: none;
    opacity: 1;
    transform: none;
  }

  .hover-lift:hover,
  .entry-card:hover,
  .article-card:hover {
    transform: none;
  }

  .decoration-circle {
    animation: none;
  }
}
</style>
