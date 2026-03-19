<template>
  <div class="article-list-container">
    <!-- 页面头部 - Hero Section 风格 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">HEALTH ARTICLES</div>
        <h1 class="hero-title">健康资讯</h1>
        <p class="hero-subtitle">Health Information Center</p>
        <div class="hero-desc">
          <p>探索健康生活的无限可能</p>
          <p>获取专业的健康知识，开启健康生活</p>
        </div>
      </div>
    </section>



    <!-- 文章列表 -->
    <div class="articles-section">
      <!-- 加载状态 -->
      <el-row :gutter="24" v-if="loading">
        <el-col
          v-for="n in 9"
          :key="n"
          :xs="24"
          :sm="12"
          :md="8"
          class="article-col"
        >
          <el-card class="article-card skeleton-card">
            <el-skeleton animated>
              <template #template>
                <el-skeleton-item variant="image" style="width: 100%; height: 180px" />
                <div style="padding: 16px">
                  <el-skeleton-item variant="h3" style="width: 60%" />
                  <div style="margin-top: 12px">
                    <el-skeleton-item variant="text" style="width: 100%" />
                    <el-skeleton-item variant="text" style="width: 80%; margin-top: 8px" />
                  </div>
                </div>
              </template>
            </el-skeleton>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty
        v-else-if="articles.length === 0"
        description="暂无相关文章"
        :image-size="200"
      >
        <el-button type="primary" @click="resetFilter">查看全部文章</el-button>
      </el-empty>

      <!-- 文章网格 -->
      <el-row :gutter="24" v-else>
        <el-col
          v-for="article in articles"
          :key="article.id"
          :xs="24"
          :sm="12"
          :md="8"
          class="article-col"
        >
          <el-card
            class="article-card hover-lift"
            @click="readArticle(article)"
          >
            <!-- 文章封面 -->
            <div
              class="article-cover"
              :style="article.imageUrl
                ? { backgroundImage: `url(${getImageUrl(article.imageUrl)})` }
                : { background: article.gradient }"
            >
              <div class="cover-overlay">
                <el-tag
                  class="category-tag"
                  :type="article.tagType"
                  effect="dark"
                >
                  {{ article.tag }}
                </el-tag>
              </div>
            </div>

            <!-- 文章内容 -->
            <div class="article-body">
              <h3 class="article-title">{{ article.title }}</h3>
              <p class="article-summary">{{ article.summary }}</p>

              <!-- 文章元信息 -->
              <div class="article-meta">
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ article.date }}
                </span>
                <span class="meta-item">
                  <el-icon><View /></el-icon>
                  {{ article.views }} 阅读
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[9, 18, 27, 36]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * ArticleList.vue - 健康资讯列表页面
 * 展示所有健康文章，支持分类筛选、搜索和分页
 */
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Search,
  Calendar,
  View
} from '@element-plus/icons-vue'
import { getArticles, getCategories } from '@/api/article'
import { getImageUrl } from '@/utils/image'

const router = useRouter()
const route = useRoute()

// 加载状态
const loading = ref(false)

// 文章列表
const articles = ref([])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)

// 分类筛选
const selectedCategory = ref('')
const categories = ref([
  { label: '健康资讯', value: 'health' },
  { label: '疾病科普', value: 'disease' },
  { label: '饮食建议', value: 'diet' },
  { label: '运动指导', value: 'exercise' },
  { label: '心理健康', value: 'mental' },
  { label: '用药指南', value: 'medication' }
])

// 搜索关键词
const searchKeyword = ref('')

/**
 * 加载文章列表
 */
