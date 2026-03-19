<template>
  <div class="article-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 文章内容 -->
    <template v-else-if="article">
      <!-- 文章头部 -->
      <header class="article-header" :style="{ background: article.gradient }">
        <div class="header-content">
          <div class="article-meta-top">
            <el-tag :type="article.tagType" size="large" effect="dark">{{ article.tag }}</el-tag>
            <span class="publish-date">
              <el-icon><Calendar /></el-icon>
              {{ formatDate(article.createTime) }}
            </span>
          </div>
          <h1 class="article-title">{{ article.title }}</h1>
          <p class="article-summary">{{ article.summary }}</p>
          <div class="article-stats">
            <span class="stat-item">
              <el-icon><View /></el-icon>
              {{ article.views }} 阅读
            </span>
            <span class="stat-item">
              <el-icon><Timer /></el-icon>
              {{ readTime }} 分钟阅读
            </span>
          </div>
        </div>
        <div class="header-icon">
          <el-icon :size="120" color="rgba(255,255,255,0.2)">
            <component :is="article.icon" />
          </el-icon>
        </div>
      </header>

      <!-- 文章主体 -->
      <main class="article-main">
        <div class="article-content-wrapper">
          <!-- 左侧文章内容 -->
          <div class="article-body">
            <div class="content-card">
              <div class="article-content" v-html="processedContent"></div>
            </div>

            <!-- 文章底部操作 -->
            <div class="article-actions">
              <el-button type="primary" size="large" @click="shareArticle">
                <el-icon><Share /></el-icon>
                分享文章
              </el-button>
              <el-button size="large" @click="printArticle">
                <el-icon><Printer /></el-icon>
                打印
              </el-button>
            </div>
          </div>

          <!-- 右侧相关推荐 -->
          <aside class="article-sidebar">
            <!-- 作者信息 -->
            <el-card class="sidebar-card author-card" v-if="article.author">
              <div class="author-info">
                <el-avatar :size="60" :icon="UserFilled" />
                <div class="author-details">
                  <h4>{{ article.author }}</h4>
                  <p>健康领域专家</p>
                </div>
              </div>
            </el-card>

            <!-- 相关文章推荐 -->
            <el-card class="sidebar-card related-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Collection /></el-icon>
                  <span>相关文章</span>
                </div>
              </template>
              <div v-if="relatedArticles.length === 0" class="empty-related">
                <el-empty description="暂无相关文章" :image-size="80" />
              </div>
              <ul v-else class="related-list">
                <li
                  v-for="item in relatedArticles"
                  :key="item.id"
                  class="related-item"
                  @click="navigateToArticle(item.id)"
                >
                  <div class="related-icon" :style="{ background: item.gradient }">
                    <el-icon><component :is="item.icon" /></el-icon>
                  </div>
                  <div class="related-info">
                    <h5>{{ item.title }}</h5>
                    <span>{{ item.views }} 阅读</span>
                  </div>
                </li>
              </ul>
            </el-card>

            <!-- 健康提示 -->
            <el-card class="sidebar-card tips-card">
              <template #header>
                <div class="card-header">
                  <el-icon><InfoFilled /></el-icon>
                  <span>健康提示</span>
                </div>
              </template>
              <p class="tips-content">本文内容仅供参考，不能替代专业医疗建议。如有健康问题，请及时咨询医生。</p>
            </el-card>
          </aside>
        </div>
      </main>
    </template>

    <!-- 错误状态 -->
    <el-empty
      v-else
      description="文章不存在或已下架"
      :image-size="200"
    >
      <el-button type="primary" @click="goBack">返回首页</el-button>
    </el-empty>
  </div>
</template>

<script setup>
/**
 * ArticleDetail.vue - 文章详情阅览页面
 * 展示健康知识的详细内容
 */
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Calendar,
  View,
  Timer,
  Share,
  Printer,
  UserFilled,
  Collection,
  InfoFilled
} from '@element-plus/icons-vue'
import { getArticle } from '@/api/article'

const route = useRoute()
const router = useRouter()

// 加载状态
const loading = ref(true)

// 文章数据
const article = ref(null)

// 相关文章列表
const relatedArticles = ref([])

