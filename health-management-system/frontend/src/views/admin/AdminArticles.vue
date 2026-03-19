<template>
  <!-- 文章管理列表页面 -->
  <div class="admin-articles">
    <!-- 页面标题卡片 -->
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <div class="title-section">
          <h2 class="page-title">文章管理</h2>
          <p class="page-desc">管理普通文章（非轮播图），支持新增、编辑、删除和搜索功能</p>
        </div>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          新增文章
        </el-button>
      </div>
    </el-card>

    <!-- 搜索筛选区域 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline class="search-form">
        <!-- 关键词搜索 -->
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入标题或内容关键词"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <!-- 分类筛选 -->
        <el-form-item label="分类">
          <el-select
            v-model="searchForm.category"
            placeholder="请选择分类"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="item in categoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <!-- 状态筛选 -->
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
            <el-option label="已下线" value="offline" />
          </el-select>
        </el-form-item>

        <!-- 日期范围 -->
        <el-form-item label="发布日期">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格区域 -->
    <el-card class="table-card" shadow="never">
      <!-- 批量操作工具栏 -->
      <div class="table-toolbar">
        <el-button
          type="danger"
          :icon="Delete"
          :disabled="selectedRows.length === 0"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
        <el-button
          type="success"
          :icon="Top"
          :disabled="selectedRows.length === 0"
          @click="handleBatchPublish"
        >
          批量发布
        </el-button>
        <span class="selection-count" v-if="selectedRows.length > 0">
          已选择 {{ selectedRows.length }} 项
        </span>
      </div>

      <!-- 文章表格 -->
      <el-table
        v-loading="loading"
        :data="articleList"
        stripe
        border
        @selection-change="handleSelectionChange"
        class="article-table"
      >
        <!-- 多选列 -->
        <el-table-column type="selection" width="55" align="center" />

        <!-- 文章ID -->
        <el-table-column prop="id" label="ID" width="80" align="center" />

        <!-- 封面图 -->
        <el-table-column label="封面" width="100" align="center">
          <template #default="{ row }">
            <div v-if="row.imageUrl" class="cover-wrapper">
              <el-image
                :src="getImageUrl(row.imageUrl)"
                :preview-src-list="[getImageUrl(row.imageUrl)]"
                fit="cover"
                class="cover-image"
                preview-teleported
              />
            </div>
            <div v-else class="cover-placeholder">
              <el-icon :size="24"><Picture /></el-icon>
              <span class="placeholder-text">暂无</span>
            </div>
          </template>
        </el-table-column>

        <!-- 标题 -->
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-text">{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- 标签 -->
        <el-table-column prop="tag" label="标签" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="row.tagType || 'info'">
              {{ row.tag || '未分类' }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 浏览量 -->
        <el-table-column prop="views" label="浏览量" width="100" align="center">
          <template #default="{ row }">
            <el-icon><View /></el-icon>
            {{ formatNumber(row.views) }}
          </template>
        </el-table-column>

        <!-- 状态 -->
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 创建时间 -->
        <el-table-column prop="createTime" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            <el-icon><Clock /></el-icon>
            {{ row.createTime }}
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                type="success"
                size="small"
                :icon="View"
                @click="handlePreview(row)"
              >
                预览
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="文章预览"
      width="800px"
      destroy-on-close
    >
      <div class="preview-content" v-if="currentArticle">
        <h2 class="preview-title">{{ currentArticle.title }}</h2>
        <div class="preview-meta">
          <span><el-icon><User /></el-icon> {{ currentArticle.author }}</span>
          <span><el-icon><Clock /></el-icon> {{ currentArticle.publishTime }}</span>
          <span><el-icon><View /></el-icon> {{ currentArticle.views }} 次浏览</span>
        </div>
        <el-divider />
        <div class="preview-body" v-html="currentArticle.content"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * AdminArticles.vue - 文章管理列表页面
 * 提供文章列表展示、搜索筛选、分页、批量操作等功能
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus,
  Search,
  Refresh,
  Delete,
  Edit,
  View,
  Top,
  Clock,
  User,
  Picture
} from '@element-plus/icons-vue'
import { deleteArticle, batchDeleteArticles } from '@/api/admin'
import request from '@/utils/request'
import { getImageUrl } from '@/utils/image'

// 路由实例
const router = useRouter()

// 默认封面图 - 使用本地图标代替外部服务
const defaultCover = ''

// 加载状态
const loading = ref(false)

// 预览对话框显示状态
const previewVisible = ref(false)

// 当前预览的文章
const currentArticle = ref(null)

// 选中的行数据
const selectedRows = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  status: '',
  dateRange: []
})

// 分类选项
const categoryOptions = [
  { label: '健康资讯', value: 'health' },
  { label: '疾病科普', value: 'disease' },
  { label: '饮食建议', value: 'diet' },
  { label: '运动指导', value: 'exercise' },
  { label: '心理健康', value: 'mental' },
  { label: '用药指南', value: 'medication' }
]

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 文章列表数据
const articleList = ref([])