const loadArticles = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      category: selectedCategory.value || undefined,
      keyword: searchKeyword.value || undefined
    }

    const res = await getArticles(params)

    if (res && res.list) {
      articles.value = res.list.map(item => ({
        id: item.id,
        title: item.title,
        summary: item.summary,
        tag: item.categoryName || item.tag || '健康知识',
        tagType: getTagType(item.category),
        date: item.createTime ? item.createTime.split(' ')[0] : '2024-01-01',
        views: item.views || 0,
        gradient: getGradientByCategory(item.category),
        imageUrl: item.imageUrl,
        category: item.category
      }))
      total.value = res.total || 0
    } else if (Array.isArray(res)) {
      // 兼容直接返回数组的情况
      articles.value = res.map(item => ({
        id: item.id,
        title: item.title,
        summary: item.summary,
        tag: item.categoryName || item.tag || '健康知识',
        tagType: getTagType(item.category),
        date: item.createTime ? item.createTime.split(' ')[0] : '2024-01-01',
        views: item.views || 0,
        gradient: getGradientByCategory(item.category),
        imageUrl: item.imageUrl,
        category: item.category
      }))
      total.value = res.length
    }
  } catch (error) {
    console.error('加载文章失败:', error)
    ElMessage.error('加载文章失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

/**
 * 根据分类获取标签类型
 */
const getTagType = (category) => {
  const typeMap = {
    'health': 'primary',
    'disease': 'danger',
    'diet': 'success',
    'exercise': 'warning',
    'mental': 'info',
    'medication': ''
  }
  return typeMap[category] || 'primary'
}

/**
 * 根据分类获取渐变背景
 */
const getGradientByCategory = (category) => {
  const gradientMap = {
    'health': 'linear-gradient(135deg, #1890ff 0%, #36cfc9 100%)',
    'disease': 'linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%)',
    'diet': 'linear-gradient(135deg, #52c41a 0%, #95de64 100%)',
    'exercise': 'linear-gradient(135deg, #faad14 0%, #ffc53d 100%)',
    'mental': 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
    'medication': 'linear-gradient(135deg, #13c2c2 0%, #5cdbd3 100%)'
  }
  return gradientMap[category] || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}

/**
 * 处理分类变化
 */
const handleCategoryChange = () => {
  currentPage.value = 1
  loadArticles()
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  currentPage.value = 1
  loadArticles()
}

/**
 * 重置筛选
 */
const resetFilter = () => {
  selectedCategory.value = ''
  searchKeyword.value = ''
  currentPage.value = 1
  loadArticles()
}

/**
 * 处理分页大小变化
 */
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadArticles()
}

/**
 * 处理页码变化
 */
const handlePageChange = (page) => {
  currentPage.value = page
  loadArticles()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

/**
 * 阅读文章
 */
const readArticle = (article) => {
  router.push(`/article/${article.id}`)
}

/**
 * 加载分类列表
 */
const loadCategories = async () => {
  try {
    const res = await getCategories()
    if (res && Array.isArray(res)) {
      // 将字符串数组转换为 {label, value} 对象数组
      categories.value = res.map((cat, index) => ({
        label: cat,
        value: ['health', 'disease', 'diet', 'exercise', 'mental', 'medication'][index] || cat
      }))
    }
  } catch (error) {
    console.error('加载分类失败:', error)
    // 使用默认分类
  }
}

// 监听路由参数变化
watch(() => route.query, (newQuery) => {
  if (newQuery.category) {
    selectedCategory.value = newQuery.category
  }
  if (newQuery.keyword) {
    searchKeyword.value = newQuery.keyword
  }
}, { immediate: true })

// 页面加载
onMounted(() => {
  loadCategories()
  loadArticles()
})
</script>

<style scoped lang="scss">
.article-list-container {
  min-height: 100vh;
  background: #f5f7fa;
}

// Hero Section - 仿体检机构页面风格
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

// 筛选区域
.filter-section {
  background: white;
  padding: 24px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
}

.filter-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.category-filter {
  flex: 1;
  min-width: 300px;
}

.search-box {
  width: 320px;
}

// 文章列表区域
.articles-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.article-col {
  margin-bottom: 24px;
}

.article-card {
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  :deep(.el-card__body) {
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.skeleton-card {
  cursor: default;

  &:hover {
    transform: none;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }
}

.article-cover {
  height: 180px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3) 0%, transparent 50%);
  padding: 12px;
}

.category-tag {
  border-radius: 4px;
}

.article-body {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 10px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-summary {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #999;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

// 分页
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

// 悬浮效果
.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

// 响应式适配
@media (max-width: 768px) {
  .page-header {
    padding: 40px 0;
  }

  .page-title {
    font-size: 28px;
  }

  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }

  .category-filter {
    min-width: auto;
    overflow-x: auto;

    :deep(.el-radio-group) {
      display: flex;
      flex-wrap: nowrap;
    }
  }

  .search-box {
    width: 100%;
  }

  .articles-section {
    padding: 24px 16px;
  }
}
</style>