// 计算阅读时间（按每分钟300字计算）
const readTime = computed(() => {
  if (!article.value?.content) return 1
  const textLength = article.value.content.replace(/<[^>]+>/g, '').length
  return Math.max(1, Math.ceil(textLength / 300))
})

// 处理文章内容，将 Markdown 转换为 HTML
const processedContent = computed(() => {
  if (!article.value?.content) return ''
  let content = article.value.content

  // 如果内容已经是 HTML 格式，直接返回
  if (content.includes('<') && content.includes('>')) {
    return content
  }

  // 处理 Markdown 格式
  // 1. 代码块（需要在行内代码之前处理）
  content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')

  // 2. 行内代码
  content = content.replace(/`([^`]+)`/g, '<code>$1</code>')

  // 3. 标题
  content = content.replace(/^###### (.*$)/gim, '<h6>$1</h6>')
  content = content.replace(/^##### (.*$)/gim, '<h5>$1</h5>')
  content = content.replace(/^#### (.*$)/gim, '<h4>$1</h4>')
  content = content.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  content = content.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  content = content.replace(/^# (.*$)/gim, '<h1>$1</h1>')

  // 4. 粗体和斜体
  content = content.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/\*(.*?)\*/g, '<em>$1</em>')
  content = content.replace(/__(.*?)__/g, '<strong>$1</strong>')
  content = content.replace(/_(.*?)_/g, '<em>$1</em>')

  // 5. 删除线
  content = content.replace(/~~(.*?)~~/g, '<del>$1</del>')

  // 6. 引用块
  content = content.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')

  // 7. 无序列表
  content = content.replace(/^\- (.*$)/gim, '<ul><li>$1</li></ul>')
  content = content.replace(/^\* (.*$)/gim, '<ul><li>$1</li></ul>')

  // 8. 有序列表
  content = content.replace(/^\d+\. (.*$)/gim, '<ol><li>$1</li></ol>')

  // 9. 链接
  content = content.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')

  // 10. 图片
  content = content.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')

  // 11. 分割线
  content = content.replace(/^---$/gim, '<hr />')
  content = content.replace(/^\*\*\*$/gim, '<hr />')
  content = content.replace(/^___$/gim, '<hr />')

  // 12. 换行符处理（段落）
  // 将连续的换行符分隔的文本包裹在 <p> 标签中
  const paragraphs = content.split(/\n\n+/)
  content = paragraphs.map(p => {
    p = p.trim()
    if (!p) return ''
    // 如果已经是块级元素，不添加 <p>
    if (p.match(/^<(h[1-6]|blockquote|pre|ul|ol|hr)/)) {
      return p
    }
    // 将单个换行符替换为 <br>
    p = p.replace(/\n/g, '<br>')
    return `<p>${p}</p>`
  }).join('\n')

  return content
})

/**
 * 获取文章详情
 */
const fetchArticleDetail = async () => {
  const articleId = route.params.id
  if (!articleId) {
    ElMessage.error('文章ID不能为空')
    loading.value = false
    return
  }

  loading.value = true
  try {
    const res = await getArticle(articleId)
    // request.js 拦截器已经返回了 res.data，所以这里直接使用 res
    article.value = res
    // 增加浏览量
    incrementViews(articleId)
    // 获取相关文章
    await fetchRelatedArticles()
  } catch (error) {
    console.error('获取文章详情失败:', error)
    ElMessage.error('获取文章详情失败')
  } finally {
    loading.value = false
  }
}

/**
 * 增加文章浏览量
 */
const incrementViews = async (articleId) => {
  // 浏览量增加由后端处理，这里可以添加本地记录防止重复计数
  const viewedArticles = JSON.parse(localStorage.getItem('viewedArticles') || '[]')
  if (!viewedArticles.includes(articleId)) {
    viewedArticles.push(articleId)
    localStorage.setItem('viewedArticles', JSON.stringify(viewedArticles))
  }
}

/**
 * 获取相关文章
 */
const fetchRelatedArticles = async () => {
  try {
    // 这里可以调用API获取相关文章，暂时使用模拟数据
    // const res = await getArticles({ category: article.value.category, limit: 5 })
    // relatedArticles.value = res.data.filter(item => item.id !== article.value.id)
    relatedArticles.value = []
  } catch (error) {
    console.error('获取相关文章失败:', error)
  }
}

/**
 * 返回上一页
 */
const goBack = () => {
  router.back()
}

/**
 * 跳转到其他文章
 */
const navigateToArticle = (articleId) => {
  router.push(`/article/${articleId}`)
}

/**
 * 分享文章
 */
const shareArticle = () => {
  if (navigator.share) {
    navigator.share({
      title: article.value.title,
      text: article.value.summary,
      url: window.location.href
    })
  } else {
    // 复制链接到剪贴板
    navigator.clipboard.writeText(window.location.href)
    ElMessage.success('链接已复制到剪贴板')
  }
}

/**
 * 打印文章
 */
const printArticle = () => {
  window.print()
}

/**
 * 格式化日期
 */
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 页面加载时获取文章详情
onMounted(() => {
  fetchArticleDetail()
})
</script>

<style scoped lang="scss">
.article-detail-container {
  min-height: 100vh;
  background: #f5f7fa;
}

// 加载状态
.loading-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

// 文章头部
.article-header {
  position: relative;
  padding: 60px 0;
  color: #1a1a1a;
  overflow: hidden;

  .header-content {
    position: relative;
    z-index: 2;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 40px;
  }

  .article-meta-top {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;

    .publish-date {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      color: #606266;
    }
  }

  .article-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 16px;
    line-height: 1.3;
    color: #1a1a1a;
  }

  .article-summary {
    font-size: 18px;
    line-height: 1.6;
    color: #606266;
    max-width: 700px;
    margin-bottom: 24px;
  }

  .article-stats {
    display: flex;
    gap: 24px;

    .stat-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      color: #909399;
    }
  }

  .header-icon {
    position: absolute;
    right: 60px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
  }
}

// 文章主体
.article-main {
  max-width: 1200px;
  margin: -40px auto 0;
  padding: 0 20px 60px;
  position: relative;
  z-index: 3;
}

.article-content-wrapper {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

// 文章内容
.article-body {
  .content-card {
    background: white;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }

  .article-content {
    font-size: 16px;
    line-height: 1.8;
    color: #333;

    /* 标题样式 */
    :deep(h1) {
      font-size: 28px;
      font-weight: 600;
      margin: 36px 0 20px;
      color: #1a1a1a;
      padding-bottom: 12px;
      border-bottom: 2px solid #409eff;
    }

    :deep(h2) {
      font-size: 24px;
      font-weight: 600;
      margin: 32px 0 16px;
      color: #1a1a1a;
      padding-bottom: 10px;
      border-bottom: 1px solid #e4e7ed;
    }

    :deep(h3) {
      font-size: 20px;
      font-weight: 600;
      margin: 24px 0 12px;
      color: #2c3e50;
    }

    :deep(h4) {
      font-size: 18px;
      font-weight: 600;
      margin: 20px 0 10px;
      color: #34495e;
    }

    :deep(h5), :deep(h6) {
      font-size: 16px;
      font-weight: 600;
      margin: 16px 0 8px;
      color: #34495e;
    }

    /* 段落样式 */
    :deep(p) {
      margin-bottom: 16px;
      text-align: justify;
    }

    /* 列表样式 */
    :deep(ul), :deep(ol) {
      margin: 16px 0;
      padding-left: 24px;

      li {
        margin-bottom: 8px;
      }
    }

    :deep(ul) {
      list-style-type: disc;
    }

    :deep(ol) {
      list-style-type: decimal;
    }

    /* 任务列表 */
    :deep(.vditor-task) {
      list-style: none;
      padding-left: 0;

      input[type="checkbox"] {
        margin-right: 8px;
        cursor: default;
      }
    }

    /* 图片样式 */
    :deep(img) {
      max-width: 100%;
      border-radius: 8px;
      margin: 20px 0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    /* 引用块样式 */
    :deep(blockquote) {
      border-left: 4px solid #409eff;
      padding: 16px 20px;
      margin: 20px 0;
      background: #f5f7fa;
      border-radius: 0 8px 8px 0;
      font-style: italic;
      color: #606266;

      p:last-child {
        margin-bottom: 0;
      }
    }

    /* 代码样式 */
    :deep(code) {
      background: #f5f7fa;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 14px;
      color: #e83e8c;
    }

    :deep(pre) {
      background: #2d2d2d;
      color: #f8f8f2;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 20px 0;

      code {
        background: transparent;
        color: inherit;
        padding: 0;
        font-size: 14px;
      }
    }

    /* 表格样式 */
    :deep(table) {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 14px;

      th, td {
        border: 1px solid #e4e7ed;
        padding: 12px;
        text-align: left;
      }

      th {
        background: #f5f7fa;
        font-weight: 600;
        color: #1a1a1a;
      }

      tr:nth-child(even) {
        background: #fafafa;
      }

      tr:hover {
        background: #f5f7fa;
      }
    }

    /* 链接样式 */
    :deep(a) {
      color: #409eff;
      text-decoration: none;
      border-bottom: 1px solid transparent;
      transition: border-color 0.3s;

      &:hover {
        border-bottom-color: #409eff;
      }
    }

    /* 分割线 */
    :deep(hr) {
      border: none;
      border-top: 1px solid #e4e7ed;
      margin: 32px 0;
    }

    /* 强调样式 */
    :deep(strong) {
      font-weight: 600;
      color: #1a1a1a;
    }

    :deep(em) {
      font-style: italic;
    }

    /* 删除线 */
    :deep(del) {
      text-decoration: line-through;
      color: #909399;
    }

    /* 上标下标 */
    :deep(sup), :deep(sub) {
      font-size: 12px;
    }

    /* 脚注 */
    :deep(.vditor-footnotes) {
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid #e4e7ed;
      font-size: 14px;
      color: #606266;
    }

    /* 数学公式 */
    :deep(.katex) {
      font-size: 1.1em;
    }

    /* 图表容器 */
    :deep(.vditor-graph) {
      text-align: center;
      margin: 20px 0;
    }

    /* 音频视频 */
    :deep(audio), :deep(video) {
      max-width: 100%;
      margin: 20px 0;
    }

    /* 嵌入内容 */
    :deep(iframe) {
      max-width: 100%;
      border: none;
      border-radius: 8px;
      margin: 20px 0;
    }
  }

  .article-actions {
    display: flex;
    gap: 16px;
    margin-top: 32px;
    padding-top: 32px;
    border-top: 1px solid #e4e7ed;
  }
}

// 侧边栏
.article-sidebar {
  .sidebar-card {
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);

    :deep(.el-card__header) {
      padding: 16px 20px;
      border-bottom: 1px solid #e4e7ed;
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      color: #1a1a1a;
    }
  }

  .author-card {
    .author-info {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 8px;

      .author-details {
        h4 {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 4px;
        }

        p {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .related-card {
    .empty-related {
      padding: 20px 0;
    }

    .related-list {
      list-style: none;
      padding: 0;
      margin: 0;

      .related-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          background: #f5f7fa;
        }

        &:not(:last-child) {
          border-bottom: 1px solid #e4e7ed;
        }

        .related-icon {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
        }

        .related-info {
          flex: 1;
          min-width: 0;

          h5 {
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 4px;
            color: #1a1a1a;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          span {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }
  }

  .tips-card {
    .tips-content {
      font-size: 14px;
      line-height: 1.6;
      color: #606266;
      padding: 8px;
    }
  }
}

// 响应式适配
@media screen and (max-width: 1024px) {
  .article-content-wrapper {
    grid-template-columns: 1fr;
  }

  .article-sidebar {
    order: 2;
  }
}

@media screen and (max-width: 768px) {
  .article-header {
    padding: 40px 0;

    .header-content {
      padding: 0 20px;
    }

    .article-title {
      font-size: 24px;
    }

    .article-summary {
      font-size: 14px;
    }

    .header-icon {
      display: none;
    }
  }

  .article-main {
    margin-top: -20px;
    padding: 0 16px 40px;
  }

  .article-body {
    .content-card {
      padding: 24px;
    }
  }
}

// 打印样式
@media print {
  .article-header {
    background: white !important;
    color: black !important;
    padding: 20px 0;

    .back-btn,
    .header-icon {
      display: none;
    }
  }

  .article-sidebar,
  .article-actions {
    display: none;
  }

  .article-content-wrapper {
    grid-template-columns: 1fr;
  }
}
</style>
