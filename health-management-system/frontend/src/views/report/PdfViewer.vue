<template>
  <div class="pdf-viewer-page">
    <!-- 顶部导航栏 -->
    <div class="pdf-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        <div class="file-info">
          <h3 class="file-name">{{ reportInfo?.report_name || '体检报告' }}</h3>
          <span class="file-meta">{{ reportInfo?.hospital_name }} · {{ formatDate(reportInfo?.exam_date) }}</span>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-action" @click="downloadPdf" v-if="pdfUrl">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          下载PDF
        </button>
      </div>
    </div>

    <!-- PDF预览区域 -->
    <div class="pdf-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载PDF...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <p>{{ error }}</p>
        <button class="btn-retry" @click="loadPdf">重新加载</button>
      </div>

      <div v-else-if="pdfUrl" class="pdf-wrapper">
        <!-- 使用 embed 标签替代 iframe，兼容性更好 -->
        <embed
          :src="pdfUrl"
          class="pdf-embed"
          type="application/pdf"
          width="100%"
          height="100%"
        />
      </div>

      <div v-else class="empty-state">
        <p>暂无PDF文件</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getReportDetail } from '@/api/report'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const pdfUrl = ref('')
const reportInfo = ref(null)

// 获取报告ID
const reportId = route.params.id

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 加载PDF
const loadPdf = async () => {
  if (!reportId) {
    error.value = '报告ID不存在'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const res = await getReportDetail(reportId)
    console.log('获取报告详情响应:', res)

    // 处理两种可能的响应结构
    // 结构1: {code: 200, data: {report: {...}}}
    // 结构2: {report: {...}, indicators: [...]}
    let reportData

    if (res.code === 200 && res.data) {
      // 结构1: 标准响应格式
      reportData = res.data.report || res.data
    } else if (res.report) {
      // 结构2: 直接返回report对象
      reportData = res.report
    } else {
      error.value = '获取报告失败，响应格式错误'
      console.error('未知的响应格式:', res)
      return
    }

    reportInfo.value = reportData
    console.log('报告数据:', reportData)

    // 构建PDF URL - 参考轮播图 getImageUrl 函数的实现
    let fileUrl = reportData?.fileUrl || reportData?.file_url || reportData?.pdfUrl || reportData?.pdf_url || reportData?.filePath || reportData?.file_path

    if (fileUrl) {
      // 如果已经是完整URL，直接使用
      if (fileUrl.startsWith('http://') || fileUrl.startsWith('https://')) {
        pdfUrl.value = fileUrl
      }
      // 如果已经是 /api/uploads/ 开头的路径，直接使用
      else if (fileUrl.startsWith('/api/uploads/')) {
        pdfUrl.value = fileUrl
      }
      // 处理旧格式路径 /uploads/xxx/xxx.pdf -> 转换为 /api/uploads/xxx/xxx.pdf
      else if (fileUrl.startsWith('/uploads/')) {
        pdfUrl.value = '/api' + fileUrl
      }
      // 处理相对路径 report/xxx.pdf -> 转换为 /api/uploads/report/xxx.pdf
      else {
        pdfUrl.value = '/api/uploads/' + fileUrl
      }
      console.log('PDF URL:', pdfUrl.value)
    } else {
      error.value = 'PDF文件不存在'
      console.error('未找到PDF文件URL，报告数据:', reportData)
    }
  } catch (err) {
    console.error('加载PDF失败:', err)
    error.value = '加载PDF失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 下载PDF
const downloadPdf = () => {
  if (!pdfUrl.value) return

  const link = document.createElement('a')
  link.href = pdfUrl.value
  link.download = `${reportInfo.value?.report_name || '体检报告'}.pdf`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  loadPdf()
})
</script>

<style scoped lang="scss">
.pdf-viewer-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

// 顶部导航栏
.pdf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 100;

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    .btn-back {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border: 1px solid #d9d9d9;
      background: #fff;
      border-radius: 6px;
      color: #595959;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        border-color: #1890ff;
        color: #1890ff;
      }
    }

    .file-info {
      .file-name {
        font-size: 16px;
        font-weight: 600;
        color: #262626;
        margin: 0 0 4px 0;
      }

      .file-meta {
        font-size: 13px;
        color: #8c8c8c;
      }
    }
  }

  .header-right {
    .btn-action {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border: 1px solid #1890ff;
      background: #1890ff;
      border-radius: 6px;
      color: #fff;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: #40a9ff;
        border-color: #40a9ff;
      }
    }
  }
}

// PDF容器
.pdf-container {
  flex: 1;
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 73px);
}

.pdf-wrapper {
  width: 100%;
  height: 100%;
  max-width: 1200px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.pdf-embed {
  width: 100%;
  height: calc(100vh - 121px);
  border: none;
}

// 加载状态
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #8c8c8c;

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top-color: #1890ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

// 错误状态
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #595959;

  .error-icon {
    color: #ff4d4f;
  }

  .btn-retry {
    padding: 8px 24px;
    border: 1px solid #1890ff;
    background: #fff;
    border-radius: 6px;
    color: #1890ff;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: #e6f7ff;
    }
  }
}

// 空状态
.empty-state {
  color: #8c8c8c;
  font-size: 14px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// 响应式
@media (max-width: 768px) {
  .pdf-header {
    flex-direction: column;
    gap: 12px;
    padding: 12px 16px;

    .header-left {
      width: 100%;

      .file-info {
        .file-name {
          font-size: 14px;
        }
      }
    }
  }

  .pdf-container {
    padding: 12px;
  }

  .pdf-embed {
    height: calc(100vh - 140px);
  }
}
</style>