/**
 * 获取分类标签文本
 * @param {string} value - 分类值
 */
const getCategoryLabel = (value) => {
  const category = categoryOptions.find(item => item.value === value)
  return category ? category.label : value
}

/**
 * 获取状态标签类型
 * @param {string} status - 状态值
 */
const getStatusType = (status) => {
  const typeMap = {
    published: 'success',
    draft: 'info',
    offline: 'danger'
  }
  return typeMap[status] || 'info'
}

/**
 * 获取状态标签文本
 * @param {string} status - 状态值
 */
const getStatusLabel = (status) => {
  const labelMap = {
    published: '已发布',
    draft: '草稿',
    offline: '已下线'
  }
  return labelMap[status] || status
}

/**
 * 格式化数字（超过1000显示为k）
 * @param {number} num - 数字
 */
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num
}

/**
 * 获取文章列表数据
 */
const fetchArticleList = async () => {
  loading.value = true
  try {
    // 调用真实API获取文章列表
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      ...searchForm,
      startDate: searchForm.dateRange?.[0],
      endDate: searchForm.dateRange?.[1]
    }
    const res = await request.get('/admin/articles', { params })
    // 注意：响应拦截器已经提取了 res.data，所以直接访问 list 和 total
    articleList.value = res?.list || []
    pagination.total = res?.total || 0
  } catch (error) {
    ElMessage.error('获取文章列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  pagination.page = 1
  fetchArticleList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.category = ''
  searchForm.status = ''
  searchForm.dateRange = []
  pagination.page = 1
  fetchArticleList()
}

/**
 * 处理表格选择变化
 * @param {Array} selection - 选中的行
 */
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

/**
 * 处理新增文章
 */
const handleAdd = () => {
  router.push('/admin/articles/edit')
}

/**
 * 处理编辑文章
 * @param {Object} row - 文章数据
 */
const handleEdit = (row) => {
  router.push(`/admin/articles/edit/${row.id}`)
}

/**
 * 处理预览文章
 * @param {Object} row - 文章数据
 */
const handlePreview = (row) => {
  currentArticle.value = row
  previewVisible.value = true
}

/**
 * 处理删除文章
 * @param {Object} row - 文章数据
 */
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文章 "${row.title}" 吗？删除后不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteArticle(row.id)
    ElMessage.success('删除成功')
    fetchArticleList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文章失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 处理批量删除
 */
const handleBatchDelete = async () => {
  const ids = selectedRows.value.map(row => row.id)
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${ids.length} 篇文章吗？删除后不可恢复！`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await batchDeleteArticles(ids)
    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchArticleList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

/**
 * 处理批量发布
 */
const handleBatchPublish = () => {
  const ids = selectedRows.value.map(row => row.id)
  ElMessageBox.confirm(
    `确定要发布选中的 ${ids.length} 篇文章吗？`,
    '确认批量发布',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  )
    .then(async () => {
      // 模拟批量发布请求
      // await request.post('/api/admin/articles/batch-publish', { ids })
      ElMessage.success('批量发布成功')
      selectedRows.value = []
      fetchArticleList()
    })
    .catch(() => {})
}

/**
 * 处理分页大小变化
 * @param {number} size - 每页条数
 */
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchArticleList()
}

/**
 * 处理页码变化
 * @param {number} page - 页码
 */
const handlePageChange = (page) => {
  pagination.page = page
  fetchArticleList()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchArticleList()
})
</script>

<style scoped>
/* 页面容器 */
.admin-articles {
  padding: 0;
}

/* 页面头部卡片 */
.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.page-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* 搜索卡片 */
.search-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

/* 表格卡片 */
.table-card {
  margin-bottom: 20px;
}

/* 表格工具栏 */
.table-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.selection-count {
  margin-left: auto;
  font-size: 14px;
  color: #606266;
}

/* 文章表格 */
.article-table {
  margin-bottom: 20px;
}

/* 封面图片 */
.cover-image {
  width: 80px;
  height: 56px;
  border-radius: 4px;
  object-fit: cover;
}

/* 封面占位 */
.cover-placeholder {
  width: 80px;
  height: 56px;
  border-radius: 4px;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 4px;
}

.cover-placeholder .placeholder-text {
  font-size: 12px;
}

/* 标题单元格 */
.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.carousel-tag {
  flex-shrink: 0;
}

.title-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 分页区域 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

/* 预览内容 */
.preview-content {
  padding: 10px;
}

.preview-title {
  margin: 0 0 15px;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  text-align: center;
}

.preview-meta {
  display: flex;
  justify-content: center;
  gap: 30px;
  font-size: 14px;
  color: #909399;
}

.preview-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.preview-body {
  line-height: 1.8;
  color: #606266;
}

/* 响应式适配 */
@media screen and (max-width: 1200px) {
  .search-form {
    flex-direction: column;
  }

  .search-form :deep(.el-form-item) {
    margin-bottom: 15px;
  }
}
</style>
